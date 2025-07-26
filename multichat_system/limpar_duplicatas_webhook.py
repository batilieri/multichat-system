#!/usr/bin/env python
"""
Script para limpar duplicatas de message_id no WebhookEvent.
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from webhook.models import WebhookEvent
from django.db import transaction

def limpar_duplicatas_webhook():
    """
    Remove duplicatas de message_id no WebhookEvent, mantendo apenas o mais recente.
    """
    print("🧹 Iniciando limpeza de duplicatas no WebhookEvent...")
    
    # Buscar todos os message_ids que aparecem mais de uma vez
    from django.db.models import Count
    duplicatas = WebhookEvent.objects.filter(
        message_id__isnull=False
    ).exclude(
        message_id=''
    ).values('message_id').annotate(
        count=Count('message_id')
    ).filter(count__gt=1)
    
    print(f"📊 Message_ids duplicados encontrados: {duplicatas.count()}")
    
    if duplicatas.count() == 0:
        print("✅ Nenhuma duplicata encontrada!")
        return
    
    # Para cada message_id duplicado, manter apenas o mais recente
    removidos = 0
    
    for duplicata in duplicatas:
        message_id = duplicata['message_id']
        
        # Buscar todos os eventos com este message_id, ordenados por timestamp
        eventos = WebhookEvent.objects.filter(
            message_id=message_id
        ).order_by('-timestamp')
        
        # Manter apenas o primeiro (mais recente)
        eventos_para_remover = eventos[1:]
        
        with transaction.atomic():
            for evento in eventos_para_remover:
                evento.delete()
                removidos += 1
        
        print(f"✅ Removidos {len(eventos_para_remover)} eventos duplicados para message_id: {message_id}")
    
    print(f"\n📊 Resumo da limpeza:")
    print(f"✅ Eventos removidos: {removidos}")

def verificar_duplicatas():
    """
    Verifica se ainda há duplicatas.
    """
    print("🔍 Verificando duplicatas...")
    
    from django.db.models import Count
    duplicatas = WebhookEvent.objects.filter(
        message_id__isnull=False
    ).exclude(
        message_id=''
    ).values('message_id').annotate(
        count=Count('message_id')
    ).filter(count__gt=1)
    
    print(f"📊 Message_ids ainda duplicados: {duplicatas.count()}")
    
    if duplicatas.count() > 0:
        print("⚠️ Ainda há duplicatas:")
        for duplicata in duplicatas[:5]:  # Mostrar apenas os primeiros 5
            print(f"   - {duplicata['message_id']}: {duplicata['count']} ocorrências")
    else:
        print("✅ Nenhuma duplicata encontrada!")

if __name__ == "__main__":
    print("🚀 Script de limpeza de duplicatas")
    print("=" * 50)
    
    # Verificar duplicatas atuais
    verificar_duplicatas()
    
    print("\n" + "=" * 50)
    
    # Perguntar se deve limpar
    resposta = input("\nDeseja executar a limpeza? (s/n): ").lower().strip()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        limpar_duplicatas_webhook()
        
        print("\n" + "=" * 50)
        print("🔍 Verificação final:")
        verificar_duplicatas()
    else:
        print("❌ Limpeza cancelada.") 