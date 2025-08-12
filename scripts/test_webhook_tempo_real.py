#!/usr/bin/env python3
"""
Script para testar o sistema de tempo real enviando webhooks simulados
"""

import requests
import json
import time
from datetime import datetime
import random

# Configurações
WEBHOOK_URL = "http://localhost:8000/webhook/receiver/"
FRONTEND_URL = "http://localhost:3000"

def send_test_webhook(chat_id, message_text, from_me=False, message_type="text"):
    """
    Envia um webhook de teste para simular uma nova mensagem
    """
    # Gerar message_id único
    message_id = f"test_msg_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Preparar dados do webhook baseado no tipo de mensagem
    if message_type == "text":
        msg_content = {
            "conversation": message_text
        }
    elif message_type == "image":
        msg_content = {
            "imageMessage": {
                "url": "https://example.com/test-image.jpg",
                "caption": message_text,
                "mimetype": "image/jpeg",
                "fileLength": 1024000,
                "height": 1080,
                "width": 1920
            }
        }
    elif message_type == "audio":
        msg_content = {
            "audioMessage": {
                "url": "https://example.com/test-audio.mp3",
                "mimetype": "audio/mp3",
                "fileLength": 512000,
                "seconds": 30
            }
        }
    else:
        msg_content = {
            "conversation": message_text
        }
    
    webhook_data = {
        "instanceId": "test_instance_123",
        "event": "message",
        "messageId": message_id,
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
        "msgContent": msg_content,
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
            print(f"✅ Webhook enviado com sucesso: {message_text}")
            return True
        else:
            print(f"❌ Erro ao enviar webhook: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def test_realtime_system():
    """
    Testa o sistema de tempo real enviando mensagens simuladas
    """
    print("🚀 Iniciando teste do sistema de tempo real...")
    print(f"📡 Webhook URL: {WEBHOOK_URL}")
    print(f"🌐 Frontend URL: {FRONTEND_URL}")
    print()
    
    # Lista de mensagens de teste com diferentes tipos
    test_messages = [
        {"text": "Olá! Como você está?", "type": "text", "from_me": False},
        {"text": "Tudo bem, obrigado por perguntar!", "type": "text", "from_me": True},
        {"text": "Você pode me ajudar com uma dúvida?", "type": "text", "from_me": False},
        {"text": "Claro! Estou aqui para ajudar.", "type": "text", "from_me": True},
        {"text": "Muito obrigado pela sua atenção!", "type": "text", "from_me": False},
        {"text": "De nada! Fico feliz em poder ajudar.", "type": "text", "from_me": True},
        {"text": "Tenha um ótimo dia!", "type": "text", "from_me": False},
        {"text": "Você também! Até logo!", "type": "text", "from_me": True},
        {"text": "Enviando uma imagem", "type": "image", "from_me": False},
        {"text": "Enviando um áudio", "type": "audio", "from_me": True}
    ]
    
    chat_id = "5511999999999@s.whatsapp.net"
    
    print(f"📱 Chat ID de teste: {chat_id}")
    print("📝 Enviando mensagens simuladas...")
    print("🎯 Verifique se a lista de chats é atualizada automaticamente!")
    print()
    
    for i, message_data in enumerate(test_messages, 1):
        message_text = message_data["text"]
        message_type = message_data["type"]
        from_me = message_data["from_me"]
        
        print(f"📨 Mensagem {i}/{len(test_messages)}: {'[ENVIADA]' if from_me else '[RECEBIDA]'} {message_text} ({message_type})")
        
        success = send_test_webhook(chat_id, message_text, from_me, message_type)
        
        if success:
            print(f"   ✅ Enviada com sucesso")
            print(f"   🔄 Aguarde 2 segundos para ver a atualização automática...")
        else:
            print(f"   ❌ Falha no envio")
        
        # Aguardar 2 segundos entre mensagens para ver a atualização
        time.sleep(2)
        print()
    
    print("🎉 Teste concluído!")
    print("📋 Verifique no frontend se as mensagens apareceram automaticamente")
    print("🔍 Verifique o console do navegador para logs de tempo real")
    print("🌐 Acesse: http://localhost:3000/chats")
    print("✅ A lista de chats deve ter sido atualizada automaticamente!")

def test_multiple_chats():
    """
    Testa enviando mensagens para múltiplos chats
    """
    print("🧪 Testando múltiplos chats...")
    print()
    
    chat_ids = [
        "5511999999999@s.whatsapp.net",
        "5511888888888@s.whatsapp.net", 
        "5511777777777@s.whatsapp.net"
    ]
    
    for chat_id in chat_ids:
        print(f"📱 Enviando mensagem para chat: {chat_id}")
        success = send_test_webhook(chat_id, f"Mensagem de teste para {chat_id}", False)
        if success:
            print(f"   ✅ Enviada com sucesso")
            print(f"   🔄 Aguarde 1 segundo para ver a atualização...")
        else:
            print(f"   ❌ Falha no envio")
        time.sleep(1)
    
    print("✅ Teste de múltiplos chats concluído!")
    print("📋 Verifique se todos os chats foram atualizados na lista!")

def test_continuous_updates():
    """
    Testa atualizações contínuas para simular uso real
    """
    print("🔄 Testando atualizações contínuas...")
    print("📝 Enviando mensagens a cada 3 segundos...")
    print("🛑 Pressione Ctrl+C para parar")
    print()
    
    chat_id = "5511999999999@s.whatsapp.net"
    counter = 1
    
    try:
        while True:
            message_text = f"Mensagem automática #{counter} - {datetime.now().strftime('%H:%M:%S')}"
            
            print(f"📨 Enviando: {message_text}")
            success = send_test_webhook(chat_id, message_text, counter % 2 == 0)
            
            if success:
                print(f"   ✅ Enviada com sucesso")
            else:
                print(f"   ❌ Falha no envio")
            
            counter += 1
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
        print(f"📊 Total de mensagens enviadas: {counter-1}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "multi":
            test_multiple_chats()
        elif sys.argv[1] == "continuous":
            test_continuous_updates()
        else:
            print("Uso: python test_webhook_tempo_real.py [multi|continuous]")
    else:
        test_realtime_system() 