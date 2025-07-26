from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import json
import logging
import uuid # Importar uuid para gerar IDs únicos

from core.models import WebhookEvent, WhatsappInstance, Chat, Mensagem, Sender, MessageMedia

logger = logging.getLogger(__name__)

class WhatsappWebhookView(APIView):
    """View para receber e processar webhooks da API do WhatsApp (W-APi).

    Esta view não requer autenticação, pois é um endpoint para receber dados
    externos. Ela salva o evento bruto e tenta processá-lo para atualizar
    os modelos do sistema (instâncias, chats, mensagens, etc.).
    """
    authentication_classes = [] # Não requer autenticação para webhooks
    permission_classes = []     # Não requer permissão para webhooks

    def post(self, request, *args, **kwargs):
        """Recebe e processa um evento de webhook POST.

        Args:
            request (Request): Objeto de requisição contendo o payload do webhook.

        Returns:
            Response: Resposta HTTP indicando o status do processamento.
        """
        payload = request.data
        instance_id = payload.get("instanceId")
        event_type = payload.get("event")
        # messageId é usado como event_id para garantir unicidade e rastreabilidade
        event_unique_id = payload.get("messageId", str(uuid.uuid4())) # Gerar um UUID se messageId não existir

        if not instance_id or not event_type:
            logger.warning(f"Webhook inválido recebido (instanceId ou event_type ausente): {payload}")
            return Response({"status": "error", "message": "Payload inválido: instanceId ou event_type ausente"}, status=status.HTTP_400_BAD_REQUEST)

        # Evitar processamento duplicado de eventos com o mesmo ID
        if WebhookEvent.objects.filter(event_id=event_unique_id).exists():
            logger.info(f"Evento {event_unique_id} já recebido e processado. Ignorando duplicata.")
            return Response({"status": "success", "message": "Evento já processado"}, status=status.HTTP_200_OK)

        try:
            # Salvar o evento bruto do webhook
            webhook_event = WebhookEvent.objects.create(
                event_id=event_unique_id,
                instance_id=instance_id,
                event_type=event_type,
                payload=payload
            )
            logger.info(f"WebhookEvent salvo: {webhook_event.event_id}")

            # Processar o evento em segundo plano ou de forma síncrona
            # Para simplicidade, processaremos síncronamente aqui. Em produção, considere Celery/RQ.
            self._process_webhook_event(webhook_event)

            return Response({"status": "success", "message": "Webhook recebido e processado"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Erro ao processar webhook {event_unique_id}: {e}", exc_info=True)
            # Atualizar o evento com a mensagem de erro
            if webhook_event and not webhook_event.processed:
                webhook_event.error_message = str(e)
                webhook_event.save()
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _process_webhook_event(self, webhook_event):
        """Processa um WebhookEvent salvo, atualizando os modelos do sistema.

        Args:
            webhook_event (WebhookEvent): O objeto WebhookEvent a ser processado.
        """
        payload = webhook_event.payload
        instance_id = webhook_event.instance_id
        event_type = webhook_event.event_type

        try:
            # Tentar encontrar a instância do WhatsApp associada
            whatsapp_instance = WhatsappInstance.objects.filter(instance_id=instance_id).first()
            if not whatsapp_instance:
                logger.warning(f"Instância do WhatsApp {instance_id} não encontrada para o evento {webhook_event.event_id}. O evento será salvo, mas não processado completamente.")
                webhook_event.error_message = f"Instância {instance_id} não encontrada"
                webhook_event.save()
                return

            # Lógica de roteamento para diferentes tipos de eventos
            if event_type == "message":
                self._process_message_event(webhook_event, whatsapp_instance)
            elif event_type == "instanceStatus":
                self._process_instance_status_event(webhook_event, whatsapp_instance)
            elif event_type == "qrCode": # Evento de QR Code
                self._process_qrcode_event(webhook_event, whatsapp_instance)
            # Adicionar outros tipos de eventos conforme a documentação da W-APi
            else:
                logger.info(f"Tipo de evento \'{event_type}\' não suportado ou não requer processamento específico.")

            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()

        except Exception as e:
            logger.error(f"Erro no processamento detalhado do evento {webhook_event.event_id}: {e}", exc_info=True)
            webhook_event.error_message = str(e)
            webhook_event.save()

    def _process_message_event(self, webhook_event, whatsapp_instance):
        """Processa um evento de mensagem recebido do WhatsApp.

        Cria ou atualiza o Chat, Mensagem, Sender e Mídia (se houver).

        Args:
            webhook_event (WebhookEvent): O objeto WebhookEvent da mensagem.
            whatsapp_instance (WhatsappInstance): A instância do WhatsApp associada.
        """
        payload = webhook_event.payload
        message_data = payload.get("msgContent", {})
        sender_data = payload.get("sender", {})

        # Extrair informações do remetente
        sender_id = sender_data.get("id")
        sender_name = sender_data.get("pushName", sender_id) # Usa pushName se disponível, senão o ID
        is_group = payload.get("isGroup", False)
        
        # LÓGICA MELHORADA PARA DETERMINAR from_me
        from_me = False
        
        # Método 1: Verificar campo fromMe no payload raiz
        if payload.get('fromMe') is not None:
            from_me = payload.get('fromMe', False)
        # Método 2: Verificar campo fromMe no sender_data
        elif sender_data.get('fromMe') is not None:
            from_me = sender_data.get('fromMe', False)
        # Método 3: Verificar se o sender_id é o mesmo da instância (usuário atual)
        else:
            # Se o sender_id contém o instance_id, é uma mensagem enviada pelo usuário
            instance_id = whatsapp_instance.instance_id
            if instance_id and sender_id and instance_id in sender_id:
                from_me = True
            # Método 4: Verificar pelo nome do remetente (fallback)
            elif sender_name and "Elizeu" in sender_name:
                from_me = True
        
        profile_pic = sender_data.get("profilePicThumb")

        # Atualizar foto de perfil do cliente/contato se NÃO for você mesmo
        if not from_me and profile_pic and sender_id:
            try:
                from core.models import Cliente
                contato = Cliente.objects.filter(telefone=sender_id).first()
                if contato and (not contato.foto_perfil or contato.foto_perfil != profile_pic):
                    contato.foto_perfil = profile_pic
                    contato.save()
            except Exception as e:
                logger.error(f"Erro ao atualizar foto de perfil do cliente {sender_id}: {e}")

        # Criar ou atualizar o Sender (remetente da mensagem)
        sender, created = Sender.objects.get_or_create(
            event=webhook_event, # Associar ao evento para rastreamento
            sender_id=sender_id,
            defaults={
                'push_name': sender_name,
                'is_group': is_group,
                'group_name': payload.get("chatName") if is_group else None
            }
        )
        if not created:
            # Atualizar informações do sender se já existir
            sender.push_name = sender_name
            sender.is_group = is_group
            sender.group_name = payload.get("chatName") if is_group else None
            sender.save()

        # Criar ou obter o Chat
        chat_id = payload.get("chatId") # ID do chat (pode ser o mesmo do sender_id para chats individuais)
        chat, created = Chat.objects.get_or_create(
            chat_id=chat_id,
            cliente=whatsapp_instance.cliente,
            defaults={
                'chat_name': sender_name, # Nome do contato/grupo
                'is_group': is_group,
                'canal': 'whatsapp',
                'status': 'active',
                'last_message_at': timezone.now()
            }
        )
        if not created:
            # Atualizar o chat se já existir
            chat.last_message_at = timezone.now()
            chat.chat_name = sender_name # Atualiza nome do contato/grupo
            chat.save()

        # Criar a Mensagem
        message_type = self._detect_message_type(payload)
        content = self._extract_message_content(payload)
        # O timestamp do payload geralmente vem em segundos. Converter para datetime.
        timestamp = timezone.datetime.fromtimestamp(payload.get("timestamp"), tz=timezone.utc)

        mensagem = Mensagem.objects.create(
            chat=chat,
            message_id=payload.get("messageId"),
            sender_id=sender_id,
            sender_name=sender_name,
            from_me=from_me,
            type=message_type,
            content=content,
            timestamp=timestamp,
            raw_data=payload
        )
        logger.info(f"Mensagem {payload.get('messageId')} processada para o chat {chat.chat_id}")

        # Processar mídia, se houver
        self._process_message_media(webhook_event, mensagem, payload)

    def _process_instance_status_event(self, webhook_event, whatsapp_instance):
        """Processa um evento de status da instância do WhatsApp.

        Atualiza o status da instância e a data de conexão/desconexão.

        Args:
            webhook_event (WebhookEvent): O objeto WebhookEvent do status da instância.
            whatsapp_instance (WhatsappInstance): A instância do WhatsApp associada.
        """
        payload = webhook_event.payload
        status_data = payload.get("statusData", {})
        new_status = status_data.get("status")

        if new_status:
            whatsapp_instance.status = new_status
            if new_status == "connected":
                whatsapp_instance.data_conexao = timezone.now()
                whatsapp_instance.qr_code = None # Limpar QR Code após conexão bem-sucedida
            elif new_status == "disconnected":
                whatsapp_instance.data_desconexao = timezone.now()
            whatsapp_instance.save()
            logger.info(f"Instância {whatsapp_instance.instance_id} atualizada para status: {new_status}")

    def _process_qrcode_event(self, webhook_event, whatsapp_instance):
        """Processa um evento de QR Code recebido do WhatsApp.

        Atualiza o QR Code da instância.

        Args:
            webhook_event (WebhookEvent): O objeto WebhookEvent do QR Code.
            whatsapp_instance (WhatsappInstance): A instância do WhatsApp associada.
        """
        payload = webhook_event.payload
        qr_code_data = payload.get("qrCode")

        if qr_code_data:
            whatsapp_instance.qr_code = qr_code_data
            whatsapp_instance.status = "aguardando_qrcode" # Ou outro status apropriado
            whatsapp_instance.save()
            logger.info(f"QR Code atualizado para instância {whatsapp_instance.instance_id}")

    def _detect_message_type(self, payload):
        """Detecta o tipo de mensagem com base no payload do webhook.

        Args:
            payload (dict): O payload completo do webhook.

        Returns:
            str: O tipo de mensagem (ex: 'text', 'image', 'video', 'unknown').
        """
        msg_content = payload.get("msgContent", {})
        if "conversation" in msg_content:
            return "text"
        elif "imageMessage" in msg_content:
            return "image"
        elif "videoMessage" in msg_content:
            return "video"
        elif "audioMessage" in msg_content:
            return "audio"
        elif "documentMessage" in msg_content:
            return "document"
        elif "stickerMessage" in msg_content:
            return "sticker"
        elif "locationMessage" in msg_content:
            return "location"
        elif "contactMessage" in msg_content:
            return "contact"
        elif "pollCreationMessageV3" in msg_content:
            return "poll"
        elif "listMessage" in msg_content:
            return "list"
        elif "buttonsMessage" in msg_content:
            return "buttons"
        return "unknown"

    def _extract_message_content(self, payload):
        """Extrai o conteúdo principal da mensagem com base no tipo.

        Args:
            payload (dict): O payload completo do webhook.

        Returns:
            str: O conteúdo da mensagem (texto, legenda, URL, etc.).
        """
        msg_content = payload.get("msgContent", {})
        if "conversation" in msg_content:
            return msg_content["conversation"]
        elif "imageMessage" in msg_content:
            return msg_content["imageMessage"].get("caption", "") # Legenda da imagem
        elif "videoMessage" in msg_content:
            return msg_content["videoMessage"].get("caption", "") # Legenda do vídeo
        elif "documentMessage" in msg_content:
            return msg_content["documentMessage"].get("title", "") # Título do documento
        elif "locationMessage" in msg_content:
            return f"Latitude: {msg_content['locationMessage'].get('degreesLatitude')}, Longitude: {msg_content['locationMessage'].get('degreesLongitude')}"
        elif "contactMessage" in msg_content:
            return msg_content["contactMessage"].get("displayName", "") # Nome do contato
        elif "pollCreationMessageV3" in msg_content:
            return msg_content["pollCreationMessageV3"].get("name", "") # Nome da enquete
        # Adicionar extração para outros tipos de mensagem conforme necessário
        return json.dumps(msg_content) # Retorna o JSON completo se não for um tipo conhecido

    def _process_message_media(self, webhook_event, mensagem, payload):
        """Processa a mídia de uma mensagem, se houver.

        Cria um registro em MessageMedia.

        Args:
            webhook_event (WebhookEvent): O objeto WebhookEvent da mensagem.
            mensagem (Mensagem): O objeto Mensagem recém-criado.
            payload (dict): O payload completo do webhook.
        """
        msg_content = payload.get("msgContent", {})
        media_info = None
        media_type = self._detect_message_type(payload)

        if media_type == "image" and "imageMessage" in msg_content:
            media_info = msg_content["imageMessage"]
        elif media_type == "video" and "videoMessage" in msg_content:
            media_info = msg_content["videoMessage"]
        elif media_type == "audio" and "audioMessage" in msg_content:
            media_info = msg_content["audioMessage"]
        elif media_type == "document" and "documentMessage" in msg_content:
            media_info = msg_content["documentMessage"]

        if media_info and "url" in media_info:
            MessageMedia.objects.create(
                event=webhook_event,
                media_type=media_type,
                mimetype=media_info.get("mimetype", "application/octet-stream"),
                file_size=media_info.get("fileLength", 0),
                media_url=media_info["url"],
                # media_path será preenchido após o download, se implementado
                download_status="pending"
            )
            logger.info(f"Mídia detectada e registrada para o evento {webhook_event.event_id}")




