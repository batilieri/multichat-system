"""
Views para processamento de webhooks do WhatsApp
Integração com o sistema MultiChat para salvar mensagens nos chats
"""

import json
import logging
import re
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import Chat, Mensagem, Cliente, WhatsappInstance
from webhook.models import WebhookEvent, Sender
from .media_processor import process_webhook_media
from core.webhook_media_analyzer import analisar_webhook_whatsapp, processar_webhook_whatsapp
from api.utils import determine_from_me_saas

logger = logging.getLogger(__name__)

# Cache para armazenar atualizações pendentes
REALTIME_CACHE_KEY = "realtime_updates"
REALTIME_CACHE_TIMEOUT = 300  # 5 minutos

# Signal movido para signals.py

def normalize_chat_id(chat_id):
    """
    Normaliza o chat_id para garantir que seja um número de telefone válido
    Remove sufixos como @lid, @c.us, etc e extrai apenas o número
    Retorna None se for um grupo (contém @g.us ou padrão de grupo)
    """
    if not chat_id:
        return None
    
    # Verificar se é um grupo (contém @g.us)
    if '@g.us' in chat_id:
        logger.info(f"🚫 Ignorando grupo: {chat_id}")
        return None
    
    # Remover sufixos comuns do WhatsApp
    chat_id = re.sub(r'@[^.]+\.us$', '', chat_id)  # Remove @c.us, @lid, etc
    chat_id = re.sub(r'@[^.]+$', '', chat_id)      # Remove outros sufixos
    
    # Extrair apenas números
    numbers_only = re.sub(r'[^\d]', '', chat_id)
    
    # Verificar se é um grupo baseado no padrão (números longos que começam com 120363)
    if len(numbers_only) > 15 and numbers_only.startswith('120363'):
        logger.info(f"🚫 Ignorando grupo (padrão 120363): {chat_id}")
        return None
    
    # Validar se é um número de telefone válido (mínimo 10 dígitos)
    if len(numbers_only) >= 10:
        return numbers_only
    
    logger.warning(f"Chat ID inválido após normalização: {chat_id} -> {numbers_only}")
    return chat_id  # Retornar original se não conseguir normalizar

