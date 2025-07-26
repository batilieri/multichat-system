from django.db import models
from django.utils import timezone
import uuid
import json
from pathlib import Path
from django.conf import settings


class WebhookEvent(models.Model):
    """
    Armazena todos os eventos de webhook recebidos do WhatsApp
    Baseado na estrutura do betZap com integração de cliente
    """
    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey('core.Cliente', on_delete=models.CASCADE, verbose_name="Cliente", related_name='webhook_events')
    instance_id = models.CharField(max_length=255, verbose_name="ID da Instância")
    event_type = models.CharField(max_length=100, verbose_name="Tipo do Evento")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Timestamp")
    
    # Dados brutos do webhook
    raw_data = models.JSONField(verbose_name="Dados Brutos")
    
    # Dados processados
    chat_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID do Chat")
    sender_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID do Remetente")
    sender_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome do Remetente")
    message_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID da Mensagem")
    message_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tipo da Mensagem")
    message_content = models.TextField(blank=True, null=True, verbose_name="Conteúdo da Mensagem")
    
    # Status e processamento
    processed = models.BooleanField(default=False, verbose_name="Processado")
    error_message = models.TextField(blank=True, null=True, verbose_name="Mensagem de Erro")
    
    # Metadados
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP de Origem")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    
    class Meta:
        verbose_name = "Evento de Webhook"
        verbose_name_plural = "Eventos de Webhook"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['cliente', 'timestamp']),
            models.Index(fields=['event_type', 'processed']),
            models.Index(fields=['chat_id', 'sender_id']),
        ]

    def __str__(self):
        return f"Evento {self.event_type} - {self.cliente.nome} - {self.timestamp}"


class Chat(models.Model):
    """
    Representa uma conversa/chat do WhatsApp
    """
    chat_id = models.CharField(max_length=255, unique=True, verbose_name="ID do Chat")
    cliente = models.ForeignKey('core.Cliente', on_delete=models.CASCADE, verbose_name="Cliente", related_name='webhook_chats')
    
    # Informações do chat
    chat_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome do Chat")
    is_group = models.BooleanField(default=False, verbose_name="É Grupo")
    group_id = models.CharField(max_length=255, blank=True, null=True, unique=True, verbose_name="ID Único do Grupo")
    group_participants = models.JSONField(default=list, blank=True, verbose_name="Participantes do Grupo")
    profile_picture = models.URLField(blank=True, null=True, verbose_name="Foto de Perfil")
    
    # Status e metadados
    status = models.CharField(max_length=50, default='active', verbose_name="Status")
    last_message_at = models.DateTimeField(blank=True, null=True, verbose_name="Última Mensagem")
    message_count = models.IntegerField(default=0, verbose_name="Total de Mensagens")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chats"
        ordering = ['-last_message_at']
        indexes = [
            models.Index(fields=['cliente', 'chat_id']),
            models.Index(fields=['status', 'last_message_at']),
            models.Index(fields=['is_group', 'group_id']),
        ]

    def __str__(self):
        return f"Chat {self.chat_name or self.chat_id} - {self.cliente.nome}"
    
    def save(self, *args, **kwargs):
        # Gerar group_id único se for um grupo e não tiver um
        if self.is_group and not self.group_id:
            import uuid
            self.group_id = f"group_{uuid.uuid4().hex[:16]}"
        super().save(*args, **kwargs)


class Sender(models.Model):
    """
    Representa um remetente/destinatário de mensagens
    """
    sender_id = models.CharField(max_length=255, verbose_name="ID do Remetente")
    cliente = models.ForeignKey('core.Cliente', on_delete=models.CASCADE, verbose_name="Cliente", related_name='webhook_senders')
    
    # Informações do remetente
    push_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome de Exibição")
    verified_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome Verificado")
    is_business = models.BooleanField(default=False, verbose_name="É Business")
    business_profile = models.JSONField(default=dict, blank=True, verbose_name="Perfil Business")
    profile_picture = models.URLField(blank=True, null=True, verbose_name="Foto de Perfil")
    
    # Estatísticas
    message_count = models.IntegerField(default=0, verbose_name="Total de Mensagens")
    last_seen = models.DateTimeField(blank=True, null=True, verbose_name="Última Vez Online")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Remetente"
        verbose_name_plural = "Remetentes"
        unique_together = ['sender_id', 'cliente']
        ordering = ['-last_seen']
        indexes = [
            models.Index(fields=['cliente', 'sender_id']),
            models.Index(fields=['is_business', 'last_seen']),
        ]

    def __str__(self):
        return f"{self.push_name or self.sender_id} - {self.cliente.nome}"


