#!/usr/bin/env python3
"""
Script para verificar os grupos específicos que aparecem na interface
"""

import os
import sys
import django
import logging
import re

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem
from webhook.views import normalize_chat_id

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verificar_grupos_especificos():
    """
    Verifica os grupos específicos mencionados pelo usuário
    """
    print("🔍 VERIFICANDO GRUPOS ESPECÍFICOS")
    print("=" * 50)
    
    # Grupos mencionados pelo usuário
    grupos_especificos = [
        "6641881@g.us",
        "3541629@g.us"
    ]
    
    for grupo_id in grupos_especificos:
        print(f"\n📱 Verificando: {grupo_id}")
        
        # Testar normalização
        resultado = normalize_chat_id(grupo_id)
        print(f"   🔍 Resultado da normalização: {resultado}")
        
        # Verificar se existe no banco
        chats = Chat.objects.filter(chat_id=grupo_id)
        print(f"   📊 Encontrado no banco: {chats.count()}")
        
        if chats.exists():
            for chat in chats:
                print(f"      - ID: {chat.id}")
                print(f"      - Cliente: {chat.cliente.nome if chat.cliente else 'N/A'}")
                print(f"      - Status: {chat.status}")
                print(f"      - Criado em: {chat.data_inicio}")
                
                # Verificar mensagens
                mensagens = Mensagem.objects.filter(chat=chat)
                print(f"      - Mensagens: {mensagens.count()}")
        
        # Verificar se é detectado como grupo
        if '@g.us' in grupo_id:
            print(f"   🚫 Detectado como grupo (@g.us)")
        else:
            print(f"   ✅ Não detectado como grupo")
    
    print("\n🎯 ANÁLISE GERAL:")
    print("=" * 30)
    
    # Listar todos os chats que contêm @g.us
    todos_grupos = Chat.objects.filter(chat_id__icontains='@g.us')
    print(f"📊 Total de chats com @g.us no banco: {todos_grupos.count()}")
    
    if todos_grupos.exists():
        print("🚫 Grupos encontrados no banco:")
        for grupo in todos_grupos:
            print(f"   - {grupo.chat_id}")
    else:
        print("✅ Nenhum grupo com @g.us encontrado no banco")
    
    # Listar todos os chats que começam com 120363
    chats_120363 = Chat.objects.filter(chat_id__startswith='120363')
    print(f"\n📊 Total de chats que começam com 120363: {chats_120363.count()}")
    
    if chats_120363.exists():
        print("🚫 Chats com padrão 120363 encontrados:")
        for chat in chats_120363:
            print(f"   - {chat.chat_id}")
    else:
        print("✅ Nenhum chat com padrão 120363 encontrado")

if __name__ == "__main__":
    verificar_grupos_especificos()
    print("\n✅ Verificação concluída!") 