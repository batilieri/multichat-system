#!/usr/bin/env python3
"""
Script para corrigir mensagens duplicadas no sistema MultiChat

Este script identifica e remove mensagens duplicadas baseado no message_id
e corrige problemas de identificação de mensagens próprias.
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente
from django.db import transaction
from django.db.models import Count

def identificar_mensagens_duplicadas():
    """Identifica mensagens duplicadas baseado no message_id"""
    print("🔍 Identificando mensagens duplicadas...")
    
    # Mensagens com message_id duplicado
    duplicadas = Mensagem.objects.values('message_id').annotate(
        count=Count('id')
    ).filter(
        message_id__isnull=False,
        count__gt=1
    )
    
    print(f"📊 Encontradas {duplicadas.count()} mensagens com message_id duplicado")
    
    for dup in duplicadas:
        message_id = dup['message_id']
        count = dup['count']
        print(f"   - message_id: {message_id} (aparece {count} vezes)")
        
        # Listar todas as mensagens com este message_id
        mensagens = Mensagem.objects.filter(message_id=message_id).order_by('id')
        for msg in mensagens:
            print(f"     ID: {msg.id}, Chat: {msg.chat.chat_id}, Remetente: {msg.remetente}, Conteúdo: {msg.conteudo[:50]}...")
    
    return duplicadas

def remover_mensagens_duplicadas():
    """Remove mensagens duplicadas mantendo apenas a mais recente"""
    print("\n🗑️ Removendo mensagens duplicadas...")
    
    with transaction.atomic():
        # Encontrar message_ids duplicados
        duplicadas = Mensagem.objects.values('message_id').annotate(
            count=Count('id')
        ).filter(
            message_id__isnull=False,
            count__gt=1
        )
        
        total_removidas = 0
        
        for dup in duplicadas:
            message_id = dup['message_id']
            
            # Pegar todas as mensagens com este message_id, ordenadas por data_envio (mais recente primeiro)
            mensagens = Mensagem.objects.filter(message_id=message_id).order_by('-data_envio')
            
            # Manter a primeira (mais recente) e remover as outras
            mensagem_manter = mensagens.first()
            mensagens_remover = mensagens[1:]
            
            print(f"   - message_id: {message_id}")
            print(f"     Mantendo: ID {mensagem_manter.id} (mais recente)")
            
            for msg in mensagens_remover:
                print(f"     Removendo: ID {msg.id}")
                msg.delete()
                total_removidas += 1
        
        print(f"✅ Total de mensagens removidas: {total_removidas}")

def corrigir_identificacao_mensagens_proprias():
    """Corrige a identificação de mensagens próprias baseado no remetente"""
    print("\n🔧 Corrigindo identificação de mensagens próprias...")
    
    # Lista de nomes que indicam mensagens próprias
    nomes_proprios = [
        "Elizeu Batiliere",
        "Elizeu Batiliere Dos Santos",
        "Elizeu"
    ]
    
    with transaction.atomic():
        # Mensagens que têm remetente próprio mas from_me = False
        mensagens_incorretas = Mensagem.objects.filter(
            remetente__in=nomes_proprios,
            from_me=False
        )
        
        print(f"📊 Encontradas {mensagens_incorretas.count()} mensagens próprias com from_me=False")
        
        for msg in mensagens_incorretas:
            print(f"   - ID: {msg.id}, Remetente: {msg.remetente}, from_me: {msg.from_me} -> True")
            msg.from_me = True
            msg.save()
        
        # Mensagens que têm remetente de outros mas from_me = True
        mensagens_incorretas_2 = Mensagem.objects.exclude(
            remetente__in=nomes_proprios
        ).filter(from_me=True)
        
        print(f"📊 Encontradas {mensagens_incorretas_2.count()} mensagens de outros com from_me=True")
        
        for msg in mensagens_incorretas_2:
            print(f"   - ID: {msg.id}, Remetente: {msg.remetente}, from_me: {msg.from_me} -> False")
            msg.from_me = False
            msg.save()

def verificar_estado_atual():
    """Verifica o estado atual das mensagens"""
    print("\n📊 Estado atual das mensagens:")
    
    total_mensagens = Mensagem.objects.count()
    mensagens_proprias = Mensagem.objects.filter(from_me=True).count()
    mensagens_outros = Mensagem.objects.filter(from_me=False).count()
    mensagens_sem_message_id = Mensagem.objects.filter(message_id__isnull=True).count()
    
    print(f"   - Total de mensagens: {total_mensagens}")
    print(f"   - Mensagens próprias (from_me=True): {mensagens_proprias}")
    print(f"   - Mensagens de outros (from_me=False): {mensagens_outros}")
    print(f"   - Mensagens sem message_id: {mensagens_sem_message_id}")
    
    # Top 5 remetentes
    print("\n   - Top 5 remetentes:")
    remetentes = Mensagem.objects.values('remetente').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    for rem in remetentes:
        print(f"     {rem['remetente']}: {rem['count']} mensagens")

def main():
    """Função principal"""
    print("🚀 Iniciando correção de mensagens duplicadas...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar estado inicial
    verificar_estado_atual()
    
    # Identificar duplicatas
    duplicadas = identificar_mensagens_duplicadas()
    
    if duplicadas.count() > 0:
        # Perguntar se deve remover
        resposta = input("\n❓ Deseja remover as mensagens duplicadas? (s/N): ").strip().lower()
        if resposta in ['s', 'sim', 'y', 'yes']:
            remover_mensagens_duplicadas()
        else:
            print("❌ Operação cancelada pelo usuário")
    else:
        print("✅ Nenhuma mensagem duplicada encontrada")
    
    # Corrigir identificação de mensagens próprias
    resposta = input("\n❓ Deseja corrigir a identificação de mensagens próprias? (s/N): ").strip().lower()
    if resposta in ['s', 'sim', 'y', 'yes']:
        corrigir_identificacao_mensagens_proprias()
    else:
        print("❌ Operação cancelada pelo usuário")
    
    # Verificar estado final
    print("\n" + "="*50)
    verificar_estado_atual()
    
    print("\n✅ Correção concluída!")

if __name__ == "__main__":
    main() 