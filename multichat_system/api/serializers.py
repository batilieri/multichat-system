from rest_framework import serializers
from core.models import Cliente, Departamento, WhatsappInstance, Chat, Mensagem, WebhookEvent, MediaFile
from authentication.models import Usuario  # Importação corrigida para o modelo de usuário


class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Cliente.
    
    Inclui campos para integração com W-APi do WhatsApp.
    """
    whatsapp_status = serializers.SerializerMethodField()

    def get_whatsapp_status(self, obj):
        # Importação lazy para evitar problemas de importação circular e linter
        from core.models import WhatsappInstance
        instance = WhatsappInstance.objects.filter(cliente=obj).first()
        if instance:
            return instance.status or "desconectado"
        return "desconectado"

    class Meta:
        model = Cliente
        fields = ["id", "nome", "email", "telefone", "empresa", "data_cadastro", "ativo", "wapi_instance_id", "wapi_token", "whatsapp_status"]
        read_only_fields = ["data_cadastro"]


class WhatsappInstanceSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo WhatsappInstance.
    
    Gerencia instâncias de conexão do WhatsApp via W-APi.
    """
    cliente_nome = serializers.ReadOnlyField(source="cliente.nome")
    
    class Meta:
        model = WhatsappInstance
        fields = [
            "id", "instance_id", "token", "cliente", "cliente_nome", 
            "status", "qr_code", "last_seen", "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at", "last_seen"]
        extra_kwargs = {
            'token': {'write_only': True},  # Token não deve ser exposto na leitura
        }


class WhatsappInstanceEditSerializer(serializers.ModelSerializer):
    """
    Serializer para edição de instâncias WhatsApp que inclui o token.
    
    Usado apenas para formulários de edição onde o token precisa ser exibido.
    """
    cliente_nome = serializers.ReadOnlyField(source="cliente.nome")
    
    class Meta:
        model = WhatsappInstance
        fields = [
            "id", "instance_id", "token", "cliente", "cliente_nome", 
            "status", "qr_code", "last_seen", "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at", "last_seen"]


class DepartamentoSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Departamento.
    """
    class Meta:
        model = Departamento
        fields = ["id", "nome", "cliente", "ativo"]


class ChatSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Chat com campos adicionais para o frontend.
    """
    cliente_nome = serializers.ReadOnlyField(source="cliente.nome")
    atendente_nome = serializers.ReadOnlyField(source="atendente.username")
    ultima_mensagem = serializers.SerializerMethodField()
    total_mensagens = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    chat_name = serializers.CharField(read_only=True)  # <-- Adicionado para expor o nome do contato/grupo
    profile_picture = serializers.SerializerMethodField()  # <-- Novo campo para compatibilidade
    is_group = serializers.BooleanField(read_only=True)  # <-- Campo para identificar grupos
    group_id = serializers.CharField(read_only=True)  # <-- ID único do grupo
    sender_name = serializers.SerializerMethodField()  # <-- Número de telefone
    contact_name = serializers.SerializerMethodField()  # <-- Nome do contato

    class Meta:
        model = Chat
        fields = [
            "id", "chat_id", "chat_name", "cliente", "cliente_nome", "data_inicio", 
            "data_fim", "status", "atendente", "atendente_nome", "canal", 
            "last_message_at", "ultima_mensagem", "total_mensagens", "unread_count", 
            "profile_picture", "is_group", "group_id", "foto_perfil", "sender_name", "contact_name"
        ]
        read_only_fields = ["data_inicio", "last_message_at"]

    def get_sender_name(self, obj):
        """
        Retorna o número de telefone como sender_name
        """
        return obj.chat_id

    def get_contact_name(self, obj):
        """
        Retorna o nome do contato baseado na última mensagem do chat
        Se você enviou a última mensagem, mostra o número de telefone
        Se a pessoa respondeu, mostra o nome dela
        """
        try:
            # Buscar a última mensagem do chat
            ultima_mensagem = obj.mensagens.order_by('-data_envio').first()
            
            if ultima_mensagem:
                # Se a última mensagem foi enviada por você (from_me=True)
                if ultima_mensagem.from_me:
                    # Buscar a última mensagem da pessoa (não from_me)
                    ultima_pessoa = obj.mensagens.filter(from_me=False).order_by('-data_envio').first()
                    
                    if ultima_pessoa:
                        # Mostrar o nome da pessoa que respondeu
                        if ultima_pessoa.sender_display_name:
                            return ultima_pessoa.sender_display_name
                        elif ultima_pessoa.remetente and ultima_pessoa.remetente != obj.chat_id:
                            return ultima_pessoa.remetente
                        else:
                            # Buscar no sender
                            from webhook.models import Sender
                            sender = Sender.objects.filter(
                                sender_id=obj.chat_id,
                                cliente=obj.cliente
                            ).order_by('-id').first()
                            
                            if sender:
                                return sender.push_name or sender.verified_name or obj.chat_id
                            else:
                                return obj.chat_id
                    else:
                        # Se nunca houve resposta da pessoa, mostrar o número
                        return obj.chat_id
                else:
                    # Se a pessoa respondeu, mostrar o nome dela
                    # Primeiro tentar usar o sender_display_name da mensagem
                    if ultima_mensagem.sender_display_name:
                        return ultima_mensagem.sender_display_name
                    
                    # Depois tentar usar o remetente da mensagem
                    if ultima_mensagem.remetente and ultima_mensagem.remetente != obj.chat_id:
                        return ultima_mensagem.remetente
                    
                    # Por último, buscar no sender
                    from webhook.models import Sender
                    sender = Sender.objects.filter(
                        sender_id=obj.chat_id,
                        cliente=obj.cliente
                    ).order_by('-id').first()
                    
                    if sender:
                        return sender.push_name or sender.verified_name or obj.chat_id
                    else:
                        return obj.chat_id
            
            # Se não há mensagens, mostrar o número de telefone
            return obj.chat_id
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"❌ Erro ao buscar nome do contato: {e}")
            return obj.chat_id

    def get_ultima_mensagem(self, obj):
        """Retorna a última mensagem do chat"""
        ultima = obj.mensagens.order_by('-data_envio').first()
        if ultima:
            return {
                "tipo": ultima.tipo,
                "conteudo": ultima.conteudo,
                "data": ultima.data_envio.isoformat(),
                "remetente": ultima.remetente,
                "sender_display_name": ultima.get_sender_display_name()
            }
        return {
            "tipo": "text",
            "conteudo": "Nenhuma mensagem ainda",
            "data": obj.data_inicio.isoformat(),
            "remetente": "Sistema"
        }

    def get_total_mensagens(self, obj):
        """Retorna o total de mensagens do chat"""
        return obj.mensagens.count()

    def get_unread_count(self, obj):
        """Retorna o número de mensagens não lidas"""
        return obj.mensagens.filter(lida=False).count()

    def get_profile_picture(self, obj):
        """Retorna a foto de perfil do chat com fallbacks robustos"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Prioridade 1: foto_perfil do objeto Chat
        if obj.foto_perfil:
            logger.info(f"🖼️ Foto encontrada no campo foto_perfil: {obj.foto_perfil}")
            return obj.foto_perfil
        
        # Prioridade 2: buscar da última mensagem do webhook relacionada
        try:
            from webhook.models import WebhookEvent
            last_event = WebhookEvent.objects.filter(
                chat_id=obj.chat_id,
                cliente=obj.cliente
            ).order_by('-received_at').first()
            
            if last_event and last_event.raw_data:
                webhook_data = last_event.raw_data
                
                # Tentar extrair de múltiplas fontes
                sources = [
                    webhook_data.get('sender', {}).get('profilePicture'),
                    webhook_data.get('sender', {}).get('profile_picture'),
                    webhook_data.get('chat', {}).get('profilePicture'),
                    webhook_data.get('chat', {}).get('profile_picture'),
                    webhook_data.get('profilePicture'),
                    webhook_data.get('profile_picture'),
                ]
                
                for source in sources:
                    if source and isinstance(source, str) and source.strip():
                        photo_url = source.strip()
                        logger.info(f"🖼️ Foto encontrada no webhook: {photo_url}")
                        
                        # Atualizar o campo foto_perfil para próximas consultas
                        try:
                            obj.foto_perfil = photo_url
                            obj.save(update_fields=['foto_perfil'])
                            logger.info(f"🖼️ Campo foto_perfil atualizado para chat {obj.chat_id}")
                        except Exception as e:
                            logger.error(f"❌ Erro ao atualizar foto_perfil: {e}")
                        
                        return photo_url
        
        except Exception as e:
            logger.error(f"❌ Erro ao buscar foto de perfil do webhook: {e}")
        
        logger.info(f"🖼️ Nenhuma foto encontrada para chat {obj.chat_id}")
        return None


class MensagemSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Mensagem.
    """
    tipo = serializers.SerializerMethodField()
    fromMe = serializers.BooleanField(source='from_me', read_only=True)  # Campo para o frontend
    from_me = serializers.BooleanField(read_only=True)  # Campo adicional para compatibilidade
    sender_display_name = serializers.SerializerMethodField()  # Nome do remetente em grupos
    conteudo = serializers.SerializerMethodField()  # Processar conteúdo de mídia
    media_url = serializers.SerializerMethodField()  # URL do arquivo local

    class Meta:
        model = Mensagem
        fields = [
            "id", "chat", "remetente", "conteudo", "data_envio", "tipo", "lida", "fromMe", "from_me",
            "sender_display_name", "sender_push_name", "sender_verified_name", "message_id", "reacoes",
            "media_url"
        ]
        read_only_fields = ["data_envio"]

    def get_tipo(self, obj):
        # Mapeamento para garantir compatibilidade frontend (português)
        tipo_map = {
            "text": "texto",
            "texto": "texto",
            "image": "imagem",
            "imagem": "imagem",
            "audio": "audio",
            "video": "video",
            "document": "documento",
            "documento": "documento",
            "sticker": "sticker"
        }
        return tipo_map.get(obj.tipo, obj.tipo)
    
    def get_sender_display_name(self, obj):
        """Retorna o nome de exibição do remetente para grupos"""
        return obj.get_sender_display_name()
    
    def get_conteudo(self, obj):
        """Processa o conteúdo da mensagem, substituindo URLs externas por locais"""
        import re
        from pathlib import Path
        import os
        
        conteudo = obj.conteudo
        
        # Se é uma mensagem de mídia, tentar encontrar o arquivo local
        if obj.tipo in ['audio', 'image', 'video', 'document', 'sticker'] and conteudo:
            # Extrair o message_id do conteúdo se possível
            message_id = None
            if obj.message_id:
                message_id = obj.message_id[:8]  # Primeiros 8 caracteres
            
            # Tentar encontrar arquivo local baseado no message_id
            if message_id:
                media_path = self._get_local_media_url(obj, message_id)
                if media_path:
                    return media_path
        
        return conteudo
    
    def get_media_url(self, obj):
        """Retorna a URL do arquivo local de mídia"""
        if obj.tipo in ['audio', 'image', 'video', 'document', 'sticker'] and obj.message_id:
            message_id = obj.message_id[:8]
            return self._get_local_media_url(obj, message_id)
        return None
    
    def _get_local_media_url(self, obj, message_id):
        """Busca o arquivo local de mídia e retorna a URL"""
        import os
        from pathlib import Path
        import glob
        
        try:
            # Caminho base da instância
            if not hasattr(obj.chat, 'cliente') or not obj.chat.cliente.whatsapp_instances.first():
                return None
                
            instance = obj.chat.cliente.whatsapp_instances.first()
            cliente_id = obj.chat.cliente.id
            instance_id = instance.instance_id
            chat_id = obj.chat.chat_id
            
            # Normalizar tipo de mídia
            tipo_map = {
                'audio': 'audio',
                'image': 'imagens', 
                'video': 'videos',
                'document': 'documentos',
                'sticker': 'stickers'
            }
            
            tipo_pasta = tipo_map.get(obj.tipo, obj.tipo)
            
            # Caminho da pasta de mídia - CORRIGIDO
            base_path = Path(__file__).parent.parent / "media_storage" / f"cliente_{cliente_id}" / f"instance_{instance_id}" / "chats" / str(chat_id) / tipo_pasta
            
            print(f"🔍 Procurando em: {base_path}")
            
            if not base_path.exists():
                print(f"❌ Pasta não existe: {base_path}")
                return None
            
            # Procurar arquivo que começa com msg_{message_id}
            pattern = f"msg_{message_id}_*"
            arquivos = list(base_path.glob(pattern))
            
            print(f"🔍 Padrão: {pattern}")
            print(f"🔍 Arquivos encontrados: {len(arquivos)}")
            
            if arquivos:
                arquivo = arquivos[0]  # Pegar o primeiro arquivo encontrado
                print(f"✅ Arquivo encontrado: {arquivo.name}")
                # Retornar URL relativa para o frontend
                return f"/media/whatsapp_media/cliente_{cliente_id}/instance_{instance_id}/chats/{chat_id}/{tipo_pasta}/{arquivo.name}"
            else:
                # Tentar outros padrões
                outros_padroes = [
                    f"audio_{message_id}_*",
                    f"{message_id}_*",
                    f"msg_*_{message_id}_*",
                    "*"
                ]
                
                for padrao in outros_padroes:
                    arquivos = list(base_path.glob(padrao))
                    if arquivos:
                        arquivo = arquivos[0]
                        print(f"✅ Arquivo encontrado com padrão '{padrao}': {arquivo.name}")
                        return f"/media/whatsapp_media/cliente_{cliente_id}/instance_{instance_id}/chats/{chat_id}/{tipo_pasta}/{arquivo.name}"
                
                print(f"❌ Nenhum arquivo encontrado para message_id: {message_id}")
                return None
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao buscar URL de mídia local: {e}")
            print(f"❌ Erro ao buscar mídia: {e}")
        
        return None


class WebhookEventSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo WebhookEvent.
    """
    class Meta:
        model = WebhookEvent
        fields = ["event_id", "instance_id", "event_type", "payload", "received_at", "processed", "error_message"]
        read_only_fields = ["event_id", "received_at"]


class WebhookMessageSerializer(serializers.ModelSerializer):
    """
    Serializer para mensagens do webhook com campos de identificação do remetente
    """
    sender_display_name = serializers.SerializerMethodField()
    
    class Meta:
        from webhook.models import Message
        model = Message
        fields = '__all__'
    
    def get_sender_display_name(self, obj):
        """Retorna o nome de exibição do remetente para grupos"""
        return obj.get_sender_display_name()


class MediaFileSerializer(serializers.ModelSerializer):
    """Serializer para MediaFile"""
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    instance_id = serializers.CharField(source='instance.instance_id', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaFile
        fields = [
            'id', 'cliente', 'cliente_nome', 'instance', 'instance_id', 'chat',
            'message_id', 'sender_name', 'sender_id', 'media_type', 'mimetype',
            'file_name', 'file_path', 'file_size', 'caption', 'width', 'height',
            'duration_seconds', 'is_ptt', 'download_status', 'is_group', 'from_me',
            'media_key', 'direct_path', 'file_sha256', 'file_enc_sha256',
            'media_key_timestamp', 'message_timestamp', 'download_timestamp',
            'created_at', 'updated_at', 'file_url'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_file_url(self, obj):
        """Retorna a URL para acessar o arquivo"""
        if obj.file_path and obj.download_status == 'success':
            # Usar o endpoint de mídias WAPI
            if obj.media_type == 'audio':
                return f"/api/wapi-media/audios/{obj.file_name}"
            elif obj.media_type == 'image':
                return f"/api/wapi-media/imagens/{obj.file_name}"
            elif obj.media_type == 'video':
                return f"/api/wapi-media/videos/{obj.file_name}"
            elif obj.media_type == 'document':
                return f"/api/wapi-media/documentos/{obj.file_name}"
            elif obj.media_type == 'sticker':
                return f"/api/wapi-media/stickers/{obj.file_name}"
        return None





