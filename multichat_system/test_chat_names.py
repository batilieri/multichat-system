#!/usr/bin/env python
"""
Script para testar as alterações nos nomes dos chats
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat
from webhook.models import Sender
from api.serializers import ChatSerializer

def test_chat_names():
    """Testa as alterações nos nomes dos chats"""
    print("🧪 Testando alterações nos nomes dos chats...")
    
    # Buscar alguns chats para teste
    chats = Chat.objects.all()[:5]
    
    if not chats:
        print("❌ Nenhum chat encontrado para teste")
        return
    
    print(f"📊 Testando {len(chats)} chats...")
    
    for chat in chats:
        print(f"\n🔍 Chat ID: {chat.id}")
        print(f"   chat_id: {chat.chat_id}")
        print(f"   chat_name: {chat.chat_name}")
        
        # Testar serializer
        serializer = ChatSerializer(chat)
        data = serializer.data
        
        print(f"   sender_name (número): {data.get('sender_name')}")
        print(f"   contact_name (nome): {data.get('contact_name')}")
        
        # Verificar sender
        try:
            sender = Sender.objects.filter(
                sender_id=chat.chat_id,
                cliente=chat.cliente
            ).first()
            
            if sender:
                print(f"   sender.push_name: {sender.push_name}")
                print(f"   sender.verified_name: {sender.verified_name}")
            else:
                print(f"   ⚠️ Nenhum sender encontrado")
        except Exception as e:
            print(f"   ❌ Erro ao buscar sender: {e}")
    
    print("\n✅ Teste concluído!")

def test_api_response():
    """Testa a resposta da API"""
    print("\n🌐 Testando resposta da API...")
    
    try:
        import requests
        
        # URL da API (ajuste conforme necessário)
        url = "http://localhost:8000/api/chats/"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API retornou {len(data)} chats")
            
            if data:
                chat = data[0]
                print(f"📱 Exemplo de chat:")
                print(f"   ID: {chat.get('id')}")
                print(f"   chat_id: {chat.get('chat_id')}")
                print(f"   sender_name: {chat.get('sender_name')}")
                print(f"   contact_name: {chat.get('contact_name')}")
                print(f"   chat_name: {chat.get('chat_name')}")
        else:
            print(f"❌ API retornou status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")

if __name__ == "__main__":
    test_chat_names()
    test_api_response() 