#!/usr/bin/env python3
"""
Script para analisar dados de webhook e entender a estrutura
"""

import os
import sys
import json
from datetime import datetime

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
import django
django.setup()

from webhook.models import WebhookEvent, Chat as WebhookChat, Sender, Message
from core.models import Cliente


def analisar_webhooks_recentes():
    """Analisa os webhooks mais recentes"""
    print("🔍 ANALISANDO WEBHOOKS RECENTES")
    print("=" * 60)
    
    # Buscar eventos recentes
    eventos = WebhookEvent.objects.all().order_by('-timestamp')[:10]
    
    if not eventos:
        print("❌ Nenhum evento de webhook encontrado")
        return
    
    print(f"📊 Total de eventos encontrados: {eventos.count()}")
    print()
    
    for i, evento in enumerate(eventos, 1):
        print(f"📋 EVENTO {i} - {evento.timestamp}")
        print("-" * 40)
        print(f"ID: {evento.event_id}")
        print(f"Cliente: {evento.cliente.nome}")
        print(f"Tipo: {evento.event_type}")
        print(f"Instance ID: {evento.instance_id}")
        print(f"Processado: {evento.processed}")
        if evento.error_message:
            print(f"❌ Erro: {evento.error_message}")
        else:
            print(f"✅ Sem erros")
        # Analisar dados brutos
        print("\n📄 DADOS BRUTOS:")
        dados = evento.raw_data
        # Mostrar se tem campos para fallback
        if 'sender' in dados and 'msgContent' in dados:
            print("⚡️ Fallback sender/msgContent: ATIVADO")
            print(f"  sender.id: {dados['sender'].get('id')}")
            print(f"  sender.pushName: {dados['sender'].get('pushName')}")
            print(f"  msgContent: {json.dumps(dados['msgContent'], ensure_ascii=False)}")
        else:
            print("⚠️  Fallback NÃO acionado neste evento")
        # Verificar se o chat correspondente existe
        chat_id = None
        if 'sender' in dados:
            sender_id = dados['sender'].get('id', None)
            if sender_id:
                # Remover @s.whatsapp.net para ficar igual ao novo processor
                chat_id_simple = sender_id.replace('@s.whatsapp.net', '').replace('@c.us', '')
                from webhook.models import Chat
                chat = WebhookChat.objects.filter(chat_id=chat_id_simple).first()
                if chat:
                    print(f"✅ Chat criado: {chat.chat_id} | Nome: {chat.chat_name}")
                else:
                    print(f"❌ Chat NÃO criado para chat_id: {chat_id_simple}")
                    
                # Verificar também se existe com o formato antigo (para compatibilidade)
                chat_old = WebhookChat.objects.filter(chat_id=sender_id).first()
                if chat_old:
                    print(f"⚠️ Chat encontrado com formato antigo: {chat_old.chat_id}")
        print("\n" + "=" * 60)


def analisar_chats_criados():
    """Analisa os chats criados a partir dos webhooks"""
    print("\n💬 ANALISANDO CHATS CRIADOS")
    print("=" * 60)
    
    chats = WebhookChat.objects.all().order_by('-created_at')
    
    if not chats:
        print("❌ Nenhum chat encontrado")
        return
    
    print(f"📊 Total de chats: {chats.count()}")
    print()
    
    for chat in chats:
        print(f"💬 CHAT: {chat.chat_name or chat.chat_id}")
        print(f"   ID: {chat.chat_id}")
        print(f"   Cliente: {chat.cliente.nome}")
        print(f"   É grupo: {chat.is_group}")
        print(f"   Status: {chat.status}")
        print(f"   Mensagens: {chat.message_count}")
        print(f"   Última mensagem: {chat.last_message_at}")
        print(f"   Criado: {chat.created_at}")
        print()


def analisar_mensagens():
    """Analisa as mensagens processadas"""
    print("\n📱 ANALISANDO MENSAGENS")
    print("=" * 60)
    
    mensagens = Message.objects.all().order_by('-timestamp')[:20]
    
    if not mensagens:
        print("❌ Nenhuma mensagem encontrada")
        return
    
    print(f"📊 Total de mensagens: {Message.objects.count()}")
    print(f"📋 Últimas {mensagens.count()} mensagens:")
    print()
    
    for msg in mensagens:
        print(f"📱 {msg.timestamp.strftime('%H:%M:%S')} - {msg.chat.chat_name}")
        print(f"   De: {msg.sender.push_name or msg.sender.sender_id}")
        print(f"   Tipo: {msg.message_type}")
        print(f"   Texto: {msg.text_content[:100] if msg.text_content else 'N/A'}...")
        print(f"   De mim: {msg.from_me}")
        print()


def analisar_estrutura_dados():
    """Analisa a estrutura dos dados de webhook"""
    print("\n🔧 ANALISANDO ESTRUTURA DOS DADOS")
    print("=" * 60)
    
    # Buscar um evento com dados completos
    evento = WebhookEvent.objects.filter(processed=True).first()
    
    if not evento:
        print("❌ Nenhum evento processado encontrado")
        return
    
    dados = evento.raw_data
    print(f"📄 Estrutura dos dados do evento {evento.event_id}:")
    print(json.dumps(dados, indent=2, ensure_ascii=False))
    
    # Verificar campos específicos
    print("\n🎯 CAMPOS ESPECÍFICOS:")
    
    if 'key' in dados:
        key_data = dados['key']
        print(f"  key.remoteJid: {key_data.get('remoteJid', 'N/A')}")
        print(f"  key.participant: {key_data.get('participant', 'N/A')}")
        print(f"  key.fromMe: {key_data.get('fromMe', 'N/A')}")
        print(f"  key.id: {key_data.get('id', 'N/A')}")
    
    if 'message' in dados:
        message_data = dados['message']
        print(f"  message: {list(message_data.keys()) if isinstance(message_data, dict) else 'N/A'}")
    
    if 'msgContent' in dados:
        msg_content = dados['msgContent']
        print(f"  msgContent: {list(msg_content.keys()) if isinstance(msg_content, dict) else 'N/A'}")


def main():
    """Função principal"""
    print("🚀 ANÁLISE DE WEBHOOKS - MULTICHAT SYSTEM")
    print("=" * 60)
    
    # Verificar se há clientes
    clientes = Cliente.objects.all()
    print(f"👥 Clientes cadastrados: {clientes.count()}")
    for cliente in clientes:
        print(f"   - {cliente.nome} (ID: {cliente.id})")
    
    print()
    
    # Executar análises
    analisar_webhooks_recentes()
    analisar_chats_criados()
    analisar_mensagens()
    analisar_estrutura_dados()
    
    print("\n✅ Análise concluída!")


if __name__ == '__main__':
    main() 