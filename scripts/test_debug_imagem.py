#!/usr/bin/env python3
"""
Teste de debug para envio de imagem
"""

import requests
import json
import base64

def test_envio_imagem():
    """Testa o envio de imagem com dados de debug"""
    
    API_BASE_URL = "http://localhost:8000"
    
    # Token de teste (substitua por um token válido)
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM1NzI4MDAwLCJpYXQiOjE3MzU3MjQ0MDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoxfQ.example"
    
    # Chat ID de teste
    chat_id = 21
    
    # Criar uma imagem de teste em base64
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # Payload que o frontend envia
    payload = {
        'chat_id': chat_id,
        'image_data': test_image_base64,
        'image_type': 'base64',
        'caption': 'Teste de imagem'
    }
    
    print(f"🧪 Testando envio de imagem...")
    print(f"📦 Payload enviado: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/mensagens/enviar-imagem/",
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            },
            json=payload,
            timeout=10
        )
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso: {result}")
        else:
            try:
                error_data = response.json()
                print(f"❌ Erro: {error_data}")
            except:
                print(f"❌ Erro: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando teste de debug...")
    test_envio_imagem()
    print("\n✅ Teste concluído!") 