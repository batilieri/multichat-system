#!/usr/bin/env python3
"""
Script para testar a captura de fotos de perfil no sistema MultiChat
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Cliente, Mensagem
from webhook.models import WebhookEvent, Sender
from webhook.processors import WhatsAppWebhookProcessor
import json

def test_profile_picture_capture():
    """
    Testa a captura de fotos de perfil com dados simulados do webhook
    """
    print("🧪 Testando captura de fotos de perfil...")
    
    # Buscar cliente para teste
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado. Crie um cliente primeiro.")
        return
    
    print(f"👤 Usando cliente: {cliente.nome}")
    
    # Dados simulados do webhook com foto de perfil
    webhook_data = {
        "instanceId": "test_instance",
        "event": "message",
        "messageId": f"test_msg_{datetime.now().timestamp()}",
        "chat": {
            "id": "5511999999999@s.whatsapp.net",
            "name": "João Silva",
            "profilePicture": "https://example.com/profile1.jpg"
        },
        "sender": {
            "id": "5511999999999@s.whatsapp.net",
            "pushName": "João Silva",
            "profilePicture": "https://example.com/profile2.jpg"
        },
        "msgContent": {
            "conversation": "Olá! Esta é uma mensagem de teste com foto de perfil."
        },
        "fromMe": False,
        "isGroup": False
    }
    
    # Processar webhook
    try:
        processor = WhatsAppWebhookProcessor(cliente)
        webhook_event = processor.process_webhook_data(webhook_data)
        
        print(f"✅ Webhook processado: {webhook_event.event_id}")
        print(f"   Chat ID: {webhook_event.chat_id}")
        print(f"   Sender ID: {webhook_event.sender_id}")
        print(f"   Processado: {webhook_event.processed}")
        
        # Verificar se o chat foi criado com foto de perfil
        chat = Chat.objects.filter(chat_id=webhook_event.chat_id, cliente=cliente).first()
        if chat:
            print(f"✅ Chat encontrado: {chat.chat_name}")
            print(f"   Foto de perfil: {chat.foto_perfil}")
            print(f"   É grupo: {chat.is_group}")
        else:
            print("❌ Chat não encontrado")
        
        # Verificar se o sender foi criado com foto de perfil
        sender = Sender.objects.filter(sender_id=webhook_event.sender_id, cliente=cliente).first()
        if sender:
            print(f"✅ Sender encontrado: {sender.push_name}")
            print(f"   Foto de perfil: {sender.profile_picture}")
        else:
            print("❌ Sender não encontrado")
        
        # Verificar mensagem
        mensagem = Mensagem.objects.filter(message_id=webhook_event.message_id).first()
        if mensagem:
            print(f"✅ Mensagem criada: {mensagem.conteudo}")
            print(f"   From me: {mensagem.from_me}")
        else:
            print("❌ Mensagem não encontrada")
            
    except Exception as e:
        print(f"❌ Erro ao processar webhook: {e}")
        import traceback
        traceback.print_exc()

def check_existing_chats():
    """
    Verifica chats existentes e suas fotos de perfil
    """
    print("\n📋 Verificando chats existentes...")
    
    chats = Chat.objects.all().order_by('-last_message_at')[:10]
    
    if not chats:
        print("❌ Nenhum chat encontrado")
        return
    
    for chat in chats:
        print(f"💬 Chat: {chat.chat_name} (ID: {chat.chat_id})")
        print(f"   Cliente: {chat.cliente.nome}")
        print(f"   Foto de perfil: {chat.foto_perfil}")
        print(f"   É grupo: {chat.is_group}")
        print(f"   Última mensagem: {chat.last_message_at}")
        print(f"   Total mensagens: {chat.mensagens.count()}")
        print("---")

def check_existing_senders():
    """
    Verifica senders existentes e suas fotos de perfil
    """
    print("\n👥 Verificando senders existentes...")
    
    senders = Sender.objects.all().order_by('-last_seen')[:10]
    
    if not senders:
        print("❌ Nenhum sender encontrado")
        return
    
    for sender in senders:
        print(f"👤 Sender: {sender.push_name} (ID: {sender.sender_id})")
        print(f"   Cliente: {sender.cliente.nome}")
        print(f"   Foto de perfil: {sender.profile_picture}")
        print(f"   Nome verificado: {sender.verified_name}")
        print(f"   É business: {sender.is_business}")
        print(f"   Total mensagens: {sender.message_count}")
        print("---")

def test_api_response():
    """
    Testa a resposta da API para verificar se a foto de perfil está sendo retornada
    """
    print("\n🌐 Testando resposta da API...")
    
    from django.test import Client
    from django.urls import reverse
    
    client = Client()
    
    # Simular requisição para a API de chats
    try:
        response = client.get('/api/chats/')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API respondeu com status {response.status_code}")
            
            if 'results' in data:
                chats = data['results']
                print(f"📊 Total de chats retornados: {len(chats)}")
                
                for chat in chats[:3]:  # Mostrar apenas os 3 primeiros
                    print(f"💬 Chat: {chat.get('chat_name', 'N/A')}")
                    print(f"   Foto de perfil: {chat.get('foto_perfil', 'N/A')}")
                    print(f"   Profile picture: {chat.get('profile_picture', 'N/A')}")
                    print("---")
            else:
                print("⚠️ Resposta não contém 'results'")
                print(f"Estrutura da resposta: {list(data.keys())}")
        else:
            print(f"❌ API respondeu com status {response.status_code}")
            print(f"Conteúdo: {response.content.decode()}")
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes de foto de perfil...")
    
    # Testar captura de foto de perfil
    test_profile_picture_capture()
    
    # Verificar chats existentes
    check_existing_chats()
    
    # Verificar senders existentes
    check_existing_senders()
    
    # Testar resposta da API
    test_api_response()
    
    print("\n✅ Testes concluídos!") 