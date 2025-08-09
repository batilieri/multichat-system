#!/usr/bin/env python3
"""
🔍 DEBUG WEBHOOK COMPLETO
Mostra o conteúdo completo de um webhook para identificar onde está o chat_id
"""

import os
import sys
import django
import json
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

def mostrar_webhook_completo():
    """Mostra o conteúdo completo de um webhook recente"""
    print("🔍 CONTEÚDO COMPLETO DO WEBHOOK")
    print("=" * 80)
    
    from webhook.models import WebhookEvent
    
    # Buscar último webhook com áudio
    ultimo_webhook = None
    
    for webhook in WebhookEvent.objects.all().order_by('-timestamp')[:10]:
        try:
            data = webhook.raw_data
            msg_content = data.get('msgContent', {})
            
            if 'audioMessage' in msg_content:
                ultimo_webhook = webhook
                break
        except:
            continue
    
    if not ultimo_webhook:
        print("❌ Nenhum webhook com áudio encontrado")
        return
    
    print(f"🎵 Webhook encontrado: {ultimo_webhook.timestamp}")
    print("=" * 80)
    
    # Mostrar JSON completo formatado
    data = ultimo_webhook.raw_data
    print("📋 CONTEÚDO COMPLETO DO WEBHOOK:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print()
    
    # Análise de campos relacionados a chat
    print("🔍 ANÁLISE DE CAMPOS RELACIONADOS A CHAT:")
    print("=" * 80)
    
    campos_chat = [
        'chatId', 'chat', 'sender', 'fromMe', 'to', 'from', 
        'remote', 'key', 'participant', 'author'
    ]
    
    for campo in campos_chat:
        valor = data.get(campo)
        if valor is not None:
            print(f"✅ {campo}: {json.dumps(valor, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ {campo}: não presente")
    
    print()
    
    # Tentar extrair chat_id de diferentes fontes
    print("🎯 TENTATIVAS DE EXTRAIR CHAT_ID:")
    print("=" * 80)
    
    # Opção 1: chatId direto
    chat_id_1 = data.get('chatId')
    print(f"1. data.get('chatId'): {chat_id_1}")
    
    # Opção 2: chat.id
    chat_id_2 = data.get('chat', {}).get('id') if isinstance(data.get('chat'), dict) else None
    print(f"2. data.get('chat', {{}}).get('id'): {chat_id_2}")
    
    # Opção 3: sender.id
    chat_id_3 = data.get('sender', {}).get('id') if isinstance(data.get('sender'), dict) else None
    print(f"3. data.get('sender', {{}}).get('id'): {chat_id_3}")
    
    # Opção 4: key.remoteJid
    chat_id_4 = data.get('key', {}).get('remoteJid') if isinstance(data.get('key'), dict) else None
    print(f"4. data.get('key', {{}}).get('remoteJid'): {chat_id_4}")
    
    # Opção 5: to
    chat_id_5 = data.get('to')
    print(f"5. data.get('to'): {chat_id_5}")
    
    # Opção 6: from
    chat_id_6 = data.get('from')
    print(f"6. data.get('from'): {chat_id_6}")
    
    print()
    print("🎯 MELHOR OPÇÃO:")
    melhor_opcao = chat_id_4 or chat_id_1 or chat_id_2 or chat_id_3 or chat_id_5 or chat_id_6
    print(f"   {melhor_opcao}")

def main():
    """Função principal"""
    print("🔍 DEBUG WEBHOOK COMPLETO")
    print("=" * 100)
    print("OBJETIVO: Encontrar onde está o chat_id nos webhooks")
    print("=" * 100)
    
    mostrar_webhook_completo()

if __name__ == "__main__":
    main() 