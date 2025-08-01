from django.db import models
from django.utils import timezone
from authentication.models import Usuario


class Cliente(models.Model):
    # Modelo para representar um cliente do sistema MultiChat.
    
    # Cada cliente pode ter múltiplas instâncias do WhatsApp e departamentos.

    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    empresa = models.CharField(max_length=255, blank=True, null=True, verbose_name="Empresa")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    # Campos para integração com W-APi
    wapi_instance_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID da Instância W-APi")
    wapi_token = models.CharField(max_length=255, blank=True, null=True, verbose_name="Token W-APi")
    
    # Novo campo para foto de perfil do cliente/contato
    foto_perfil = models.URLField(blank=True, null=True, verbose_name="Foto de Perfil")
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome']
    def __str__(self):
        return self.nome


class Departamento(models.Model):
    # Modelo para representar departamentos de um cliente.
    
    # Cada cliente pode ter múltiplos departamentos para organizar atendimentos.

    nome = models.CharField(max_length=255, verbose_name="Nome do Departamento")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente", related_name='departamentos')
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ['nome']
        unique_together = ['nome', 'cliente']
    def __str__(self):
        return f"{self.nome} - {self.cliente.nome}"


class WhatsappInstance(models.Model):
    # Modelo para representar instâncias do WhatsApp conectadas via W-APi.
    
    # Cada cliente pode ter uma instância do WhatsApp para receber e enviar mensagens.
  
    instance_id = models.CharField(max_length=255, unique=True, verbose_name="ID da Instância")
    token = models.CharField(max_length=255, verbose_name="Token de Acesso")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente", related_name='whatsapp_instances')
    
    # Status da conexão
    status = models.CharField(max_length=50, default='disconnected', verbose_name="Status")
    qr_code = models.TextField(blank=True, null=True, verbose_name="QR Code")
    last_seen = models.DateTimeField(blank=True, null=True, verbose_name="Última Vez Online")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Instância do WhatsApp"
        verbose_name_plural = "Instâncias do WhatsApp"
        ordering = ['-created_at']
    def __str__(self):
        return f"Instância {self.instance_id} - {self.cliente.nome}"


class Chat(models.Model):
    # Modelo para representar conversas/chats do WhatsApp.
    
    # Cada chat está associado a um cliente e pode ter um atendente designado.
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('closed', 'Fechado'),
        ('pending', 'Pendente'),
    ]
    
    CANAL_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente", related_name='chats')
    atendente = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Atendente")
    
    # Informações do chat
    chat_id = models.CharField(max_length=255, verbose_name="ID do Chat", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES, default='whatsapp', verbose_name="Canal")
    chat_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome do Chat")
    is_group = models.BooleanField(default=False, verbose_name="É Grupo")
    group_id = models.CharField(max_length=255, blank=True, null=True, unique=True, verbose_name="ID Único do Grupo")

    # Novo campo para foto de perfil do contato/cliente
    foto_perfil = models.URLField(blank=True, null=True, verbose_name="Foto de Perfil")
    
    # Timestamps
    data_inicio = models.DateTimeField(auto_now_add=True, verbose_name="Data de Início")
    data_fim = models.DateTimeField(blank=True, null=True, verbose_name="Data de Fim")
    last_message_at = models.DateTimeField(blank=True, null=True, verbose_name="Última Mensagem")
    
    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chats"
        ordering = ['-last_message_at', '-data_inicio']
        unique_together = ['chat_id', 'cliente']
        indexes = [
            models.Index(fields=['cliente', 'chat_id']),
            models.Index(fields=['is_group', 'group_id']),
        ]
    
    def __str__(self):
        return f"Chat {self.chat_id} - {self.cliente.nome}"
    
    def save(self, *args, **kwargs):
        # Normalizar chat_id se necessário
        if self.chat_id:
            self.chat_id = self.normalize_chat_id(self.chat_id)
        
        # Gerar group_id único se for um grupo e não tiver um
        if self.is_group and not self.group_id:
            import uuid
            self.group_id = f"group_{uuid.uuid4().hex[:16]}"
        super().save(*args, **kwargs)
    
    @staticmethod
    def normalize_chat_id(chat_id):
        """
        Normaliza o chat_id para garantir que seja um número de telefone válido
        Remove sufixos como @lid, @c.us, etc e extrai apenas o número
        """
        if not chat_id:
            return None
        
        import re
        
        # Remover sufixos comuns do WhatsApp
        chat_id = re.sub(r'@[^.]+\.us$', '', chat_id)  # Remove @c.us, @lid, etc
        chat_id = re.sub(r'@[^.]+$', '', chat_id)      # Remove outros sufixos
        
        # Extrair apenas números
        numbers_only = re.sub(r'[^\d]', '', chat_id)
        
        # Validar se é um número de telefone válido (mínimo 10 dígitos)
        if len(numbers_only) >= 10:
            return numbers_only
        
        return chat_id  # Retornar original se não conseguir normalizar


