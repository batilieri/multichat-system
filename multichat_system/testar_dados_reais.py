#!/usr/bin/env python3
"""
Script para testar se os dados reais dos chats e mensagens estão sendo carregados corretamente
MultiChat System - Teste de Dados Reais

Este script:
1. Verifica se há chats criados no modelo core.Chat
2. Verifica se há mensagens criadas no modelo core.Mensagem
3. Testa a API de chats e mensagens
4. Compara com os dados mockados
"""

import os
import sys
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
import django
django.setup()

from core.models import Chat as CoreChat, Mensagem as CoreMensagem, Cliente
from webhook.models import WebhookEvent, Chat as WebhookChat, Message as WebhookMessage
from django.db.models import Count
from django.test import RequestFactory
from api.views import ChatViewSet, MensagemViewSet
from rest_framework.test import force_authenticate
from authentication.models import Usuario

class DadosReaisTester:
    """Testador de dados reais"""
    
    def __init__(self):
        self.stats = {
            'core_chats': 0,
            'core_mensagens': 0,
            'webhook_events': 0,
            'webhook_chats': 0,
            'webhook_messages': 0,
            'api_chats': 0,
            'api_mensagens': 0
        }
    
    def test_core_models(self):
        """Testa os modelos core"""
        print("🔍 Testando modelos core...")
        print("=" * 50)
        
        # Testar Chat
        core_chats = CoreChat.objects.all()
        self.stats['core_chats'] = core_chats.count()
        print(f"📱 Chats no modelo core.Chat: {self.stats['core_chats']}")
        
        if self.stats['core_chats'] > 0:
            print("   Primeiros 5 chats:")
            for chat in core_chats[:5]:
                print(f"   - {chat.chat_id} - {chat.chat_name} - Cliente: {chat.cliente.nome if chat.cliente else 'N/A'}")
        
        # Testar Mensagem
        core_mensagens = CoreMensagem.objects.all()
        self.stats['core_mensagens'] = core_mensagens.count()
        print(f"💬 Mensagens no modelo core.Mensagem: {self.stats['core_mensagens']}")
        
        if self.stats['core_mensagens'] > 0:
            print("   Primeiras 5 mensagens:")
            for msg in core_mensagens[:5]:
                print(f"   - {msg.message_id} - {msg.conteudo[:50]}... - Chat: {msg.chat.chat_id if msg.chat else 'N/A'}")
    
    def test_webhook_models(self):
        """Testa os modelos webhook"""
        print("\n🔍 Testando modelos webhook...")
        print("=" * 50)
        
        # Testar WebhookEvent
        webhook_events = WebhookEvent.objects.all()
        self.stats['webhook_events'] = webhook_events.count()
        print(f"📡 WebhookEvents: {self.stats['webhook_events']}")
        
        # Testar Chat do webhook
        webhook_chats = WebhookChat.objects.all()
        self.stats['webhook_chats'] = webhook_chats.count()
        print(f"📱 Chats no modelo webhook.Chat: {self.stats['webhook_chats']}")
        
        # Testar Message do webhook
        webhook_messages = WebhookMessage.objects.all()
        self.stats['webhook_messages'] = webhook_messages.count()
        print(f"💬 Messages no modelo webhook.Message: {self.stats['webhook_messages']}")
    
    def test_api_endpoints(self):
        """Testa os endpoints da API"""
        print("\n🔍 Testando endpoints da API...")
        print("=" * 50)
        
        factory = RequestFactory()
        
        # Buscar um usuário admin
        try:
            user = Usuario.objects.filter(is_superuser=True).first()
            if not user:
                user = Usuario.objects.first()
            
            if user:
                print(f"👤 Usuário de teste: {user.username} ({user.email})")
                
                # Testar ChatViewSet
                request = factory.get('/api/chats/')
                force_authenticate(request, user=user)
                
                viewset = ChatViewSet()
                viewset.request = request
                viewset.action = 'list'
                
                queryset = viewset.get_queryset()
                self.stats['api_chats'] = queryset.count()
                print(f"📱 Chats via API: {self.stats['api_chats']}")
                
                if self.stats['api_chats'] > 0:
                    print("   Primeiros 3 chats via API:")
                    for chat in queryset[:3]:
                        print(f"   - {chat.chat_id} - {chat.chat_name} - Status: {chat.status}")
                
                # Testar MensagemViewSet
                request = factory.get('/api/mensagens/')
                force_authenticate(request, user=user)
                
                viewset = MensagemViewSet()
                viewset.request = request
                viewset.action = 'list'
                
                queryset = viewset.get_queryset()
                self.stats['api_mensagens'] = queryset.count()
                print(f"💬 Mensagens via API: {self.stats['api_mensagens']}")
                
                if self.stats['api_mensagens'] > 0:
                    print("   Primeiras 3 mensagens via API:")
                    for msg in queryset[:3]:
                        print(f"   - {msg.message_id} - {msg.conteudo[:50]}... - FromMe: {msg.from_me}")
            
        except Exception as e:
            print(f"❌ Erro ao testar API: {e}")
    
    def compare_data_sources(self):
        """Compara diferentes fontes de dados"""
        print("\n🔍 Comparando fontes de dados...")
        print("=" * 50)
        
        print("📊 Resumo:")
        print(f"   Core.Chat: {self.stats['core_chats']}")
        print(f"   Core.Mensagem: {self.stats['core_mensagens']}")
        print(f"   Webhook.Chat: {self.stats['webhook_chats']}")
        print(f"   Webhook.Message: {self.stats['webhook_messages']}")
        print(f"   API Chats: {self.stats['api_chats']}")
        print(f"   API Mensagens: {self.stats['api_mensagens']}")
        
        # Verificar se há dados
        if self.stats['core_chats'] == 0:
            print("\n⚠️ AVISO: Nenhum chat encontrado no modelo core.Chat!")
            print("   Isso significa que a migração pode não ter funcionado corretamente.")
        
        if self.stats['core_mensagens'] == 0:
            print("\n⚠️ AVISO: Nenhuma mensagem encontrada no modelo core.Mensagem!")
            print("   Isso significa que a migração pode não ter funcionado corretamente.")
        
        # Verificar se API está funcionando
        if self.stats['api_chats'] != self.stats['core_chats']:
            print(f"\n⚠️ DIFERENÇA: API retorna {self.stats['api_chats']} chats, mas há {self.stats['core_chats']} no modelo!")
        
        if self.stats['api_mensagens'] != self.stats['core_mensagens']:
            print(f"\n⚠️ DIFERENÇA: API retorna {self.stats['api_mensagens']} mensagens, mas há {self.stats['core_mensagens']} no modelo!")
    
    def check_migration_status(self):
        """Verifica o status da migração"""
        print("\n🔍 Verificando status da migração...")
        print("=" * 50)
        
        # Verificar webhooks processados
        webhook_events = WebhookEvent.objects.filter(processed=True)
        processed_count = webhook_events.count()
        total_count = WebhookEvent.objects.count()
        
        print(f"📡 Webhooks processados: {processed_count}/{total_count}")
        
        if processed_count > 0:
            print("   Últimos 3 webhooks processados:")
            for event in webhook_events.order_by('-timestamp')[:3]:
                print(f"   - {event.event_id} - {event.event_type} - {event.timestamp}")
        
        # Verificar se há dados migrados
        if self.stats['core_chats'] > 0 and self.stats['core_mensagens'] > 0:
            print("\n✅ Migração parece ter funcionado!")
            print("   Os dados estão disponíveis nos modelos core.")
        else:
            print("\n❌ Migração pode ter falhado!")
            print("   Não há dados nos modelos core.")
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("🧪 MultiChat System - Teste de Dados Reais")
        print("=" * 60)
        
        self.test_core_models()
        self.test_webhook_models()
        self.test_api_endpoints()
        self.compare_data_sources()
        self.check_migration_status()
        
        print("\n" + "=" * 60)
        print("🏁 Teste concluído!")

def main():
    """Função principal"""
    tester = DadosReaisTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 