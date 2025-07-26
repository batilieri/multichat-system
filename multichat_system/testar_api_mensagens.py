#!/usr/bin/env python3
"""
Script para testar especificamente a API de mensagens
MultiChat System - Teste da API de Mensagens

Este script:
1. Testa a API de mensagens com diferentes filtros
2. Verifica se as mensagens estão sendo filtradas por chat_id
3. Testa a transformação de dados
"""

import os
import sys
import json
from datetime import datetime
from django.db.models import Count

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
import django
django.setup()

from core.models import Chat as CoreChat, Mensagem as CoreMensagem
from webhook.models import WebhookEvent, Chat as WebhookChat, Message as WebhookMessage
from django.test import RequestFactory
from api.views import MensagemViewSet
from rest_framework.test import force_authenticate
from authentication.models import Usuario
from api.serializers import MensagemSerializer

class MensagensAPITester:
    """Testador da API de mensagens"""
    
    def __init__(self):
        self.factory = RequestFactory()
        self.user = None
        self.setup_user()
    
    def setup_user(self):
        """Configura o usuário para teste"""
        try:
            self.user = Usuario.objects.filter(is_superuser=True).first()
            if not self.user:
                self.user = Usuario.objects.first()
            print(f"👤 Usuário de teste: {self.user.username} ({self.user.email})")
        except Exception as e:
            print(f"❌ Erro ao configurar usuário: {e}")
    
    def test_mensagens_por_chat(self):
        """Testa mensagens filtradas por chat_id"""
        print("🔍 Testando mensagens por chat...")
        print("=" * 50)
        
        # Buscar todos os chats
        chats = CoreChat.objects.all()
        print(f"📱 Total de chats: {chats.count()}")
        
        for chat in chats[:3]:  # Testar apenas os 3 primeiros
            print(f"\n📱 Chat: {chat.chat_id} - {chat.chat_name}")
            
            # Buscar mensagens diretamente no modelo
            mensagens_modelo = CoreMensagem.objects.filter(chat=chat)
            print(f"   💬 Mensagens no modelo: {mensagens_modelo.count()}")
            
            if mensagens_modelo.count() > 0:
                print("   Primeiras 3 mensagens:")
                for msg in mensagens_modelo[:3]:
                    print(f"   - {msg.message_id} - {msg.conteudo[:50]}... - FromMe: {msg.from_me}")
            
            # Testar API com filtro
            try:
                request = self.factory.get(f'/api/mensagens/?chat_id={chat.chat_id}')
                force_authenticate(request, user=self.user)
                
                viewset = MensagemViewSet()
                viewset.request = request
                viewset.action = 'list'
                
                # Simular o método list diretamente
                queryset = viewset.get_queryset()
                mensagens_api = queryset.filter(chat__chat_id=chat.chat_id)
                print(f"   💬 Mensagens via API: {mensagens_api.count()}")
                
                if mensagens_api.count() > 0:
                    print("   Primeiras 3 mensagens via API:")
                    for msg in mensagens_api[:3]:
                        print(f"   - {msg.message_id} - {msg.conteudo[:50]}... - FromMe: {msg.from_me}")
                
                # Verificar se os números batem
                if mensagens_modelo.count() != mensagens_api.count():
                    print(f"   ⚠️ DIFERENÇA: Modelo tem {mensagens_modelo.count()}, API retorna {mensagens_api.count()}")
                else:
                    print(f"   ✅ OK: Números batem ({mensagens_modelo.count()})")
                    
            except Exception as e:
                print(f"   ❌ Erro na API: {e}")
                # Tentar sem autenticação
                try:
                    viewset = MensagemViewSet()
                    queryset = viewset.get_queryset()
                    mensagens_api = queryset.filter(chat__chat_id=chat.chat_id)
                    print(f"   💬 Mensagens via API (sem auth): {mensagens_api.count()}")
                except Exception as e2:
                    print(f"   ❌ Erro na API (sem auth): {e2}")
    
    def test_serializer_mensagens(self):
        """Testa o serializer de mensagens"""
        print("\n🔍 Testando serializer de mensagens...")
        print("=" * 50)
        
        # Buscar algumas mensagens
        mensagens = CoreMensagem.objects.all()[:5]
        print(f"📝 Testando serializer com {mensagens.count()} mensagens")
        
        for msg in mensagens:
            try:
                serializer = MensagemSerializer(msg)
                data = serializer.data
                print(f"   ✅ {msg.message_id} - {data.get('conteudo', '')[:30]}...")
                print(f"      chat_id: {data.get('chat')}")
                print(f"      from_me: {data.get('from_me')}")
                print(f"      tipo: {data.get('tipo')}")
            except Exception as e:
                print(f"   ❌ Erro no serializer: {e}")
    
    def test_webhook_messages(self):
        """Testa mensagens do webhook"""
        print("\n🔍 Testando mensagens do webhook...")
        print("=" * 50)
        
        # Verificar mensagens do webhook
        webhook_messages = WebhookMessage.objects.all()
        print(f"📡 Webhook Messages: {webhook_messages.count()}")
        
        if webhook_messages.count() > 0:
            print("   Primeiras 3 mensagens do webhook:")
            for msg in webhook_messages[:3]:
                print(f"   - {msg.message_id} - Chat: {msg.chat.chat_id if msg.chat else 'N/A'}")
        
        # Verificar se há correspondência com mensagens core
        for msg in webhook_messages[:3]:
            if msg.chat:
                core_mensagens = CoreMensagem.objects.filter(
                    chat__chat_id=msg.chat.chat_id,
                    message_id=msg.message_id
                )
                print(f"   📱 {msg.message_id} - Core matches: {core_mensagens.count()}")
    
    def test_chat_relationships(self):
        """Testa relacionamentos entre chats e mensagens"""
        print("\n🔍 Testando relacionamentos...")
        print("=" * 50)
        
        # Verificar chats com mensagens
        chats_com_mensagens = CoreChat.objects.annotate(
            msg_count=Count('mensagens')
        ).filter(msg_count__gt=0)
        
        print(f"📱 Chats com mensagens: {chats_com_mensagens.count()}")
        
        for chat in chats_com_mensagens[:5]:
            print(f"   📱 {chat.chat_id} - {chat.chat_name} - {chat.msg_count} mensagens")
            
            # Verificar tipos de mensagens
            tipos = chat.mensagens.values('tipo').annotate(count=Count('tipo'))
            tipos_str = ", ".join([f"{t['tipo']}: {t['count']}" for t in tipos])
            print(f"      Tipos: {tipos_str}")
            
            # Verificar mensagens enviadas vs recebidas
            enviadas = chat.mensagens.filter(from_me=True).count()
            recebidas = chat.mensagens.filter(from_me=False).count()
            print(f"      Enviadas: {enviadas}, Recebidas: {recebidas}")
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("🧪 MultiChat System - Teste da API de Mensagens")
        print("=" * 60)
        
        if not self.user:
            print("❌ Não foi possível configurar usuário para teste")
            return
        
        self.test_mensagens_por_chat()
        self.test_serializer_mensagens()
        self.test_webhook_messages()
        self.test_chat_relationships()
        
        print("\n" + "=" * 60)
        print("🏁 Teste concluído!")

def main():
    """Função principal"""
    tester = MensagensAPITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 