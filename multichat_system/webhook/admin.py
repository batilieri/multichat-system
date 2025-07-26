from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

from .models import (
    WebhookEvent, Chat, Sender, Message, MessageStats, 
    ContactStats, RealTimeStats
)


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    """
    Admin para eventos de webhook
    """
    list_display = [
        'event_id_short', 'cliente', 'event_type', 'timestamp', 
        'processed', 'has_error', 'chat_id_short', 'sender_name'
    ]
    list_filter = [
        'cliente', 'event_type', 'processed', 'timestamp',
        ('error_message', admin.BooleanFieldListFilter)
    ]
    search_fields = [
        'event_id', 'cliente__nome', 'event_type', 'chat_id', 
        'sender_id', 'sender_name', 'message_content'
    ]
    readonly_fields = [
        'event_id', 'timestamp', 'ip_address', 'user_agent',
        'raw_data_formatted', 'processed', 'error_message'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('event_id', 'cliente', 'instance_id', 'event_type', 'timestamp')
        }),
        ('Dados Processados', {
            'fields': ('chat_id', 'sender_id', 'sender_name', 'message_id', 
                      'message_type', 'message_content')
        }),
        ('Status', {
            'fields': ('processed', 'error_message')
        }),
        ('Metadados', {
            'fields': ('ip_address', 'user_agent', 'raw_data_formatted'),
            'classes': ('collapse',)
        }),
    )
    
    def event_id_short(self, obj):
        """ID do evento abreviado"""
        return str(obj.event_id)[:8] + "..."
    event_id_short.short_description = "Event ID"
    
    def chat_id_short(self, obj):
        """ID do chat abreviado"""
        if obj.chat_id:
            return obj.chat_id[-8:] if len(obj.chat_id) > 8 else obj.chat_id
        return "-"
    chat_id_short.short_description = "Chat ID"
    
    def has_error(self, obj):
        """Indica se há erro"""
        return bool(obj.error_message)
    has_error.boolean = True
    has_error.short_description = "Erro"
    
    def raw_data_formatted(self, obj):
        """Dados brutos formatados"""
        if obj.raw_data:
            return format_html(
                '<pre style="max-height: 300px; overflow-y: auto;">{}</pre>',
                json.dumps(obj.raw_data, indent=2, ensure_ascii=False)
            )
        return "-"
    raw_data_formatted.short_description = "Dados Brutos"


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    """
    Admin para chats
    """
    list_display = [
        'chat_id_short', 'cliente', 'chat_name', 'is_group', 
        'status', 'message_count', 'last_message_at'
    ]
    list_filter = ['cliente', 'is_group', 'status', 'created_at']
    search_fields = ['chat_id', 'chat_name', 'cliente__nome']
    readonly_fields = ['created_at', 'updated_at', 'group_participants_formatted']
    date_hierarchy = 'created_at'
    ordering = ['-last_message_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('chat_id', 'cliente', 'chat_name', 'is_group', 'status')
        }),
        ('Estatísticas', {
            'fields': ('message_count', 'last_message_at')
        }),
        ('Grupo', {
            'fields': ('group_participants_formatted',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def chat_id_short(self, obj):
        """ID do chat abreviado"""
        return obj.chat_id[-12:] if len(obj.chat_id) > 12 else obj.chat_id
    chat_id_short.short_description = "Chat ID"
    
    def group_participants_formatted(self, obj):
        """Participantes do grupo formatados"""
        if obj.group_participants:
            return format_html(
                '<pre>{}</pre>',
                json.dumps(obj.group_participants, indent=2, ensure_ascii=False)
            )
        return "-"
    group_participants_formatted.short_description = "Participantes"


@admin.register(Sender)
class SenderAdmin(admin.ModelAdmin):
    """
    Admin para remetentes
    """
    list_display = [
        'sender_id_short', 'cliente', 'push_name', 'verified_name', 
        'is_business', 'message_count', 'last_seen'
    ]
    list_filter = ['cliente', 'is_business', 'created_at']
    search_fields = ['sender_id', 'push_name', 'verified_name', 'cliente__nome']
    readonly_fields = ['created_at', 'updated_at', 'business_profile_formatted']
    date_hierarchy = 'created_at'
    ordering = ['-last_seen']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('sender_id', 'cliente', 'push_name', 'verified_name', 'is_business')
        }),
        ('Estatísticas', {
            'fields': ('message_count', 'last_seen')
        }),
        ('Perfil Business', {
            'fields': ('business_profile_formatted',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def sender_id_short(self, obj):
        """ID do remetente abreviado"""
        return obj.sender_id[-12:] if len(obj.sender_id) > 12 else obj.sender_id
    sender_id_short.short_description = "Sender ID"
    
    def business_profile_formatted(self, obj):
        """Perfil business formatado"""
        if obj.business_profile:
            return format_html(
                '<pre>{}</pre>',
                json.dumps(obj.business_profile, indent=2, ensure_ascii=False)
            )
        return "-"
    business_profile_formatted.short_description = "Perfil Business"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin para mensagens
    """
    list_display = [
        'message_id_short', 'cliente', 'chat_name', 'sender_name', 
        'message_type', 'from_me', 'status', 'timestamp'
    ]
    list_filter = [
        'cliente', 'message_type', 'from_me', 'status', 'timestamp'
    ]
    search_fields = [
        'message_id', 'text_content', 'cliente__nome', 
        'chat__chat_name', 'sender__push_name'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'content_formatted', 
        'reactions_formatted'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('message_id', 'cliente', 'chat', 'sender', 'message_type')
        }),
        ('Conteúdo', {
            'fields': ('text_content', 'from_me', 'status', 'timestamp')
        }),
        ('Mídia', {
            'fields': ('media_url', 'media_type', 'media_size'),
            'classes': ('collapse',)
        }),
        ('Dados Extras', {
            'fields': ('content_formatted', 'reactions_formatted', 'quoted_message_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def message_id_short(self, obj):
        """ID da mensagem abreviado"""
        return obj.message_id[:8] + "..." if len(obj.message_id) > 8 else obj.message_id
    message_id_short.short_description = "Message ID"
    
    def chat_name(self, obj):
        """Nome do chat"""
        return obj.chat.chat_name if obj.chat else "-"
    chat_name.short_description = "Chat"
    
    def sender_name(self, obj):
        """Nome do remetente"""
        return obj.sender.push_name if obj.sender else "-"
    sender_name.short_description = "Remetente"
    
    def content_formatted(self, obj):
        """Conteúdo formatado"""
        if obj.content:
            return format_html(
                '<pre style="max-height: 200px; overflow-y: auto;">{}</pre>',
                json.dumps(obj.content, indent=2, ensure_ascii=False)
            )
        return "-"
    content_formatted.short_description = "Conteúdo"
    
    def reactions_formatted(self, obj):
        """Reações formatadas"""
        if obj.reactions:
            return format_html(
                '<pre>{}</pre>',
                json.dumps(obj.reactions, indent=2, ensure_ascii=False)
            )
        return "-"
    reactions_formatted.short_description = "Reações"


@admin.register(MessageStats)
class MessageStatsAdmin(admin.ModelAdmin):
    """
    Admin para estatísticas de mensagens
    """
    list_display = [
        'cliente', 'date', 'total_messages', 'received_messages', 
        'sent_messages', 'success_rate'
    ]
    list_filter = ['cliente', 'date']
    search_fields = ['cliente__nome']
    readonly_fields = ['date']
    date_hierarchy = 'date'
    ordering = ['-date']
    
    def success_rate(self, obj):
        """Taxa de sucesso"""
        if obj.total_messages > 0:
            rate = (obj.delivered_messages / obj.total_messages) * 100
            return f"{rate:.1f}%"
        return "0%"
    success_rate.short_description = "Taxa de Sucesso"


@admin.register(ContactStats)
class ContactStatsAdmin(admin.ModelAdmin):
    """
    Admin para estatísticas de contatos
    """
    list_display = [
        'cliente', 'sender_name', 'date', 'message_count', 
        'first_message_at', 'last_message_at'
    ]
    list_filter = ['cliente', 'date']
    search_fields = ['cliente__nome', 'sender__push_name']
    readonly_fields = ['date', 'first_message_at', 'last_message_at']
    date_hierarchy = 'date'
    ordering = ['-date']
    
    def sender_name(self, obj):
        """Nome do remetente"""
        return obj.sender.push_name if obj.sender else "-"
    sender_name.short_description = "Remetente"


@admin.register(RealTimeStats)
class RealTimeStatsAdmin(admin.ModelAdmin):
    """
    Admin para estatísticas em tempo real
    """
    list_display = [
        'cliente', 'timestamp', 'active_chats', 'pending_messages', 
        'online_users', 'avg_response_time'
    ]
    list_filter = ['cliente', 'timestamp']
    search_fields = ['cliente__nome']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def avg_response_time(self, obj):
        """Tempo médio de resposta formatado"""
        if obj.avg_response_time > 0:
            return f"{obj.avg_response_time:.1f}s"
        return "N/A"
    avg_response_time.short_description = "Tempo Médio Resposta"
