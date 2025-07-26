#!/usr/bin/env python
"""
Script para verificar se os message_ids dos webhooks estão sendo salvos corretamente.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente
from webhook.models import WebhookEvent
from django.db.models import Count

def verificar_message_ids_webhook():
    """Verifica se os message_ids dos webhooks estão sendo salvos corretamente"""
    print("🔍 Verificando message_ids dos webhooks...")
    print("=" * 60)
    
    # 1. Verificar eventos de webhook
    print("📊 Eventos de webhook:")
    total_webhooks = WebhookEvent.objects.count()
    webhooks_com_message_id = WebhookEvent.objects.filter(message_id__isnull=False).exclude(message_id='').count()
    print(f"   - Total: {total_webhooks}")
    print(f"   - Com message_id: {webhooks_com_message_id}")
    print(f"   - Sem message_id: {total_webhooks - webhooks_com_message_id}")
    
    # 2. Verificar mensagens do core
    print("\n📊 Mensagens do core:")
    total_mensagens = Mensagem.objects.count()
    mensagens_com_message_id = Mensagem.objects.filter(message_id__isnull=False).exclude(message_id='').count()
    print(f"   - Total: {total_mensagens}")
    print(f"   - Com message_id: {mensagens_com_message_id}")
    print(f"   - Sem message_id: {total_mensagens - mensagens_com_message_id}")
    
    # 3. Verificar message_ids duplicados
    print("\n🔍 Verificando duplicatas:")
    duplicatas_webhook = WebhookEvent.objects.values('message_id').annotate(
        count=Count('message_id')
    ).filter(
        message_id__isnull=False,
        message_id__gt='',
        count__gt=1
    )
    
    duplicatas_mensagem = Mensagem.objects.values('message_id').annotate(
        count=Count('message_id')
    ).filter(
        message_id__isnull=False,
        message_id__gt='',
        count__gt=1
    )
    
    print(f"   - Webhook duplicados: {duplicatas_webhook.count()}")
    print(f"   - Mensagens duplicadas: {duplicatas_mensagem.count()}")
    
    # 4. Mostrar alguns exemplos de message_ids
    print("\n📋 Exemplos de message_ids (Webhook):")
    webhooks_exemplo = WebhookEvent.objects.filter(
        message_id__isnull=False
    ).exclude(
        message_id=''
    ).order_by('-timestamp')[:10]
    
    for webhook in webhooks_exemplo:
        print(f"   - {webhook.message_id} (Evento: {webhook.event_type})")
    
    print("\n📋 Exemplos de message_ids (Mensagens):")
    mensagens_exemplo = Mensagem.objects.filter(
        message_id__isnull=False
    ).exclude(
        message_id=''
    ).order_by('-data_envio')[:10]
    
    for msg in mensagens_exemplo:
        print(f"   - {msg.message_id} (Tipo: {msg.tipo}, From_me: {msg.from_me})")
    
    # 5. Verificar se há message_ids que são números (problema)
    print("\n⚠️ Verificando message_ids problemáticos:")
    webhooks_numericos = WebhookEvent.objects.filter(
        message_id__regex=r'^\d+$'
    ).exclude(message_id='')
    
    mensagens_numericas = Mensagem.objects.filter(
        message_id__regex=r'^\d+$'
    ).exclude(message_id='')
    
    print(f"   - Webhooks com message_id numérico: {webhooks_numericos.count()}")
    print(f"   - Mensagens com message_id numérico: {mensagens_numericas.count()}")
    
    if webhooks_numericos.exists():
        print("   ⚠️ Webhooks com message_id numérico encontrados:")
        for webhook in webhooks_numericos[:5]:
            print(f"      - {webhook.message_id} (Evento: {webhook.event_type})")
    
    if mensagens_numericas.exists():
        print("   ⚠️ Mensagens com message_id numérico encontradas:")
        for msg in mensagens_numericas[:5]:
            print(f"      - {msg.message_id} (ID: {msg.id}, Tipo: {msg.tipo})")

if __name__ == "__main__":
    verificar_message_ids_webhook() 