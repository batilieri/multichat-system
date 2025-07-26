#!/usr/bin/env python3
"""
Script para debugar o problema real do webhook
"""

import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente, WhatsappInstance
from webhook.models import WebhookEvent

def debug_webhook_real():
    """
    Debuga o problema real do webhook
    """
    print("=== DEBUG DO WEBHOOK REAL ===")
    
    # Verificar mensagens recentes
    mensagens_recentes = Mensagem.objects.order_by('-data_envio')[:10]
    print(f"Últimas 10 mensagens:")
    
    for msg in mensagens_recentes:
        print(f"ID: {msg.id}, Remetente: '{msg.remetente}', from_me: {msg.from_me}, Conteúdo: {msg.conteudo[:30]}..., Data: {msg.data_envio}")
    
    # Verificar webhooks recentes
    webhooks_recentes = WebhookEvent.objects.order_by('-timestamp')[:5]
    print(f"\nÚltimos 5 webhooks:")
    
    for webhook in webhooks_recentes:
        print(f"ID: {webhook.event_id}, Tipo: {webhook.event_type}, Instance: {webhook.instance_id}")
        if webhook.raw_data:
            # Verificar se tem fromMe no webhook
            from_me_webhook = webhook.raw_data.get('fromMe', 'N/A')
            from_me_data = webhook.raw_data.get('data', {}).get('fromMe', 'N/A')
            from_me_key = webhook.raw_data.get('data', {}).get('key', {}).get('fromMe', 'N/A')
            
            print(f"  fromMe (raiz): {from_me_webhook}")
            print(f"  fromMe (data): {from_me_data}")
            print(f"  fromMe (key): {from_me_key}")
            
            # Verificar sender
            sender = webhook.raw_data.get('sender', {})
            sender_name = sender.get('pushName', 'N/A')
            sender_id = sender.get('id', 'N/A')
            print(f"  Sender: {sender_name} ({sender_id})")
    
    # Simular webhook real que pode estar chegando
    print(f"\n=== SIMULAÇÃO DE WEBHOOK REAL ===")
    
    # Simular diferentes formatos de webhook
    webhook_formats = [
        {
            "instanceId": "test_instance",
            "event": "messages.upsert",
            "data": {
                "key": {
                    "id": "test_msg_1",
                    "remoteJid": "556999267344@s.whatsapp.net",
                    "fromMe": True
                },
                "message": {
                    "conversation": "Teste do Elizeu"
                },
                "messageTimestamp": 1640995200,
                "pushName": "Elizeu Batiliere"
            },
            "sender": {
                "id": "556999267344@s.whatsapp.net",
                "pushName": "Elizeu Batiliere"
            },
            "fromMe": True
        },
        {
            "instanceId": "test_instance",
            "event": "messages.upsert",
            "data": {
                "key": {
                    "id": "test_msg_2",
                    "remoteJid": "556999267344@s.whatsapp.net",
                    "fromMe": False
                },
                "message": {
                    "conversation": "Teste de outro"
                },
                "messageTimestamp": 1640995200,
                "pushName": "Outro Usuário"
            },
            "sender": {
                "id": "556999267344@s.whatsapp.net",
                "pushName": "Outro Usuário"
            },
            "fromMe": False
        }
    ]
    
    for i, webhook in enumerate(webhook_formats, 1):
        print(f"\nWebhook {i}:")
        print(f"  fromMe (raiz): {webhook.get('fromMe', 'N/A')}")
        print(f"  fromMe (data): {webhook.get('data', {}).get('fromMe', 'N/A')}")
        print(f"  fromMe (key): {webhook.get('data', {}).get('key', {}).get('fromMe', 'N/A')}")
        print(f"  Sender: {webhook.get('sender', {}).get('pushName', 'N/A')}")
        
        # Testar lógica de determinação
        from_me = False
        
        # Método 1: Verificar campo fromMe no payload raiz
        if webhook.get('fromMe') is not None:
            from_me = webhook.get('fromMe', False)
        # Método 2: Verificar campo fromMe no data
        elif webhook.get('data', {}).get('fromMe') is not None:
            from_me = webhook.get('data', {}).get('fromMe', False)
        # Método 3: Verificar campo fromMe no key
        elif webhook.get('data', {}).get('key', {}).get('fromMe') is not None:
            from_me = webhook.get('data', {}).get('key', {}).get('fromMe', False)
        # Método 4: Verificar pelo nome do remetente
        else:
            sender_name = webhook.get('sender', {}).get('pushName', '')
            if sender_name and "Elizeu" in sender_name:
                from_me = True
        
        print(f"  from_me determinado: {from_me}")

if __name__ == "__main__":
    debug_webhook_real() 