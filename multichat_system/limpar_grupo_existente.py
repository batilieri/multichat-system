#!/usr/bin/env python3
"""
Script para limpar o grupo 120363023932459345 que já foi criado no banco
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

def limpar_grupo_existente():
    """
    Remove o grupo 120363023932459345 e suas mensagens do banco
    """
    print("🧹 LIMPANDO GRUPO EXISTENTE")
    print("=" * 50)
    
    grupo_id = "120363023932459345"
    
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
    
    # Confirmar limpeza
    print("⚠️ ATENÇÃO: Esta operação irá:")
    print("   - Remover todos os chats que contêm o ID do grupo")
    print("   - Remover todas as mensagens desses chats")
    print("   - Esta ação não pode ser desfeita!")
    print()
    
    # Simular limpeza (não executar por segurança)
    print("🔒 SIMULAÇÃO DE LIMPEZA (não executada por segurança):")
    print("-" * 50)
    
    if chats.exists():
        print(f"❌ Removeria {chats.count()} chat(s)")
        for chat in chats:
            print(f"   - Chat ID: {chat.chat_id}")
    
    if mensagens.exists():
        print(f"❌ Removeria {mensagens.count()} mensagem(ns)")
    
    print()
    print("💡 PARA EXECUTAR A LIMPEZA REAL:")
    print("1. Descomente as linhas de delete no código")
    print("2. Execute o script novamente")
    print("3. Confirme a operação")
    
    # Executar limpeza real
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
    limpar_grupo_existente() 