"""
Views para processamento de webhooks do WhatsApp
Integração com o sistema MultiChat para salvar mensagens nos chats
"""

import json
import logging
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

def extract_profile_picture_robust(webhook_data):
    """Extrai foto de perfil de forma mais robusta do webhook"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Lista de possíveis locais onde a foto pode estar
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
    """
    Processa mensagens do webhook do WhatsApp
    """
    try:
        print(f"📨 Processando mensagem: {event_type}")
        
        # Extrair dados básicos
        instance_id = webhook_data.get('instanceId')
        message_id = webhook_data.get('messageId')
        
        if not instance_id:
            print("❌ instanceId não encontrado")
            return False
        
        # Buscar instância no banco
        try:
            instance = WhatsappInstance.objects.get(instance_id=instance_id)
            cliente = instance.cliente
        except WhatsappInstance.DoesNotExist:
            print(f"❌ Instância {instance_id} não encontrada")
            return False
        
        # IDENTIFICAÇÃO AUTOMÁTICA: Determinar se é mensagem enviada pelo usuário
        from_me = determine_from_me_saas(webhook_data, instance_id)
        print(f"🔍 from_me determinado: {from_me}")
        
        # Verificar se a mensagem já foi processada
        if message_id and Mensagem.objects.filter(message_id=message_id).exists():
            print(f"⚠️ Mensagem já processada: {message_id}")
            return True
        
        # Criar evento de webhook
        event = WebhookEvent.objects.create(
            cliente=cliente,
            instance_id=instance_id,
            event_type=event_type,
            raw_data=webhook_data,
            ip_address='127.0.0.1',  # Para testes
            user_agent='Test Agent'
        )
        
        # SALVAR MENSAGEM COM from_me CORRETO
        if 'msgContent' in webhook_data or 'data' in webhook_data:
            try:
                # Usar a função save_message_to_chat com from_me já determinado
                success = save_message_to_chat_with_from_me(webhook_data, event, from_me, cliente)
                if success:
                    print(f"✅ Mensagem salva com from_me={from_me}")
                    
                    # Processar mídia automaticamente se for uma mensagem de mídia
                    msg_content = webhook_data.get('msgContent', {})
                    if any(media_type in msg_content for media_type in [
                        'imageMessage', 'videoMessage', 'audioMessage', 
                        'documentMessage', 'stickerMessage'
                    ]):
                        try:
                            # Usar analisador completo para processar mídia
                            resultado = processar_webhook_whatsapp(webhook_data)
                            
                            if resultado.get('sucesso'):
                                print(f"✅ Mídia processada com sucesso para mensagem {message_id}")
                            else:
                                print(f"❌ Falha no processamento de mídia: {resultado.get('erro')}")
                                
                        except Exception as e:
                            print(f"❌ Erro ao processar mídia: {e}")
                    
                    return True
                else:
                    print("⚠️ Falha ao salvar mensagem")
                    return False
            except Exception as e:
                print(f"❌ Erro ao salvar mensagem: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao processar mensagem: {e}")
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
                return False
            
            # Processar cada mensagem
            for message_data in messages:
                success = save_message_to_chat(webhook_data, event)
                if not success:
                    logger.error(f"Falha ao salvar mensagem: {message_data.get('key', {}).get('id', 'unknown')}")
                    return False
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem: {e}")
        return False


def save_message_to_chat(payload, event):
    """
    Salva a mensagem no sistema de chats principal
    """
    try:
        chat_id = payload.get("chat", {}).get("id", "")
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
        if Mensagem.objects.filter(chat__chat_id=chat_id, data_envio__timestamp=payload.get('messageTimestamp', 0)).exists():
            logger.info(f"Mensagem já existe (timestamp): {message_id}")
            return True
        
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
        chat_id = payload.get("chat", {}).get("id", "")
        message_key = payload.get('key', {})
        message_id = message_key.get('id', '')
        
        logger.info(f"🔍 Salvando mensagem com from_me={from_me} para cliente: {cliente.nome if cliente else 'N/A'}")
        
        # Verificar se já existe usando message_id (mais confiável)
        if message_id and Mensagem.objects.filter(message_id=message_id).exists():
            logger.info(f"Mensagem já existe (message_id): {message_id}")
            return True
        
        # Verificação adicional por chat_id e timestamp (fallback)
        if Mensagem.objects.filter(chat__chat_id=chat_id, data_envio__timestamp=payload.get('messageTimestamp', 0)).exists():
            logger.info(f"Mensagem já existe (timestamp): {message_id}")
            return True
        
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
        # Verificar se o chat já existe
        chat = Chat.objects.filter(chat_id=chat_id).first()
        
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
            logger.error(f"Nenhum cliente encontrado para criar chat: {chat_id}")
            return None
        
        # Criar novo chat
        chat = Chat.objects.create(
            chat_id=chat_id,
            cliente=cliente,
            status='active',
            canal='whatsapp'
        )
        
        logger.info(f"✅ Novo chat criado: {chat_id} para cliente {cliente.nome}")
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
        
        # Extrair foto de perfil de forma robusta
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
            if profile_picture and chat.foto_perfil != profile_picture:
                chat.foto_perfil = profile_picture
                updated = True
                logger.info(f"🖼️ Foto de perfil atualizada para chat {chat_id}: {profile_picture}")
            
            if updated:
                chat.save()
        
        logger.info(f"✅ Chat e sender processados: {chat_id} - Foto: {profile_picture}")
        
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

