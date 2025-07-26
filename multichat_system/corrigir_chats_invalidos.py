#!/usr/bin/env python
"""
Script para corrigir registros inválidos de chats:
- Remove chats com chat_id vazio
- Remove duplicados, mantendo apenas um por chat_id
"""

import os
import django
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from webhook.models import Chat as WebhookChat
from core.models import Chat as CoreChat

def corrigir_chats_invalidos():
    print("=== CORRIGINDO CHATS INVÁLIDOS ===\n")
    # 1. Remover chats com chat_id vazio ou None
    chats_vazios = WebhookChat.objects.filter(chat_id__isnull=True) | WebhookChat.objects.filter(chat_id='')
    count_vazios = chats_vazios.count()
    if count_vazios > 0:
        print(f"Removendo {count_vazios} chats com chat_id vazio...")
        chats_vazios.delete()
    else:
        print("Nenhum chat com chat_id vazio encontrado.")

    # 2. Remover duplicados, mantendo apenas o mais antigo por chat_id
    print("\nVerificando duplicados...")
    chats = WebhookChat.objects.all().order_by('chat_id', 'created_at')
    chat_ids = defaultdict(list)
    for chat in chats:
        chat_ids[chat.chat_id].append(chat)
    removidos = 0
    for chat_id, lista in chat_ids.items():
        if chat_id and len(lista) > 1:
            # Mantém o mais antigo, remove os demais
            for chat in lista[1:]:
                print(f"Removendo chat duplicado: id={chat.id}, chat_id={chat.chat_id}, cliente={chat.cliente.nome}")
                chat.delete()
                removidos += 1
    if removidos == 0:
        print("Nenhum chat duplicado encontrado.")
    else:
        print(f"Total de chats duplicados removidos: {removidos}")
    print("\n=== FIM DA CORREÇÃO ===")

if __name__ == "__main__":
    corrigir_chats_invalidos() 