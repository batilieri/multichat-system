#!/usr/bin/env python3
"""
Script para testar webhooks reais do WhatsApp
"""

import requests
import json
import time
from datetime import datetime

# Configurações
WEBHOOK_URL = "http://localhost:8000/webhook/receiver/"
FRONTEND_URL = "http://localhost:3000"

def send_real_webhook(chat_id, message_text, from_me=False, message_type="text"):
    """
    Envia um webhook que simula o formato real do WhatsApp
    """
    # Gerar message_id único
    message_id = f"test_msg_{int(time.time())}_{chat_id.replace('@', '_')}"
    
    # Estrutura real do webhook do WhatsApp
    webhook_data = {
        "instanceId": "test_instance_123",
        "event": "messages.upsert",
        "data": {
            "messages": [
                {
                    "key": {
                        "remoteJid": chat_id,
                        "fromMe": from_me,
                        "id": message_id
                    },
                    "message": {
                        "conversation": message_text
                    },
                    "messageTimestamp": int(time.time()),
                    "status": "PENDING"
                }
            ]
        },
        "chat": {
            "id": chat_id,
            "name": "Test Contact"
        },
        "sender": {
            "id": chat_id,
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
            print(f"✅ Webhook real enviado: {message_text}")
            return True
        else:
            print(f"❌ Erro ao enviar webhook: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_real_webhooks():
    """
    Testa webhooks no formato real do WhatsApp
    """
    print("🧪 Testando webhooks reais do WhatsApp")
    print("📡 Webhook URL:", WEBHOOK_URL)
    print("🌐 Frontend URL:", FRONTEND_URL)
    print()
    
    chat_id = "5511999999999@s.whatsapp.net"
    
    print("📝 Enviando mensagens no formato real do WhatsApp...")
    print("🎯 Verifique se as mensagens aparecem no chat!")
    print()
    
    # Mensagens de teste
    mensagens = [
        "Olá! Esta é uma mensagem real do WhatsApp",
        "Como você está?",
        "Tudo bem, obrigado!",
        "Você pode me ajudar com uma dúvida?",
        "Claro! Estou aqui para ajudar.",
        "Muito obrigado pela sua atenção!"
    ]
    
    for i, mensagem in enumerate(mensagens, 1):
        from_me = i % 2 == 0  # Alternar entre enviado e recebido
        
        print(f"📨 Mensagem {i}/{len(mensagens)}: {'[ENVIADA]' if from_me else '[RECEBIDA]'} {mensagem}")
        
        success = send_real_webhook(chat_id, mensagem, from_me)
        
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
    print("   ✅ Se o chat específico foi atualizado")
    print("   ✅ Se não houve piscamento na interface")
    print()
    print("🌐 Acesse: http://localhost:3000/chats")

if __name__ == "__main__":
    test_real_webhooks() 