class Mensagem(models.Model):
    # Modelo para representar mensagens individuais em um chat.
    
    # Cada mensagem está associada a um chat e pode ser de diferentes tipos.
    TIPO_CHOICES = [
        ('text', 'Texto'),
        ('image', 'Imagem'),
        ('video', 'Vídeo'),
        ('audio', 'Áudio'),
        ('document', 'Documento'),
        ('sticker', 'Sticker'),
        ('location', 'Localização'),
        ('contact', 'Contato'),
        ('poll', 'Enquete'),
    ]
    
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, verbose_name="Chat", related_name='mensagens')
    remetente = models.CharField(max_length=255, verbose_name="Remetente")
    conteudo = models.TextField(verbose_name="Conteúdo")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='text', verbose_name="Tipo")
    lida = models.BooleanField(default=False, verbose_name="Lida")
    from_me = models.BooleanField(default=False, verbose_name="Enviada por Mim")

    # Novo campo para garantir unicidade da mensagem do WhatsApp
    message_id = models.CharField(max_length=255, blank=True, null=True, unique=True, verbose_name="ID da Mensagem WhatsApp")
    
    # Campos para identificação do remetente em grupos
    sender_display_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome de Exibição do Remetente")
    sender_push_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome Push do Remetente")
    sender_verified_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome Verificado do Remetente")
    
    # Timestamps
    data_envio = models.DateTimeField(auto_now_add=True, verbose_name="Data de Envio")
    
    # Campo para reações (JSON array de emojis)
    reacoes = models.JSONField(default=list, blank=True, verbose_name="Reações")
    
    class Meta:
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
        ordering = ['data_envio']  # Ordem cronológica para chat tradicional
        indexes = [
            models.Index(fields=['chat', 'data_envio']),
            models.Index(fields=['remetente', 'from_me']),
            models.Index(fields=['chat', 'sender_display_name']),
        ]
    
    def __str__(self):
        return f"Mensagem de {self.remetente} - {self.chat.chat_name}"
    
    def get_sender_display_name(self):
        """
        Retorna o nome de exibição do remetente para grupos
        """
        if self.chat.is_group and not self.from_me:
            return self.sender_display_name or self.sender_push_name or self.sender_verified_name or self.remetente
        return None


class WebhookEvent(models.Model):
    # Modelo para armazenar eventos de webhook recebidos do WhatsApp.
    
    # Cada evento representa uma interação recebida via webhook da API W-APi.
    
    event_id = models.CharField(max_length=255, unique=True, verbose_name="ID do Evento")
    instance_id = models.CharField(max_length=255, verbose_name="ID da Instância")
    event_type = models.CharField(max_length=100, verbose_name="Tipo do Evento")
    payload = models.JSONField(verbose_name="Payload do Evento")
    
    # Status de processamento
    processed = models.BooleanField(default=False, verbose_name="Processado")
    error_message = models.TextField(blank=True, null=True, verbose_name="Mensagem de Erro")
    
    # Timestamps
    received_at = models.DateTimeField(auto_now_add=True, verbose_name="Recebido em")
    
    class Meta:
        verbose_name = "Evento de Webhook"
        verbose_name_plural = "Eventos de Webhook"
        ordering = ['-received_at']
    def __str__(self):
        return f"Evento {self.event_type} - {self.instance_id} - {self.received_at}"