class Message(models.Model):
    """
    Representa uma mensagem individual do WhatsApp
    """
    message_id = models.CharField(max_length=255, unique=True, verbose_name="ID da Mensagem")
    cliente = models.ForeignKey('core.Cliente', on_delete=models.CASCADE, verbose_name="Cliente", related_name='webhook_messages')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, verbose_name="Chat")
    sender = models.ForeignKey(Sender, on_delete=models.CASCADE, verbose_name="Remetente")
    
    # Conteúdo da mensagem
    message_type = models.CharField(max_length=50, verbose_name="Tipo da Mensagem")
    content = models.JSONField(verbose_name="Conteúdo")
    text_content = models.TextField(blank=True, null=True, verbose_name="Texto da Mensagem")
    
    # Metadados da mensagem
    from_me = models.BooleanField(default=False, verbose_name="Enviada por Mim")
    timestamp = models.DateTimeField(verbose_name="Timestamp")
    status = models.CharField(max_length=50, default='sent', verbose_name="Status")
    
    # Campos para identificação do remetente em grupos
    sender_display_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome de Exibição do Remetente")
    sender_push_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome Push do Remetente")
    sender_verified_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome Verificado do Remetente")
    
    # Mídia (se aplicável)
    media_url = models.URLField(blank=True, null=True, verbose_name="URL da Mídia")
    media_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tipo da Mídia")
    media_size = models.BigIntegerField(blank=True, null=True, verbose_name="Tamanho da Mídia")
    
    # Campos detalhados para mídias
    media_caption = models.TextField(blank=True, null=True, verbose_name="Legenda da Mídia")
    media_height = models.IntegerField(blank=True, null=True, verbose_name="Altura da Mídia")
    media_width = models.IntegerField(blank=True, null=True, verbose_name="Largura da Mídia")
    jpeg_thumbnail = models.TextField(blank=True, null=True, verbose_name="Thumbnail JPEG (base64)")
    file_sha256 = models.CharField(max_length=100, blank=True, null=True, verbose_name="SHA256 do Arquivo")
    media_key = models.CharField(max_length=100, blank=True, null=True, verbose_name="Chave de Mídia")
    direct_path = models.TextField(blank=True, null=True, verbose_name="Caminho Direto da Mídia")
    media_key_timestamp = models.CharField(max_length=20, blank=True, null=True, verbose_name="Timestamp da Chave de Mídia")
    # Documento
    document_url = models.URLField(blank=True, null=True, verbose_name="URL do Documento")
    document_filename = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nome do Documento")
    document_mimetype = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mimetype do Documento")
    document_file_length = models.CharField(max_length=20, blank=True, null=True, verbose_name="Tamanho do Documento")
    document_page_count = models.IntegerField(blank=True, null=True, verbose_name="Páginas do Documento")
    # Localização
    location_latitude = models.FloatField(blank=True, null=True, verbose_name="Latitude")
    location_longitude = models.FloatField(blank=True, null=True, verbose_name="Longitude")
    location_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nome do Local")
    location_address = models.TextField(blank=True, null=True, verbose_name="Endereço do Local")
    # Enquete
    poll_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nome da Enquete")
    poll_options = models.TextField(blank=True, null=True, verbose_name="Opções da Enquete (JSON)")
    poll_selectable_count = models.IntegerField(blank=True, null=True, verbose_name="Qtd Selecionável")
    # Sticker
    sticker_url = models.URLField(blank=True, null=True, verbose_name="URL do Sticker")
    sticker_mimetype = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mimetype do Sticker")
    sticker_file_length = models.CharField(max_length=20, blank=True, null=True, verbose_name="Tamanho do Sticker")
    sticker_is_animated = models.BooleanField(default=False, verbose_name="Sticker Animado")
    sticker_is_avatar = models.BooleanField(default=False, verbose_name="Sticker Avatar")
    sticker_is_ai = models.BooleanField(default=False, verbose_name="Sticker AI")
    sticker_is_lottie = models.BooleanField(default=False, verbose_name="Sticker Lottie")
    # Thumbnails extras
    thumbnail_direct_path = models.TextField(blank=True, null=True, verbose_name="Caminho Direto do Thumbnail")
    thumbnail_sha256 = models.CharField(max_length=100, blank=True, null=True, verbose_name="SHA256 do Thumbnail")
    thumbnail_enc_sha256 = models.CharField(max_length=100, blank=True, null=True, verbose_name="SHA256 Enc do Thumbnail")
    thumbnail_height = models.IntegerField(blank=True, null=True, verbose_name="Altura do Thumbnail")
    thumbnail_width = models.IntegerField(blank=True, null=True, verbose_name="Largura do Thumbnail")
    
    # Reações e respostas
    reactions = models.JSONField(default=list, blank=True, verbose_name="Reações")
    quoted_message_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Mensagem Citada")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['cliente', 'chat', 'timestamp']),
            models.Index(fields=['sender', 'from_me']),
            models.Index(fields=['message_type', 'status']),
            models.Index(fields=['chat', 'sender_display_name']),
        ]

    def __str__(self):
        return f"Msg {self.message_id[:8]} - {self.chat.chat_name} - {self.timestamp}"
    
    def get_sender_display_name(self):
        """
        Retorna o nome de exibição do remetente para grupos
        """
        if self.chat.is_group and not self.from_me:
            return self.sender_display_name or self.sender_push_name or self.sender_verified_name or self.sender.sender_id
        return None


