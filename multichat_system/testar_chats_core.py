#!/usr/bin/env python
"""
Script para testar se os chats estão sendo criados no modelo core.Chat
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat as CoreChat
from webhook.models import Chat as WebhookChat
from core.models import Cliente

def testar_chats():
    print("=== TESTE DE CHATS ===\n")
    
    # Verificar chats no modelo core
    print("1. CHATS NO MODELO CORE:")
    core_chats = CoreChat.objects.all()
    for chat in core_chats:
        print(f"   - ID: {chat.id}, chat_id: '{chat.chat_id}', cliente: {chat.cliente.nome}, status: {chat.status}")
    print(f"   Total core chats: {core_chats.count()}")
    
    # Verificar chats no modelo webhook
    print(f"\n2. CHATS NO MODELO WEBHOOK:")
    webhook_chats = WebhookChat.objects.all()
    for chat in webhook_chats:
        print(f"   - ID: {chat.id}, chat_id: '{chat.chat_id}', cliente: {chat.cliente.nome}, status: {chat.status}")
    print(f"   Total webhook chats: {webhook_chats.count()}")
    
    # Verificar cliente específico
    print(f"\n3. CHATS DO CLIENTE ELIZEU BATILIERE DOS SANTOS:")
    cliente = Cliente.objects.filter(nome__icontains="ELIZEU").first()
    if cliente:
        print(f"   Cliente: {cliente.nome}")
        
        core_chats_cliente = CoreChat.objects.filter(cliente=cliente)
        print(f"   Core chats: {core_chats_cliente.count()}")
        for chat in core_chats_cliente:
            print(f"     - chat_id: '{chat.chat_id}', status: {chat.status}")
        
        webhook_chats_cliente = WebhookChat.objects.filter(cliente=cliente)
        print(f"   Webhook chats: {webhook_chats_cliente.count()}")
        for chat in webhook_chats_cliente:
            print(f"     - chat_id: '{chat.chat_id}', status: {chat.status}")
    
    print("\n=== FIM DO TESTE ===")

if __name__ == "__main__":
    testar_chats() 