"""
URLs do módulo webhook para receber eventos da W-APi.

Define as rotas para:
- Receber webhooks do WhatsApp
- Verificar status dos webhooks
- Testar processamento de webhooks
- Gerenciar eventos de webhook

Autor: Sistema MultiChat
Data: 2025-07-11
"""

from django.urls import path
from .views import (
    webhook_receiver, webhook_status,
    webhook_send_message, webhook_receive_message,
    webhook_chat_presence, webhook_message_status,
    webhook_connect, webhook_disconnect
)

app_name = 'webhook'

urlpatterns = [
    # Endpoint principal para receber webhooks do WhatsApp (nova integração)
    path('whatsapp/', webhook_receiver, name='webhook_whatsapp'),

    # Endpoints separados por tipo de evento
    path('send-message/', webhook_send_message, name='webhook_send_message'),
    path('receive-message/', webhook_receive_message, name='webhook_receive_message'),
    path('chat-presence/', webhook_chat_presence, name='webhook_chat_presence'),
    path('message-status/', webhook_message_status, name='webhook_message_status'),
    path('connect/', webhook_connect, name='webhook_connect'),
    path('disconnect/', webhook_disconnect, name='webhook_disconnect'),

    # Endpoint para status dos webhooks (nova integração)
    path('status/', webhook_status, name='webhook_status'),
]

