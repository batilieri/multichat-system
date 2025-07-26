#!/usr/bin/env python
"""
Script para verificar a mensagem específica que está causando erro na exclusão.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente, WhatsappInstance

def verificar_mensagem_especifica():
    """Verifica a mensagem específica que está causando erro"""
    print("🔍 Verificando mensagem específica...")
    
    # Verificar se a mensagem existe
    try:
        mensagem = Mensagem.objects.get(id=1753569108972)
        print(f"✅ Mensagem encontrada:")
        print(f"   - ID: {mensagem.id}")
        print(f"   - message_id: {mensagem.message_id}")
        print(f"   - from_me: {mensagem.from_me}")
        print(f"   - chat_id: {mensagem.chat.chat_id}")
        print(f"   - cliente: {mensagem.chat.cliente.nome}")
        print(f"   - conteúdo: {mensagem.conteudo[:100]}...")
        
        # Verificar se tem instância WhatsApp
        try:
            instancia = WhatsappInstance.objects.get(cliente=mensagem.chat.cliente)
            print(f"   - instância: {instancia.instance_id}")
            print(f"   - token: {instancia.token[:20]}..." if instancia.token else "   - token: None")
        except WhatsappInstance.DoesNotExist:
            print("   ❌ Instância WhatsApp não encontrada")
            
    except Mensagem.DoesNotExist:
        print("❌ Mensagem não encontrada no banco de dados")
        
        # Verificar mensagens próximas
        mensagens_proximas = Mensagem.objects.filter(
            id__gte=1753569108970,
            id__lte=1753569108980
        )
        print(f"📊 Mensagens próximas encontradas: {mensagens_proximas.count()}")
        
        for msg in mensagens_proximas:
            print(f"   - ID: {msg.id}, message_id: {msg.message_id}, from_me: {msg.from_me}")

if __name__ == "__main__":
    verificar_mensagem_especifica() 