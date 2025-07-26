#!/usr/bin/env python
"""
Script para verificar a mensagem 499
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem

def verificar_msg_499():
    """Verifica a mensagem 499"""
    try:
        msg = Mensagem.objects.get(id=499)
        print(f"Msg 499:")
        print(f"  Chat ID: {msg.chat.chat_id}")
        print(f"  Cliente: {msg.chat.cliente.nome}")
        print(f"  From_me: {msg.from_me}")
        print(f"  Remetente: '{msg.remetente}'")
        print(f"  Conteúdo: '{msg.conteudo}'")
        print(f"  Tipo: {msg.tipo}")
        print(f"  Data: {msg.data_envio}")
    except Mensagem.DoesNotExist:
        print("Mensagem 499 não encontrada")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    verificar_msg_499() 