#!/usr/bin/env python
"""
Teste direto da API de mensagens
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem, Cliente
from authentication.models import Usuario
from django.test import RequestFactory
from api.views import MensagemViewSet
from rest_framework.test import force_authenticate
from rest_framework.test import APIRequestFactory

def test_api_direto():
    """Testa a API diretamente"""
    print("🔍 Teste direto da API de mensagens...")
    print("=" * 50)
    
    # Buscar um chat com mensagens
    chat_com_mensagens = Chat.objects.filter(mensagens__isnull=False).first()
    
    if not chat_com_mensagens:
        print("❌ Nenhum chat com mensagens encontrado")
        return
    
    print(f"📱 Chat selecionado: {chat_com_mensagens.chat_id}")
    print(f"   Cliente: {chat_com_mensagens.cliente.nome}")
    print(f"   Total de mensagens: {chat_com_mensagens.mensagens.count()}")
    
    # Buscar um usuário admin
    user = Usuario.objects.filter(tipo_usuario='admin').first()
    if not user:
        user = Usuario.objects.first()
    
    if not user:
        print("❌ Nenhum usuário encontrado")
        return
    
    print(f"👤 Usuário: {user.username} ({user.tipo_usuario})")
    
    # Criar request factory
    factory = APIRequestFactory()
    
    # Testar endpoint de mensagens
    request = factory.get(f'/api/mensagens/?chat_id={chat_com_mensagens.chat_id}')
    force_authenticate(request, user=user)
    
    # Definir query_params manualmente
    request.query_params = request.GET
    
    # Criar viewset
    viewset = MensagemViewSet()
    viewset.request = request
    viewset.action = 'list'
    
    # Testar get_queryset
    print("\n🔍 Testando get_queryset...")
    try:
        queryset = viewset.get_queryset()
        print(f"   Total de mensagens no queryset: {queryset.count()}")
        
        # Filtrar por chat_id
        mensagens_chat = queryset.filter(chat__chat_id=chat_com_mensagens.chat_id)
        print(f"   Mensagens do chat específico: {mensagens_chat.count()}")
        
        if mensagens_chat.exists():
            primeira_msg = mensagens_chat.first()
            print(f"   Primeira mensagem: ID={primeira_msg.id}, Conteúdo={primeira_msg.conteudo[:50]}...")
        
    except Exception as e:
        print(f"   ❌ Erro no get_queryset: {e}")
        import traceback
        traceback.print_exc()
    
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
        import traceback
        traceback.print_exc()
    
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

if __name__ == "__main__":
    test_api_direto() 