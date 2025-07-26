#!/usr/bin/env python
"""
Script para testar a lógica dinâmica dos nomes dos contatos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem
from webhook.models import Sender
from api.serializers import ChatSerializer

def test_dynamic_names():
    """Testa a lógica dinâmica dos nomes"""
    print("🧪 Testando lógica dinâmica dos nomes...")
    
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
        
        # Buscar mensagens do chat
        mensagens = chat.mensagens.order_by('-data_envio')[:3]
        
        if mensagens:
            print(f"   📝 Últimas mensagens:")
            for i, msg in enumerate(mensagens, 1):
                print(f"      {i}. {msg.remetente} ({'Você' if msg.from_me else 'Contato'}) - {msg.conteudo[:50]}...")
        
        # Testar serializer
        serializer = ChatSerializer(chat)
        data = serializer.data
        
        print(f"   📱 API Response:")
        print(f"      sender_name (número): {data.get('sender_name')}")
        print(f"      contact_name (dinâmico): {data.get('contact_name')}")
        
        # Verificar sender
        try:
            sender = Sender.objects.filter(
                sender_id=chat.chat_id,
                cliente=chat.cliente
            ).order_by('-id').first()
            
            if sender:
                print(f"   👤 Sender Info:")
                print(f"      push_name: {sender.push_name}")
                print(f"      verified_name: {sender.verified_name}")
            else:
                print(f"   ⚠️ Nenhum sender encontrado")
        except Exception as e:
            print(f"   ❌ Erro ao buscar sender: {e}")
    
    print("\n✅ Teste concluído!")

def test_scenarios():
    """Testa cenários específicos"""
    print("\n🎭 Testando cenários específicos...")
    
    # Cenário 1: Chat onde você enviou a última mensagem
    print("\n📤 Cenário 1: Você enviou a última mensagem")
    chats_from_me = []
    for chat in Chat.objects.all():
        ultima = chat.mensagens.order_by('-data_envio').first()
        if ultima and ultima.from_me:
            chats_from_me.append(chat)
            if len(chats_from_me) >= 2:
                break
    
    for chat in chats_from_me:
        serializer = ChatSerializer(chat)
        data = serializer.data
        print(f"   Chat {chat.id}: contact_name = {data.get('contact_name')} (deveria ser o número)")
    
    # Cenário 2: Chat onde a pessoa respondeu
    print("\n📥 Cenário 2: Pessoa respondeu")
    chats_from_other = []
    for chat in Chat.objects.all():
        ultima = chat.mensagens.order_by('-data_envio').first()
        if ultima and not ultima.from_me:
            chats_from_other.append(chat)
            if len(chats_from_other) >= 2:
                break
    
    for chat in chats_from_other:
        serializer = ChatSerializer(chat)
        data = serializer.data
        print(f"   Chat {chat.id}: contact_name = {data.get('contact_name')} (deveria ser o nome da pessoa)")
    
    print("\n✅ Cenários testados!")

if __name__ == "__main__":
    test_dynamic_names()
    test_scenarios() 