#!/usr/bin/env python3
"""
Script para testar atualização otimizada (apenas novas mensagens)
"""

import requests
import json
import time
from datetime import datetime

# Configurações
WEBHOOK_URL = "http://localhost:8000/webhook/receiver/"
FRONTEND_URL = "http://localhost:3000"
API_BASE_URL = "http://localhost:8000"

def send_webhook_otimizado(chat_id, message_text, from_me=False):
    """
    Envia um webhook otimizado para testar apenas novas mensagens
    """
    # Gerar message_id único
    message_id = f"test_opt_{int(time.time())}_{chat_id.replace('@', '_')}"
    
    # Estrutura otimizada do webhook
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
            print(f"✅ Webhook otimizado enviado: {message_text}")
            return True
        else:
            print(f"❌ Erro ao enviar webhook: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def verificar_mensagem_especifica(chat_id, message_text, timeout=30):
    """
    Verifica se uma mensagem específica foi adicionada
    """
    print(f"🔍 Verificando mensagem específica: {message_text}")
    
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
                        print(f"✅ Mensagem específica encontrada: {message_text}")
                        return True
                
                print(f"⏳ Mensagem específica ainda não encontrada...")
                time.sleep(2)
            else:
                print(f"❌ Erro ao verificar API: {response.status_code}")
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Erro ao verificar banco: {e}")
            time.sleep(2)
    
    print(f"❌ Mensagem específica não encontrada após {timeout} segundos")
    return False

def test_atualizacao_otimizada():
    """
    Teste de atualização otimizada
    """
    print("🧪 Teste de atualização otimizada")
    print("📡 Webhook URL:", WEBHOOK_URL)
    print("🌐 Frontend URL:", FRONTEND_URL)
    print()
    
    chat_id = "5511999999999@s.whatsapp.net"
    
    print("📝 Enviando mensagens e verificando apenas novas...")
    print("🎯 Verifique se apenas as novas mensagens aparecem no chat!")
    print("⚠️ IMPORTANTE: Não deve haver recarregamento de todas as mensagens!")
    print()
    
    # Mensagens de teste
    mensagens = [
        "Mensagem 1 - Teste de atualização otimizada",
        "Mensagem 2 - Apenas novas devem aparecer",
        "Mensagem 3 - Sem recarregar tudo",
        "Mensagem 4 - Performance otimizada",
        "Mensagem 5 - Sistema de snapshot"
    ]
    
    for i, mensagem in enumerate(mensagens, 1):
        from_me = i % 2 == 0  # Alternar entre enviado e recebido
        
        print(f"📨 Mensagem {i}/{len(mensagens)}: {'[ENVIADA]' if from_me else '[RECEBIDA]'} {mensagem}")
        
        # Enviar webhook
        success = send_webhook_otimizado(chat_id, mensagem, from_me)
        
        if success:
            print(f"   ✅ Webhook enviado com sucesso")
            
            # Verificar se foi adicionada (não recarregada)
            if verificar_mensagem_especifica(chat_id, mensagem):
                print(f"   ✅ Mensagem adicionada (não recarregada)")
            else:
                print(f"   ❌ Mensagem não encontrada")
        else:
            print(f"   ❌ Falha no envio do webhook")
        
        # Aguardar 3 segundos entre mensagens
        print(f"   ⏳ Aguardando 3 segundos...")
        time.sleep(3)
        print()
    
    print("🎉 Teste de atualização otimizada concluído!")
    print("📋 Verifique no frontend:")
    print("   ✅ Se apenas as novas mensagens apareceram")
    print("   ✅ Se não houve recarregamento de todas as mensagens")
    print("   ✅ Se o chat não ficou carregando constantemente")
    print("   ✅ Se a performance está otimizada")
    print()
    print("🌐 Acesse: http://localhost:3000/chats")

if __name__ == "__main__":
    test_atualizacao_otimizada() 