#!/usr/bin/env python3
"""
Análise de padrões de grupos para identificar se 120363023932459345 é um grupo
"""

import os
import sys
import django
import logging
import re

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from webhook.views import normalize_chat_id
from core.models import Chat, Mensagem

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analisar_padrao_grupos():
    """
    Analisa padrões de grupos para identificar se o chat ID é um grupo
    """
    print("🔍 ANÁLISE DE PADRÕES DE GRUPOS")
    print("=" * 50)
    
    chat_id_teste = "120363023932459345"
    
    print(f"📱 Chat ID para análise: {chat_id_teste}")
    print()
    
    # Análise do padrão
    print("📊 ANÁLISE DO PADRÃO:")
    print("-" * 30)
    
    # Verificar comprimento
    print(f"Comprimento: {len(chat_id_teste)} dígitos")
    
    # Verificar se contém apenas números
    apenas_numeros = chat_id_teste.isdigit()
    print(f"Apenas números: {apenas_numeros}")
    
    # Verificar se começa com padrões conhecidos de grupos
    padroes_grupo = [
        "120363",  # Possível padrão de grupo
        "1203630",  # Possível padrão de grupo
        "12036302",  # Possível padrão de grupo
    ]
    
    print("\n🔍 VERIFICANDO PADRÕES DE GRUPO:")
    for padrao in padroes_grupo:
        if chat_id_teste.startswith(padrao):
            print(f"   ✅ Começa com {padrao} (possível grupo)")
        else:
            print(f"   ❌ Não começa com {padrao}")
    
    # Verificar se o número é muito longo (característica de grupos)
    if len(chat_id_teste) > 15:
        print(f"   ⚠️ Número muito longo ({len(chat_id_teste)} dígitos) - possível grupo")
    else:
        print(f"   ✅ Comprimento normal ({len(chat_id_teste)} dígitos)")
    
    print()
    
    # Verificar no banco de dados
    print("📊 DADOS NO BANCO:")
    print("-" * 20)
    
    # Buscar todos os chats que começam com 120363
    chats_120363 = Chat.objects.filter(chat_id__startswith="120363")
    print(f"Chats que começam com 120363: {chats_120363.count()}")
    
    for chat in chats_120363:
        print(f"   - {chat.chat_id} (Cliente: {chat.cliente.nome if chat.cliente else 'N/A'})")
    
    print()
    
    # Verificar mensagens desses chats
    mensagens_120363 = Mensagem.objects.filter(chat__chat_id__startswith="120363")
    print(f"Mensagens de chats 120363: {mensagens_120363.count()}")
    
    # Agrupar por chat
    chats_com_mensagens = {}
    for msg in mensagens_120363:
        chat_id = msg.chat.chat_id
        if chat_id not in chats_com_mensagens:
            chats_com_mensagens[chat_id] = 0
        chats_com_mensagens[chat_id] += 1
    
    for chat_id, count in chats_com_mensagens.items():
        print(f"   - {chat_id}: {count} mensagens")
    
    print()
    
    # Recomendação
    print("🎯 RECOMENDAÇÃO:")
    print("=" * 20)
    
    if len(chat_id_teste) > 15 and chat_id_teste.startswith("120363"):
        print("🚫 Este parece ser um grupo baseado no padrão:")
        print("   - Começa com 120363")
        print("   - Número muito longo")
        print("   - Deveria ser ignorado")
    else:
        print("✅ Este parece ser um chat individual válido")
    
    print()
    print("💡 SUGESTÃO:")
    print("Se este for realmente um grupo, podemos adicionar uma verificação")
    print("para números que começam com 120363 e têm mais de 15 dígitos")

if __name__ == "__main__":
    analisar_padrao_grupos() 