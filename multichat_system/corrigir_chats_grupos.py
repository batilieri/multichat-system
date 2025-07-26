#!/usr/bin/env python
"""
Script para corrigir chats existentes que são grupos.

Este script:
1. Identifica chats que são grupos mas não têm group_id
2. Gera group_id único para cada grupo
3. Atualiza mensagens com informações do remetente
4. Corrige a estrutura de dados para grupos

Uso: python corrigir_chats_grupos.py
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem
from webhook.models import Chat as WebhookChat, Message as WebhookMessage, Sender as WebhookSender
import uuid

def corrigir_chats_core():
    """Corrige chats no modelo core"""
    print("🔧 Corrigindo chats no modelo core...")
    
    # Buscar chats que são grupos mas não têm group_id
    chats_grupos = Chat.objects.filter(is_group=True, group_id__isnull=True)
    print(f"📊 Encontrados {chats_grupos.count()} grupos sem group_id")
    
    for chat in chats_grupos:
        # Gerar group_id único
        chat.group_id = f"group_{uuid.uuid4().hex[:16]}"
        chat.save()
        print(f"✅ Chat {chat.chat_id} - {chat.chat_name} - group_id: {chat.group_id}")
    
    # Buscar chats que podem ser grupos mas não estão marcados
    chats_suspeitos = Chat.objects.filter(
        is_group=False,
        chat_id__contains='@g.us'
    )
    print(f"📊 Encontrados {chats_suspeitos.count()} chats suspeitos de serem grupos")
    
    for chat in chats_suspeitos:
        chat.is_group = True
        if not chat.group_id:
            chat.group_id = f"group_{uuid.uuid4().hex[:16]}"
        chat.save()
        print(f"✅ Chat {chat.chat_id} marcado como grupo - group_id: {chat.group_id}")

def corrigir_chats_webhook():
    """Corrige chats no modelo webhook"""
    print("\n🔧 Corrigindo chats no modelo webhook...")
    
    # Buscar chats que são grupos mas não têm group_id
    chats_grupos = WebhookChat.objects.filter(is_group=True, group_id__isnull=True)
    print(f"📊 Encontrados {chats_grupos.count()} grupos sem group_id")
    
    for chat in chats_grupos:
        # Gerar group_id único
        chat.group_id = f"group_{uuid.uuid4().hex[:16]}"
        chat.save()
        print(f"✅ Chat {chat.chat_id} - {chat.chat_name} - group_id: {chat.group_id}")
    
    # Buscar chats que podem ser grupos mas não estão marcados
    chats_suspeitos = WebhookChat.objects.filter(
        is_group=False,
        chat_id__contains='@g.us'
    )
    print(f"📊 Encontrados {chats_suspeitos.count()} chats suspeitos de serem grupos")
    
    for chat in chats_suspeitos:
        chat.is_group = True
        if not chat.group_id:
            chat.group_id = f"group_{uuid.uuid4().hex[:16]}"
        chat.save()
        print(f"✅ Chat {chat.chat_id} marcado como grupo - group_id: {chat.group_id}")

def corrigir_mensagens_core():
    """Corrige mensagens no modelo core"""
    print("\n🔧 Corrigindo mensagens no modelo core...")
    
    # Buscar mensagens de grupos que não têm informações do remetente
    mensagens_grupos = Mensagem.objects.filter(
        chat__is_group=True,
        from_me=False,
        sender_display_name__isnull=True
    ).select_related('chat')
    
    print(f"📊 Encontradas {mensagens_grupos.count()} mensagens de grupos sem informações do remetente")
    
    for mensagem in mensagens_grupos:
        # Usar o remetente como display_name se não tiver
        if not mensagem.sender_display_name:
            mensagem.sender_display_name = mensagem.remetente
            mensagem.save()
            print(f"✅ Mensagem {mensagem.id} - sender_display_name: {mensagem.sender_display_name}")

def corrigir_mensagens_webhook():
    """Corrige mensagens no modelo webhook"""
    print("\n🔧 Corrigindo mensagens no modelo webhook...")
    
    # Buscar mensagens de grupos que não têm informações do remetente
    mensagens_grupos = WebhookMessage.objects.filter(
        chat__is_group=True,
        from_me=False,
        sender_display_name__isnull=True
    ).select_related('chat', 'sender')
    
    print(f"📊 Encontradas {mensagens_grupos.count()} mensagens de grupos sem informações do remetente")
    
    for mensagem in mensagens_grupos:
        # Usar informações do sender se disponíveis
        if not mensagem.sender_display_name:
            mensagem.sender_display_name = mensagem.sender.push_name or mensagem.sender.sender_id
            mensagem.sender_push_name = mensagem.sender.push_name
            mensagem.sender_verified_name = mensagem.sender.verified_name
            mensagem.save()
            print(f"✅ Mensagem {mensagem.message_id} - sender_display_name: {mensagem.sender_display_name}")

def verificar_correcoes():
    """Verifica se as correções foram aplicadas corretamente"""
    print("\n🔍 Verificando correções...")
    
    # Verificar chats core
    grupos_core = Chat.objects.filter(is_group=True)
    grupos_sem_id = grupos_core.filter(group_id__isnull=True)
    print(f"📊 Core - Total de grupos: {grupos_core.count()}")
    print(f"📊 Core - Grupos sem group_id: {grupos_sem_id.count()}")
    
    # Verificar chats webhook
    grupos_webhook = WebhookChat.objects.filter(is_group=True)
    grupos_sem_id_webhook = grupos_webhook.filter(group_id__isnull=True)
    print(f"📊 Webhook - Total de grupos: {grupos_webhook.count()}")
    print(f"📊 Webhook - Grupos sem group_id: {grupos_sem_id_webhook.count()}")
    
    # Verificar mensagens
    mensagens_grupos_core = Mensagem.objects.filter(chat__is_group=True, from_me=False)
    mensagens_sem_display = mensagens_grupos_core.filter(sender_display_name__isnull=True)
    print(f"📊 Core - Mensagens de grupos: {mensagens_grupos_core.count()}")
    print(f"📊 Core - Mensagens sem sender_display_name: {mensagens_sem_display.count()}")
    
    mensagens_grupos_webhook = WebhookMessage.objects.filter(chat__is_group=True, from_me=False)
    mensagens_sem_display_webhook = mensagens_grupos_webhook.filter(sender_display_name__isnull=True)
    print(f"📊 Webhook - Mensagens de grupos: {mensagens_grupos_webhook.count()}")
    print(f"📊 Webhook - Mensagens sem sender_display_name: {mensagens_sem_display_webhook.count()}")

def main():
    """Função principal"""
    print("🚀 Iniciando correção de chats e grupos...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Corrigir chats
        corrigir_chats_core()
        corrigir_chats_webhook()
        
        # Corrigir mensagens
        corrigir_mensagens_core()
        corrigir_mensagens_webhook()
        
        # Verificar correções
        verificar_correcoes()
        
        print("\n✅ Correção concluída com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante a correção: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 