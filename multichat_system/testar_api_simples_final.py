#!/usr/bin/env python
"""
Teste simples final da API
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem, Cliente
from authentication.models import Usuario

def test_final():
    """Teste final da API"""
    print("🔍 Teste final da API de mensagens...")
    print("=" * 50)
    
    # Verificar dados básicos
    print(f"Total de chats: {Chat.objects.count()}")
    print(f"Total de mensagens: {Mensagem.objects.count()}")
    print(f"Total de clientes: {Cliente.objects.count()}")
    print(f"Total de usuários: {Usuario.objects.count()}")
    
    # Verificar chats com mensagens
    chats_com_mensagens = Chat.objects.filter(mensagens__isnull=False).distinct()
    print(f"Chats com mensagens: {chats_com_mensagens.count()}")
    
    for chat in chats_com_mensagens[:3]:
        print(f"\n📱 Chat: {chat.chat_id}")
        print(f"   Cliente: {chat.cliente.nome}")
        print(f"   Mensagens: {chat.mensagens.count()}")
        
        # Verificar mensagens
        mensagens = chat.mensagens.all()[:5]
        for msg in mensagens:
            print(f"   💬 {msg.id}: {msg.conteudo[:50]}... (from_me: {msg.from_me})")
    
    # Verificar se há problemas com message_id
    print(f"\n🔍 Verificando message_id...")
    mensagens_sem_id = Mensagem.objects.filter(message_id__isnull=True)
    print(f"Mensagens sem message_id: {mensagens_sem_id.count()}")
    
    mensagens_com_id = Mensagem.objects.filter(message_id__isnull=False)
    print(f"Mensagens com message_id: {mensagens_com_id.count()}")
    
    # Verificar duplicatas
    from django.db.models import Count
    duplicatas = Mensagem.objects.values('message_id').annotate(
        count=Count('message_id')
    ).filter(count__gt=1, message_id__isnull=False)
    
    print(f"Message IDs duplicados: {duplicatas.count()}")
    
    if duplicatas.exists():
        print("⚠️ Message IDs duplicados encontrados:")
        for dup in duplicatas[:5]:
            print(f"   {dup['message_id']}: {dup['count']} vezes")
    
    # Testar busca direta por chat_id
    print(f"\n🔍 Testando busca por chat_id...")
    chat_teste = chats_com_mensagens.first()
    if chat_teste:
        mensagens_chat = Mensagem.objects.filter(chat__chat_id=chat_teste.chat_id)
        print(f"Mensagens do chat {chat_teste.chat_id}: {mensagens_chat.count()}")
        
        if mensagens_chat.exists():
            primeira_msg = mensagens_chat.first()
            print(f"Primeira mensagem: ID={primeira_msg.id}, Conteúdo={primeira_msg.conteudo[:50]}...")
            print(f"Message ID: {primeira_msg.message_id}")
            print(f"From Me: {primeira_msg.from_me}")
            print(f"Data: {primeira_msg.data_envio}")

if __name__ == "__main__":
    test_final() 