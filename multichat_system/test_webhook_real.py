#!/usr/bin/env python3
"""
Script para testar com dados reais de webhook e identificar o problema
"""

import os
import django
import json
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente, WhatsappInstance
from webhook.models import WebhookEvent

def test_real_webhook_data():
    """
    Testa com dados reais de webhook para identificar o problema
    """
    print("=== TESTE COM DADOS REAIS DE WEBHOOK ===")
    
    # Simular dados reais de webhook que podem estar chegando
    real_webhook_payloads = [
        # Formato 1: Webhook padrão da W-API
        {
            "instanceId": "test_instance",
            "event": "messages.upsert",
            "data": {
                "key": {
                    "remoteJid": "5511999999999@s.whatsapp.net",
                    "fromMe": True,
                    "id": "test_msg_1"
                },
                "message": {
                    "conversation": "Mensagem enviada por mim"
                },
                "messageTimestamp": "1734567890"
            }
        },
        # Formato 2: Webhook simplificado
        {
            "instanceId": "test_instance",
            "chat": {"id": "5511999999999@s.whatsapp.net"},
            "sender": {"id": "5511999999999@s.whatsapp.net", "pushName": "Elizeu Batiliere"},
            "msgContent": {"conversation": "Mensagem enviada por mim"},
            "fromMe": True,
            "messageId": "test_msg_2"
        },
        # Formato 3: Webhook sem fromMe explícito
        {
            "instanceId": "test_instance",
            "chat": {"id": "5511999999999@s.whatsapp.net"},
            "sender": {"id": "5511999999999@s.whatsapp.net", "pushName": "Elizeu Batiliere"},
            "msgContent": {"conversation": "Mensagem sem fromMe explícito"},
            "messageId": "test_msg_3"
        }
    ]
    
    for i, payload in enumerate(real_webhook_payloads):
        print(f"\n--- Teste {i+1} ---")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Aplicar a lógica atual do webhook/views.py
        from_me = False
        
        # Extrair dados como no webhook/views.py
        message_key = payload.get('key', {})
        chat_id = payload.get("chat", {}).get("id", "")
        
        # Método 1: Verificar campo fromMe no key
        if message_key.get('fromMe') is not None:
            from_me = message_key.get('fromMe', False)
            print(f"✅ Método 1: fromMe no key = {from_me}")
        # Método 2: Verificar campo fromMe no payload raiz
        elif payload.get('fromMe') is not None:
            from_me = payload.get('fromMe', False)
            print(f"✅ Método 2: fromMe no payload = {from_me}")
        # Método 3: Verificar se o sender_id é o mesmo da instância (usuário atual)
        else:
            sender_id = payload.get('sender', {}).get('id', '')
            instance_id = payload.get('instanceId', '')
            
            # Se o sender_id contém o instance_id, é uma mensagem enviada pelo usuário
            if sender_id and instance_id and instance_id in sender_id:
                from_me = True
                print(f"✅ Método 3a: sender_id contém instance_id = {from_me}")
            # Se o sender_id é o mesmo do chat_id (para chats individuais), pode ser do usuário
            elif sender_id and chat_id and sender_id == chat_id:
                from_me = True
                print(f"✅ Método 3b: sender_id igual ao chat_id = {from_me}")
            else:
                print(f"❌ Método 3: Nenhuma condição atendida = {from_me}")
        
        print(f"🎯 Resultado final: from_me = {from_me}")

def check_webhook_events():
    """
    Verifica eventos de webhook reais no banco
    """
    print("\n=== VERIFICAÇÃO DE EVENTOS DE WEBHOOK REAIS ===")
    
    events = WebhookEvent.objects.all().order_by('-timestamp')[:5]
    
    print(f"Últimos {len(events)} eventos de webhook:")
    for event in events:
        print(f"Event ID: {event.event_id}")
        print(f"  Tipo: {event.event_type}")
        print(f"  Chat ID: {event.chat_id}")
        print(f"  Sender ID: {event.sender_id}")
        print(f"  Sender Name: {event.sender_name}")
        print(f"  Message ID: {event.message_id}")
        print(f"  Timestamp: {event.timestamp}")
        
        # Mostrar dados brutos se disponível
        if event.raw_data:
            raw_data = event.raw_data
            print(f"  Raw Data Keys: {list(raw_data.keys())}")
            
            # Verificar estrutura específica
            if 'key' in raw_data:
                key_data = raw_data['key']
                print(f"  Key Data: {key_data}")
                if 'fromMe' in key_data:
                    print(f"  fromMe no key: {key_data['fromMe']}")
            
            if 'fromMe' in raw_data:
                print(f"  fromMe no payload: {raw_data['fromMe']}")
            
            if 'sender' in raw_data:
                print(f"  sender: {raw_data['sender']}")
            
            if 'chat' in raw_data:
                print(f"  chat: {raw_data['chat']}")
        print()

def check_message_creation():
    """
    Verifica como as mensagens estão sendo criadas
    """
    print("\n=== VERIFICAÇÃO DE CRIAÇÃO DE MENSAGENS ===")
    
    mensagens = Mensagem.objects.all().order_by('-data_envio')[:5]
    
    print(f"Últimas {len(mensagens)} mensagens criadas:")
    for msg in mensagens:
        print(f"ID: {msg.id}")
        print(f"  Remetente: '{msg.remetente}'")
        print(f"  from_me: {msg.from_me}")
        print(f"  Chat ID: {msg.chat.chat_id}")
        print(f"  Message ID: {msg.message_id}")
        print(f"  Conteúdo: {msg.conteudo[:50]}...")
        print(f"  Data: {msg.data_envio}")
        print()

def test_chat_creation():
    """
    Testa a criação de chat para verificar se há problemas
    """
    print("\n=== TESTE DE CRIAÇÃO DE CHAT ===")
    
    # Buscar cliente
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado")
        return
    
    # Testar criação de chat
    chat_id = "test_chat_123@s.whatsapp.net"
    
    try:
        chat, created = Chat.objects.get_or_create(
            chat_id=chat_id,
            cliente=cliente,
            defaults={
                "status": "active",
                "canal": "whatsapp",
                "last_message_at": timezone.now()
            }
        )
        
        if created:
            print(f"✅ Chat criado: {chat.chat_id}")
        else:
            print(f"✅ Chat encontrado: {chat.chat_id}")
        
        # Criar mensagem de teste
        mensagem = Mensagem.objects.create(
            chat=chat,
            remetente="Elizeu Batiliere",
            conteudo="Teste de mensagem",
            tipo='text',
            lida=False,
            from_me=True,
            message_id="test_webhook_real"
        )
        
        print(f"✅ Mensagem criada: ID={mensagem.id}, from_me={mensagem.from_me}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_real_webhook_data()
    check_webhook_events()
    check_message_creation()
    test_chat_creation() 