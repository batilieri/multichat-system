#!/usr/bin/env python
"""
Script para gerar message_ids únicos para mensagens que não têm.
"""

import os
import sys
import django
import uuid
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem
from django.db import transaction

def gerar_message_ids_unicos():
    """
    Gera message_ids únicos para mensagens que não têm.
    """
    print("🔧 Gerando message_ids únicos...")
    
    # Buscar mensagens sem message_id
    mensagens_sem_id = Mensagem.objects.filter(message_id__isnull=True)
    print(f"📊 Mensagens sem message_id encontradas: {mensagens_sem_id.count()}")
    
    if mensagens_sem_id.count() == 0:
        print("✅ Todas as mensagens já têm message_id!")
        return
    
    # Buscar message_ids existentes para evitar conflitos
    message_ids_existentes = set(
        Mensagem.objects.filter(
            message_id__isnull=False
        ).exclude(
            message_id=''
        ).values_list('message_id', flat=True)
    )
    
    print(f"📊 Message_ids existentes: {len(message_ids_existentes)}")
    
    # Gerar message_ids únicos
    gerados = 0
    
    for mensagem in mensagens_sem_id:
        # Gerar um message_id único baseado no ID da mensagem e timestamp
        timestamp_hex = hex(int(mensagem.data_envio.timestamp()))[2:].upper()
        id_hex = hex(mensagem.id)[2:].upper().zfill(8)
        
        # Criar um message_id único
        message_id = f"{id_hex}{timestamp_hex[-8:]}"
        
        # Se já existe, adicionar um sufixo único
        if message_id in message_ids_existentes:
            sufixo = uuid.uuid4().hex[:8].upper()
            message_id = f"{message_id}{sufixo}"
        
        # Adicionar ao conjunto de existentes
        message_ids_existentes.add(message_id)
        
        with transaction.atomic():
            mensagem.message_id = message_id
            mensagem.save()
        
        print(f"✅ Mensagem {mensagem.id} recebeu message_id: {message_id}")
        gerados += 1
    
    print(f"\n📊 Resumo da geração:")
    print(f"✅ Message_ids gerados: {gerados}")

def verificar_message_ids():
    """
    Verifica o status dos message_ids.
    """
    print("🔍 Verificando status dos message_ids...")
    
    total_mensagens = Mensagem.objects.count()
    mensagens_com_id = Mensagem.objects.filter(message_id__isnull=False).exclude(message_id='').count()
    mensagens_sem_id = Mensagem.objects.filter(message_id__isnull=True).count()
    mensagens_id_vazio = Mensagem.objects.filter(message_id='').count()
    
    print(f"📊 Total de mensagens: {total_mensagens}")
    print(f"✅ Mensagens com message_id: {mensagens_com_id}")
    print(f"⚠️ Mensagens sem message_id: {mensagens_sem_id}")
    print(f"⚠️ Mensagens com message_id vazio: {mensagens_id_vazio}")
    
    # Mostrar alguns exemplos
    print(f"\n📝 Exemplos de message_ids:")
    exemplos = Mensagem.objects.filter(
        message_id__isnull=False
    ).exclude(
        message_id=''
    ).values_list('id', 'message_id', 'conteudo')[:5]
    
    for msg_id, message_id, conteudo in exemplos:
        print(f"   - ID: {msg_id}, message_id: {message_id}, conteúdo: {conteudo[:50]}...")

if __name__ == "__main__":
    print("🚀 Script de geração de message_ids únicos")
    print("=" * 50)
    
    # Verificar status atual
    verificar_message_ids()
    
    print("\n" + "=" * 50)
    
    # Perguntar se deve gerar
    resposta = input("\nDeseja gerar message_ids únicos? (s/n): ").lower().strip()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        gerar_message_ids_unicos()
        
        print("\n" + "=" * 50)
        print("🔍 Verificação final:")
        verificar_message_ids()
    else:
        print("❌ Geração cancelada.") 