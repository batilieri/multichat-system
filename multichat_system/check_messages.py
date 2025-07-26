#!/usr/bin/env python
"""
Script para verificar os dados das mensagens no banco
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from webhook.models import Message, WebhookEvent
from core.models import Mensagem

def check_messages():
    """Verifica os dados das mensagens"""
    print("🔍 Verificando mensagens no banco de dados...")
    
    # Verificar mensagens do webhook
    print("\n📱 Mensagens do webhook.models.Message:")
    webhook_messages = Message.objects.all()
    print(f"   Total: {webhook_messages.count()}")
    
    if webhook_messages.exists():
        print("   Exemplos:")
        for msg in webhook_messages[:3]:
            print(f"      ID: {msg.id}")
            print(f"      Message ID: {msg.message_id}")
            print(f"      Cliente: {msg.cliente}")
            print(f"      Chat: {msg.chat}")
            print(f"      Sender: {msg.sender}")
            print(f"      Text Content: {msg.text_content[:50]}...")
            print(f"      From Me: {msg.from_me}")
            print(f"      Status: {msg.status}")
            print(f"      Timestamp: {msg.timestamp}")
            print("      ---")
    else:
        print("   ⚠️ Nenhuma mensagem encontrada")
    
    # Verificar mensagens do core
    print("\n💬 Mensagens do core.models.Mensagem:")
    core_messages = Mensagem.objects.all()
    print(f"   Total: {core_messages.count()}")
    
    if core_messages.exists():
        print("   Exemplos:")
        for msg in core_messages[:3]:
            print(f"      ID: {msg.id}")
            print(f"      Chat: {msg.chat}")
            print(f"      Remetente: {msg.remetente}")
            print(f"      Conteúdo: {msg.conteudo[:50]}...")
            print(f"      Tipo: {msg.tipo}")
            print(f"      From Me: {msg.from_me}")
            print(f"      Data Envio: {msg.data_envio}")
            print("      ---")
    else:
        print("   ⚠️ Nenhuma mensagem encontrada")
    
    # Verificar eventos de webhook
    print("\n🌐 Eventos de Webhook:")
    webhook_events = WebhookEvent.objects.all()
    print(f"   Total: {webhook_events.count()}")
    
    if webhook_events.exists():
        print("   Exemplos:")
        for event in webhook_events[:3]:
            print(f"      ID: {event.id}")
            print(f"      Event ID: {event.event_id}")
            print(f"      Cliente: {event.cliente}")
            print(f"      Event Type: {event.event_type}")
            print(f"      Chat ID: {event.chat_id}")
            print(f"      Sender Name: {event.sender_name}")
            print(f"      Message Content: {event.message_content[:50] if event.message_content else 'N/A'}...")
            print(f"      Processed: {event.processed}")
            print("      ---")
    else:
        print("   ⚠️ Nenhum evento encontrado")

if __name__ == "__main__":
    check_messages() 