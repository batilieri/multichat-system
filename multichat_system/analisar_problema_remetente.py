#!/usr/bin/env python
"""
Script para analisar o problema dos remetentes incorretos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Cliente
from webhook.models import WebhookEvent

def analisar_problema_remetente():
    """Analisa o problema dos remetentes incorretos"""
    print("🔍 ANALISANDO PROBLEMA DOS REMETENTES")
    print("=" * 60)
    
    # 1. Verificar mensagens com from_me=False mas remetente=Elizeu
    mensagens_incorretas = Mensagem.objects.filter(
        from_me=False, 
        remetente__icontains='Elizeu'
    )
    
    print(f"📊 Mensagens com from_me=False mas remetente=Elizeu: {mensagens_incorretas.count()}")
    
    for msg in mensagens_incorretas:
        print(f"   ID: {msg.id}, MessageID: {msg.message_id}, Remetente: {msg.remetente}, FromMe: {msg.from_me}, Conteúdo: {msg.conteudo[:30]}...")
    
    print()
    
    # 2. Verificar mensagens com from_me=True
    mensagens_enviadas = Mensagem.objects.filter(from_me=True)
    print(f"📤 Mensagens enviadas (from_me=True): {mensagens_enviadas.count()}")
    
    for msg in mensagens_enviadas[:5]:
        print(f"   ID: {msg.id}, MessageID: {msg.message_id}, Remetente: {msg.remetente}, FromMe: {msg.from_me}, Conteúdo: {msg.conteudo[:30]}...")
    
    print()
    
    # 3. Verificar eventos de webhook relacionados
    print("🔗 Eventos de webhook relacionados:")
    for msg in mensagens_incorretas:
        eventos = WebhookEvent.objects.filter(message_id=msg.message_id)
        print(f"   Mensagem {msg.id} (MessageID: {msg.message_id}): {eventos.count()} eventos")
        for evento in eventos:
            print(f"     Evento: {evento.event_id}, Sender: {evento.sender_name}, FromMe: {evento.raw_data.get('fromMe', 'N/A')}")
    
    print()
    
    # 4. Verificar clientes
    clientes = Cliente.objects.all()
    print(f"👤 Clientes cadastrados: {clientes.count()}")
    for cliente in clientes:
        print(f"   ID: {cliente.id}, Nome: {cliente.nome}, Telefone: {cliente.telefone}")
    
    print()
    
    # 5. Verificar mensagens por chat
    chat_id = "556999267344"
    mensagens_chat = Mensagem.objects.filter(chat__chat_id=chat_id).order_by('-data_envio')[:10]
    print(f"💬 Últimas 10 mensagens do chat {chat_id}:")
    
    for msg in mensagens_chat:
        print(f"   ID: {msg.id}, Remetente: {msg.remetente}, FromMe: {msg.from_me}, Conteúdo: {msg.conteudo[:30]}...")

if __name__ == "__main__":
    analisar_problema_remetente() 