class MessageStats(models.Model):
    """
    Estatísticas de mensagens por período
    """
    cliente = models.ForeignKey('core.Cliente', on_delete=models.CASCADE, verbose_name="Cliente", related_name='webhook_message_stats')
    date = models.DateField(verbose_name="Data")
    
    # Contadores
    total_messages = models.IntegerField(default=0, verbose_name="Total de Mensagens")
    received_messages = models.IntegerField(default=0, verbose_name="Mensagens Recebidas")
    sent_messages = models.IntegerField(default=0, verbose_name="Mensagens Enviadas")
    
    # Por tipo
    text_messages = models.IntegerField(default=0, verbose_name="Mensagens de Texto")
    media_messages = models.IntegerField(default=0, verbose_name="Mensagens de Mídia")
    document_messages = models.IntegerField(default=0, verbose_name="Mensagens de Documento")
    
    # Por status
    delivered_messages = models.IntegerField(default=0, verbose_name="Mensagens Entregues")
    read_messages = models.IntegerField(default=0, verbose_name="Mensagens Lidas")
    
    class Meta:
        verbose_name = "Estatística de Mensagem"
        verbose_name_plural = "Estatísticas de Mensagens"
        unique_together = ['cliente', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['cliente', 'date']),
        ]

    def __str__(self):
        return f"Stats {self.cliente.nome} - {self.date}"


class ContactStats(models.Model):
    """
    Estatísticas de contatos
    """
    cliente = models.ForeignKey('core.Cliente', on_delete=models.CASCADE, verbose_name="Cliente", related_name='webhook_contact_stats')
    sender = models.ForeignKey(Sender, on_delete=models.CASCADE, verbose_name="Remetente")
    date = models.DateField(verbose_name="Data")
    
    # Contadores
    message_count = models.IntegerField(default=0, verbose_name="Total de Mensagens")
    first_message_at = models.DateTimeField(verbose_name="Primeira Mensagem")
    last_message_at = models.DateTimeField(verbose_name="Última Mensagem")
    
    # Tempo de resposta
    avg_response_time = models.FloatField(blank=True, null=True, verbose_name="Tempo Médio de Resposta")
    
    class Meta:
        verbose_name = "Estatística de Contato"
        verbose_name_plural = "Estatísticas de Contatos"
        unique_together = ['cliente', 'sender', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['cliente', 'sender', 'date']),
        ]

    def __str__(self):
        return f"Contact Stats {self.sender.push_name} - {self.date}"


class RealTimeStats(models.Model):
    """
    Estatísticas em tempo real
    """
    cliente = models.ForeignKey('core.Cliente', on_delete=models.CASCADE, verbose_name="Cliente", related_name='webhook_realtime_stats')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")
    
    # Métricas em tempo real
    active_chats = models.IntegerField(default=0, verbose_name="Chats Ativos")
    pending_messages = models.IntegerField(default=0, verbose_name="Mensagens Pendentes")
    online_users = models.IntegerField(default=0, verbose_name="Usuários Online")
    
    # Performance
    avg_response_time = models.FloatField(default=0, verbose_name="Tempo Médio de Resposta")
    message_throughput = models.FloatField(default=0, verbose_name="Taxa de Mensagens/min")
    
    class Meta:
        verbose_name = "Estatística em Tempo Real"
        verbose_name_plural = "Estatísticas em Tempo Real"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['cliente', 'timestamp']),
        ]

    def __str__(self):
        return f"RealTime {self.cliente.nome} - {self.timestamp}"


