#!/usr/bin/env python3
"""
Teste para verificar o chat ID específico: 120363023932459345
"""

import os
import sys
import django
import logging

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from webhook.views import normalize_chat_id
from core.models import Chat, Mensagem

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def testar_chat_especifico():
    """
    Testa o chat ID específico mencionado pelo usuário
    """
    print("🧪 TESTANDO CHAT ID ESPECÍFICO")
    print("=" * 50)
    
    chat_id_teste = "120363023932459345"
    
    print(f"📱 Chat ID para teste: {chat_id_teste}")
    print()
    
    # Testar normalização
    resultado = normalize_chat_id(chat_id_teste)
    print(f"🔍 Resultado da normalização: {resultado}")
    
    # Verificar se é um grupo
    if '@g.us' in chat_id_teste:
        print("🚫 É um grupo (contém @g.us)")
    else:
        print("✅ É um chat individual")
    
    print()
    
    # Verificar se existe no banco
    chats_existentes = Chat.objects.filter(chat_id__icontains="120363023932459345")
    print(f"📊 Chats encontrados no banco: {chats_existentes.count()}")
    
    for chat in chats_existentes:
        print(f"   - Chat ID: {chat.chat_id}")
        print(f"   - Cliente: {chat.cliente.nome if chat.cliente else 'N/A'}")
        print(f"   - Status: {chat.status}")
        print(f"   - Criado em: {chat.data_inicio}")
        print()
    
    # Verificar mensagens relacionadas
    mensagens = Mensagem.objects.filter(chat__chat_id__icontains="120363023932459345")
    print(f"📨 Mensagens encontradas: {mensagens.count()}")
    
    for msg in mensagens[:5]:  # Mostrar apenas as 5 primeiras
        print(f"   - ID: {msg.id}")
        print(f"   - Remetente: {msg.remetente}")
        print(f"   - Conteúdo: {msg.conteudo[:50]}...")
        print(f"   - Tipo: {msg.tipo}")
        print(f"   - FromMe: {msg.from_me}")
        print(f"   - Data: {msg.data_envio}")
        print()
    
    print("🎯 ANÁLISE:")
    print("=" * 30)
    
    if resultado is None:
        print("❌ Chat ID deveria ser ignorado (é um grupo)")
    else:
        print("✅ Chat ID é válido (chat individual)")
    
    if chats_existentes.exists():
        print("⚠️ Chat já existe no banco")
    else:
        print("✅ Chat não existe no banco")
    
    if mensagens.exists():
        print("⚠️ Mensagens já foram salvas")
    else:
        print("✅ Nenhuma mensagem salva")

if __name__ == "__main__":
    testar_chat_especifico() 