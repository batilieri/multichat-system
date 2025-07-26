#!/usr/bin/env python3
"""
Script para debugar o problema do campo from_me
"""

import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente, WhatsappInstance
from webhook.models import WebhookEvent

def debug_from_me_logic():
    """
    Testa a lógica de determinação do from_me
    """
    print("=== DEBUG DA LÓGICA FROM_ME ===")
    
    # Simular payload de webhook
    test_payloads = [
        {
            "instanceId": "test_instance",
            "chat": {"id": "5511999999999@s.whatsapp.net"},
            "sender": {"id": "5511999999999@s.whatsapp.net", "pushName": "Elizeu Batiliere"},
            "msgContent": {"conversation": "Teste de mensagem"},
            "fromMe": True,
            "messageId": "test_msg_1"
        },
        {
            "instanceId": "test_instance", 
            "chat": {"id": "5511999999999@s.whatsapp.net"},
            "sender": {"id": "5511888888888@s.whatsapp.net", "pushName": "Outro Usuário"},
            "msgContent": {"conversation": "Resposta do outro usuário"},
            "fromMe": False,
            "messageId": "test_msg_2"
        },
        {
            "instanceId": "test_instance",
            "chat": {"id": "5511999999999@s.whatsapp.net"},
            "sender": {"id": "5511999999999@s.whatsapp.net", "pushName": "Elizeu Batiliere"},
            "msgContent": {"conversation": "Mensagem sem fromMe explícito"},
            "messageId": "test_msg_3"
        }
    ]
    
    for i, payload in enumerate(test_payloads):
        print(f"\n--- Teste {i+1} ---")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Aplicar a lógica melhorada
        from_me = False
        
        # Método 1: Verificar campo fromMe no payload raiz
        if payload.get('fromMe') is not None:
            from_me = payload.get('fromMe', False)
            print(f"✅ Método 1: fromMe no payload = {from_me}")
        # Método 2: Verificar campo fromMe no key (se existir)
        elif payload.get('key', {}).get('fromMe') is not None:
            from_me = payload.get('key', {}).get('fromMe', False)
            print(f"✅ Método 2: fromMe no key = {from_me}")
        # Método 3: Verificar se o sender_id é o mesmo da instância (usuário atual)
        else:
            sender_id = payload.get('sender', {}).get('id', '')
            instance_id = payload.get('instanceId', '')
            chat_id = payload.get('chat', {}).get('id', '')
            
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

def check_existing_messages():
    """
    Verifica mensagens existentes e suas características
    """
    print("\n=== VERIFICAÇÃO DE MENSAGENS EXISTENTES ===")
    
    mensagens = Mensagem.objects.all().order_by('-data_envio')[:20]
    
    print(f"Últimas {len(mensagens)} mensagens:")
    for msg in mensagens:
        print(f"ID: {msg.id}")
        print(f"  Remetente: '{msg.remetente}'")
        print(f"  from_me: {msg.from_me}")
        print(f"  Chat ID: {msg.chat.chat_id}")
        print(f"  Conteúdo: {msg.conteudo[:50]}...")
        print(f"  Data: {msg.data_envio}")
        print()

def check_webhook_events():
    """
    Verifica eventos de webhook para entender os dados recebidos
    """
    print("\n=== VERIFICAÇÃO DE EVENTOS DE WEBHOOK ===")
    
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
            if 'fromMe' in raw_data:
                print(f"  fromMe no raw_data: {raw_data['fromMe']}")
            if 'sender' in raw_data:
                print(f"  sender: {raw_data['sender']}")
            if 'chat' in raw_data:
                print(f"  chat: {raw_data['chat']}")
        print()

def test_message_creation():
    """
    Testa a criação de mensagens com diferentes cenários
    """
    print("\n=== TESTE DE CRIAÇÃO DE MENSAGENS ===")
    
    # Buscar cliente e chat de teste
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado")
        return
    
    chat = Chat.objects.filter(cliente=cliente).first()
    if not chat:
        print("❌ Nenhum chat encontrado")
        return
    
    # Testar criação de mensagens
    test_cases = [
        {
            'remetente': 'Elizeu Batiliere',
            'from_me': True,
            'conteudo': 'Mensagem de teste - enviada por mim'
        },
        {
            'remetente': 'Outro Usuário',
            'from_me': False,
            'conteudo': 'Mensagem de teste - enviada por outro'
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        try:
            mensagem = Mensagem.objects.create(
                chat=chat,
                remetente=test_case['remetente'],
                conteudo=test_case['conteudo'],
                tipo='text',
                lida=False,
                from_me=test_case['from_me']
            )
            print(f"✅ Mensagem {i+1} criada: ID={mensagem.id}, from_me={mensagem.from_me}")
        except Exception as e:
            print(f"❌ Erro ao criar mensagem {i+1}: {e}")

if __name__ == "__main__":
    debug_from_me_logic()
    check_existing_messages()
    check_webhook_events()
    test_message_creation() 