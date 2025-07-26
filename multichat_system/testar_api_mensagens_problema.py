#!/usr/bin/env python
"""
Script para testar a API de mensagens e identificar problemas
"""

import os
import sys
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem, Cliente
from authentication.models import Usuario
from django.test import RequestFactory
from api.views import MensagemViewSet
from rest_framework.test import force_authenticate

def test_api_mensagens():
    """Testa a API de mensagens diretamente"""
    print("🔍 Testando API de mensagens...")
    print("=" * 50)
    
    # Buscar um chat com mensagens
    chat_com_mensagens = Chat.objects.filter(mensagens__isnull=False).first()
    
    if not chat_com_mensagens:
        print("❌ Nenhum chat com mensagens encontrado")
        return
    
    print(f"📱 Chat selecionado: {chat_com_mensagens.chat_id}")
    print(f"   Cliente: {chat_com_mensagens.cliente.nome}")
    print(f"   Total de mensagens: {chat_com_mensagens.mensagens.count()}")
    
    # Buscar um usuário admin para teste
    try:
        user = Usuario.objects.filter(tipo_usuario='admin').first()
        if not user:
            user = Usuario.objects.first()
        
        if not user:
            print("❌ Nenhum usuário encontrado para teste")
            return
            
        print(f"👤 Usuário de teste: {user.username} ({user.tipo_usuario})")
        
        # Criar request factory
        factory = RequestFactory()
        
        # Testar endpoint de mensagens
        request = factory.get(f'/api/mensagens/?chat_id={chat_com_mensagens.chat_id}')
        force_authenticate(request, user=user)
        
        # Criar viewset
        viewset = MensagemViewSet()
        viewset.request = request
        viewset.action = 'list'
        
        # Testar get_queryset
        print("\n🔍 Testando get_queryset...")
        queryset = viewset.get_queryset()
        print(f"   Total de mensagens no queryset: {queryset.count()}")
        
        # Filtrar por chat_id
        mensagens_chat = queryset.filter(chat__chat_id=chat_com_mensagens.chat_id)
        print(f"   Mensagens do chat específico: {mensagens_chat.count()}")
        
        # Testar método list
        print("\n🔍 Testando método list...")
        try:
            response = viewset.list(request)
            print(f"   Status da resposta: {response.status_code}")
            
            if hasattr(response, 'data'):
                print(f"   Dados retornados: {len(response.data)} itens")
                if response.data:
                    print(f"   Primeira mensagem: {response.data[0]}")
            else:
                print(f"   Conteúdo da resposta: {response.content[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Erro no método list: {e}")
            
        # Testar busca direta no modelo
        print("\n🔍 Testando busca direta no modelo...")
        mensagens_diretas = Mensagem.objects.filter(chat=chat_com_mensagens)
        print(f"   Mensagens diretas: {mensagens_diretas.count()}")
        
        if mensagens_diretas.exists():
            primeira_msg = mensagens_diretas.first()
            print(f"   Primeira mensagem: ID={primeira_msg.id}, Conteúdo={primeira_msg.conteudo[:50]}...")
            print(f"   Message ID: {primeira_msg.message_id}")
            print(f"   From Me: {primeira_msg.from_me}")
            print(f"   Data: {primeira_msg.data_envio}")
        
        # Verificar se há problemas com message_id
        print("\n🔍 Verificando message_id...")
        mensagens_sem_id = Mensagem.objects.filter(message_id__isnull=True)
        print(f"   Mensagens sem message_id: {mensagens_sem_id.count()}")
        
        mensagens_com_id = Mensagem.objects.filter(message_id__isnull=False)
        print(f"   Mensagens com message_id: {mensagens_com_id.count()}")
        
        # Verificar duplicatas de message_id
        from django.db.models import Count
        duplicatas = Mensagem.objects.values('message_id').annotate(
            count=Count('message_id')
        ).filter(count__gt=1, message_id__isnull=False)
        
        print(f"   Message IDs duplicados: {duplicatas.count()}")
        
        if duplicatas.exists():
            print("   ⚠️ Message IDs duplicados encontrados:")
            for dup in duplicatas[:5]:
                print(f"      {dup['message_id']}: {dup['count']} vezes")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

def test_webhook_events():
    """Testa eventos de webhook relacionados"""
    print("\n🔍 Testando eventos de webhook...")
    print("=" * 50)
    
    try:
        from webhook.models import WebhookEvent
        
        total_events = WebhookEvent.objects.count()
        print(f"   Total de eventos de webhook: {total_events}")
        
        events_com_message_id = WebhookEvent.objects.filter(message_id__isnull=False)
        print(f"   Eventos com message_id: {events_com_message_id.count()}")
        
        events_sem_message_id = WebhookEvent.objects.filter(message_id__isnull=True)
        print(f"   Eventos sem message_id: {events_sem_message_id.count()}")
        
        if events_com_message_id.exists():
            primeiro_evento = events_com_message_id.first()
            print(f"   Primeiro evento com message_id: {primeiro_evento.message_id}")
            print(f"   Chat ID: {primeiro_evento.chat_id}")
            print(f"   Tipo: {primeiro_evento.event_type}")
            
    except ImportError:
        print("   ⚠️ Modelo WebhookEvent não encontrado")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def test_chat_creation():
    """Testa a criação de chats"""
    print("\n🔍 Testando criação de chats...")
    print("=" * 50)
    
    # Verificar chats sem cliente
    chats_sem_cliente = Chat.objects.filter(cliente__isnull=True)
    print(f"   Chats sem cliente: {chats_sem_cliente.count()}")
    
    # Verificar chats com cliente
    chats_com_cliente = Chat.objects.filter(cliente__isnull=False)
    print(f"   Chats com cliente: {chats_com_cliente.count()}")
    
    # Verificar chats por cliente
    for cliente in Cliente.objects.all():
        chats_cliente = Chat.objects.filter(cliente=cliente)
        print(f"   Cliente {cliente.nome}: {chats_cliente.count()} chats")
        
        if chats_cliente.exists():
            total_mensagens = sum(chat.mensagens.count() for chat in chats_cliente)
            print(f"      Total de mensagens: {total_mensagens}")

if __name__ == "__main__":
    print("🧪 Teste da API de Mensagens - Diagnóstico de Problemas")
    print("=" * 60)
    
    test_api_mensagens()
    test_webhook_events()
    test_chat_creation()
    
    print("\n" + "=" * 60)
    print("�� Teste concluído!") 