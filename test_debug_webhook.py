#!/usr/bin/env python3
"""
🔍 TESTE DEBUG WEBHOOK
Verifica se os logs de debug estão funcionando e analisa o comportamento do fromMe
"""

import os
import sys
import django
import requests
import json
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

def test_webhook_debug():
    """Testa os logs de debug do webhook"""
    print("🔍 TESTE DEBUG WEBHOOK")
    print("=" * 60)
    
    # Dados de teste simulando um áudio com fromMe=False
    webhook_data_false = {
        "fromMe": False,
        "messageId": "test_audio_false_123",
        "msgContent": {
            "audioMessage": {
                "url": "test_url",
                "mimetype": "audio/ogg"
            }
        },
        "pushName": "Test User",
        "chatId": "556999267344@c.us"
    }
    
    # Dados de teste simulando um áudio com fromMe=True
    webhook_data_true = {
        "fromMe": True,
        "messageId": "test_audio_true_456", 
        "msgContent": {
            "audioMessage": {
                "url": "test_url",
                "mimetype": "audio/ogg"
            }
        },
        "pushName": "Test User",
        "chatId": "556999267344@c.us"
    }
    
    # Dados de teste sem mídia, fromMe=False
    webhook_data_text = {
        "fromMe": False,
        "messageId": "test_text_789",
        "msgContent": {
            "conversation": "Olá, como vai?"
        },
        "pushName": "Test User", 
        "chatId": "556999267344@c.us"
    }
    
    print("📋 CENÁRIOS DE TESTE:")
    print("1. 🎵 Áudio com fromMe=False (deve processar)")
    print("2. 🎵 Áudio com fromMe=True (deve processar)")
    print("3. 💬 Texto com fromMe=False (não deve processar)")
    print()
    
    # Teste 1: Áudio fromMe=False
    print("🧪 TESTE 1: Áudio fromMe=False")
    try:
        response = requests.post(
            'http://localhost:8000/webhook/send-message/',
            json=webhook_data_false,
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    print()
    
    # Teste 2: Áudio fromMe=True  
    print("🧪 TESTE 2: Áudio fromMe=True")
    try:
        response = requests.post(
            'http://localhost:8000/webhook/send-message/',
            json=webhook_data_true,
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    print()
    
    # Teste 3: Texto fromMe=False
    print("🧪 TESTE 3: Texto fromMe=False")
    try:
        response = requests.post(
            'http://localhost:8000/webhook/send-message/',
            json=webhook_data_text,
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    print()

def verificar_logs_recentes():
    """Verifica os logs recentes para debug"""
    print("📋 ANÁLISE DE LOGS RECENTES")
    print("=" * 60)
    
    from webhook.models import WebhookEvent
    
    # Últimos 10 webhooks
    webhooks = WebhookEvent.objects.all().order_by('-timestamp')[:10]
    
    for webhook in webhooks:
        try:
            data = webhook.raw_data
            fromMe = data.get('fromMe')
            msgContent = data.get('msgContent', {})
            tem_audio = 'audioMessage' in msgContent
            
            print(f"📅 {webhook.timestamp}")
            print(f"   📧 messageId: {data.get('messageId', 'N/A')}")
            print(f"   👤 fromMe: {fromMe}")
            print(f"   🎵 tem_audio: {tem_audio}")
            print(f"   ⚙️ processed: {webhook.processed}")
            print(f"   📁 keys: {list(msgContent.keys())}")
            print()
        except Exception as e:
            print(f"   ❌ Erro ao processar webhook: {e}")

def main():
    """Função principal"""
    print("🔍 DEBUG WEBHOOK - VERIFICAÇÃO fromMe")
    print("=" * 80)
    print("OBJETIVO: Confirmar se fromMe=False e verificar endpoint correto")
    print("=" * 80)
    
    # 1. Verificar logs recentes
    verificar_logs_recentes()
    
    # 2. Testar webhook com dados simulados
    print("\n🧪 TESTES SIMULADOS")
    print("=" * 80)
    test_webhook_debug()
    
    print("\n📋 INSTRUÇÕES PARA VERIFICAÇÃO:")
    print("=" * 80)
    print("1. 🔄 Certifique-se que o Django está rodando")
    print("2. 📱 Envie um áudio pelo WhatsApp")
    print("3. 🔍 Verifique os logs no terminal do Django")
    print("4. 🎯 Procure pela linha: '[DEBUG] 🛣️ Rota recebida'")
    print("5. 🎯 Procure pela linha: '🔍 WEBHOOK DEBUG: fromMe='")
    print()
    print("💡 Se fromMe=False e keys=['audioMessage'], a causa está confirmada!")

if __name__ == "__main__":
    main() 