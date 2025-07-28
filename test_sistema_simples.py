#!/usr/bin/env python3
"""
Script simples para testar o sistema de tempo real sem piscamento
"""

import requests
import json
import time
from datetime import datetime

# Configurações
WEBHOOK_URL = "http://localhost:8000/webhook/receiver/"
FRONTEND_URL = "http://localhost:3000"

def send_simple_webhook(chat_id, message_text, from_me=False):
    """
    Envia um webhook simples para testar o sistema
    """
    webhook_data = {
        "instanceId": "test_instance_123",
        "event": "message",
        "messageId": f"test_msg_{int(time.time())}",
        "fromMe": from_me,
        "isGroup": False,
        "chat": {
            "id": chat_id,
            "name": "Test Contact"
        },
        "sender": {
            "id": "5511999999999@s.whatsapp.net" if not from_me else "5511888888888@s.whatsapp.net",
            "pushName": "Test User" if not from_me else "Elizeu Batiliere",
            "name": "Test User" if not from_me else "Elizeu Batiliere"
        },
        "msgContent": {
            "conversation": message_text
        },
        "messageTimestamp": int(time.time()),
        "moment": int(time.time())
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Webhook enviado: {message_text}")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_sistema_simples():
    """
    Teste simples do sistema
    """
    print("🧪 Teste simples do sistema de tempo real")
    print("📡 Webhook URL:", WEBHOOK_URL)
    print("🌐 Frontend URL:", FRONTEND_URL)
    print()
    
    chat_id = "5511999999999@s.whatsapp.net"
    
    print("📝 Enviando mensagens de teste...")
    print("🎯 Verifique se a lista de chats é atualizada sem piscamento!")
    print()
    
    # Mensagens de teste
    mensagens = [
        "Olá! Como você está?",
        "Tudo bem, obrigado!",
        "Você pode me ajudar?",
        "Claro! Estou aqui para ajudar.",
        "Muito obrigado!",
        "De nada! Fico feliz em ajudar."
    ]
    
    for i, mensagem in enumerate(mensagens, 1):
        from_me = i % 2 == 0  # Alternar entre enviado e recebido
        
        print(f"📨 Mensagem {i}/{len(mensagens)}: {'[ENVIADA]' if from_me else '[RECEBIDA]'} {mensagem}")
        
        success = send_simple_webhook(chat_id, mensagem, from_me)
        
        if success:
            print(f"   ✅ Enviada com sucesso")
            print(f"   ⏳ Aguarde 3 segundos para ver a atualização...")
        else:
            print(f"   ❌ Falha no envio")
        
        # Aguardar 3 segundos entre mensagens
        time.sleep(3)
        print()
    
    print("🎉 Teste concluído!")
    print("📋 Verifique no frontend:")
    print("   ✅ Se as mensagens apareceram automaticamente")
    print("   ✅ Se a lista de chats foi atualizada")
    print("   ✅ Se não houve piscamento na interface")
    print("   ✅ Se o indicador 'Auto' está ativo")
    print()
    print("🌐 Acesse: http://localhost:3000/chats")

if __name__ == "__main__":
    test_sistema_simples() 