#!/usr/bin/env python
"""
Script para verificar chats duplicados e problemas de isolamento
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem, Cliente
from django.db.models import Count

def verificar_chats_duplicados():
    """Verifica se há chats duplicados com o mesmo chat_id"""
    print("=== VERIFICANDO CHATS DUPLICADOS ===")
    
    # Buscar chats duplicados
    duplicados = Chat.objects.values('chat_id').annotate(count=Count('id')).filter(count__gt=1)
    
    if not duplicados:
        print("✅ Nenhum chat duplicado encontrado!")
        return
    
    print(f"❌ Encontrados {len(duplicados)} chat_ids duplicados:")
    
    for dup in duplicados:
        chat_id = dup['chat_id']
        count = dup['count']
        print(f"\n📱 Chat ID: {chat_id} - {count} vezes")
        
        # Mostrar detalhes de cada chat duplicado
        chats = Chat.objects.filter(chat_id=chat_id)
        for chat in chats:
            print(f"   - Chat {chat.id}: Cliente '{chat.cliente.nome}' (ID: {chat.cliente.id}) - Status: {chat.status}")

def verificar_mensagens_por_chat():
    """Verifica mensagens por chat para identificar problemas de isolamento"""
    print("\n=== VERIFICANDO MENSAGENS POR CHAT ===")
    
    # Buscar todos os chats
    chats = Chat.objects.all().order_by('chat_id')
    
    for chat in chats:
        mensagens = Mensagem.objects.filter(chat=chat)
        print(f"\n📱 Chat {chat.id}: {chat.chat_id}")
        print(f"   Cliente: {chat.cliente.nome}")
        print(f"   Total de mensagens: {mensagens.count()}")
        
        # Mostrar algumas mensagens de exemplo
        for msg in mensagens[:3]:
            print(f"   - Msg {msg.id}: {msg.remetente} (from_me: {msg.from_me})")
        
        if mensagens.count() > 3:
            print(f"   ... e mais {mensagens.count() - 3} mensagens")

def verificar_isolamento_por_cliente():
    """Verifica se as mensagens estão isoladas por cliente"""
    print("\n=== VERIFICANDO ISOLAMENTO POR CLIENTE ===")
    
    # Buscar todos os clientes
    clientes = Cliente.objects.all()
    
    for cliente in clientes:
        print(f"\n👤 Cliente: {cliente.nome}")
        
        # Buscar chats do cliente
        chats = Chat.objects.filter(cliente=cliente)
        print(f"   Total de chats: {chats.count()}")
        
        # Buscar mensagens do cliente
        mensagens = Mensagem.objects.filter(chat__cliente=cliente)
        print(f"   Total de mensagens: {mensagens.count()}")
        
        # Verificar se há mensagens de outros clientes
        mensagens_outros = Mensagem.objects.exclude(chat__cliente=cliente)
        if mensagens_outros.exists():
            print(f"   ⚠️  ATENÇÃO: Encontradas {mensagens_outros.count()} mensagens de outros clientes!")
            
            # Mostrar algumas mensagens de outros clientes
            for msg in mensagens_outros[:3]:
                print(f"      - Msg {msg.id}: Chat {msg.chat.chat_id} - Cliente: {msg.chat.cliente.nome}")
        else:
            print(f"   ✅ Isolamento correto: apenas mensagens do próprio cliente")

def verificar_problemas_específicos():
    """Verifica problemas específicos que podem causar vazamento de mensagens"""
    print("\n=== VERIFICANDO PROBLEMAS ESPECÍFICOS ===")
    
    # Verificar se há mensagens sem chat
    mensagens_sem_chat = Mensagem.objects.filter(chat__isnull=True)
    if mensagens_sem_chat.exists():
        print(f"❌ Encontradas {mensagens_sem_chat.count()} mensagens sem chat!")
    else:
        print("✅ Todas as mensagens têm chat associado")
    
    # Verificar se há chats sem cliente
    chats_sem_cliente = Chat.objects.filter(cliente__isnull=True)
    if chats_sem_cliente.exists():
        print(f"❌ Encontrados {chats_sem_cliente.count()} chats sem cliente!")
    else:
        print("✅ Todos os chats têm cliente associado")
    
    # Verificar se há mensagens com from_me=True mas remetente incorreto
    mensagens_incorretas = Mensagem.objects.filter(from_me=True).exclude(remetente__icontains='Elizeu')
    if mensagens_incorretas.exists():
        print(f"❌ Encontradas {mensagens_incorretas.count()} mensagens from_me=True com remetente incorreto!")
        for msg in mensagens_incorretas[:3]:
            print(f"   - Msg {msg.id}: {msg.remetente} (chat: {msg.chat.chat_id})")
    else:
        print("✅ Todas as mensagens from_me=True têm remetente correto")

if __name__ == "__main__":
    print("🔍 INICIANDO VERIFICAÇÃO DE ISOLAMENTO DE CHATS")
    print("=" * 50)
    
    verificar_chats_duplicados()
    verificar_mensagens_por_chat()
    verificar_isolamento_por_cliente()
    verificar_problemas_específicos()
    
    print("\n" + "=" * 50)
    print("✅ VERIFICAÇÃO CONCLUÍDA") 