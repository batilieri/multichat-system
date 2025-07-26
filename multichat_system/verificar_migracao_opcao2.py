#!/usr/bin/env python3
"""
Script para verificar o que aconteceu quando foi escolhida a opção 2 na migração
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Cliente, WhatsappInstance, Chat, Mensagem
from webhook.models import WebhookEvent
from django.db import connection

def verificar_campos_null():
    """Verifica campos que podem ter ficado NULL após a migração"""
    print("🔍 VERIFICANDO CAMPOS NULL APÓS MIGRAÇÃO")
    print("=" * 60)
    
    # Verificar WhatsappInstance
    print("\n📱 WHATSAPP INSTANCES:")
    instancias = WhatsappInstance.objects.all()
    for instancia in instancias:
        print(f"   ID: {instancia.id}")
        print(f"   Instance ID: {instancia.instance_id}")
        print(f"   Cliente: {instancia.cliente}")
        print(f"   Status: {instancia.status}")
        print(f"   Cliente é NULL: {instancia.cliente is None}")
        print()
    
    # Verificar Chats
    print("\n💬 CHATS:")
    chats = Chat.objects.all()
    for chat in chats:
        print(f"   ID: {chat.id}")
        print(f"   Chat ID: {chat.chat_id}")
        print(f"   Cliente: {chat.cliente}")
        print(f"   Status: {chat.status}")
        print(f"   Canal: {chat.canal}")
        print(f"   Cliente é NULL: {chat.cliente is None}")
        print()
    
    # Verificar Mensagens
    print("\n💌 MENSAGENS:")
    mensagens = Mensagem.objects.all()
    for msg in mensagens:
        print(f"   ID: {msg.id}")
        print(f"   Chat: {msg.chat}")
        print(f"   Remetente: {msg.remetente}")
        print(f"   Conteúdo: {msg.conteudo[:50]}...")
        print(f"   Chat é NULL: {msg.chat is None}")
        print()

def verificar_estrutura_tabela():
    """Verifica a estrutura atual das tabelas"""
    print("\n🏗️  ESTRUTURA DAS TABELAS")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        # Verificar tabela core_chat
        cursor.execute("PRAGMA table_info(core_chat)")
        columns = cursor.fetchall()
        print("\n📋 Tabela core_chat:")
        for col in columns:
            print(f"   {col[1]} ({col[2]}) - NULL: {col[3]} - Default: {col[4]}")
        
        # Verificar tabela core_whatsappinstance
        cursor.execute("PRAGMA table_info(core_whatsappinstance)")
        columns = cursor.fetchall()
        print("\n📱 Tabela core_whatsappinstance:")
        for col in columns:
            print(f"   {col[1]} ({col[2]}) - NULL: {col[3]} - Default: {col[4]}")

def corrigir_campos_null():
    """Corrige campos NULL que podem ter sido criados"""
    print("\n🔧 CORRIGINDO CAMPOS NULL")
    print("=" * 60)
    
    # Buscar cliente ELIZEU
    try:
        cliente_elizeu = Cliente.objects.get(nome__icontains='ELIZEU BATILIERE DOS SANTOS')
        print(f"✅ Cliente encontrado: {cliente_elizeu.nome}")
    except Cliente.DoesNotExist:
        print("❌ Cliente ELIZEU não encontrado!")
        return
    
    # Corrigir WhatsappInstances sem cliente
    instancias_sem_cliente = WhatsappInstance.objects.filter(cliente__isnull=True)
    print(f"📱 Instâncias sem cliente: {instancias_sem_cliente.count()}")
    
    for instancia in instancias_sem_cliente:
        instancia.cliente = cliente_elizeu
        instancia.save()
        print(f"✅ Instância {instancia.instance_id} associada ao cliente")
    
    # Corrigir Chats sem cliente
    chats_sem_cliente = Chat.objects.filter(cliente__isnull=True)
    print(f"💬 Chats sem cliente: {chats_sem_cliente.count()}")
    
    for chat in chats_sem_cliente:
        chat.cliente = cliente_elizeu
        chat.save()
        print(f"✅ Chat {chat.chat_id} associado ao cliente")

if __name__ == "__main__":
    print("🔍 VERIFICAÇÃO DA MIGRAÇÃO - OPÇÃO 2")
    print("=" * 80)
    
    # Verificar estrutura das tabelas
    verificar_estrutura_tabela()
    
    # Verificar campos NULL
    verificar_campos_null()
    
    # Corrigir campos NULL se necessário
    corrigir_campos_null()
    
    print("\n" + "=" * 80)
    print("🎯 CONCLUSÃO:")
    print("A opção 2 na migração significa 'Ignore for now' - campos NULL")
    print("foram mantidos como NULL. Se houver problemas, eles foram corrigidos acima.") 