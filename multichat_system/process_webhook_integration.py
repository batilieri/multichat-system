#!/usr/bin/env python3
"""
Script para integrar webhooks do WhatsApp com o sistema MultiChat
Processa webhooks existentes e conecta mensagens aos chats
"""

import os
import sys
import django
import json
import logging
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem, Cliente, WhatsappInstance
from webhook.models import WebhookEvent
from webhook.views import process_whatsapp_message, save_message_to_chat, find_or_create_chat

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_existing_chats():
    """Analisa os chats existentes no sistema"""
    print("=== ANÁLISE DOS CHATS EXISTENTES ===")
    
    chats = Chat.objects.all()
    print(f"Total de chats: {chats.count()}")
    
    for chat in chats:
        mensagens = Mensagem.objects.filter(chat=chat)
        print(f"Chat {chat.id}: {chat.chat_id}")
        print(f"  - Cliente: {chat.cliente.nome}")
        print(f"  - Status: {chat.status}")
        print(f"  - Mensagens: {mensagens.count()}")
        print(f"  - Última mensagem: {chat.last_message_at}")
        print("---")


def analyze_webhook_events():
    """Analisa os eventos de webhook existentes"""
    print("\n=== ANÁLISE DOS WEBHOOKS EXISTENTES ===")
    
    events = WebhookEvent.objects.all()
    print(f"Total de eventos: {events.count()}")
    
    # Agrupar por tipo
    event_types = {}
    for event in events:
        event_type = event.event_type
        if event_type not in event_types:
            event_types[event_type] = 0
        event_types[event_type] += 1
    
    print("Tipos de eventos:")
    for event_type, count in event_types.items():
        print(f"  - {event_type}: {count}")
    
    # Mostrar alguns eventos não processados
    unprocessed = WebhookEvent.objects.filter(processed=False)[:5]
    print(f"\nEventos não processados (primeiros 5):")
    for event in unprocessed:
        print(f"  - {event.event_id}: {event.event_type} - {event.received_at}")


def create_sample_webhook_data():
    """Cria dados de exemplo de webhook para teste"""
    sample_webhook = {
        "event": "messages.upsert",
        "instanceId": "test_instance",
        "data": {
            "messages": [
                {
                    "key": {
                        "id": "test_message_1",
                        "remoteJid": "5511999999999@s.whatsapp.net",
                        "fromMe": False
                    },
                    "message": {
                        "conversation": "Olá! Preciso de ajuda com meu pedido."
                    },
                    "messageTimestamp": int(datetime.now().timestamp()),
                    "pushName": "João Silva"
                },
                {
                    "key": {
                        "id": "test_message_2",
                        "remoteJid": "5511888888888@s.whatsapp.net",
                        "fromMe": True
                    },
                    "message": {
                        "conversation": "Obrigado pelo contato! Como posso ajudar?"
                    },
                    "messageTimestamp": int(datetime.now().timestamp()),
                    "pushName": "Atendente"
                }
            ]
        }
    }
    
    return sample_webhook


def test_webhook_processing():
    """Testa o processamento de webhooks"""
    print("\n=== TESTE DE PROCESSAMENTO DE WEBHOOK ===")
    
    # Criar dados de teste
    sample_webhook = create_sample_webhook_data()
    
    # Buscar primeiro cliente
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado")
        return
    
    # Criar evento de webhook
    event = WebhookEvent.objects.create(
        cliente=cliente,
        instance_id="test_instance",
        event_type="messages.upsert",
        raw_data=sample_webhook,
        processed=False
    )
    
    print(f"Evento de teste criado: {event.event_id}")
    
    # Processar webhook
    success = process_whatsapp_message(sample_webhook, event)
    
    if success:
        print("✅ Webhook processado com sucesso!")
        event.processed = True
        event.save()
        
        # Verificar mensagens criadas
        mensagens = Mensagem.objects.all()
        print(f"Total de mensagens no sistema: {mensagens.count()}")
        
        for msg in mensagens:
            print(f"  - {msg.remetente}: {msg.conteudo} ({msg.tipo})")
    else:
        print("❌ Falha ao processar webhook")


