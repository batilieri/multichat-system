#!/usr/bin/env python3
"""
Script para limpar o grupo 120363352636641881 que já foi criado no banco
"""

import os
import sys
import django
import logging

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def limpar_grupo_120363():
    """
    Remove o grupo 120363352636641881 e suas mensagens do banco
    """
    print("🧹 LIMPANDO GRUPO 120363352636641881")
    print("=" * 50)
    
    grupo_id = "120363352636641881"
    
    print(f"📱 Grupo para limpeza: {grupo_id}")
    print()
    
    # Verificar chats existentes
    chats = Chat.objects.filter(chat_id__icontains=grupo_id)
    print(f"📊 Chats encontrados: {chats.count()}")
    
    for chat in chats:
        print(f"   - Chat ID: {chat.chat_id}")
        print(f"   - Cliente: {chat.cliente.nome if chat.cliente else 'N/A'}")
        print(f"   - Status: {chat.status}")
        print(f"   - Criado em: {chat.data_inicio}")
    
    print()
    
    # Verificar mensagens
    mensagens = Mensagem.objects.filter(chat__chat_id__icontains=grupo_id)
    print(f"📨 Mensagens encontradas: {mensagens.count()}")
    
    for msg in mensagens[:5]:  # Mostrar apenas as 5 primeiras
        print(f"   - ID: {msg.id}")
        print(f"   - Remetente: {msg.remetente}")
        print(f"   - Conteúdo: {msg.conteudo[:50]}...")
        print(f"   - Data: {msg.data_envio}")
    
    if mensagens.count() > 5:
        print(f"   ... e mais {mensagens.count() - 5} mensagens")
    
    print()
    
    # Executar limpeza
    if mensagens.exists():
        print(f"🗑️ Removendo {mensagens.count()} mensagens...")
        mensagens.delete()
        print("✅ Mensagens removidas")
    
    if chats.exists():
        print(f"🗑️ Removendo {chats.count()} chats...")
        chats.delete()
        print("✅ Chats removidos")
    
    print("🎉 Limpeza concluída!")

if __name__ == "__main__":
    limpar_grupo_120363() 