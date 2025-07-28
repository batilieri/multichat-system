#!/usr/bin/env python3
"""
Script completo para testar o sistema de webhooks e tempo real
"""

import requests
import json
import time
from datetime import datetime

# Configurações
WEBHOOK_URL = "http://localhost:8000/webhook/receiver/"
FRONTEND_URL = "http://localhost:3000"
API_BASE_URL = "http://localhost:8000"

def send_webhook_completo(chat_id, message_text, from_me=False, message_type="text"):
    """
    Envia um webhook completo que simula o formato real do WhatsApp
    """
    # Gerar message_id único
    message_id = f"test_msg_{int(time.time())}_{chat_id.replace('@', '_')}"
    
    # Estrutura completa do webhook do WhatsApp
    webhook_data = {
        "instanceId": "test_instance_123",
        "event": "messages.upsert",
        "messageId": message_id,
        "fromMe": from_me,
        "isGroup": False,
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
        "moment": int(time.time()),
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
        }
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Webhook completo enviado: {message_text}")
            return True
        else:
            print(f"❌ Erro ao enviar webhook: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def verificar_mensagem_no_banco(chat_id, message_text, timeout=30):
    """
    Verifica se a mensagem foi salva no banco de dados
    """
    print(f"🔍 Verificando se mensagem foi salva no banco...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Verificar via API
            response = requests.get(
                f"{API_BASE_URL}/api/mensagens/?chat_id={chat_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get('results', [])
                
                for msg in messages:
                    if message_text in (msg.get('conteudo', '') or msg.get('content', '')):
                        print(f"✅ Mensagem encontrada no banco: {message_text}")
                        return True
                
                print(f"⏳ Mensagem ainda não encontrada, aguardando...")
                time.sleep(2)
            else:
                print(f"❌ Erro ao verificar API: {response.status_code}")
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Erro ao verificar banco: {e}")
            time.sleep(2)
    
    print(f"❌ Mensagem não encontrada no banco após {timeout} segundos")
    return False

def test_sistema_completo():
    """
    Teste completo do sistema
    """
    print("🧪 Teste completo do sistema de tempo real")
    print("📡 Webhook URL:", WEBHOOK_URL)
    print("🌐 Frontend URL:", FRONTEND_URL)
    print("🔗 API URL:", API_BASE_URL)
    print()
    
    chat_id = "5511999999999@s.whatsapp.net"
    
    print("📝 Enviando mensagens e verificando no banco...")
    print("🎯 Verifique se as mensagens aparecem automaticamente no frontend!")
    print()
    
    # Mensagens de teste
    mensagens = [
        "Olá! Esta é uma mensagem de teste do sistema completo",
        "Como você está?",
        "Tudo bem, obrigado!",
        "Você pode me ajudar com uma dúvida?",
        "Claro! Estou aqui para ajudar.",
        "Muito obrigado pela sua atenção!"
    ]
    
    for i, mensagem in enumerate(mensagens, 1):
        from_me = i % 2 == 0  # Alternar entre enviado e recebido
        
        print(f"📨 Mensagem {i}/{len(mensagens)}: {'[ENVIADA]' if from_me else '[RECEBIDA]'} {mensagem}")
        
        # Enviar webhook
        success = send_webhook_completo(chat_id, mensagem, from_me)
        
        if success:
            print(f"   ✅ Webhook enviado com sucesso")
            
            # Verificar se foi salva no banco
            if verificar_mensagem_no_banco(chat_id, mensagem):
                print(f"   ✅ Mensagem confirmada no banco")
            else:
                print(f"   ❌ Mensagem não encontrada no banco")
        else:
            print(f"   ❌ Falha no envio do webhook")
        
        # Aguardar 5 segundos entre mensagens
        print(f"   ⏳ Aguardando 5 segundos...")
        time.sleep(5)
        print()
    
    print("🎉 Teste completo concluído!")
    print("📋 Verifique no frontend:")
    print("   ✅ Se as mensagens apareceram automaticamente")
    print("   ✅ Se a lista de chats foi atualizada")
    print("   ✅ Se o chat específico foi atualizado")
    print("   ✅ Se não houve piscamento na interface")
    print("   ✅ Se o indicador 'Tempo real' está ativo")
    print()
    print("🌐 Acesse: http://localhost:3000/chats")

def verificar_status_sistema():
    """
    Verifica o status do sistema
    """
    print("🔍 Verificando status do sistema...")
    
    # Verificar backend
    try:
        response = requests.get(f"{API_BASE_URL}/api/chats/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend funcionando")
        else:
            print(f"❌ Backend com erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend não acessível: {e}")
    
    # Verificar frontend
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend funcionando")
        else:
            print(f"❌ Frontend com erro: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend não acessível: {e}")
    
    # Verificar webhook
    try:
        response = requests.post(
            WEBHOOK_URL,
            json={"test": "connection"},
            timeout=5
        )
        print("✅ Webhook endpoint acessível")
    except Exception as e:
        print(f"❌ Webhook não acessível: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "status":
            verificar_status_sistema()
        else:
            print("Uso: python test_webhook_completo.py [status]")
    else:
        test_sistema_completo() 