#!/usr/bin/env python3
"""
Script para limpar todos os grupos existentes no banco
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

def is_group_chat(chat_id):
    """
    Verifica se um chat_id é um grupo
    """
    if not chat_id:
        return False
    
    # Verificar se é um grupo (contém @g.us)
    if '@g.us' in chat_id:
        return True
    
    # Extrair apenas números
    numbers_only = re.sub(r'[^\d]', '', chat_id)
    
    # Verificar se é um grupo baseado no padrão (números longos que começam com 120363)
    if len(numbers_only) > 15 and numbers_only.startswith('120363'):
        return True
    
    return False

def limpar_todos_grupos():
    """
    Remove todos os grupos existentes no banco
    """
    print("🧹 LIMPANDO TODOS OS GRUPOS")
    print("=" * 50)
    
    # Buscar todos os chats
    todos_chats = Chat.objects.all()
    print(f"📊 Total de chats no banco: {todos_chats.count()}")
    
    grupos_encontrados = []
    chats_para_remover = []
    
    # Identificar grupos
    for chat in todos_chats:
        if is_group_chat(chat.chat_id):
            grupos_encontrados.append(chat)
            chats_para_remover.append(chat)
            print(f"🚫 Grupo identificado: {chat.chat_id}")
    
    print(f"\n📊 Grupos encontrados: {len(grupos_encontrados)}")
    
    if not grupos_encontrados:
        print("✅ Nenhum grupo encontrado para remover")
        return
    
    # Contar mensagens dos grupos
    total_mensagens = 0
    for grupo in grupos_encontrados:
        mensagens = Mensagem.objects.filter(chat=grupo)
        total_mensagens += mensagens.count()
        print(f"   - {grupo.chat_id}: {mensagens.count()} mensagens")
    
    print(f"\n📨 Total de mensagens em grupos: {total_mensagens}")
    
    # Confirmar limpeza
    print(f"\n⚠️ ATENÇÃO: Esta operação irá:")
    print(f"   - Remover {len(grupos_encontrados)} grupos")
    print(f"   - Remover {total_mensagens} mensagens")
    print(f"   - Esta ação não pode ser desfeita!")
    
    # Executar limpeza
    if grupos_encontrados:
        # Remover mensagens primeiro
        for grupo in grupos_encontrados:
            mensagens = Mensagem.objects.filter(chat=grupo)
            if mensagens.exists():
                print(f"🗑️ Removendo {mensagens.count()} mensagens do grupo {grupo.chat_id}")
                mensagens.delete()
        
        # Remover chats
        for grupo in grupos_encontrados:
            print(f"🗑️ Removendo grupo: {grupo.chat_id}")
            grupo.delete()
        
        print("✅ Limpeza concluída!")
    else:
        print("✅ Nenhum grupo para remover")

def listar_grupos_restantes():
    """
    Lista grupos que ainda podem existir após a limpeza
    """
    print("\n🔍 VERIFICANDO GRUPOS RESTANTES")
    print("=" * 40)
    
    todos_chats = Chat.objects.all()
    grupos_restantes = []
    
    for chat in todos_chats:
        if is_group_chat(chat.chat_id):
            grupos_restantes.append(chat)
    
    if grupos_restantes:
        print(f"⚠️ Ainda existem {len(grupos_restantes)} grupos:")
        for grupo in grupos_restantes:
            print(f"   - {grupo.chat_id}")
    else:
        print("✅ Nenhum grupo restante encontrado!")

if __name__ == "__main__":
    limpar_todos_grupos()
    listar_grupos_restantes()
    print("\n✅ Processo concluído!") 