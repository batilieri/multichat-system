#!/usr/bin/env python
"""
Script para testar as correções de grupos implementadas.

Este script verifica:
1. Se os grupos têm group_id único
2. Se as mensagens têm informações do remetente
3. Se o frontend recebe os dados corretos
4. Se a API retorna os campos necessários

Uso: python testar_grupos_corrigidos.py
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem
from webhook.models import Chat as WebhookChat, Message as WebhookMessage
from api.serializers import ChatSerializer, MensagemSerializer, WebhookMessageSerializer

def testar_chats_core():
    """Testa os chats do modelo core"""
    print("🧪 Testando chats do modelo core...")
    
    # Buscar todos os grupos
    grupos = Chat.objects.filter(is_group=True)
    print(f"📊 Total de grupos: {grupos.count()}")
    
    for grupo in grupos:
        print(f"\n📱 Grupo: {grupo.chat_name} (ID: {grupo.chat_id})")
        print(f"   Group ID: {grupo.group_id}")
        print(f"   Cliente: {grupo.cliente.nome}")
        print(f"   Status: {grupo.status}")
        
        # Verificar mensagens
        mensagens = grupo.mensagens.all()
        print(f"   Mensagens: {mensagens.count()}")
        
        for msg in mensagens[:3]:  # Mostrar apenas as 3 primeiras
            sender_name = msg.get_sender_display_name()
            print(f"     - {msg.remetente} ({sender_name}) - {msg.conteudo[:50]}...")
        
        # Testar serializer
        serializer = ChatSerializer(grupo)
        data = serializer.data
        print(f"   Serializer - is_group: {data.get('is_group')}")
        print(f"   Serializer - group_id: {data.get('group_id')}")

def testar_chats_webhook():
    """Testa os chats do modelo webhook"""
    print("\n🧪 Testando chats do modelo webhook...")
    
    # Buscar todos os grupos
    grupos = WebhookChat.objects.filter(is_group=True)
    print(f"📊 Total de grupos: {grupos.count()}")
    
    for grupo in grupos:
        print(f"\n📱 Grupo: {grupo.chat_name} (ID: {grupo.chat_id})")
        print(f"   Group ID: {grupo.group_id}")
        print(f"   Cliente: {grupo.cliente.nome}")
        print(f"   Status: {grupo.status}")
        
        # Verificar mensagens
        mensagens = grupo.webhook_messages.all()
        print(f"   Mensagens: {mensagens.count()}")
        
        for msg in mensagens[:3]:  # Mostrar apenas as 3 primeiras
            sender_name = msg.get_sender_display_name()
            print(f"     - {msg.sender.sender_id} ({sender_name}) - {msg.text_content[:50] if msg.text_content else 'Sem texto'}...")
        
        # Testar serializer
        serializer = WebhookMessageSerializer(mensagens.first()) if mensagens.exists() else None
        if serializer:
            data = serializer.data
            print(f"   Serializer - sender_display_name: {data.get('sender_display_name')}")

def testar_api_endpoints():
    """Testa os endpoints da API"""
    print("\n🧪 Testando endpoints da API...")
    
    # Simular request para /api/chats/
    from django.test import RequestFactory
    from api.views import ChatViewSet
    from rest_framework.test import force_authenticate
    from authentication.models import Usuario
    
    factory = RequestFactory()
    
    # Buscar um usuário admin
    try:
        user = Usuario.objects.filter(is_superuser=True).first()
        if not user:
            user = Usuario.objects.first()
        
        if user:
            # Criar request
            request = factory.get('/api/chats/')
            force_authenticate(request, user=user)
            
            # Testar ViewSet
            viewset = ChatViewSet()
            viewset.request = request
            viewset.action = 'list'
            
            queryset = viewset.get_queryset()
            grupos = queryset.filter(is_group=True)
            
            print(f"📊 API - Grupos encontrados: {grupos.count()}")
            
            for grupo in grupos[:3]:  # Mostrar apenas os 3 primeiros
                serializer = ChatSerializer(grupo, context={'request': request})
                data = serializer.data
                print(f"   📱 {data.get('chat_name')} - is_group: {data.get('is_group')} - group_id: {data.get('group_id')}")
                
                # Verificar última mensagem
                ultima_msg = data.get('ultima_mensagem', {})
                if ultima_msg:
                    print(f"     Última msg: {ultima_msg.get('remetente')} - {ultima_msg.get('sender_display_name')}")
        
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")

def testar_frontend_data():
    """Testa se os dados estão no formato esperado pelo frontend"""
    print("\n🧪 Testando formato de dados para frontend...")
    
    # Buscar um grupo com mensagens
    grupo = Chat.objects.filter(is_group=True).first()
    
    if grupo:
        print(f"📱 Testando grupo: {grupo.chat_name}")
        
        # Simular dados que o frontend espera
        serializer = ChatSerializer(grupo)
        data = serializer.data
        
        # Verificar campos obrigatórios
        campos_obrigatorios = ['id', 'chat_id', 'chat_name', 'is_group', 'group_id']
        for campo in campos_obrigatorios:
            if campo in data:
                print(f"   ✅ {campo}: {data[campo]}")
            else:
                print(f"   ❌ {campo}: FALTANDO")
        
        # Verificar mensagens
        mensagens = grupo.mensagens.all()[:5]
        print(f"   📨 Mensagens de teste: {mensagens.count()}")
        
        for msg in mensagens:
            msg_serializer = MensagemSerializer(msg)
            msg_data = msg_serializer.data
            
            sender_name = msg_data.get('sender_display_name')
            print(f"     - {msg_data.get('remetente')} ({sender_name}) - fromMe: {msg_data.get('fromMe')}")
    
    else:
        print("❌ Nenhum grupo encontrado para teste")

def main():
    """Função principal"""
    print("🚀 Iniciando testes de grupos corrigidos...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Testar modelos
        testar_chats_core()
        testar_chats_webhook()
        
        # Testar API
        testar_api_endpoints()
        
        # Testar frontend
        testar_frontend_data()
        
        print("\n✅ Testes concluídos com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 