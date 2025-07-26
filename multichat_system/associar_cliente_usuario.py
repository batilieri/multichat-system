#!/usr/bin/env python
"""
Script para associar o usuário cliente 'teste@empresa.com' ao cliente 'Elizeu Batiliere Dos Santos' e definir a senha.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from authentication.models import Usuario
from core.models import Chat, Mensagem, Cliente

def associar_usuario_cliente():
    cliente = Cliente.objects.get(id=2)
    Chat.objects.all().update(cliente=cliente)
    print(f"Todos os chats agora pertencem ao cliente: {cliente.nome}")

def associar_mensagens_ao_chat_correto():
    print('Associando mensagens ao chat correto pelo chat_id do WhatsApp...')
    for chat in Chat.objects.all():
        mensagens = Mensagem.objects.filter(chat__chat_id=chat.chat_id)
        mensagens.update(chat=chat)
    print('Mensagens associadas ao chat correto.')

# Executa as funções automaticamente ao rodar o script
associar_usuario_cliente()
associar_mensagens_ao_chat_correto() 