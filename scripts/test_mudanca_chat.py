#!/usr/bin/env python3
"""
Script para testar mudança de chat e carregamento na última mensagem
"""

import requests
import json
import time
from datetime import datetime

# Configurações
WEBHOOK_URL = "http://localhost:8000/webhook/receiver/"
FRONTEND_URL = "http://localhost:3000"
API_BASE_URL = "http://localhost:8000"

def send_webhook_multi_chat(chat_id, message_text, from_me=False):
    """
    Envia webhook para múltiplos chats
    """
    # Gerar message_id único
    message_id = f"test_multi_{int(time.time())}_{chat_id.replace('@', '_')}"
    
    # Estrutura do webhook
    webhook_data = {
        "instanceId": "test_instance_123",
        "event": "messages.upsert",
        "messageId": message_id,
        "fromMe": from_me,
        "isGroup": False,
        "chat": {
            "id": chat_id,
            "name": f"Chat {chat_id}"
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
            print(f"✅ Webhook enviado para {chat_id}: {message_text}")
            return True
        else:
            print(f"❌ Erro ao enviar webhook: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_mudanca_chat():
    """
    Teste de mudança de chat e carregamento na última mensagem
    """
    print("🧪 Teste de mudança de chat e carregamento na última mensagem")
    print("📡 Webhook URL:", WEBHOOK_URL)
    print("🌐 Frontend URL:", FRONTEND_URL)
    print()
    
    # Múltiplos chats para testar
    chats = [
        "5511999999999@s.whatsapp.net",
        "5511888888888@s.whatsapp.net", 
        "5511777777777@s.whatsapp.net"
    ]
    
    print("📝 Enviando mensagens para múltiplos chats...")
    print("🎯 Verifique se ao trocar de chat as mensagens carregam na última!")
    print()
    
    # Mensagens para cada chat
    for i, chat_id in enumerate(chats, 1):
        print(f"📱 Chat {i}/{len(chats)}: {chat_id}")
        
        # Enviar 3 mensagens para cada chat
        for j in range(1, 4):
            message_text = f"Mensagem {j} do chat {i} - {datetime.now().strftime('%H:%M:%S')}"
            from_me = j % 2 == 0  # Alternar entre enviado e recebido
            
            print(f"   📨 Mensagem {j}: {'[ENVIADA]' if from_me else '[RECEBIDA]'} {message_text}")
            
            success = send_webhook_multi_chat(chat_id, message_text, from_me)
            
            if success:
                print(f"      ✅ Enviada com sucesso")
            else:
                print(f"      ❌ Falha no envio")
            
            # Aguardar 2 segundos entre mensagens
            time.sleep(2)
        
        print()
    
    print("🎉 Teste de múltiplos chats concluído!")
    print("📋 Verifique no frontend:")
    print("   ✅ Se ao trocar de chat as mensagens carregam")
    print("   ✅ Se o chat abre direto na última mensagem")
    print("   ✅ Se não há recarregamento de todas as mensagens")
    print("   ✅ Se apenas as novas mensagens são adicionadas")
    print()
    print("🌐 Acesse: http://localhost:3000/chats")
    print("🔄 Teste: Clique em diferentes chats para ver se carregam corretamente")

if __name__ == "__main__":
    test_mudanca_chat() 