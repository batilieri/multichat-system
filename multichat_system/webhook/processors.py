"""
Processadores de webhook para o MultiChat System
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from django.db import transaction
from django.utils import timezone as django_timezone

from core.models import Cliente, Chat as CoreChat, Mensagem as CoreMensagem
from .models import (
    WebhookEvent, Chat, Sender, Message,
    MessageMedia, MessageStats, ContactStats, RealTimeStats
)
from .media_downloader import processar_midias_automaticamente
from .audio_processor import process_audio_from_webhook
from .audio_processor_simple import process_audio_from_webhook_simple
import subprocess

logger = logging.getLogger(__name__)


class WhatsAppWebhookProcessor:
    """
    Processador de webhooks do WhatsApp baseado na estrutura do betZap
    """
    
    def __init__(self, cliente: Cliente):
        self.cliente = cliente
        self.instance_id = None
        
    def detect_whatsapp(self, data: Dict[str, Any]) -> bool:
        """
        Detecta se os dados são do WhatsApp Business API
        Baseado na estrutura do betZap
        """
        # Verificar campos específicos do WhatsApp
        whatsapp_fields = [
            'key', 'message', 'messageTimestamp', 'status',
            'sender', 'chat', 'msgContent', 'fromMe'
        ]
        
        # Verificar se contém campos do WhatsApp
        has_whatsapp_fields = any(field in data for field in whatsapp_fields)
        
        # Verificar estrutura específica
        if 'key' in data and 'message' in data:
            return True
            
        if 'sender' in data and 'msgContent' in data:
            return True
            
        if 'messageTimestamp' in data:
            return True
            
        return has_whatsapp_fields
    
    def process_webhook_data(self, raw_data: Dict[str, Any], ip_address: str = None, user_agent: str = None) -> WebhookEvent:
        """
        Processa dados do webhook e salva no banco
        """
        try:
            logger.info(f"[PROCESSOR] Iniciando processamento do webhook")
            logger.info(f"[PROCESSOR] Dados recebidos: {list(raw_data.keys())}")
            
            # Criar evento de webhook
            webhook_event = WebhookEvent.objects.create(
                cliente=self.cliente,
                instance_id=raw_data.get('instanceId', 'unknown'),
                event_type=self._determine_event_type(raw_data),
                raw_data=raw_data,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # PRIORIDADE 1: Se tem chat['id'], sempre usar fallback
            if 'chat' in raw_data and 'sender' in raw_data:
                logger.info(f"[PROCESSOR] Chat['id'] detectado - usando FALLBACK obrigatório")
                self.process_fallback_sender_msgcontent(webhook_event, raw_data)
                webhook_event.processed = True
                webhook_event.save()
            # PRIORIDADE 2: Se detect_whatsapp retornou True mas sem chat['id']
            elif self.detect_whatsapp(raw_data):
                logger.info(f"[PROCESSOR] WhatsApp detectado (sem chat) - usando process_whatsapp_data")
                self.process_whatsapp_data(webhook_event, raw_data)
                webhook_event.processed = True
                webhook_event.save()
            # PRIORIDADE 3: Fallback para sender/msgContent
            elif 'sender' in raw_data and 'msgContent' in raw_data:
                logger.info(f"[PROCESSOR] Fallback sender/msgContent - usando process_fallback_sender_msgcontent")
                self.process_fallback_sender_msgcontent(webhook_event, raw_data)
                webhook_event.processed = True
                webhook_event.save()
            else:
                logger.warning(f"[PROCESSOR] Nenhum método aplicável encontrado")
            
            return webhook_event
            
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {e}")
            if 'webhook_event' in locals():
                webhook_event.error_message = str(e)
                webhook_event.save()
            raise
    
    def _determine_event_type(self, data: Dict[str, Any]) -> str:
        """
        Determina o tipo de evento baseado nos dados
        """
        if 'status' in data:
            return 'status'
        elif 'message' in data:
            return 'message'
        elif 'qrCode' in data:
            return 'qr_code'
        elif 'connection' in data:
            return 'connection'
        else:
            return 'unknown'
    
    def process_whatsapp_data(self, webhook_event: WebhookEvent, data: Dict[str, Any]):
        """
        Processa dados específicos do WhatsApp
        """
        try:
            # Extrair dados básicos
            payload = data.get('data', {})
            key_data = payload.get('key', {})
            
            # Informações do chat
            chat_data = payload.get('chat', {})
            chat_id = chat_data.get('id', '')
            chat_name = chat_data.get('name', '')
            is_group = chat_data.get('isGroup', False) or '@g.us' in chat_id
            
            # Informações do remetente
            sender_data = payload.get('sender', {})
            sender_id = sender_data.get('id', '')
            sender_name = sender_data.get('pushName', '')
            
            # ID da mensagem
            message_id = key_data.get('id', '')
            
            # Conteúdo da mensagem
            msg_content = payload.get('msgContent', {})
            
            # Determinar se a mensagem foi enviada pelo usuário atual
            from_me = False
            
            # Método 1: Verificar campo fromMe no key
            if key_data.get('fromMe') is not None:
                from_me = key_data.get('fromMe', False)
            # Método 2: Verificar campo fromMe no payload raiz
            elif payload.get('fromMe') is not None:
                from_me = payload.get('fromMe', False)
            # Método 3: Verificar se o sender_id é o mesmo da instância (usuário atual)
            else:
                # Se o sender_id contém o instance_id, é uma mensagem enviada pelo usuário
                instance_id = data.get('instanceId', '')
                if sender_id and instance_id and instance_id in sender_id:
                    from_me = True
                # Se o sender_id é o mesmo do chat_id (para chats individuais), pode ser do usuário
                elif sender_id and chat_id and sender_id == chat_id:
                    from_me = True
            
            # Conteúdo da mensagem
            message_content = data.get('msgContent', {})
            message_type = self._extract_message_type(message_content)
            text_content = self._extract_text_content(message_content)
            
            # Timestamp
            timestamp = self._parse_timestamp(data.get('messageTimestamp', ''))
            
            # Foto de perfil do contato
            # LÓGICA CORRIGIDA: Priorizar foto do chat quando fromMe=true
            foto_perfil = None
            
            if from_me:
                # Se é mensagem enviada pelo usuário, priorizar foto do chat (contato/grupo)
                foto_perfil = chat_data.get('profilePicture') or data.get('profilePicture')
                logger.info(f"🔄 Mensagem enviada pelo usuário - usando foto do chat: {foto_perfil}")
            else:
                # Se é mensagem recebida, usar lógica normal
                foto_perfil = chat_data.get('profilePicture') or data.get('profilePicture')
                logger.info(f"📥 Mensagem recebida - usando foto do chat: {foto_perfil}")
            
            # Atualizar evento com dados processados
            webhook_event.chat_id = chat_id
            webhook_event.sender_id = sender_id
            webhook_event.sender_name = sender_name
            webhook_event.message_id = message_id
            webhook_event.message_type = message_type
            webhook_event.message_content = text_content
            webhook_event.save()
            
            # Processar com transação
            with transaction.atomic():
                # Criar/atualizar chat (agora com foto_perfil e detecção melhorada de grupos)
                chat = self._get_or_create_chat(chat_id, chat_name, is_group=is_group, foto_perfil=foto_perfil)
                
                # Criar/atualizar remetente
                sender = self._get_or_create_sender(sender_id, sender_name, data)
                
                # Criar mensagem
                if message_id and text_content:
                    message = self._create_message(
                        message_id, chat, sender, message_type, 
                        message_content, text_content, from_me, timestamp
                    )
                    
                    # Atualizar estatísticas
                    if message:
                        self._update_stats(chat, sender, message, timestamp)
                        
                    # INTEGRAÇÃO: Processar download automático de mídias
                    try:
                        processar_midias_automaticamente(webhook_event)
                        logger.info(f"✅ Download automático de mídias processado para mensagem {message_id}")
                    except Exception as e:
                        logger.error(f"❌ Erro no download automático de mídias: {e}")
                        
        except Exception as e:
            logger.error(f"Erro ao processar dados do WhatsApp: {e}")
            raise
    
    def _extract_message_type(self, message_content: Dict[str, Any]) -> str:
        """
        Extrai o tipo da mensagem
        """
        if 'conversation' in message_content:
            return 'text'
        elif 'imageMessage' in message_content:
            return 'image'
        elif 'videoMessage' in message_content:
            return 'video'
        elif 'audioMessage' in message_content:
            return 'audio'
        elif 'documentMessage' in message_content:
            return 'document'
        elif 'stickerMessage' in message_content:
            return 'sticker'
        elif 'locationMessage' in message_content:
            return 'location'
        elif 'contactMessage' in message_content:
            return 'contact'
        else:
            return 'unknown'
    
    def _extract_text_content(self, message_content: Dict[str, Any]) -> str:
        """
        Extrai o conteúdo de texto da mensagem
        """
        if 'conversation' in message_content:
            return message_content['conversation']
        elif 'extendedTextMessage' in message_content:
            return message_content['extendedTextMessage'].get('text', '')
        else:
            return ''
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """
        Converte timestamp do WhatsApp para datetime
        """
        try:
            if timestamp_str:
                # WhatsApp usa timestamp em segundos
                timestamp = int(timestamp_str)
                return datetime.fromtimestamp(timestamp, tz=timezone.utc)
            else:
                return django_timezone.now()
        except (ValueError, TypeError):
            return django_timezone.now()
    
    def _get_or_create_chat(self, chat_id: str, chat_name: str, is_group: bool = False, foto_perfil: str = None) -> Chat:
        """
        Cria ou obtém um chat e atualiza nome/foto se mudarem
        """
        safe_chat_id = chat_id or "sem_id"
        safe_chat_name = chat_name or (f"Chat {safe_chat_id[-8:]}" if safe_chat_id else "Chat")
        
        # Determinar se é grupo baseado no chat_id ou parâmetro
        is_group_chat = is_group or ('@g.us' in safe_chat_id if safe_chat_id else False)
        
        # Para grupos, usar o chat_id como identificador único
        # Para chats individuais, usar o chat_id normal
        chat, created = Chat.objects.get_or_create(
            chat_id=safe_chat_id,
            cliente=self.cliente,
            defaults={
                'chat_name': safe_chat_name,
                'is_group': is_group_chat,
                'canal': 'whatsapp',
                'status': 'active',
                'last_message_at': django_timezone.now(),
                'foto_perfil': foto_perfil
            }
        )
        
        # Atualizar campos se mudarem
        updated = False
        if not created:
            if chat.last_message_at != django_timezone.now():
                chat.last_message_at = django_timezone.now()
                updated = True
            # Sempre atualizar o nome do chat para o sender_name recebido
            if safe_chat_name and chat.chat_name != safe_chat_name:
                chat.chat_name = safe_chat_name
                updated = True
            if foto_perfil and chat.foto_perfil != foto_perfil:
                chat.foto_perfil = foto_perfil
                updated = True
            # Atualizar is_group se necessário
            if chat.is_group != is_group_chat:
                chat.is_group = is_group_chat
                updated = True
            if updated:
                chat.save()
        return chat
    
    def _get_or_create_sender(self, sender_id: str, sender_name: str, data: Dict[str, Any]) -> Sender:
        """
        Cria ou obtém um remetente no modelo webhook.Sender
        """
        sender, created = Sender.objects.get_or_create(
            sender_id=sender_id,
            cliente=self.cliente,
            defaults={
                'push_name': sender_name,
                'verified_name': data.get('verifiedName', ''),
                'is_business': data.get('isBusiness', False),
                'business_profile': data.get('businessProfile', {}),
                'last_seen': django_timezone.now()
            }
        )
        
        if not created:
            # Atualizar informações se mudaram
            if sender_name and sender_name != sender.push_name:
                sender.push_name = sender_name
            sender.last_seen = django_timezone.now()
            sender.message_count += 1
            sender.save()
            
        return sender
    
    def _create_message(self, message_id: str, chat: Chat, sender: Sender, 
                       message_type: str, message_content: Dict[str, Any], 
                       text_content: str, from_me: bool, timestamp: datetime) -> Message:
        """
        Cria uma nova mensagem no modelo webhook.Message, preenchendo todos os campos detalhados de mídia e criando registro em MessageMedia se necessário
        """
        # Verificação de duplicidade
        if message_id and CoreMensagem.objects.filter(message_id=message_id).exists():
            logger.info(f"Mensagem já existe: {message_id}")
            return None
            
        # VERIFICAR SE É MENSAGEM DE PROTOCOLO (não deve ser salva)
        is_protocol_message = (
            'protocolMessage' in text_content or
            'APP_STATE_SYNC_KEY_REQUEST' in text_content or
            'deviceListMetadata' in text_content or
            'messageContextInfo' in text_content or
            'senderKeyHash' in text_content or
            'senderTimestamp' in text_content or
            'deviceListMetadataVersion' in text_content or
            'keyIds' in text_content or
            'keyId' in text_content or
            'AAAAACSE' in text_content
        )
        
        if is_protocol_message:
            logger.info(f"Mensagem de protocolo ignorada: {message_id}")
            return None
        # Inicializar campos detalhados
        media_url = None
        media_type = None
        media_size = None
        media_caption = None
        media_height = None
        media_width = None
        jpeg_thumbnail = None
        file_sha256 = None
        media_key = None
        direct_path = None
        media_key_timestamp = None
        document_url = None
        document_filename = None
        document_mimetype = None
        document_file_length = None
        document_page_count = None
        location_latitude = None
        location_longitude = None
        location_name = None
        location_address = None
        poll_name = None
        poll_options = None
        poll_selectable_count = None
        sticker_url = None
        sticker_mimetype = None
        sticker_file_length = None
        sticker_is_animated = False
        sticker_is_avatar = False
        sticker_is_ai = False
        sticker_is_lottie = False
        thumbnail_direct_path = None
        thumbnail_sha256 = None
        thumbnail_enc_sha256 = None
        thumbnail_height = None
        thumbnail_width = None
        reactions = None
        quoted_message_id = None

        # Preencher campos conforme o tipo de mensagem
        if message_type in ['image', 'video', 'audio', 'document']:
            media_data = message_content.get(f'{message_type}Message', {})
            media_url = media_data.get('url', '')
            media_type = message_type
            media_size = media_data.get('fileLength', 0)
            media_caption = media_data.get('caption')
            media_height = media_data.get('height')
            media_width = media_data.get('width')
            jpeg_thumbnail = media_data.get('jpegThumbnail')
            file_sha256 = media_data.get('fileSha256')
            media_key = media_data.get('mediaKey')
            direct_path = media_data.get('directPath')
            media_key_timestamp = media_data.get('mediaKeyTimestamp')
            
            # PROCESSAMENTO ESPECIAL PARA ÁUDIOS
            if message_type == 'audio':
                logger.info(f"🎵 Processando áudio: {message_id}")
                
                # Verificar se FFmpeg está disponível
                ffmpeg_available = False
                try:
                    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
                    ffmpeg_available = result.returncode == 0
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    ffmpeg_available = False
                
                if ffmpeg_available:
                    logger.info("✅ FFmpeg disponível - usando processador completo")
                    # Processar áudio usando o processador completo
                    audio_result = process_audio_from_webhook({
                        'msgContent': message_content,
                        'messageId': message_id
                    }, self.cliente)
                else:
                    logger.warning("⚠️ FFmpeg não disponível - usando processador simplificado")
                    # Processar áudio usando o processador simplificado
                    audio_result = process_audio_from_webhook_simple({
                        'msgContent': message_content,
                        'messageId': message_id
                    }, self.cliente)
                
                if audio_result and audio_result.get('status') == 'success':
                    # Atualizar URL para o arquivo processado
                    media_url = f"/media/{audio_result['file_path']}"
                    media_size = audio_result.get('file_size', 0)
                    media_type = 'audio'
                    
                    logger.info(f"✅ Áudio processado com sucesso: {media_url}")
                    if audio_result.get('note'):
                        logger.info(f"📝 Nota: {audio_result['note']}")
                else:
                    logger.warning(f"⚠️ Falha ao processar áudio: {message_id}")
            
            # Documento
            if message_type == 'document':
                document_url = media_data.get('url')
                document_filename = media_data.get('fileName')
                document_mimetype = media_data.get('mimetype')
                document_file_length = media_data.get('fileLength')
                document_page_count = media_data.get('pageCount')
            # Criar registro em MessageMedia
            if media_url:
                MessageMedia.objects.create(
                    event=chat.webhook_events.last(),
                    media_path=media_url,
                    media_type=media_type,
                    mimetype=media_data.get('mimetype'),
                    file_size=media_size,
                    download_status='pending'
                )
        # Sticker
        if message_type == 'sticker':
            sticker_data = message_content.get('stickerMessage', {})
            sticker_url = sticker_data.get('url')
            sticker_mimetype = sticker_data.get('mimetype')
            sticker_file_length = sticker_data.get('fileLength')
            sticker_is_animated = sticker_data.get('isAnimated', False)
            sticker_is_avatar = sticker_data.get('isAvatar', False)
            sticker_is_ai = sticker_data.get('isAiSticker', False)
            sticker_is_lottie = sticker_data.get('isLottie', False)
            # Campos comuns de mídia
            file_sha256 = sticker_data.get('fileSha256')
            media_key = sticker_data.get('mediaKey')
            direct_path = sticker_data.get('directPath')
            media_key_timestamp = sticker_data.get('mediaKeyTimestamp')
            jpeg_thumbnail = sticker_data.get('jpegThumbnail')
            # Criar registro em MessageMedia
            if sticker_url:
                MessageMedia.objects.create(
                    event=chat.webhook_events.last(),
                    media_path=sticker_url,
                    media_type='sticker',
                    mimetype=sticker_mimetype,
                    file_size=sticker_file_length,
                    download_status='pending'
                )
        # Localização
        if message_type == 'location':
            location_data = message_content.get('locationMessage', {})
            location_latitude = location_data.get('degreesLatitude')
            location_longitude = location_data.get('degreesLongitude')
            location_name = location_data.get('name')
            location_address = location_data.get('address')
        # Enquete
        if message_type == 'poll':
            poll_data = message_content.get('pollCreationMessageV3', {})
            poll_name = poll_data.get('name')
            poll_options = poll_data.get('options')
            poll_selectable_count = poll_data.get('selectableCount')
        # Thumbnails extras
        if 'thumbnailDirectPath' in message_content:
            thumbnail_direct_path = message_content.get('thumbnailDirectPath')
        if 'thumbnailSha256' in message_content:
            thumbnail_sha256 = message_content.get('thumbnailSha256')
        if 'thumbnailEncSha256' in message_content:
            thumbnail_enc_sha256 = message_content.get('thumbnailEncSha256')
        if 'thumbnailHeight' in message_content:
            thumbnail_height = message_content.get('thumbnailHeight')
        if 'thumbnailWidth' in message_content:
            thumbnail_width = message_content.get('thumbnailWidth')

        # Criar a mensagem preenchendo todos os campos
        message = Message.objects.create(
            message_id=message_id,
            cliente=self.cliente,
            chat=chat,
            sender=sender,
            message_type=message_type,
            content=message_content,
            text_content=text_content,
            from_me=from_me,
            timestamp=timestamp,
            # Campos para identificação do remetente em grupos
            sender_display_name=sender.push_name,
            sender_push_name=sender.push_name,
            sender_verified_name=sender.verified_name,
            media_url=media_url,
            media_type=media_type,
            media_size=media_size,
            media_caption=media_caption,
            media_height=media_height,
            media_width=media_width,
            jpeg_thumbnail=jpeg_thumbnail,
            file_sha256=file_sha256,
            media_key=media_key,
            direct_path=direct_path,
            media_key_timestamp=media_key_timestamp,
            document_url=document_url,
            document_filename=document_filename,
            document_mimetype=document_mimetype,
            document_file_length=document_file_length,
            document_page_count=document_page_count,
            location_latitude=location_latitude,
            location_longitude=location_longitude,
            location_name=location_name,
            location_address=location_address,
            poll_name=poll_name,
            poll_options=poll_options,
            poll_selectable_count=poll_selectable_count,
            sticker_url=sticker_url,
            sticker_mimetype=sticker_mimetype,
            sticker_file_length=sticker_file_length,
            sticker_is_animated=sticker_is_animated,
            sticker_is_avatar=sticker_is_avatar,
            sticker_is_ai=sticker_is_ai,
            sticker_is_lottie=sticker_is_lottie,
            thumbnail_direct_path=thumbnail_direct_path,
            thumbnail_sha256=thumbnail_sha256,
            thumbnail_enc_sha256=thumbnail_enc_sha256,
            thumbnail_height=thumbnail_height,
            thumbnail_width=thumbnail_width,
            reactions=reactions,
            quoted_message_id=quoted_message_id
        )
        
        # Também criar mensagem no modelo core.Mensagem para compatibilidade com o frontend
        if not CoreMensagem.objects.filter(message_id=message_id).exists():
            # Preparar conteúdo estruturado para diferentes tipos de mídia
            conteudo_estruturado = text_content or "[Mídia]"
            
            # Para mensagens de áudio, criar JSON estruturado que o frontend espera
            if message_type == 'audio' and message_content.get('audioMessage'):
                import json
                audio_data = message_content['audioMessage']
                conteudo_estruturado = json.dumps({
                    "audioMessage": {
                        "url": audio_data.get('url', ''),
                        "mediaKey": audio_data.get('mediaKey', ''),
                        "mimetype": audio_data.get('mimetype', 'audio/ogg'),
                        "fileLength": audio_data.get('fileLength', ''),
                        "seconds": audio_data.get('seconds', 0),
                        "ptt": audio_data.get('ptt', False),
                        "directPath": audio_data.get('directPath', ''),
                        "fileSha256": audio_data.get('fileSha256', ''),
                        "fileEncSha256": audio_data.get('fileEncSha256', ''),
                        "mediaKeyTimestamp": audio_data.get('mediaKeyTimestamp', ''),
                        "waveform": audio_data.get('waveform', '')
                    }
                }, ensure_ascii=False)
                logger.info(f"OK - Criando mensagem de áudio estruturada para frontend")
            
            CoreMensagem.objects.create(
                chat=chat,
                remetente=sender.push_name or sender.sender_id,
                conteudo=conteudo_estruturado,
                tipo=message_type,
                data_envio=timestamp,
                from_me=from_me,
                lida=False,
                message_id=message_id,  # Adicionar o message_id do webhook
                # Campos de mídia
                media_type=media_type,
                media_url=media_url,
                media_size=media_size,
                media_caption=media_caption,
                media_height=media_height,
                media_width=media_width,
                jpeg_thumbnail=jpeg_thumbnail,
                file_sha256=file_sha256,
                media_key=media_key,
                direct_path=direct_path,
                media_key_timestamp=media_key_timestamp,
                # Documento
                document_url=document_url,
                document_filename=document_filename,
                document_mimetype=document_mimetype,
                document_file_length=document_file_length,
                document_page_count=document_page_count,
                # Localização
                location_latitude=location_latitude,
                location_longitude=location_longitude,
                location_name=location_name,
                location_address=location_address,
                # Enquete
                poll_name=poll_name,
                poll_options=json.dumps(poll_options) if poll_options else None,
                poll_selectable_count=poll_selectable_count,
                # Sticker
                sticker_url=sticker_url,
                sticker_mimetype=sticker_mimetype,
                sticker_file_length=sticker_file_length,
                sticker_is_animated=sticker_is_animated,
                sticker_is_avatar=sticker_is_avatar,
                sticker_is_ai=sticker_is_ai,
                sticker_is_lottie=sticker_is_lottie,
                # Thumbnails
                thumbnail_direct_path=thumbnail_direct_path,
                thumbnail_sha256=thumbnail_sha256,
                thumbnail_enc_sha256=thumbnail_enc_sha256,
                thumbnail_height=thumbnail_height,
                thumbnail_width=thumbnail_width
            )
        
        # Atualizar estatísticas
        self._update_stats(chat, sender, message, timestamp)

        # INTEGRAÇÃO: Processar download automático de mídias
        try:
            processar_midias_automaticamente(webhook_event)
            logger.info(f"✅ Download automático de mídias processado para mensagem {message_id}")
        except Exception as e:
            logger.error(f"❌ Erro no download automático de mídias: {e}")

        return message
    
    def _update_stats(self, chat: Chat, sender: Sender, message: Message, timestamp: datetime):
        """
        Atualiza estatísticas
        """
        date = timestamp.date()
        
        # Atualizar estatísticas de mensagens
        stats, created = MessageStats.objects.get_or_create(
            cliente=self.cliente,
            date=date,
            defaults={
                'total_messages': 1,
                'received_messages': 0 if message.from_me else 1,
                'sent_messages': 1 if message.from_me else 0,
                'text_messages': 1 if message.message_type == 'text' else 0,
                'media_messages': 1 if message.message_type in ['image', 'video', 'audio'] else 0,
                'document_messages': 1 if message.message_type == 'document' else 0,
                'delivered_messages': 1,
                'read_messages': 0
            }
        )
        
        if not created:
            stats.total_messages += 1
            if message.from_me:
                stats.sent_messages += 1
            else:
                stats.received_messages += 1
                
            if message.message_type == 'text':
                stats.text_messages += 1
            elif message.message_type in ['image', 'video', 'audio']:
                stats.media_messages += 1
            elif message.message_type == 'document':
                stats.document_messages += 1
                
            stats.delivered_messages += 1
            stats.save()
        
        # Atualizar estatísticas de contato
        contact_stats, created = ContactStats.objects.get_or_create(
            cliente=self.cliente,
            sender=sender,
            date=date,
            defaults={
                'message_count': 1,
                'first_message_at': timestamp,
                'last_message_at': timestamp
            }
        )
        
        if not created:
            contact_stats.message_count += 1
            contact_stats.last_message_at = timestamp
            contact_stats.save()
        
        # Atualizar estatísticas em tempo real
        realtime_stats, created = RealTimeStats.objects.get_or_create(
            cliente=self.cliente,
            defaults={
                'active_chats': 1,
                'pending_messages': 0 if message.from_me else 1,
                'online_users': 1,
                'avg_response_time': 0,
                'message_throughput': 1
            }
        )
        
        if not created:
            realtime_stats.pending_messages += 0 if message.from_me else 1
            realtime_stats.save()

    def process_fallback_sender_msgcontent(self, webhook_event: WebhookEvent, data: Dict[str, Any]):
        """
        Processa webhooks que chegam apenas com sender e msgContent
        Seguindo a lógica dos dados mockados do frontend
        """
        try:
            # Extrair dados seguindo o padrão dos dados mockados
            sender_data = data.get('sender', {})
            chat_data = data.get('chat', {})
            msg_content = data.get('msgContent', {})
            
            # IDs seguindo a estrutura dos dados mockados
            sender_id = sender_data.get('id')
            sender_name = sender_data.get('pushName', '')
            message_id = data.get('messageId', webhook_event.event_id.hex)
            
            # Verificar se a mensagem já foi processada
            if message_id and CoreMensagem.objects.filter(message_id=message_id).exists():
                logger.info(f"[FALLBACK] Mensagem já processada: {message_id}")
                return
            
            # PRIORIDADE 1: Usar chat['id'] se disponível (como no exemplo)
            chat_id = None
            if chat_data and chat_data.get('id'):
                chat_id = chat_data.get('id')
                logger.info(f"[FALLBACK] Usando chat['id'] do webhook: {chat_id}")
            # PRIORIDADE 2: Fallback para sender['id'] (número simples, como nos dados mockados)
            elif sender_id:
                # Remover @s.whatsapp.net se existir para ficar igual aos dados mockados
                chat_id = sender_id.replace('@s.whatsapp.net', '').replace('@c.us', '')
                logger.info(f"[FALLBACK] Usando fallback sender['id']: {chat_id}")
            else:
                logger.error(f"[FALLBACK] Nenhum ID de chat disponível nos dados: {data}")
                webhook_event.error_message = 'Nenhum ID de chat disponível no webhook.'
                webhook_event.save()
                return

            # VALIDAÇÃO EXTRA: Não permitir chat_id vazio
            if not chat_id or str(chat_id).strip() == '':
                logger.error(f"[FALLBACK] chat_id está vazio após extração. Ignorando criação de chat.")
                webhook_event.error_message = 'chat_id vazio após extração.'
                webhook_event.save()
                return
            
            # Outros campos seguindo os dados mockados
            # Detectar tipo de mensagem baseado no msgContent
            if 'audioMessage' in msg_content:
                message_type = 'audio'
            elif 'imageMessage' in msg_content:
                message_type = 'image'
            elif 'videoMessage' in msg_content:
                message_type = 'video'
            elif 'documentMessage' in msg_content:
                message_type = 'document'
            elif 'conversation' in msg_content or 'extendedTextMessage' in msg_content:
                message_type = 'text'
            else:
                message_type = 'unknown'
            
            # Extrair texto de múltiplas fontes possíveis
            text_content = ''
            if 'conversation' in msg_content:
                text_content = msg_content.get('conversation', '')
            elif 'extendedTextMessage' in msg_content:
                text_content = msg_content.get('extendedTextMessage', {}).get('text', '')
            elif 'textMessage' in msg_content:
                text_content = msg_content.get('textMessage', {}).get('text', '')
            
            timestamp = webhook_event.timestamp
            is_group = data.get('isGroup', False)
            group_name = data.get('groupName') if is_group else None
            
            # Extrair foto de perfil de múltiplas fontes possíveis
            # LÓGICA MELHORADA PARA DETERMINAR from_me - MOVIDO PARA CIMA
            from_me = False
            
            # Método 1: Verificar campo fromMe no payload raiz
            if data.get('fromMe') is not None:
                from_me = data.get('fromMe', False)
            # Método 2: Verificar campo fromMe no key (se existir)
            elif data.get('key', {}).get('fromMe') is not None:
                from_me = data.get('key', {}).get('fromMe', False)
            # Método 3: Verificar se o sender_id é o mesmo da instância (usuário atual)
            else:
                instance_id = data.get('instanceId', '')
                # Se o sender_id contém o instance_id, é uma mensagem enviada pelo usuário
                if sender_id and instance_id and instance_id in sender_id:
                    from_me = True
                # Se o sender_id é o mesmo do chat_id (para chats individuais), pode ser do usuário
                elif sender_id and chat_id and sender_id == chat_id:
                    from_me = True

            profile_picture = None
            
            # LÓGICA CORRIGIDA: Priorizar foto do chat quando fromMe=true
            if from_me:
                # Se é mensagem enviada pelo usuário, priorizar foto do chat (contato/grupo)
                # e evitar usar a foto do sender (usuário)
                if chat_data.get('profilePicture'):
                    profile_picture = chat_data.get('profilePicture')
                elif data.get('profilePicture'):
                    profile_picture = data.get('profilePicture')
                # Última opção: sender (apenas se não houver outras)
                elif sender_data.get('profilePicture'):
                    profile_picture = sender_data.get('profilePicture')
                logger.info(f"OK - Mensagem enviada pelo usuário - priorizando foto do chat: {profile_picture}")
            else:
                # Se é mensagem recebida, usar lógica normal
                # Prioridade 1: Foto do sender (remetente)
                if sender_data.get('profilePicture'):
                    profile_picture = sender_data.get('profilePicture')
                # Prioridade 2: Foto do chat
                elif chat_data.get('profilePicture'):
                    profile_picture = chat_data.get('profilePicture')
                # Prioridade 3: Foto no nível raiz do webhook
                elif data.get('profilePicture'):
                    profile_picture = data.get('profilePicture')
                logger.info(f"INFO - Mensagem recebida - usando lógica normal: {profile_picture}")

            # Log detalhado
            logger.info(f"[FALLBACK] Criando chat_id: {chat_id}, sender_name: {sender_name}, message_id: {message_id}, texto: '{text_content}', is_group: {is_group}, from_me: {from_me}, profile_picture: {profile_picture}")
            logger.info(f"[FALLBACK] msgContent estrutura: {list(msg_content.keys())}")
            if 'extendedTextMessage' in msg_content:
                logger.info(f"[FALLBACK] extendedTextMessage: {msg_content['extendedTextMessage']}")

            # Atualizar evento
            webhook_event.chat_id = chat_id
            webhook_event.sender_id = sender_id
            webhook_event.sender_name = sender_name
            webhook_event.message_id = message_id
            webhook_event.message_type = message_type
            webhook_event.message_content = text_content
            webhook_event.save()

            with transaction.atomic():
                # Criar/atualizar chat (seguindo a estrutura dos dados mockados)
                chat = self._get_or_create_chat_mock_structure(chat_id, sender_name, is_group, group_name, profile_picture)
                if not chat or not chat.chat_id:
                    logger.error(f"[FALLBACK] Falha ao criar chat para chat_id: {chat_id}")
                    webhook_event.error_message = f'Falha ao criar chat para chat_id: {chat_id}'
                    webhook_event.save()
                    return
                
                # VERIFICAR SE É MENSAGEM DE PROTOCOLO (não deve ser salva)
                is_protocol_message = (
                    'protocolMessage' in text_content or
                    'APP_STATE_SYNC_KEY_REQUEST' in text_content or
                    'deviceListMetadata' in text_content or
                    'messageContextInfo' in text_content or
                    'senderKeyHash' in text_content or
                    'senderTimestamp' in text_content or
                    'deviceListMetadataVersion' in text_content or
                    'keyIds' in text_content or
                    'keyId' in text_content or
                    'AAAAACSE' in text_content
                )
                
                # Criar mensagem usando core.Mensagem (apenas se não existir e não for protocolo)
                # Para áudios e outras mídias, o text_content pode estar vazio, mas temos msg_content
                has_valid_content = text_content or (msg_content and any(key in msg_content for key in ['audioMessage', 'imageMessage', 'videoMessage', 'documentMessage']))
                
                if message_id and has_valid_content and not is_protocol_message and not CoreMensagem.objects.filter(message_id=message_id).exists():
                    # Buscar ou criar chat no modelo core.Chat
                    core_chat, created = CoreChat.objects.get_or_create(
                        chat_id=chat_id,
                        cliente=self.cliente,
                        defaults={
                            'chat_name': sender_name or sender_id or "desconhecido",
                            'is_group': is_group,
                            'canal': 'whatsapp',
                            'status': 'ativo',
                            'last_message_at': django_timezone.now(),
                            'foto_perfil': profile_picture
                        }
                    )
                    
                    # Atualizar chat se já existia
                    if not created:
                        core_chat.chat_name = sender_name or sender_id or "desconhecido"
                        core_chat.last_message_at = django_timezone.now()
                        if profile_picture:
                            core_chat.foto_perfil = profile_picture
                        core_chat.save()
                    
                    # Preparar conteúdo estruturado para diferentes tipos de mídia
                    conteudo_estruturado = text_content or "[Mídia]"
                    
                    # Para mensagens de áudio, criar JSON estruturado que o frontend espera
                    if message_type == 'audio' and msg_content.get('audioMessage'):
                        import json
                        audio_data = msg_content['audioMessage']
                        conteudo_estruturado = json.dumps({
                            "audioMessage": {
                                "url": audio_data.get('url', ''),
                                "mediaKey": audio_data.get('mediaKey', ''),
                                "mimetype": audio_data.get('mimetype', 'audio/ogg'),
                                "fileLength": audio_data.get('fileLength', ''),
                                "seconds": audio_data.get('seconds', 0),
                                "ptt": audio_data.get('ptt', False),
                                "directPath": audio_data.get('directPath', ''),
                                "fileSha256": audio_data.get('fileSha256', ''),
                                "fileEncSha256": audio_data.get('fileEncSha256', ''),
                                "mediaKeyTimestamp": audio_data.get('mediaKeyTimestamp', ''),
                                "waveform": audio_data.get('waveform', '')
                            }
                        }, ensure_ascii=False)
                        logger.info(f"[FALLBACK] OK - Criando mensagem de áudio estruturada")
                    
                    CoreMensagem.objects.create(
                        chat=core_chat,  # Agora usando o chat do modelo core.Chat
                        remetente=sender_name or sender_id or "desconhecido",
                        conteudo=conteudo_estruturado,
                        tipo=message_type,
                        lida=False,
                        from_me=from_me,
                        message_id=message_id,
                        data_envio=django_timezone.now()
                    )
                    logger.info(f"[FALLBACK] ✅ Mensagem criada com sucesso: {message_id}")
                else:
                    logger.info(f"[FALLBACK] Mensagem já existe ou conteúdo vazio: {message_id}")
                
                logger.info(f"[FALLBACK] ✅ Chat processado com sucesso para chat_id: {chat_id}")
                
        except Exception as e:
            logger.error(f"Erro no fallback sender/msgContent: {e}")
            webhook_event.error_message = f"Erro no fallback: {e}"
            webhook_event.save()
            raise

    def _get_or_create_chat_mock_structure(self, chat_id: str, sender_name: str, is_group: bool = False, group_name: str = None, profile_picture: str = None) -> Chat:
        """
        Cria ou obtém um chat seguindo a estrutura dos dados mockados
        Se já existir, atualiza os campos relevantes com os dados mais recentes
        """
        try:
            logger.info(f"[FALLBACK] Tentando criar/obter chat: chat_id={chat_id}, sender_name={sender_name}, is_group={is_group}, profile_picture={profile_picture}")
            
            # VALIDAÇÃO: Garantir que chat_id não seja vazio
            safe_chat_id = chat_id or "sem_id"
            if not safe_chat_id or str(safe_chat_id).strip() == '':
                logger.error(f"[FALLBACK] chat_id está vazio ou None: '{chat_id}' (bloqueado por validação extra)")
                return None
            
            # Usar get_or_create para evitar problemas de duplicação
            safe_chat_name = sender_name or (group_name if is_group else safe_chat_id)
            chat, created = CoreChat.objects.get_or_create(
                chat_id=safe_chat_id,
                cliente=self.cliente,
                defaults={
                    'chat_name': safe_chat_name,
                    'is_group': is_group,
                    'canal': 'whatsapp',
                    'status': 'ativo',
                    'last_message_at': django_timezone.now(),
                    'foto_perfil': profile_picture
                }
            )
            
            # Se chat já existia, atualizar campos relevantes
            if not created:
                chat.status = 'ativo'
                chat.last_message_at = django_timezone.now()
                # Atualizar foto de perfil se uma nova foi fornecida
                if profile_picture and chat.foto_perfil != profile_picture:
                    chat.foto_perfil = profile_picture
                chat.save()
                logger.info(f"[FALLBACK] Chat existente atualizado: {chat.chat_id} - Foto: {profile_picture}")
            else:
                logger.info(f"[FALLBACK] Chat criado: {chat.chat_id} - Foto: {profile_picture}")
            
            return chat
        except Exception as e:
            logger.error(f"[FALLBACK] Erro ao criar/obter chat: {e}")
            logger.error(f"[FALLBACK] Parâmetros: chat_id={chat_id}, sender_name={sender_name}, is_group={is_group}, group_name={group_name}, profile_picture={profile_picture}")
            return None


class WebhookValidator:
    """
    Validador de webhooks
    """
    
    @staticmethod
    def validate_webhook_data(data: Dict[str, Any]) -> bool:
        """
        Valida se os dados do webhook são válidos
        """
        if not data:
            return False
            
        # Verificar se tem pelo menos um campo obrigatório
        required_fields = ['key', 'message', 'sender', 'msgContent']
        has_required = any(field in data for field in required_fields)
        
        return has_required
    
    @staticmethod
    def sanitize_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitiza os dados do webhook
        """
        # Remover campos sensíveis se necessário
        sensitive_fields = ['password', 'token', 'secret']
        
        sanitized = data.copy()
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = '***REDACTED***'
                
        return sanitized

