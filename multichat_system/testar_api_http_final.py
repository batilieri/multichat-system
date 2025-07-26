#!/usr/bin/env python
"""
Teste HTTP final da API
"""

import requests
import json
import time

def test_api_http():
    """Testa a API via HTTP"""
    print("🔍 Testando API via HTTP...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Aguardar servidor iniciar
    print("⏳ Aguardando servidor iniciar...")
    time.sleep(3)
    
    # Testar endpoint público primeiro
    try:
        response = requests.get(f"{base_url}/api/test-chats/", timeout=10)
        print(f"✅ Endpoint público: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Dados: {data}")
    except Exception as e:
        print(f"❌ Erro no endpoint público: {e}")
        return
    
    # Testar endpoint de mensagens (sem autenticação)
    try:
        response = requests.get(f"{base_url}/api/mensagens/?chat_id=120363362003830637@g.us", timeout=10)
        print(f"\n📨 API de mensagens (sem auth): {response.status_code}")
        print(f"   Resposta: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Erro na API de mensagens: {e}")
    
    # Testar endpoint de chats
    try:
        response = requests.get(f"{base_url}/api/chats/", timeout=10)
        print(f"\n📱 API de chats (sem auth): {response.status_code}")
        print(f"   Resposta: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Erro na API de chats: {e}")

if __name__ == "__main__":
    test_api_http() 