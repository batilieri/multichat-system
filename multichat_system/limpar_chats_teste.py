#!/usr/bin/env python3
"""
Script para limpar chats existentes e testar criação
"""

import os
import sys

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
import django
django.setup()

from webhook.models import Chat, Message, Sender, WebhookEvent
from core.models import Cliente


def limpar_chats_teste():
    """Limpa chats de teste e testa criação"""
    print("🧹 LIMPANDO CHATS DE TESTE")
    print("=" * 50)
    
    # Contar antes
    total_chats = Chat.objects.count()
    total_messages = Message.objects.count()
    total_senders = Sender.objects.count()
    total_events = WebhookEvent.objects.count()
    
    print(f"📊 ANTES da limpeza:")
    print(f"   Chats: {total_chats}")
    print(f"   Mensagens: {total_messages}")
    print(f"   Senders: {total_senders}")
    print(f"   Events: {total_events}")
    
    # Deletar chats que começam com 556993291093
    chats_deletados = Chat.objects.filter(chat_id__startswith='556993291093').delete()
    print(f"🗑️ Chats deletados: {chats_deletados}")
    
    # Deletar todos os chats (para teste limpo)
    todos_chats = Chat.objects.all().delete()
    print(f"🗑️ Todos os chats deletados: {todos_chats}")
    
    # Contar depois
    total_chats_depois = Chat.objects.count()
    print(f"📊 DEPOIS da limpeza:")
    print(f"   Chats: {total_chats_depois}")
    
    print("✅ Limpeza concluída!")
    print("\n💡 Agora você pode testar novamente o webhook")


if __name__ == '__main__':
    limpar_chats_teste() 