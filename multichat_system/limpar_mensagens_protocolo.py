#!/usr/bin/env python
"""
Script para limpar mensagens de protocolo do WhatsApp
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem
from django.db import transaction

def limpar_mensagens_protocolo():
    """Remove mensagens de protocolo do WhatsApp que não devem aparecer no chat"""
    print("🧹 INICIANDO LIMPEZA DE MENSAGENS DE PROTOCOLO")
    print("=" * 50)
    
    # Critérios para identificar mensagens de protocolo
    protocolo_keywords = [
        'protocolMessage',
        'APP_STATE_SYNC_KEY_REQUEST',
        'deviceListMetadata',
        'messageContextInfo',
        'senderKeyHash',
        'senderTimestamp',
        'deviceListMetadataVersion',
        'keyIds',
        'keyId',
        'AAAAACSE'
    ]
    
    # Buscar mensagens de protocolo
    mensagens_protocolo = []
    for keyword in protocolo_keywords:
        msgs = Mensagem.objects.filter(conteudo__icontains=keyword)
        mensagens_protocolo.extend(list(msgs))
    
    # Remover duplicatas
    mensagens_protocolo = list(set(mensagens_protocolo))
    
    if not mensagens_protocolo:
        print("✅ Nenhuma mensagem de protocolo encontrada!")
        return
    
    print(f"❌ Encontradas {len(mensagens_protocolo)} mensagens de protocolo:")
    
    # Mostrar detalhes das mensagens que serão removidas
    for msg in mensagens_protocolo:
        print(f"   - Msg {msg.id}: Chat {msg.chat.chat_id} - From_me: {msg.from_me} - Remetente: '{msg.remetente}'")
        print(f"     Conteúdo: {msg.conteudo[:100]}...")
    
    # Confirmar remoção
    confirmacao = input("\n🤔 Deseja remover essas mensagens? (s/N): ").strip().lower()
    
    if confirmacao != 's':
        print("❌ Operação cancelada pelo usuário")
        return
    
    # Remover mensagens com transação
    with transaction.atomic():
        for msg in mensagens_protocolo:
            print(f"🗑️  Removendo mensagem {msg.id}...")
            msg.delete()
    
    print(f"\n✅ {len(mensagens_protocolo)} mensagens de protocolo removidas com sucesso!")
    
    # Verificar se ainda há mensagens de protocolo
    mensagens_restantes = []
    for keyword in protocolo_keywords:
        msgs = Mensagem.objects.filter(conteudo__icontains=keyword)
        mensagens_restantes.extend(list(msgs))
    
    mensagens_restantes = list(set(mensagens_restantes))
    
    if mensagens_restantes:
        print(f"⚠️  Ainda existem {len(mensagens_restantes)} mensagens de protocolo!")
    else:
        print("✅ Todas as mensagens de protocolo foram removidas!")

def verificar_mensagens_vazias():
    """Verifica e remove mensagens com remetente vazio"""
    print("\n🔍 VERIFICANDO MENSAGENS COM REMETENTE VAZIO")
    print("=" * 50)
    
    mensagens_vazias = Mensagem.objects.filter(remetente='')
    
    if not mensagens_vazias:
        print("✅ Nenhuma mensagem com remetente vazio encontrada!")
        return
    
    print(f"❌ Encontradas {mensagens_vazias.count()} mensagens com remetente vazio:")
    
    for msg in mensagens_vazias[:5]:  # Mostrar apenas as primeiras 5
        print(f"   - Msg {msg.id}: Chat {msg.chat.chat_id} - From_me: {msg.from_me} - Conteúdo: {msg.conteudo[:50]}...")
    
    if mensagens_vazias.count() > 5:
        print(f"   ... e mais {mensagens_vazias.count() - 5} mensagens")
    
    # Confirmar remoção
    confirmacao = input("\n🤔 Deseja remover essas mensagens? (s/N): ").strip().lower()
    
    if confirmacao != 's':
        print("❌ Operação cancelada pelo usuário")
        return
    
    # Remover mensagens com transação
    with transaction.atomic():
        count = mensagens_vazias.count()
        mensagens_vazias.delete()
        print(f"✅ {count} mensagens com remetente vazio removidas!")

if __name__ == "__main__":
    limpar_mensagens_protocolo()
    verificar_mensagens_vazias()
    
    print("\n" + "=" * 50)
    print("✅ LIMPEZA CONCLUÍDA") 