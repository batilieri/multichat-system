#!/usr/bin/env python
"""
Script para verificar especificamente o chat 20 da Thayna
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

def test_chat_20():
    """Testa especificamente o chat 20"""
    print("🔍 Verificando Chat 20 (Thayna)...")
    
    try:
        chat = Chat.objects.get(id=20)
        print(f"📱 Chat ID: {chat.id}")
        print(f"   chat_id: {chat.chat_id}")
        print(f"   chat_name: {chat.chat_name}")
        
        # Buscar mensagens do chat
        mensagens = chat.mensagens.order_by('-data_envio')[:5]
        
        if mensagens:
            print(f"   📝 Últimas mensagens:")
            for i, msg in enumerate(mensagens, 1):
                print(f"      {i}. {msg.remetente} ({'Você' if msg.from_me else 'Contato'}) - {msg.conteudo[:50]}...")
                print(f"         from_me: {msg.from_me}")
                print(f"         sender_display_name: {msg.sender_display_name}")
        
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
        
        # Verificar última mensagem
        ultima = chat.mensagens.order_by('-data_envio').first()
        if ultima:
            print(f"   🕐 Última mensagem:")
            print(f"      remetente: {ultima.remetente}")
            print(f"      from_me: {ultima.from_me}")
            print(f"      data: {ultima.data_envio}")
            
            # Verificar se deveria mostrar o nome da Thayna
            if not ultima.from_me:
                print(f"   ✅ Deveria mostrar: {ultima.remetente}")
            else:
                print(f"   📞 Deveria mostrar: {chat.chat_id}")
        
    except Chat.DoesNotExist:
        print("❌ Chat 20 não encontrado")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_chat_20() 