class MediaFile(models.Model):
    """
    Modelo para armazenar informações de mídias baixadas
    Integrado com o banco principal do Django
    """
    TIPO_CHOICES = [
        ('image', 'Imagem'),
        ('video', 'Vídeo'),
        ('audio', 'Áudio'),
        ('document', 'Documento'),
        ('sticker', 'Sticker'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('success', 'Baixado'),
        ('failed', 'Falhou'),
        ('expired', 'Expirado'),
    ]
    
    # Relacionamentos
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente", related_name='media_files')
    instance = models.ForeignKey(WhatsappInstance, on_delete=models.CASCADE, verbose_name="Instância", related_name='media_files')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, verbose_name="Chat", related_name='media_files', null=True, blank=True)
    
    # Identificação da mensagem
    message_id = models.CharField(max_length=255, unique=True, verbose_name="ID da Mensagem WhatsApp")
    
    # Informações do remetente
    sender_name = models.CharField(max_length=255, verbose_name="Nome do Remetente")
    sender_id = models.CharField(max_length=255, verbose_name="ID do Remetente")
    
    # Informações da mídia
    media_type = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de Mídia")
    mimetype = models.CharField(max_length=100, verbose_name="Mimetype")
    file_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nome do Arquivo")
    file_path = models.TextField(blank=True, null=True, verbose_name="Caminho do Arquivo")
    file_size = models.BigIntegerField(blank=True, null=True, verbose_name="Tamanho do Arquivo (bytes)")
    
    # Metadados da mídia
    caption = models.TextField(blank=True, null=True, verbose_name="Legenda")
    width = models.IntegerField(blank=True, null=True, verbose_name="Largura")
    height = models.IntegerField(blank=True, null=True, verbose_name="Altura")
    duration_seconds = models.IntegerField(blank=True, null=True, verbose_name="Duração (segundos)")
    is_ptt = models.BooleanField(default=False, verbose_name="Push to Talk")
    
    # Status e controle
    download_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status do Download")
    is_group = models.BooleanField(default=False, verbose_name="É Grupo")
    from_me = models.BooleanField(default=False, verbose_name="Enviada por Mim")
    
    # Chaves de segurança da W-APi
    media_key = models.CharField(max_length=255, blank=True, null=True, verbose_name="Chave de Mídia")
    direct_path = models.TextField(blank=True, null=True, verbose_name="Caminho Direto")
    file_sha256 = models.CharField(max_length=255, blank=True, null=True, verbose_name="SHA256 do Arquivo")
    file_enc_sha256 = models.CharField(max_length=255, blank=True, null=True, verbose_name="SHA256 Enc do Arquivo")
    media_key_timestamp = models.CharField(max_length=20, blank=True, null=True, verbose_name="Timestamp da Chave")
    
    # Timestamps
    message_timestamp = models.DateTimeField(blank=True, null=True, verbose_name="Timestamp da Mensagem")
    download_timestamp = models.DateTimeField(blank=True, null=True, verbose_name="Timestamp do Download")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Arquivo de Mídia"
        verbose_name_plural = "Arquivos de Mídia"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cliente', 'instance']),
            models.Index(fields=['message_id']),
            models.Index(fields=['media_type', 'download_status']),
            models.Index(fields=['sender_id', 'chat']),
        ]
    
    def __str__(self):
        return f"Mídia {self.media_type} - {self.message_id[:8]} - {self.cliente.nome}"
    
    @property
    def file_size_mb(self):
        """Retorna o tamanho do arquivo em MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
    @property
    def is_downloaded(self):
        """Verifica se o arquivo foi baixado com sucesso"""
        return self.download_status == 'success' and self.file_path
    
    def get_file_url(self):
        """Retorna URL para acessar o arquivo (se implementado)"""
        if self.is_downloaded:
            # Aqui você pode implementar a lógica para gerar URLs
            # Por exemplo, usando Django Storage ou nginx
            return f"/media/{self.file_path}"
        return None 