class MessageMedia(models.Model):
    """
    Tabela para relacionar mensagens/eventos com suas mídias baixadas
    """
    event = models.ForeignKey(WebhookEvent, on_delete=models.CASCADE, related_name='message_medias', verbose_name="Evento de Webhook")
    media_path = models.TextField(verbose_name="Caminho do Arquivo de Mídia")
    media_type = models.CharField(max_length=50, verbose_name="Tipo da Mídia")  # image, video, audio, document, sticker
    mimetype = models.CharField(max_length=50, blank=True, null=True, verbose_name="Mimetype")
    file_size = models.BigIntegerField(blank=True, null=True, verbose_name="Tamanho do Arquivo")
    download_status = models.CharField(max_length=20, default='pending', verbose_name="Status do Download")  # pending, success, failed, invalid_data, corrupted
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    # Campos adicionais para descriptografia e validação
    media_key = models.CharField(max_length=100, blank=True, null=True, verbose_name="Chave de Mídia")
    direct_path = models.TextField(blank=True, null=True, verbose_name="Caminho Direto da Mídia")
    file_sha256 = models.CharField(max_length=100, blank=True, null=True, verbose_name="SHA256 do Arquivo")
    file_enc_sha256 = models.CharField(max_length=100, blank=True, null=True, verbose_name="SHA256 Enc do Arquivo")
    media_key_timestamp = models.CharField(max_length=20, blank=True, null=True, verbose_name="Timestamp da Chave de Mídia")
    
    # Campos específicos por tipo de mídia
    caption = models.TextField(blank=True, null=True, verbose_name="Legenda")
    width = models.IntegerField(blank=True, null=True, verbose_name="Largura")
    height = models.IntegerField(blank=True, null=True, verbose_name="Altura")
    duration_seconds = models.IntegerField(blank=True, null=True, verbose_name="Duração (segundos)")
    is_ptt = models.BooleanField(default=False, verbose_name="Push to Talk")
    
    # Campos específicos de documento
    document_filename = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nome do Documento")
    document_title = models.CharField(max_length=200, blank=True, null=True, verbose_name="Título do Documento")
    document_page_count = models.IntegerField(blank=True, null=True, verbose_name="Páginas do Documento")
    
    # Campos específicos de sticker
    sticker_is_animated = models.BooleanField(default=False, verbose_name="Sticker Animado")
    sticker_is_avatar = models.BooleanField(default=False, verbose_name="Sticker Avatar")
    sticker_is_ai = models.BooleanField(default=False, verbose_name="Sticker AI")
    sticker_is_lottie = models.BooleanField(default=False, verbose_name="Sticker Lottie")
    
    # Campos de thumbnail
    jpeg_thumbnail = models.TextField(blank=True, null=True, verbose_name="Thumbnail JPEG (base64)")
    thumbnail_direct_path = models.TextField(blank=True, null=True, verbose_name="Caminho Direto do Thumbnail")
    thumbnail_sha256 = models.CharField(max_length=100, blank=True, null=True, verbose_name="SHA256 do Thumbnail")
    thumbnail_enc_sha256 = models.CharField(max_length=100, blank=True, null=True, verbose_name="SHA256 Enc do Thumbnail")
    thumbnail_height = models.IntegerField(blank=True, null=True, verbose_name="Altura do Thumbnail")
    thumbnail_width = models.IntegerField(blank=True, null=True, verbose_name="Largura do Thumbnail")
    
    # Campos de controle
    download_timestamp = models.DateTimeField(blank=True, null=True, verbose_name="Timestamp do Download")
    error_message = models.TextField(blank=True, null=True, verbose_name="Mensagem de Erro")
    retry_count = models.IntegerField(default=0, verbose_name="Tentativas de Download")

    class Meta:
        verbose_name = "Mídia de Mensagem"
        verbose_name_plural = "Mídias de Mensagem"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event', 'media_type']),
            models.Index(fields=['download_status']),
            models.Index(fields=['media_key']),
        ]

    def __str__(self):
        return f"Mídia {self.media_type} - {self.media_path}"
        
    def get_file_url(self):
        """Retorna a URL para acessar o arquivo de mídia"""
        if self.media_path and self.download_status == 'success':
            # Converter caminho relativo para URL
            media_url = self.media_path.replace(str(settings.MEDIA_ROOT), '')
            return f"{settings.MEDIA_URL}{media_url}"
        return None
        
    def get_file_exists(self):
        """Verifica se o arquivo físico existe"""
        if self.media_path and self.download_status == 'success':
            return Path(self.media_path).exists()
        return False