def connect_existing_webhooks():
    """Conecta webhooks existentes aos chats"""
    print("\n=== CONECTANDO WEBHOOKS EXISTENTES ===")
    
    # Buscar eventos não processados
    unprocessed_events = WebhookEvent.objects.filter(processed=False)
    print(f"Eventos não processados encontrados: {unprocessed_events.count()}")
    
    processed_count = 0
    
    for event in unprocessed_events:
        try:
            payload = event.raw_data
            
            # Verificar se é evento de mensagem
            if payload.get('event') == 'messages.upsert':
                success = process_whatsapp_message(payload, event)
                if success:
                    event.processed = True
                    event.save()
                    processed_count += 1
                    print(f"✅ Evento {event.event_id} processado")
                else:
                    print(f"⚠️ Falha ao processar evento {event.event_id}")
            else:
                print(f"⏭️ Evento {event.event_id} não é de mensagem: {payload.get('event')}")
                
        except Exception as e:
            print(f"❌ Erro ao processar evento {event.event_id}: {e}")
    
    print(f"\nTotal de eventos processados: {processed_count}")


def create_test_chat_with_messages():
    """Cria um chat de teste com mensagens"""
    print("\n=== CRIANDO CHAT DE TESTE COM MENSAGENS ===")
    
    # Buscar primeiro cliente
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado")
        return
    
    # Criar chat de teste
    chat = Chat.objects.create(
        chat_id="test_chat_123@s.whatsapp.net",
        cliente=cliente,
        status='active',
        canal='whatsapp'
    )
    
    print(f"Chat de teste criado: {chat.chat_id}")
    
    # Criar algumas mensagens de teste
    mensagens_teste = [
        {
            'remetente': 'Cliente Teste',
            'conteudo': 'Olá! Preciso de ajuda.',
            'tipo': 'text',
            'from_me': False
        },
        {
            'remetente': 'Eu',
            'conteudo': 'Olá! Como posso ajudar você?',
            'tipo': 'text',
            'from_me': True
        },
        {
            'remetente': 'Cliente Teste',
            'conteudo': '[Imagem] - Foto do produto',
            'tipo': 'image',
            'from_me': False
        }
    ]
    
    for i, msg_data in enumerate(mensagens_teste):
        mensagem = Mensagem.objects.create(
            chat=chat,
            remetente=msg_data['remetente'],
            conteudo=msg_data['conteudo'],
            tipo=msg_data['tipo'],
            lida=False
        )
        print(f"  - Mensagem {i+1} criada: {msg_data['remetente']}: {msg_data['conteudo']}")
    
    # Atualizar última mensagem
    chat.last_message_at = datetime.now()
    chat.save()
    
    print(f"✅ Chat de teste criado com {len(mensagens_teste)} mensagens")


def show_final_status():
    """Mostra status final do sistema"""
    print("\n=== STATUS FINAL DO SISTEMA ===")
    
    total_chats = Chat.objects.count()
    total_mensagens = Mensagem.objects.count()
    total_webhooks = WebhookEvent.objects.count()
    processed_webhooks = WebhookEvent.objects.filter(processed=True).count()
    
    print(f"Total de chats: {total_chats}")
    print(f"Total de mensagens: {total_mensagens}")
    print(f"Total de webhooks: {total_webhooks}")
    print(f"Webhooks processados: {processed_webhooks}")
    print(f"Webhooks pendentes: {total_webhooks - processed_webhooks}")


def main():
    """Função principal"""
    print("🔗 INTEGRAÇÃO DE WEBHOOKS COM SISTEMA MULTICHAT")
    print("=" * 60)
    
    # Análise inicial
    analyze_existing_chats()
    analyze_webhook_events()
    
    # Testes
    test_webhook_processing()
    create_test_chat_with_messages()
    
    # Conectar webhooks existentes
    connect_existing_webhooks()
    
    # Status final
    show_final_status()
    
    print("\n" + "=" * 60)
    print("✅ Integração concluída!")
    print("\nPróximos passos:")
    print("1. Configure o endpoint de webhook no W-API: http://localhost:8000/webhook/whatsapp/")
    print("2. Teste enviando mensagens via WhatsApp")
    print("3. Verifique se as mensagens aparecem no frontend")


if __name__ == "__main__":
    main() 