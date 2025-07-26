#!/usr/bin/env python3
"""
Script para verificar se o chat foi criado no banco
"""

import os
import sys

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
import django
django.setup()

from webhook.models import Chat as WebhookChat, Message, Sender, WebhookEvent
from core.models import Chat, Mensagem, Cliente


def verificar_chat_criado():
    """Verifica se o chat foi criado no banco"""
    print("🔍 VERIFICANDO CHAT CRIADO")
    print("=" * 50)
    
    # Verificar todos os chats
    chats = WebhookChat.objects.all()
    print(f"📊 Total de chats: {chats.count()}")
    
    for chat in chats:
        print(f"💬 Chat: {chat.chat_id} - {chat.chat_name}")
        print(f"   Cliente: {chat.cliente.nome}")
        print(f"   É grupo: {chat.is_group}")
        print(f"   Status: {chat.status}")
        print(f"   Mensagens: {chat.message_count}")
        print(f"   Criado: {chat.created_at}")
        print(f"   Última mensagem: {chat.last_message_at}")
        print()
    
    # Verificar mensagens
    messages = Message.objects.all()
    print(f"📱 Total de mensagens: {messages.count()}")
    
    for msg in messages:
        print(f"💌 Mensagem: {msg.message_id}")
        print(f"   Chat: {msg.chat.chat_id}")
        print(f"   Sender: {msg.sender.sender_id}")
        print(f"   Tipo: {msg.message_type}")
        print(f"   Texto: {msg.text_content}")
        print(f"   De mim: {msg.from_me}")
        print(f"   Timestamp: {msg.timestamp}")
        print()
    
    # Verificar senders
    senders = Sender.objects.all()
    print(f"👤 Total de senders: {senders.count()}")
    
    for sender in senders:
        print(f"👤 Sender: {sender.sender_id} - {sender.push_name}")
        print(f"   Cliente: {sender.cliente.nome}")
        print(f"   Mensagens: {sender.message_count}")
        print(f"   Última vez: {sender.last_seen}")
        print()


def atualizar_nomes_chats():
    """Atualiza o campo chat_name de todos os chats para o nome do contato (nunca o próprio cliente)"""
    from core.models import Chat, Mensagem
    print("\n🔄 Atualizando nomes dos chats (apenas para o nome do contato)...")
    chats = Chat.objects.filter(is_group=False)
    for chat in chats:
        # Busca a primeira mensagem enviada por alguém que não seja o cliente
        msg_contato = Mensagem.objects.filter(chat=chat).exclude(remetente=chat.cliente.nome).order_by('data_envio').first()
        if msg_contato and msg_contato.remetente:
            if chat.chat_name != msg_contato.remetente:
                print(f"Chat {chat.chat_id}: '{chat.chat_name}' -> '{msg_contato.remetente}'")
                chat.chat_name = msg_contato.remetente
                chat.save()
    print("✅ Atualização concluída!")


if __name__ == '__main__':
    verificar_chat_criado()
    atualizar_nomes_chats()

print("==== CHATS POR CLIENTE E CHAT_ID ====")
for cliente in Cliente.objects.all():
    print(f"\nCliente: {cliente.nome} (id={cliente.id})")
    chat_ids = Chat.objects.filter(cliente=cliente).values_list('chat_id', flat=True).distinct()
    for chat_id in chat_ids:
        chats = Chat.objects.filter(cliente=cliente, chat_id=chat_id)
        print(f"  chat_id={chat_id} | Total de objetos Chat: {chats.count()} | IDs internos: {[c.id for c in chats]}")
        for chat in chats:
            mensagens = Mensagem.objects.filter(chat=chat)
            print(f"    Chat.id={chat.id} | Total de mensagens: {mensagens.count()}")
            for m in mensagens:
                print(f"      Mensagem.id={m.id} | remetente={m.remetente} | conteudo={m.conteudo[:30]} | data={m.data_envio}")

print("\n==== FIM DO DIAGNÓSTICO ====") 