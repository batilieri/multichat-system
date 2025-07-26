from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Cliente, Departamento, WhatsappInstance, Chat, Mensagem

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'telefone', 'empresa', 'ativo', 'data_cadastro']
    list_filter = ['ativo', 'data_cadastro']
    search_fields = ['nome', 'email', 'telefone', 'empresa']
    readonly_fields = ['data_cadastro']

@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cliente', 'ativo']
    list_filter = ['ativo', 'cliente']
    search_fields = ['nome', 'cliente__nome']

@admin.register(WhatsappInstance)
class WhatsappInstanceAdmin(admin.ModelAdmin):
    list_display = ['instance_id', 'cliente', 'status', 'last_seen', 'created_at']
    list_filter = ['status', 'created_at', 'cliente']
    search_fields = ['instance_id', 'cliente__nome']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = [
        'chat_id_short', 'cliente', 'chat_name', 'is_group', 
        'status', 'atendente', 'last_message_at', 'total_mensagens'
    ]
    list_filter = ['cliente', 'is_group', 'status', 'canal', 'data_inicio']
    search_fields = ['chat_id', 'chat_name', 'cliente__nome', 'atendente__username']
    readonly_fields = ['data_inicio', 'last_message_at', 'total_mensagens']
    date_hierarchy = 'data_inicio'
    ordering = ['-last_message_at']
    
    def chat_id_short(self, obj):
        """ID do chat abreviado"""
        return obj.chat_id[-12:] if len(obj.chat_id) > 12 else obj.chat_id
    chat_id_short.short_description = "Chat ID"
    
    def total_mensagens(self, obj):
        """Total de mensagens do chat"""
        return obj.mensagens.count()
    total_mensagens.short_description = "Total Msgs"

@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    """
    Admin para mensagens do core
    """
    list_display = [
        'id', 'chat_info', 'remetente', 'tipo', 'from_me', 
        'lida', 'data_envio', 'conteudo_short'
    ]
    list_filter = [
        'chat__cliente', 'tipo', 'from_me', 'lida', 'data_envio'
    ]
    search_fields = [
        'remetente', 'conteudo', 'chat__chat_id', 'chat__cliente__nome'
    ]
    readonly_fields = [
        'data_envio', 'message_id', 'sender_display_name', 
        'sender_push_name', 'sender_verified_name'
    ]
    date_hierarchy = 'data_envio'
    ordering = ['-data_envio']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('chat', 'remetente', 'conteudo', 'tipo', 'lida', 'from_me')
        }),
        ('Identificação', {
            'fields': ('message_id', 'sender_display_name', 'sender_push_name', 'sender_verified_name'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('data_envio',),
            'classes': ('collapse',)
        }),
    )
    
    def chat_info(self, obj):
        """Informações do chat"""
        if obj.chat:
            return f"{obj.chat.chat_id} - {obj.chat.cliente.nome if obj.chat.cliente else 'N/A'}"
        return "N/A"
    chat_info.short_description = "Chat"
    
    def conteudo_short(self, obj):
        """Conteúdo abreviado"""
        if obj.conteudo:
            return obj.conteudo[:50] + "..." if len(obj.conteudo) > 50 else obj.conteudo
        return "N/A"
    conteudo_short.short_description = "Conteúdo"
