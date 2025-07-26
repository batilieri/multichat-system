#!/usr/bin/env python
"""
Script para corrigir chats que não têm cliente associado
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem, Cliente, WhatsappInstance
from webhook.models import WebhookEvent

def corrigir_chats_sem_cliente():
    """Corrige chats que não têm cliente associado"""
    print("🔧 Corrigindo chats sem cliente...")
    print("=" * 50)
    
    # Buscar chats sem cliente
    chats_sem_cliente = Chat.objects.filter(cliente__isnull=True)
    print(f"Chats sem cliente encontrados: {chats_sem_cliente.count()}")
    
    if chats_sem_cliente.count() == 0:
        print("✅ Todos os chats já têm cliente associado!")
        return
    
    # Buscar o cliente principal (assumindo que é o Elizeu)
    try:
        cliente = Cliente.objects.get(nome__icontains="Elizeu")
        print(f"👤 Cliente encontrado: {cliente.nome}")
    except Cliente.DoesNotExist:
        cliente = Cliente.objects.first()
        if not cliente:
            print("❌ Nenhum cliente encontrado no sistema")
            return
        print(f"👤 Usando cliente: {cliente.nome}")
    
    # Buscar instância do WhatsApp
    try:
        instancia = WhatsappInstance.objects.get(cliente=cliente)
        print(f"📱 Instância encontrada: {instancia.instance_id}")
    except WhatsappInstance.DoesNotExist:
        print("⚠️ Nenhuma instância WhatsApp encontrada para o cliente")
        instancia = None
    
    # Corrigir chats
    corrigidos = 0
    for chat in chats_sem_cliente:
        try:
            chat.cliente = cliente
            chat.save()
            print(f"✅ Chat {chat.chat_id} associado ao cliente {cliente.nome}")
            corrigidos += 1
        except Exception as e:
            print(f"❌ Erro ao corrigir chat {chat.chat_id}: {e}")
    
    print(f"\n📊 Resumo:")
    print(f"   Chats corrigidos: {corrigidos}")
    print(f"   Chats restantes sem cliente: {Chat.objects.filter(cliente__isnull=True).count()}")

def verificar_mensagens_sem_message_id():
    """Verifica mensagens que não têm message_id"""
    print("\n🔍 Verificando mensagens sem message_id...")
    print("=" * 50)
    
    mensagens_sem_id = Mensagem.objects.filter(message_id__isnull=True)
    print(f"Mensagens sem message_id: {mensagens_sem_id.count()}")
    
    if mensagens_sem_id.count() > 0:
        print("⚠️ Mensagens sem message_id encontradas:")
        for msg in mensagens_sem_id[:5]:
            print(f"   ID: {msg.id}, Chat: {msg.chat.chat_id}, Conteúdo: {msg.conteudo[:50]}...")
    
    # Verificar se há message_ids duplicados
    from django.db.models import Count
    duplicatas = Mensagem.objects.values('message_id').annotate(
        count=Count('message_id')
    ).filter(count__gt=1, message_id__isnull=False)
    
    print(f"\nMessage IDs duplicados: {duplicatas.count()}")
    
    if duplicatas.exists():
        print("⚠️ Message IDs duplicados encontrados:")
        for dup in duplicatas[:5]:
            print(f"   {dup['message_id']}: {dup['count']} vezes")

def verificar_webhook_events():
    """Verifica eventos de webhook"""
    print("\n🔍 Verificando eventos de webhook...")
    print("=" * 50)
    
    total_events = WebhookEvent.objects.count()
    print(f"Total de eventos de webhook: {total_events}")
    
    events_com_message_id = WebhookEvent.objects.filter(message_id__isnull=False)
    print(f"Eventos com message_id: {events_com_message_id.count()}")
    
    events_sem_message_id = WebhookEvent.objects.filter(message_id__isnull=True)
    print(f"Eventos sem message_id: {events_sem_message_id.count()}")
    
    if events_com_message_id.exists():
        primeiro_evento = events_com_message_id.first()
        print(f"Primeiro evento com message_id: {primeiro_evento.message_id}")
        print(f"Chat ID: {primeiro_evento.chat_id}")
        print(f"Tipo: {primeiro_evento.event_type}")

if __name__ == "__main__":
    print("🧪 Correção de Chats e Verificação de Dados")
    print("=" * 60)
    
    corrigir_chats_sem_cliente()
    verificar_mensagens_sem_message_id()
    verificar_webhook_events()
    
    print("\n" + "=" * 60)
    print("🏁 Correção concluída!") 