def extract_profile_picture_robust(webhook_data):
    """Extrai foto de perfil de forma mais robusta do webhook"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Verificar se é uma mensagem enviada pelo usuário (fromMe: true)
    from_me = webhook_data.get('fromMe', False)
    
    # Lista de possíveis locais onde a foto pode estar
    extraction_paths = []
    
    if from_me:
        # Se é mensagem enviada pelo usuário, PRIORIZAR a foto do CHAT (contato/grupo)
        # e evitar usar a foto do SENDER (usuário)
        extraction_paths = [
            # PRIORIDADE 1: Foto do chat (contato/grupo)
            ('chat.profilePicture', lambda data: data.get('chat', {}).get('profilePicture')),
            ('chat.profile_picture', lambda data: data.get('chat', {}).get('profile_picture')),
            
            # PRIORIDADE 2: Nível raiz (pode ser do chat)
            ('root.profilePicture', lambda data: data.get('profilePicture')),
            ('root.profile_picture', lambda data: data.get('profile_picture')),
            
            # PRIORIDADE 3: Dentro de msgContent
            ('msgContent.profilePicture', lambda data: data.get('msgContent', {}).get('profilePicture')),
            
            # PRIORIDADE 4: Dentro de data (estrutura aninhada)
            ('data.chat.profilePicture', lambda data: data.get('data', {}).get('chat', {}).get('profilePicture')),
            
            # ÚLTIMA OPÇÃO: Sender (apenas se não houver outras opções)
            ('sender.profilePicture', lambda data: data.get('sender', {}).get('profilePicture')),
            ('sender.profile_picture', lambda data: data.get('sender', {}).get('profile_picture')),
            ('data.sender.profilePicture', lambda data: data.get('data', {}).get('sender', {}).get('profilePicture')),
        ]
        logger.info("🔄 Mensagem enviada pelo usuário - priorizando foto do chat/contato")
    else:
        # Se é mensagem recebida, usar a lógica normal
        extraction_paths = [
            # Dados do sender
            ('sender.profilePicture', lambda data: data.get('sender', {}).get('profilePicture')),
            ('sender.profile_picture', lambda data: data.get('sender', {}).get('profile_picture')),
            
            # Dados do chat
            ('chat.profilePicture', lambda data: data.get('chat', {}).get('profilePicture')),
            ('chat.profile_picture', lambda data: data.get('chat', {}).get('profile_picture')),
            
            # Nível raiz
            ('root.profilePicture', lambda data: data.get('profilePicture')),
            ('root.profile_picture', lambda data: data.get('profile_picture')),
            
            # Dentro de msgContent (algumas APIs colocam aqui)
            ('msgContent.profilePicture', lambda data: data.get('msgContent', {}).get('profilePicture')),
            
            # Dentro de data (estrutura aninhada)
            ('data.sender.profilePicture', lambda data: data.get('data', {}).get('sender', {}).get('profilePicture')),
            ('data.chat.profilePicture', lambda data: data.get('data', {}).get('chat', {}).get('profilePicture')),
        ]
        logger.info("📥 Mensagem recebida - usando lógica normal")
    
    for path_name, extractor in extraction_paths:
        try:
            result = extractor(webhook_data)
            if result and isinstance(result, str) and result.strip():
                profile_url = result.strip()
                
                # Validar se parece uma URL válida
                if profile_url.startswith(('http://', 'https://', 'data:image/')):
                    logger.info(f"🖼️ Foto de perfil extraída de {path_name}: {profile_url[:50]}...")
                    return profile_url
                else:
                    logger.warning(f"⚠️ URL inválida em {path_name}: {profile_url[:50]}...")
        except Exception as e:
            logger.error(f"❌ Erro ao extrair de {path_name}: {e}")
    
    logger.info("🖼️ Nenhuma foto de perfil encontrada no webhook")
    return None

@csrf_exempt
def webhook_receiver(request):
    """
    Recebe webhooks do WhatsApp e processa mídias automaticamente
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        # Obter dados do webhook
        webhook_data = json.loads(request.body)
        
        # Extrair informações básicas
        instance_id = webhook_data.get('instanceId')
        event_type = webhook_data.get('event')
        message_id = webhook_data.get('messageId')
        
        if not instance_id:
            return JsonResponse({'error': 'instanceId não fornecido'}, status=400)
        
        print(f"📨 Webhook recebido: {event_type} - {message_id}")
        print(f"📊 Dados do webhook: {json.dumps(webhook_data, indent=2)}")
        
        # Processar diferentes tipos de eventos
        if event_type == 'messages.upsert':
            success = process_webhook_message(webhook_data, event_type)
        elif event_type == 'messages.update':
            success = process_webhook_message(webhook_data, event_type)
        elif event_type == 'presence.update':
            success = process_webhook_presence(webhook_data)
        elif event_type == 'connection.update':
            success = process_webhook_connection(webhook_data, 'connect')
        elif event_type == 'disconnect':
            success = process_webhook_connection(webhook_data, 'disconnect')
        else:
            # Tentar processar como mensagem genérica
            success = process_whatsapp_message(webhook_data, event_type)
        
        if success:
            print(f"✅ Webhook processado com sucesso: {event_type}")
            return JsonResponse({'status': 'success', 'event': event_type})
        else:
            print(f"❌ Falha ao processar webhook: {event_type}")
            return JsonResponse({'error': 'Falha ao processar webhook'}, status=500)
            
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {e}")
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def webhook_send_message(request):
    """
    Webhook específico para mensagens enviadas
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        webhook_data = json.loads(request.body)
        print(f"📤 WEBHOOK ENVIAR MENSAGEM: {webhook_data}")
        
        # Processar apenas mensagens enviadas (fromMe: true)
        if webhook_data.get('fromMe') or webhook_data.get('data', {}).get('fromMe'):
            return process_webhook_message(webhook_data, 'send_message')
        else:
            return JsonResponse({'status': 'ignored', 'message': 'Não é mensagem enviada'})
            
    except Exception as e:
        logger.error(f"❌ Erro no webhook send_message: {e}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


@csrf_exempt
def webhook_receive_message(request):
    """
    Webhook específico para mensagens recebidas
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        webhook_data = json.loads(request.body)
        print(f"📥 WEBHOOK RECEBER MENSAGEM: {webhook_data}")
        
        # Processar apenas mensagens recebidas (fromMe: false)
        if not webhook_data.get('fromMe') and not webhook_data.get('data', {}).get('fromMe'):
            return process_webhook_message(webhook_data, 'receive_message')
        else:
            return JsonResponse({'status': 'ignored', 'message': 'Não é mensagem recebida'})
            
    except Exception as e:
        logger.error(f"❌ Erro no webhook receive_message: {e}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


@csrf_exempt
def webhook_chat_presence(request):
    """
    Webhook específico para presença do chat
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        webhook_data = json.loads(request.body)
        print(f"👥 WEBHOOK PRESENÇA DO CHAT: {webhook_data}")
        
        # Processar eventos de presença
        return process_webhook_presence(webhook_data)
            
    except Exception as e:
        logger.error(f"❌ Erro no webhook chat_presence: {e}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


@csrf_exempt
def webhook_message_status(request):
    """
    Webhook específico para status da mensagem
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        webhook_data = json.loads(request.body)
        print(f"📊 WEBHOOK STATUS DA MENSAGEM: {webhook_data}")
        
        # Processar eventos de status
        return process_webhook_status(webhook_data)
            
    except Exception as e:
        logger.error(f"❌ Erro no webhook message_status: {e}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


@csrf_exempt
def webhook_connect(request):
    """
    Webhook específico para conexão
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        webhook_data = json.loads(request.body)
        print(f"🔗 WEBHOOK CONECTAR: {webhook_data}")
        
        # Processar eventos de conexão
        return process_webhook_connection(webhook_data, 'connect')
            
    except Exception as e:
        logger.error(f"❌ Erro no webhook connect: {e}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


@csrf_exempt
def webhook_disconnect(request):
    """
    Webhook específico para desconexão
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        webhook_data = json.loads(request.body)
        print(f"🔌 WEBHOOK DESCONECTAR: {webhook_data}")
        
        # Processar eventos de desconexão
        return process_webhook_connection(webhook_data, 'disconnect')
            
    except Exception as e:
        logger.error(f"❌ Erro no webhook disconnect: {e}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


def process_webhook_message(webhook_data, event_type):
    """Processa mensagens de webhook com download automático de mídias"""
    try:
        print("🎯 WhatsApp detectado!")
        print("🔄 Processando dados do WhatsApp...")
        
        # Extrair dados básicos
        instance_id = webhook_data.get('instanceId')
        message_id = webhook_data.get('messageId')
        from_me = webhook_data.get('fromMe', False)
        is_group = webhook_data.get('isGroup', False)
        
        # Buscar cliente e instância
        cliente = None
        instance = None
        
        try:
            instance = WhatsappInstance.objects.get(instance_id=instance_id)
            cliente = instance.cliente
            print(f"👤 Cliente: {cliente.nome}")
        except WhatsappInstance.DoesNotExist:
            print(f"❌ Instância não encontrada: {instance_id}")
            return False
        
        # Processar mídia automaticamente se presente
        msg_content = webhook_data.get('msgContent', {})
        media_downloaded = process_media_automatically(webhook_data, cliente, instance)
        
        if media_downloaded:
            print(f"✅ Mídia processada automaticamente: {message_id}")
        
        # Continuar com o processamento normal
        return process_whatsapp_message(webhook_data, event_type)
        
    except Exception as e:
        print(f"❌ Erro ao processar webhook: {e}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)

def process_media_automatically(webhook_data, cliente, instance):
    """Processa mídias automaticamente quando recebidas via webhook"""
    try:
        msg_content = webhook_data.get('msgContent', {})
        message_id = webhook_data.get('messageId')
        
        # Detectar tipo de mídia
        media_types = {
            'imageMessage': 'image',
            'videoMessage': 'video', 
            'audioMessage': 'audio',
            'documentMessage': 'document',
            'stickerMessage': 'sticker'
        }
        
        detected_media = None
        media_type = None
        
        for content_key, media_type_name in media_types.items():
            if content_key in msg_content:
                detected_media = msg_content[content_key]
                media_type = media_type_name
                break
        
        if not detected_media:
            return False
        
        print(f"📎 Mídia detectada: {media_type}")
        print(f"📋 Dados da mídia: {list(detected_media.keys())}")
        
        # CRIAÇÃO AUTOMÁTICA DE PASTAS DE MÍDIA
        # Buscar chat baseado no sender_id
        sender = webhook_data.get('sender', {})
        sender_id = sender.get('id', '')
        
        if sender_id:
            # Normalizar chat_id
            chat_id = normalize_chat_id(sender_id)
            
            if chat_id:
                # Buscar ou criar chat
                chat, created = Chat.objects.get_or_create(
                    chat_id=chat_id,
                    cliente=cliente,
                    defaults={
                        "status": "active",
                        "canal": "whatsapp",
                        "data_inicio": timezone.now(),
                        "last_message_at": timezone.now()
                    }
                )
                
                if chat:
                    # Criar pasta específica para o tipo de mídia
                    if media_type == 'audio':
                        pasta_criada = criar_pasta_audio_automatica(chat, instance, message_id)
                        if pasta_criada:
                            print(f"🎵 Pasta de áudio criada automaticamente: {pasta_criada}")
                    elif media_type == 'image':
                        pasta_criada = criar_pasta_imagem_automatica(chat, instance, message_id)
                        if pasta_criada:
                            print(f"🖼️ Pasta de imagem criada automaticamente: {pasta_criada}")
                    elif media_type == 'video':
                        pasta_criada = criar_pasta_video_automatica(chat, instance, message_id)
                        if pasta_criada:
                            print(f"🎬 Pasta de vídeo criada automaticamente: {pasta_criada}")
                    elif media_type == 'document':
                        pasta_criada = criar_pasta_documento_automatica(chat, instance, message_id)
                        if pasta_criada:
                            print(f"📄 Pasta de documento criada automaticamente: {pasta_criada}")
                    elif media_type == 'sticker':
                        pasta_criada = criar_pasta_sticker_automatica(chat, instance, message_id)
                        if pasta_criada:
                            print(f"😀 Pasta de sticker criada automaticamente: {pasta_criada}")
        
        # Extrair dados necessários para download
        media_key = detected_media.get('mediaKey', '')
        direct_path = detected_media.get('directPath', '')
        mimetype = detected_media.get('mimetype', '')
        file_length = detected_media.get('fileLength', 0)
        caption = detected_media.get('caption', '')
        
        # Dados do remetente
        sender_name = sender.get('pushName', 'Desconhecido')
        
        # Fazer download da mídia
        if media_key and direct_path and mimetype:
            print(f"🔄 Iniciando download da mídia...")
            
            # Preparar dados para W-API
            media_data = {
                'mediaKey': media_key,
                'directPath': direct_path,
                'type': media_type,
                'mimetype': mimetype
            }
            
            # Fazer download via W-API
            wapi_result = download_media_via_wapi(
                instance.instance_id,
                instance.token,
                media_data
            )
            
            if wapi_result and wapi_result.get('fileLink'):
                # Salvar arquivo
                file_path = save_media_file(
                    wapi_result['fileLink'],
                    media_type,
                    message_id,
                    sender_name,
                    cliente,
                    instance
                )
                
                if file_path:
                    print(f"✅ Mídia processada com sucesso!")
                    print(f"📁 Arquivo salvo: {file_path}")
                    return True
                else:
                    print(f"❌ Falha ao salvar arquivo")
                    return False
            else:
                print(f"❌ Falha no download via W-API")
                return False
        else:
            print(f"⚠️ Dados insuficientes para download:")
            print(f"   mediaKey: {'✅' if media_key else '❌'}")
            print(f"   directPath: {'✅' if direct_path else '❌'}")
            print(f"   mimetype: {'✅' if mimetype else '❌'}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao processar mídia automaticamente: {e}")
        import traceback
        traceback.print_exc()
        return False


def process_webhook_presence(webhook_data):
    """
    Processa webhook de presença do chat
    """
    try:
        instance_id = webhook_data.get('instanceId')
        
        if not instance_id:
            return JsonResponse({'error': 'instanceId não fornecido'}, status=400)
        
        # Buscar instância no banco
        try:
            instance = WhatsappInstance.objects.get(instance_id=instance_id)
            cliente = instance.cliente
        except WhatsappInstance.DoesNotExist:
            return JsonResponse({'error': f'Instância {instance_id} não encontrada'}, status=404)
        
        # Criar evento de webhook
        event = WebhookEvent.objects.create(
            cliente=cliente,
            instance_id=instance_id,
            event_type="chat_presence",
            raw_data=webhook_data,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        logger.info(f"✅ Evento de presença processado: {event.event_id}")
        return JsonResponse({'status': 'success', 'event_id': str(event.event_id)})
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar webhook de presença: {e}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


def process_webhook_status(webhook_data):
    """
    Processa webhook de status da mensagem
    """
    try:
        instance_id = webhook_data.get('instanceId')
        
        if not instance_id:
            return JsonResponse({'error': 'instanceId não fornecido'}, status=400)
        
        # Buscar instância no banco
        try:
            instance = WhatsappInstance.objects.get(instance_id=instance_id)
            cliente = instance.cliente
        except WhatsappInstance.DoesNotExist:
            return JsonResponse({'error': f'Instância {instance_id} não encontrada'}, status=404)
        
        # Criar evento de webhook
        event = WebhookEvent.objects.create(
            cliente=cliente,
            instance_id=instance_id,
            event_type="message_status",
            raw_data=webhook_data,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        logger.info(f"✅ Evento de status processado: {event.event_id}")
        return JsonResponse({'status': 'success', 'event_id': str(event.event_id)})
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar webhook de status: {e}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


def process_webhook_connection(webhook_data, connection_type):
    """
    Processa webhook de conexão/desconexão
    """
    try:
        instance_id = webhook_data.get('instanceId')
        
        if not instance_id:
            return JsonResponse({'error': 'instanceId não fornecido'}, status=400)
        
        # Buscar instância no banco
        try:
            instance = WhatsappInstance.objects.get(instance_id=instance_id)
            cliente = instance.cliente
        except WhatsappInstance.DoesNotExist:
            return JsonResponse({'error': f'Instância {instance_id} não encontrada'}, status=404)
        
        # Atualizar status da instância
        if connection_type == 'connect':
            instance.status = 'conectado'
            instance.data_conexao = timezone.now()
        else:  # disconnect
            instance.status = 'desconectado'
            instance.data_desconexao = timezone.now()
        
        instance.save()
        
        # Criar evento de webhook
        event = WebhookEvent.objects.create(
            cliente=cliente,
            instance_id=instance_id,
            event_type=f"instance_{connection_type}",
            raw_data=webhook_data,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        logger.info(f"✅ Evento de {connection_type} processado: {event.event_id}")
        return JsonResponse({'status': 'success', 'event_id': str(event.event_id)})
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar webhook de {connection_type}: {e}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


def process_whatsapp_message(webhook_data, event):
    """
    Processa uma mensagem do WhatsApp e salva no sistema
    """
    try:
        with transaction.atomic():
            # Extrair dados da mensagem
            messages = webhook_data.get('data', {}).get('messages', [])
            
            if not messages:
                logger.warning("Nenhuma mensagem encontrada no webhook")
                return JsonResponse({'status': 'ignored', 'message': 'Nenhuma mensagem encontrada'})
            
            # Processar cada mensagem
            for message_data in messages:
                success = save_message_to_chat(webhook_data, event)
                if not success:
                    logger.error(f"Falha ao salvar mensagem: {message_data.get('key', {}).get('id', 'unknown')}")
                    return JsonResponse({'error': 'Falha ao salvar mensagem'}, status=500)
            
            return JsonResponse({'status': 'success', 'message': 'Mensagem processada com sucesso'})
            
    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem: {e}")
        return JsonResponse({'error': 'Erro interno do servidor'}, status=500)


def save_message_to_chat(payload, event):
    """
    Salva a mensagem no sistema de chats principal
    """
    try:
        raw_chat_id = payload.get("chat", {}).get("id", "")
        # Normalizar o chat_id para garantir que seja um número de telefone
        chat_id = normalize_chat_id(raw_chat_id)
        
        if not chat_id:
            logger.error(f"Chat ID inválido: {raw_chat_id}")
            return False
        
        logger.info(f"📱 Chat ID normalizado: {raw_chat_id} -> {chat_id}")
        
        # Extrair informações básicas
        message_key = payload.get('key', {})
        message_id = message_key.get('id', '')
        instance_id = payload.get('instanceId', '')
        # Usar função centralizada
        from_me = determine_from_me_saas(payload, instance_id)
        
        logger.info(f"🔍 Determinação from_me: sender_id={payload.get('sender', {}).get('id', '')}, instance_id={payload.get('instanceId', '')}, from_me={from_me}")
        
        # Verificar se já existe usando message_id (mais confiável)
        if message_id and Mensagem.objects.filter(message_id=message_id).exists():
            logger.info(f"Mensagem já existe (message_id): {message_id}")
            return True
        
        # Verificação adicional por chat_id e timestamp (fallback)
        # Comentado temporariamente para evitar erro de lookup
        # if Mensagem.objects.filter(chat__chat_id=chat_id, data_envio__timestamp=payload.get('messageTimestamp', 0)).exists():
        #     logger.info(f"Mensagem já existe (timestamp): {message_id}")
        #     return True
        
        # Encontrar ou criar o chat
        # Primeiro tentar encontrar um chat existente
        chat = Chat.objects.filter(chat_id=chat_id).first()
        
        if not chat:
            # Se não existir, criar um novo chat
            # Buscar o cliente da instância
            try:
                instance = WhatsappInstance.objects.get(instance_id=instance_id)
                cliente = instance.cliente
            except WhatsappInstance.DoesNotExist:
                logger.error(f"Instância {instance_id} não encontrada")
                return False
            
            chat = Chat.objects.create(
                chat_id=chat_id,
                cliente=cliente,  # Associar ao cliente correto
                status="active",
                canal="whatsapp",
                data_inicio=timezone.now(),
                last_message_at=timezone.now()
            )
            logger.info(f"✅ Chat criado: {chat_id} para cliente: {cliente.nome}")
        else:
            # Se o chat existir mas não tiver cliente, associar
            if not chat.cliente:
                try:
                    instance = WhatsappInstance.objects.get(instance_id=instance_id)
                    chat.cliente = instance.cliente
                    chat.save()
                    logger.info(f"✅ Chat {chat_id} associado ao cliente: {instance.cliente.nome}")
                except WhatsappInstance.DoesNotExist:
                    logger.error(f"Instância {instance_id} não encontrada para chat {chat_id}")
                    return False
        
        if not chat:
            logger.error(f"Não foi possível encontrar/criar chat para: {chat_id}")
            return False
        
        # Determinar tipo de mensagem
        message_type = detect_message_type(payload)
        
        # Extrair conteúdo da mensagem
        content = extract_message_content(payload, message_type)
        
        # Determinar remetente
        if from_me:
            remetente = "Elizeu Batiliere"  # Nome do usuário atual
        else:
            # Usar o nome do remetente do webhook
            sender_data = payload.get('sender', {})
            remetente = sender_data.get('pushName', '') or sender_data.get('name', '') or chat_id.split('@')[0]
        
        # Criar mensagem
        mensagem = Mensagem.objects.create(
            chat=chat,
            remetente=remetente,
            conteudo=content,
            tipo=message_type,
            lida=False,
            from_me=from_me,
            message_id=message_id  # Adicionar message_id para evitar duplicatas
        )
        
        # Atualizar última mensagem do chat
        chat.last_message_at = datetime.fromtimestamp(payload.get('messageTimestamp', 0))
        chat.save()
        
        logger.info(f"✅ Mensagem salva: {message_id} - Tipo: {message_type} - FromMe: {from_me}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar mensagem: {e}")
        return False


def save_message_to_chat_with_from_me(payload, event, from_me, cliente):
    """
    Salva a mensagem no sistema de chats principal com from_me já determinado
    """
    try:
        raw_chat_id = payload.get("chat", {}).get("id", "")
        # Normalizar o chat_id para garantir que seja um número de telefone
        chat_id = normalize_chat_id(raw_chat_id)
        
        if not chat_id:
            logger.error(f"Chat ID inválido: {raw_chat_id}")
            return False
        
        logger.info(f"📱 Chat ID normalizado: {raw_chat_id} -> {chat_id}")
        
        message_key = payload.get('key', {})
        message_id = message_key.get('id', '')
        
        logger.info(f"🔍 Salvando mensagem com from_me={from_me} para cliente: {cliente.nome if cliente else 'N/A'}")
        
        # Verificar se já existe usando message_id (mais confiável)
        if message_id and Mensagem.objects.filter(message_id=message_id).exists():
            logger.info(f"Mensagem já existe (message_id): {message_id}")
            return True
        
        # Verificação adicional por chat_id e timestamp (fallback)
        # Comentado temporariamente para evitar erro de lookup
        # if Mensagem.objects.filter(chat__chat_id=chat_id, data_envio__timestamp=payload.get('messageTimestamp', 0)).exists():
        #     logger.info(f"Mensagem já existe (timestamp): {message_id}")
        #     return True
        
        # Encontrar ou criar o chat associado ao cliente
        chat, created = Chat.objects.get_or_create(
            chat_id=chat_id,
            cliente=cliente,  # Associar ao cliente correto
            defaults={
                "status": "active",
                "canal": "whatsapp",
                "data_inicio": timezone.now(),
                "last_message_at": timezone.now()
            }
        )
        
        if not chat:
            logger.error(f"Não foi possível encontrar/criar chat para: {chat_id}")
            return False
        
        # Determinar tipo de mensagem
        message_type = detect_message_type(payload)
        
        # Extrair conteúdo da mensagem
        content = extract_message_content(payload, message_type)
        
        # DETERMINAR REMETENTE BASEADO EM from_me E CLIENTE
        if from_me:
            remetente = cliente.nome if cliente else "Usuário"  # Usar nome do cliente dinamicamente
        else:
            # Usar o nome do remetente do webhook (NUNCA usar o nome do cliente para mensagens recebidas)
            sender_data = payload.get('sender', {})
            
            # Priorizar pushName, depois verifiedName, depois name
            remetente = (
                sender_data.get('pushName', '') or 
                sender_data.get('verifiedName', '') or 
                sender_data.get('name', '')
            )
            
            # Se não encontrar nome no sender, usar um nome padrão baseado no chat_id
            if not remetente:
                if chat_id and '@' in chat_id:
                    # Para grupos, extrair o número do participante
                    if 'g.us' in chat_id:
                        remetente = f"Participante"
                    else:
                        remetente = f"Contato {chat_id.split('@')[0]}"
                else:
                    remetente = "Contato"
            
            # Garantir que não está usando o nome do cliente para mensagens recebidas
            if cliente and cliente.nome in remetente:
                logger.warning(f"⚠️ Tentativa de usar nome do cliente para mensagem recebida: {remetente}")
                remetente = "Contato"
            
            # Atualizar o sender com o nome capturado
            try:
                from webhook.models import Sender
                sender, created = Sender.objects.get_or_create(
                    sender_id=chat_id,
                    cliente=cliente,
                    defaults={
                        'push_name': remetente,
                        'verified_name': remetente,
                    }
                )
                
                if not created:
                    # Atualizar o sender existente se o nome for diferente
                    if sender.push_name != remetente:
                        sender.push_name = remetente
                        sender.save(update_fields=['push_name'])
                        logger.info(f"🔄 Nome do sender atualizado: {remetente}")
                
            except Exception as e:
                logger.error(f"❌ Erro ao atualizar sender: {e}")
        
        # Criar mensagem com from_me já determinado
        mensagem = Mensagem.objects.create(
            chat=chat,
            remetente=remetente,
            conteudo=content,
            tipo=message_type,
            lida=False,
            from_me=from_me,  # Usar o valor já determinado
            message_id=message_id
        )
        
        # CRIAÇÃO AUTOMÁTICA DE PASTA PARA ÁUDIOS
        if message_type == 'audio':
            # Buscar instância do WhatsApp para este chat
            instance = chat.cliente.whatsapp_instances.first()
            if instance:
                # Criar pasta de áudio automaticamente
                pasta_criada = criar_pasta_audio_automatica(chat, instance, message_id)
                if pasta_criada:
                    logger.info(f"🎵 Pasta de áudio criada automaticamente: {pasta_criada}")
                else:
                    logger.warning(f"⚠️ Não foi possível criar pasta de áudio para mensagem {message_id}")
            else:
                logger.warning(f"⚠️ Nenhuma instância WhatsApp encontrada para cliente {chat.cliente.nome}")
        
        # Atualizar última mensagem do chat
        chat.last_message_at = datetime.fromtimestamp(payload.get('messageTimestamp', 0))
        chat.save()
        
        logger.info(f"✅ Mensagem salva: {message_id} - Tipo: {message_type} - FromMe: {from_me} - Remetente: {remetente} - Cliente: {cliente.nome if cliente else 'N/A'}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar mensagem: {e}")
        return False


def find_or_create_chat(chat_id, message_data):
    """
    Encontra ou cria um chat baseado no chat_id
    """
    try:
        # Normalizar o chat_id primeiro
        normalized_chat_id = normalize_chat_id(chat_id)
        
        if not normalized_chat_id:
            logger.error(f"Chat ID inválido após normalização: {chat_id}")
            return None
        
        logger.info(f"📱 Chat ID normalizado: {chat_id} -> {normalized_chat_id}")
        
        # Verificar se o chat já existe
        chat = Chat.objects.filter(chat_id=normalized_chat_id).first()
        
        if chat:
            return chat
        
        # Se não existe, criar novo chat
        # Determinar cliente baseado na instância
        instance_id = message_data.get('instanceId', '')
        cliente = None
        
        if instance_id:
            # Tentar encontrar instância e cliente
            try:
                instance = WhatsappInstance.objects.get(instance_id=instance_id)
                cliente = instance.cliente
            except WhatsappInstance.DoesNotExist:
                # Se não encontrar instância, usar cliente padrão ou primeiro cliente
                cliente = Cliente.objects.first()
        
        if not cliente:
            logger.error(f"Nenhum cliente encontrado para criar chat: {normalized_chat_id}")
            return None
        
        # Criar novo chat
        chat = Chat.objects.create(
            chat_id=normalized_chat_id,
            cliente=cliente,
            status='active',
            canal='whatsapp'
        )
        
        logger.info(f"✅ Novo chat criado: {normalized_chat_id} para cliente {cliente.nome}")
        return chat
        
    except Exception as e:
        logger.error(f"❌ Erro ao encontrar/criar chat: {e}")
        return None


def detect_message_type(message_data):
    """
    Detecta o tipo de mensagem baseado no conteúdo
    """
    message = message_data.get('message', {})
    
    if 'conversation' in message:
        return 'text'
    elif 'imageMessage' in message:
        return 'image'
    elif 'videoMessage' in message:
        return 'video'
    elif 'audioMessage' in message:
        return 'audio'
    elif 'documentMessage' in message:
        return 'document'
    elif 'stickerMessage' in message:
        return 'sticker'
    elif 'locationMessage' in message:
        return 'location'
    elif 'contactMessage' in message:
        return 'contact'
    elif 'pollCreationMessage' in message:
        return 'poll'
    else:
        return 'text'  # padrão


def extract_message_content(message_data, message_type):
    """
    Extrai o conteúdo da mensagem baseado no tipo
    """
    message = message_data.get('message', {})
    
    if message_type == 'text':
        return message.get('conversation', '')
    
    elif message_type == 'image':
        image_msg = message.get('imageMessage', {})
        caption = image_msg.get('caption', '')
        # Preservar a URL da imagem no conteúdo
        image_url = image_msg.get('url', '')
        if image_url:
            return json.dumps({
                'imageMessage': {
                    'url': image_url,
                    'caption': caption,
                    'mimetype': image_msg.get('mimetype', ''),
                    'fileLength': image_msg.get('fileLength', ''),
                    'height': image_msg.get('height'),
                    'width': image_msg.get('width'),
                    'jpegThumbnail': image_msg.get('jpegThumbnail', ''),
                    'mediaKey': image_msg.get('mediaKey', ''),
                    'directPath': image_msg.get('directPath', ''),
                    'fileSha256': image_msg.get('fileSha256', ''),
                    'fileEncSha256': image_msg.get('fileEncSha256', ''),
                    'mediaKeyTimestamp': image_msg.get('mediaKeyTimestamp', '')
                }
            }, ensure_ascii=False)
        else:
            return f"[Imagem]{' - ' + caption if caption else ''}"
    
    elif message_type == 'video':
        video_msg = message.get('videoMessage', {})
        caption = video_msg.get('caption', '')
        # Preservar a URL do vídeo no conteúdo
        video_url = video_msg.get('url', '')
        if video_url:
            return json.dumps({
                'videoMessage': {
                    'url': video_url,
                    'caption': caption,
                    'mimetype': video_msg.get('mimetype', ''),
                    'fileLength': video_msg.get('fileLength', ''),
                    'mediaKey': video_msg.get('mediaKey', ''),
                    'directPath': video_msg.get('directPath', ''),
                    'fileSha256': video_msg.get('fileSha256', ''),
                    'fileEncSha256': video_msg.get('fileEncSha256', ''),
                    'mediaKeyTimestamp': video_msg.get('mediaKeyTimestamp', '')
                }
            }, ensure_ascii=False)
        else:
            return f"[Vídeo]{' - ' + caption if caption else ''}"
    
    elif message_type == 'audio':
        audio_msg = message.get('audioMessage', {})
        # Preservar a URL do áudio no conteúdo
        audio_url = audio_msg.get('url', '')
        if audio_url:
            return json.dumps({
                'audioMessage': {
                    'url': audio_url,
                    'mimetype': audio_msg.get('mimetype', ''),
                    'fileLength': audio_msg.get('fileLength', ''),
                    'mediaKey': audio_msg.get('mediaKey', ''),
                    'directPath': audio_msg.get('directPath', ''),
                    'fileSha256': audio_msg.get('fileSha256', ''),
                    'fileEncSha256': audio_msg.get('fileEncSha256', ''),
                    'mediaKeyTimestamp': audio_msg.get('mediaKeyTimestamp', ''),
                    'isPtt': audio_msg.get('isPtt', False)
                }
            }, ensure_ascii=False)
        else:
            return "[Áudio]"
    
    elif message_type == 'document':
        doc_msg = message.get('documentMessage', {})
        filename = doc_msg.get('fileName', 'Documento')
        # Preservar a URL do documento no conteúdo
        doc_url = doc_msg.get('url', '')
        if doc_url:
            return json.dumps({
                'documentMessage': {
                    'url': doc_url,
                    'fileName': filename,
                    'mimetype': doc_msg.get('mimetype', ''),
                    'fileLength': doc_msg.get('fileLength', ''),
                    'mediaKey': doc_msg.get('mediaKey', ''),
                    'directPath': doc_msg.get('directPath', ''),
                    'fileSha256': doc_msg.get('fileSha256', ''),
                    'fileEncSha256': doc_msg.get('fileEncSha256', ''),
                    'mediaKeyTimestamp': doc_msg.get('mediaKeyTimestamp', '')
                }
            }, ensure_ascii=False)
        else:
            return f"[Documento] {filename}"
    
    elif message_type == 'sticker':
        sticker_msg = message.get('stickerMessage', {})
        # Preservar a URL do sticker no conteúdo
        sticker_url = sticker_msg.get('url', '')
        if sticker_url:
            return json.dumps({
                'stickerMessage': {
                    'url': sticker_url,
                    'mimetype': sticker_msg.get('mimetype', ''),
                    'fileLength': sticker_msg.get('fileLength', ''),
                    'mediaKey': sticker_msg.get('mediaKey', ''),
                    'directPath': sticker_msg.get('directPath', ''),
                    'fileSha256': sticker_msg.get('fileSha256', ''),
                    'fileEncSha256': sticker_msg.get('fileEncSha256', ''),
                    'mediaKeyTimestamp': sticker_msg.get('mediaKeyTimestamp', ''),
                    'isAnimated': sticker_msg.get('isAnimated', False),
                    'isAvatar': sticker_msg.get('isAvatar', False),
                    'isAi': sticker_msg.get('isAi', False),
                    'isLottie': sticker_msg.get('isLottie', False)
                }
            }, ensure_ascii=False)
        else:
            return "[Sticker]"
    
    elif message_type == 'location':
        location_msg = message.get('locationMessage', {})
        name = location_msg.get('name', 'Localização')
        return f"[Localização] {name}"
    
    elif message_type == 'contact':
        return "[Contato]"
    
    elif message_type == 'poll':
        poll_msg = message.get('pollCreationMessage', {})
        name = poll_msg.get('name', 'Enquete')
        return f"[Enquete] {name}"
    
    else:
        return "[Mensagem]"


def process_chat_and_sender(event, webhook_data):
    """
    Processa e cria/atualiza chat e sender baseado nos dados do webhook
    """
    try:
        # Extrair dados
        chat_data = webhook_data.get('chat', {})
        sender_data = webhook_data.get('sender', {})
        chat_id = chat_data.get('id')
        sender_id = sender_data.get('id')
        
        if not chat_id or not sender_id:
            return
        
        # Verificar se é mensagem enviada pelo usuário
        from_me = webhook_data.get('fromMe', False)
        
        # Extrair foto de perfil de forma robusta (já corrigida para priorizar chat quando fromMe=true)
        profile_picture = extract_profile_picture_robust(webhook_data)
        
        # Criar ou atualizar sender
        sender, created = Sender.objects.get_or_create(
            sender_id=sender_id,
            cliente=event.cliente,
            defaults={
                'push_name': sender_data.get('pushName', ''),
                'verified_name': sender_data.get('verifiedName', ''),
                'is_business': sender_data.get('isBusiness', False),
                'business_profile': sender_data.get('businessProfile', {}),
                'profile_picture': profile_picture
            }
        )
        
        if not created:
            # Atualizar dados existentes
            sender.push_name = sender_data.get('pushName', sender.push_name)
            sender.verified_name = sender_data.get('verifiedName', sender.verified_name)
            sender.is_business = sender_data.get('isBusiness', sender.is_business)
            sender.business_profile = sender_data.get('businessProfile', sender.business_profile)
            # Atualizar foto de perfil se uma nova foi fornecida
            if profile_picture and sender.profile_picture != profile_picture:
                sender.profile_picture = profile_picture
            sender.save()
        
        # Criar ou atualizar chat
        # IMPORTANTE: chat_name será sempre o número de telefone (chat_id)
        # O nome do contato será armazenado em sender.push_name ou sender.verified_name
        chat, created = Chat.objects.get_or_create(
            chat_id=chat_id,
            cliente=event.cliente,
            defaults={
                'chat_name': chat_id,  # Sempre o número de telefone
                'is_group': webhook_data.get('isGroup', False),
                'group_participants': chat_data.get('participants', []),
                'foto_perfil': profile_picture,      # Campo principal
                'status': 'active'
            }
        )
        
        if not created:
            # Atualizar dados existentes sempre que uma nova foto for fornecida
            updated = False
            if chat.last_message_at != timezone.now():
                chat.last_message_at = timezone.now()
                updated = True
            
            # IMPORTANTE: chat_name sempre será o número de telefone
            if chat.chat_name != chat_id:
                chat.chat_name = chat_id
                updated = True
            
            # IMPORTANTE: Sempre atualizar foto se uma nova for fornecida
            # Mas apenas se não for uma mensagem enviada pelo usuário OU se a foto vier do chat
            if profile_picture and chat.foto_perfil != profile_picture:
                # Se é mensagem enviada pelo usuário, só atualizar se a foto vier do chat
                if from_me:
                    # Verificar se a foto veio do chat (não do sender)
                    chat_profile_picture = chat_data.get('profilePicture') or webhook_data.get('profilePicture')
                    if profile_picture == chat_profile_picture:
                        chat.foto_perfil = profile_picture
                        updated = True
                        logger.info(f"🖼️ Foto de perfil do chat atualizada (fromMe=true): {profile_picture}")
                    else:
                        logger.info(f"🔄 Ignorando foto do sender para chat (fromMe=true): {profile_picture}")
                else:
                    # Se é mensagem recebida, atualizar normalmente
                    chat.foto_perfil = profile_picture
                    updated = True
                    logger.info(f"🖼️ Foto de perfil atualizada para chat {chat_id}: {profile_picture}")
            
            if updated:
                chat.save()
        
        logger.info(f"✅ Chat e sender processados: {chat_id} - Foto: {profile_picture} - fromMe: {from_me}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar chat e sender: {e}")


@api_view(['GET'])
def webhook_status(request):
    """
    Status dos webhooks processados
    """
    try:
        total_events = WebhookEvent.objects.count()
        processed_events = WebhookEvent.objects.filter(processed=True).count()
        recent_events = WebhookEvent.objects.order_by('-received_at')[:10]
        
        return Response({
            'total_events': total_events,
            'processed_events': processed_events,
            'pending_events': total_events - processed_events,
            'recent_events': [
                {
                    'id': event.event_id,
                    'type': event.event_type,
                    'processed': event.processed,
                    'received_at': event.received_at.isoformat()
                }
                for event in recent_events
            ]
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter status: {e}")
        return Response({
            'error': str(e)
        }, status=500)


def download_media_via_wapi(instance_id, bearer_token, media_data):
    """Faz download de mídia diretamente via API W-API com melhor tratamento de erros"""
    try:
        import requests
        import json
        import time
        
        url = f"https://api.w-api.app/v1/message/download-media?instanceId={instance_id}"
        
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'mediaKey': media_data.get('mediaKey', ''),
            'directPath': media_data.get('directPath', ''),
            'type': media_data.get('type', ''),
            'mimetype': media_data.get('mimetype', '')
        }
        
        print(f"🔄 Fazendo requisição para W-API:")
        print(f"   URL: {url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        # Tentar múltiplas vezes
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                print(f"📡 Tentativa {attempt + 1}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if not data.get('error', True):
                        print(f"✅ Download bem-sucedido:")
                        print(f"   fileLink: {data.get('fileLink', 'N/A')}")
                        print(f"   expires: {data.get('expires', 'N/A')}")
                        return data
                    else:
                        print(f"❌ Erro na resposta: {data}")
                else:
                    print(f"❌ Status code: {response.status_code}")
                    print(f"   Resposta: {response.text}")
                
                if attempt < max_retries - 1:
                    print(f"⏳ Aguardando 2 segundos antes da próxima tentativa...")
                    time.sleep(2)
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Erro de conexão (tentativa {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        print(f"❌ Todas as {max_retries} tentativas falharam")
        return None
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return None

def save_media_file(file_link, media_type, message_id, sender_name, cliente, instance):
    """Salva arquivo de mídia baixado"""
    try:
        import requests
        from pathlib import Path
        from datetime import datetime
        
        # Fazer download do arquivo
        print(f"📥 Baixando arquivo de: {file_link}")
        response = requests.get(file_link, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ Erro ao baixar arquivo: {response.status_code}")
            return None
        
        # Determinar extensão baseada no tipo
        extensions = {
            'image': '.jpg',
            'video': '.mp4',
            'audio': '.mp3',
            'document': '.pdf',
            'sticker': '.webp'
        }
        
        ext = extensions.get(media_type, '.bin')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"wapi_{message_id}_{timestamp}{ext}"
        
        # Criar pasta de destino
        media_storage_path = Path(__file__).parent.parent / "media_storage" / f"cliente_{cliente.id}" / f"instance_{instance.instance_id}" / media_type
        media_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Salvar arquivo
        file_path = media_storage_path / filename
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Arquivo salvo: {file_path}")
        print(f"📏 Tamanho: {len(response.content)} bytes")
        
        # Criar registro no banco
        from core.models import MediaFile
        from django.utils import timezone
        
        # Verificar se já existe um registro com este message_id
        existing_media = MediaFile.objects.filter(message_id=message_id).first()
        
        if existing_media:
            # Atualizar registro existente
            existing_media.file_name = filename
            existing_media.file_path = str(file_path)
            existing_media.file_size = len(response.content)
            existing_media.download_status = 'success'
            existing_media.download_timestamp = timezone.now()
            existing_media.save()
            media_file = existing_media
            print(f"✅ Registro atualizado no banco: {media_file.id}")
        else:
            # Criar novo registro
            media_file = MediaFile.objects.create(
                cliente=cliente,
                instance=instance,
                message_id=message_id,
                sender_name=sender_name,
                sender_id=sender_name,  # Usar nome como ID temporário
                media_type=media_type,
                mimetype=response.headers.get('content-type', 'application/octet-stream'),
                file_name=filename,
                file_path=str(file_path),
                file_size=len(response.content),
                download_status='success',
                download_timestamp=timezone.now(),
                message_timestamp=timezone.now(),
                is_group=False,
                from_me=False
            )
            print(f"✅ Registro criado no banco: {media_file.id}")
        
        print(f"✅ Registro criado no banco: {media_file.id}")
        return str(file_path)
        
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")
        import traceback
        traceback.print_exc()
        return None

def criar_pasta_audio_automatica(chat, instance, message_id):
    """
    Cria automaticamente a pasta de áudio para um chat quando uma mensagem de áudio é processada
    """
    try:
        from pathlib import Path
        
        # Construir caminho da pasta de áudio
        cliente_id = chat.cliente.id
        instance_id = instance.instance_id
        chat_id = chat.chat_id
        
        audio_path = Path(__file__).parent.parent / "media_storage" / f"cliente_{cliente_id}" / f"instance_{instance_id}" / "chats" / str(chat_id) / "audio"
        
        # Criar pasta se não existir
        audio_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Pasta de áudio criada/verificada: {audio_path}")
        
        return str(audio_path)
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar pasta de áudio: {e}")
        return None

def criar_pasta_imagem_automatica(chat, instance, message_id):
    """
    Cria automaticamente a pasta de imagem para um chat quando uma mensagem de imagem é processada
    """
    try:
        from pathlib import Path
        
        # Construir caminho da pasta de imagem
        cliente_id = chat.cliente.id
        instance_id = instance.instance_id
        chat_id = chat.chat_id
        
        image_path = Path(__file__).parent.parent / "media_storage" / f"cliente_{cliente_id}" / f"instance_{instance_id}" / "chats" / str(chat_id) / "imagens"
        
        # Criar pasta se não existir
        image_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Pasta de imagem criada/verificada: {image_path}")
        
        return str(image_path)
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar pasta de imagem: {e}")
        return None

def criar_pasta_video_automatica(chat, instance, message_id):
    """
    Cria automaticamente a pasta de vídeo para um chat quando uma mensagem de vídeo é processada
    """
    try:
        from pathlib import Path
        
        # Construir caminho da pasta de vídeo
        cliente_id = chat.cliente.id
        instance_id = instance.instance_id
        chat_id = chat.chat_id
        
        video_path = Path(__file__).parent.parent / "media_storage" / f"cliente_{cliente_id}" / f"instance_{instance_id}" / "chats" / str(chat_id) / "videos"
        
        # Criar pasta se não existir
        video_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Pasta de vídeo criada/verificada: {video_path}")
        
        return str(video_path)
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar pasta de vídeo: {e}")
        return None

def criar_pasta_documento_automatica(chat, instance, message_id):
    """
    Cria automaticamente a pasta de documento para um chat quando uma mensagem de documento é processada
    """
    try:
        from pathlib import Path
        
        # Construir caminho da pasta de documento
        cliente_id = chat.cliente.id
        instance_id = instance.instance_id
        chat_id = chat.chat_id
        
        documento_path = Path(__file__).parent.parent / "media_storage" / f"cliente_{cliente_id}" / f"instance_{instance_id}" / "chats" / str(chat_id) / "documentos"
        
        # Criar pasta se não existir
        documento_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Pasta de documento criada/verificada: {documento_path}")
        
        return str(documento_path)
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar pasta de documento: {e}")
        return None

def criar_pasta_sticker_automatica(chat, instance, message_id):
    """
    Cria automaticamente a pasta de sticker para um chat quando uma mensagem de sticker é processada
    """
    try:
        from pathlib import Path
        
        # Construir caminho da pasta de sticker
        cliente_id = chat.cliente.id
        instance_id = instance.instance_id
        chat_id = chat.chat_id
        
        sticker_path = Path(__file__).parent.parent / "media_storage" / f"cliente_{cliente_id}" / f"instance_{instance_id}" / "chats" / str(chat_id) / "stickers"
        
        # Criar pasta se não existir
        sticker_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Pasta de sticker criada/verificada: {sticker_path}")
        
        return str(sticker_path)
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar pasta de sticker: {e}")
        return None

