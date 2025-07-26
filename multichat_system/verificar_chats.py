#!/usr/bin/env python
"""
Script para listar todos os chats de um cliente a partir do instance_id
"""
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()
from webhook.models import Chat as WebhookChat
from core.models import Chat as CoreChat
from core.models import Cliente

def listar_chats_por_instance(instance_id):
    print(f"=== LISTA DE CHATS PARA INSTANCE_ID: {instance_id} ===\n")
    cliente = Cliente.objects.filter(wapi_instance_id=instance_id).first()
    if not cliente:
        print(f"Nenhum cliente encontrado para instance_id: {instance_id}")
        return
    print(f"Cliente: {cliente.nome}\n")
    chats = WebhookChat.objects.filter(cliente=cliente)
    if not chats:
        print("Nenhum chat encontrado para este cliente.")
        return
    for chat in chats:
        print(f"ID: {chat.id}, chat_id: '{chat.chat_id}', chat_name: '{chat.chat_name}'")
    print(f"\nTotal de chats: {chats.count()}")
    print("\n=== FIM ===")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python verificar_chats.py <instance_id>")
    else:
        listar_chats_por_instance(sys.argv[1]) 