#!/usr/bin/env python3
"""
Script para migrar webhooks salvos para criação de chats
MultiChat System - Migração de Webhooks para Chats

Este script:
1. Analisa webhooks salvos no banco
2. Cria chats correspondentes no modelo core.Chat
3. Cria mensagens no modelo core.Mensagem
4. Corrige problemas de compatibilidade entre modelos
"""

import os
import sys
import json
from datetime import datetime
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
import django
django.setup()

from webhook.models import WebhookEvent, Chat as WebhookChat, Sender as WebhookSender, Message as WebhookMessage
from core.models import Chat as CoreChat, Mensagem as CoreMensagem, Cliente
from django.db import transaction

class WebhookMigrator:
    """Migrador de webhooks para chats"""
    
    def __init__(self):
        self.stats = {
            'webhooks_processed': 0,
            'chats_created': 0,
            'messages_created': 0,
            'errors': 0
        }
    
    def analyze_webhook_data(self, webhook_event):
        """Analisa dados do webhook para extrair informações do chat"""
        try:
            raw_data = webhook_event.raw_data
            
            # Extrair informações básicas
            chat_id = raw_data.get('chat', {}).get('id')
            sender_id = raw_data.get('sender', {}).get('id')
            sender_name = raw_data.get('sender', {}).get('pushName', 'Desconhecido')
            message_id = raw_data.get('messageId')
            from_me = raw_data.get('fromMe', False)
            
            # Extrair conteúdo da mensagem
            msg_content = raw_data.get('msgContent', {})
            text_content = self.extract_text_content(msg_content)
            
            # Extrair foto de perfil
            profile_picture = raw_data.get('chat', {}).get('profilePicture') or raw_data.get('sender', {}).get('profilePicture')
            
            # Verificar se é grupo
            is_group = raw_data.get('isGroup', False)
            
            return {
                'chat_id': chat_id,
                'sender_id': sender_id,
                'sender_name': sender_name,
                'message_id': message_id,
                'text_content': text_content,
                'from_me': from_me,
                'profile_picture': profile_picture,
                'is_group': is_group,
                'timestamp': webhook_event.timestamp,
                'cliente': webhook_event.cliente
            }
        except Exception as e:
            print(f"❌ Erro ao analisar webhook {webhook_event.event_id}: {e}")
            return None
    
    def extract_text_content(self, msg_content):
        """Extrai texto da mensagem de diferentes formatos"""
        if isinstance(msg_content, dict):
            # Conversa simples
            if 'conversation' in msg_content:
                return msg_content['conversation']
            
            # Texto estendido
            if 'extendedTextMessage' in msg_content:
                return msg_content['extendedTextMessage'].get('text', '')
            
            # Outros tipos de mensagem
            for key, value in msg_content.items():
                if isinstance(value, dict) and 'text' in value:
                    return value['text']
        
        return str(msg_content) if msg_content else ''
    
    def create_or_update_core_chat(self, chat_data):
        """Cria ou atualiza chat no modelo core.Chat"""
        try:
            chat_id = chat_data['chat_id']
            cliente = chat_data['cliente']
            
            if not chat_id:
                print(f"⚠️ Chat ID vazio, pulando...")
                return None
            
            # Buscar chat existente
            chat = CoreChat.objects.filter(chat_id=chat_id, cliente=cliente).first()
            
            if chat:
                # Atualizar chat existente
                chat.chat_name = chat_data['sender_name']
                chat.last_message_at = chat_data['timestamp']
                if chat_data['profile_picture']:
                    chat.foto_perfil = chat_data['profile_picture']
                chat.save()
                print(f"✅ Chat atualizado: {chat_id} - {chat_data['sender_name']}")
                return chat
            else:
                # Criar novo chat
                chat = CoreChat.objects.create(
                    chat_id=chat_id,
                    cliente=cliente,
                    chat_name=chat_data['sender_name'],
                    is_group=chat_data['is_group'],
                    canal='whatsapp',
                    status='ativo',
                    last_message_at=chat_data['timestamp'],
                    foto_perfil=chat_data['profile_picture']
                )
                print(f"✅ Chat criado: {chat_id} - {chat_data['sender_name']}")
                self.stats['chats_created'] += 1
                return chat
                
        except Exception as e:
            print(f"❌ Erro ao criar/atualizar chat {chat_data['chat_id']}: {e}")
            self.stats['errors'] += 1
            return None
    
    def create_core_message(self, chat_data, core_chat):
        """Cria mensagem no modelo core.Mensagem"""
        try:
            message_id = chat_data['message_id']
            
            if not message_id:
                print(f"⚠️ Message ID vazio, pulando...")
                return None
            
            # Verificar se mensagem já existe
            if CoreMensagem.objects.filter(message_id=message_id).exists():
                print(f"⚠️ Mensagem já existe: {message_id}")
                return None
            
            # Criar mensagem
            message = CoreMensagem.objects.create(
                chat=core_chat,
                remetente=chat_data['sender_name'],
                conteudo=chat_data['text_content'],
                tipo='texto',
                lida=False,
                from_me=chat_data['from_me'],
                message_id=message_id,
                data_envio=chat_data['timestamp']
            )
            
            print(f"✅ Mensagem criada: {message_id} - {chat_data['text_content'][:50]}...")
            self.stats['messages_created'] += 1
            return message
            
        except Exception as e:
            print(f"❌ Erro ao criar mensagem {chat_data['message_id']}: {e}")
            self.stats['errors'] += 1
            return None
    
    def migrate_webhook_events(self, limit=None):
        """Migra eventos de webhook para chats e mensagens"""
        print("🚀 Iniciando migração de webhooks para chats...")
        print("=" * 60)
        
        # Buscar webhooks não processados
        webhook_events = WebhookEvent.objects.filter(
            processed=True,
            event_type__in=['unknown', 'message', 'webhookDelivery', 'webhookReceived']
        ).order_by('timestamp')
        
        if limit:
            webhook_events = webhook_events[:limit]
        
        total_events = webhook_events.count()
        print(f"📊 Total de webhooks para processar: {total_events}")
        
        for i, webhook_event in enumerate(webhook_events, 1):
            print(f"\n📝 Processando webhook {i}/{total_events}: {webhook_event.event_id}")
            
            try:
                # Analisar dados do webhook
                chat_data = self.analyze_webhook_data(webhook_event)
                if not chat_data:
                    continue
                
                # Criar/atualizar chat no core
                core_chat = self.create_or_update_core_chat(chat_data)
                if not core_chat:
                    continue
                
                # Criar mensagem no core
                if chat_data['text_content']:
                    self.create_core_message(chat_data, core_chat)
                
                self.stats['webhooks_processed'] += 1
                
            except Exception as e:
                print(f"❌ Erro ao processar webhook {webhook_event.event_id}: {e}")
                self.stats['errors'] += 1
        
        self.print_stats()
    
    def print_stats(self):
        """Imprime estatísticas da migração"""
        print("\n" + "=" * 60)
        print("📊 ESTATÍSTICAS DA MIGRAÇÃO")
        print("=" * 60)
        print(f"✅ Webhooks processados: {self.stats['webhooks_processed']}")
        print(f"✅ Chats criados: {self.stats['chats_created']}")
        print(f"✅ Mensagens criadas: {self.stats['messages_created']}")
        print(f"❌ Erros: {self.stats['errors']}")
        print("=" * 60)
    
    def fix_webhook_processor_compatibility(self):
        """Corrige problemas de compatibilidade no processador de webhooks"""
        print("\n🔧 Corrigindo compatibilidade do processador de webhooks...")
        
        # Verificar se há webhooks não processados
        unprocessed_events = WebhookEvent.objects.filter(processed=False).count()
        print(f"📊 Webhooks não processados: {unprocessed_events}")
        
        if unprocessed_events > 0:
            print("⚠️ Há webhooks não processados. Execute a migração primeiro.")
        else:
            print("✅ Todos os webhooks foram processados.")
    
    def cleanup_duplicate_webhook_data(self):
        """Remove dados duplicados de webhooks"""
        print("\n🧹 Limpando dados duplicados...")
        
        # Contar webhooks duplicados por message_id
        from django.db.models import Count
        duplicates = WebhookEvent.objects.values('message_id').annotate(
            count=Count('message_id')
        ).filter(count__gt=1, message_id__isnull=False)
        
        print(f"📊 Webhooks duplicados encontrados: {duplicates.count()}")
        
        for duplicate in duplicates:
            message_id = duplicate['message_id']
            events = WebhookEvent.objects.filter(message_id=message_id).order_by('timestamp')
            
            # Manter apenas o primeiro evento
            first_event = events.first()
            events.exclude(pk=first_event.pk).delete()
            
            print(f"✅ Removidos {duplicate['count'] - 1} duplicados para message_id: {message_id}")

def main():
    """Função principal"""
    print("🔧 MultiChat System - Migrador de Webhooks para Chats")
    print("=" * 60)
    
    migrator = WebhookMigrator()
    
    # Verificar argumentos
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'migrate':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else None
            migrator.migrate_webhook_events(limit)
        elif command == 'fix':
            migrator.fix_webhook_processor_compatibility()
        elif command == 'cleanup':
            migrator.cleanup_duplicate_webhook_data()
        elif command == 'all':
            migrator.cleanup_duplicate_webhook_data()
            migrator.migrate_webhook_events()
            migrator.fix_webhook_processor_compatibility()
        else:
            print("❌ Comando inválido. Use: migrate, fix, cleanup ou all")
    else:
        # Execução padrão
        print("📋 Executando migração completa...")
        migrator.cleanup_duplicate_webhook_data()
        migrator.migrate_webhook_events()
        migrator.fix_webhook_processor_compatibility()

if __name__ == "__main__":
    main() 