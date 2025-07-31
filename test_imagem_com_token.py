#!/usr/bin/env python3
"""
Teste de envio de imagem com token real
"""

import requests
import json
import sys
import os

def test_com_token_real():
    """Testa o envio de imagem com token real do sistema"""
    
    API_BASE_URL = "http://localhost:8000"
    
    # Token de teste (substitua por um token válido do seu sistema)
    # Você pode pegar este token do console do navegador executando:
    # localStorage.getItem('wapi_instances')
    token = "SEU_TOKEN_AQUI"  # Substitua pelo token real
    
    # Chat ID de teste
    chat_id = 21
    
    # Criar uma imagem de teste em base64 (1x1 pixel transparente)
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # Payload que o frontend envia
    payload = {
        'chat_id': chat_id,
        'image_data': test_image_base64,
        'image_type': 'base64',
        'caption': 'Teste de imagem'
    }
    
    print(f"🧪 Testando envio de imagem com token real...")
    print(f"📦 Payload enviado: {json.dumps(payload, indent=2)}")
    print(f"🔑 Token usado: {token[:20]}..." if token != "SEU_TOKEN_AQUI" else "❌ Token não configurado")
    
    if token == "SEU_TOKEN_AQUI":
        print("\n❌ Configure o token real no script!")
        print("💡 Para obter o token:")
        print("1. Abra o console do navegador (F12)")
        print("2. Execute: localStorage.getItem('wapi_instances')")
        print("3. Copie o token da primeira instância")
        print("4. Substitua 'SEU_TOKEN_AQUI' pelo token real")
        return
    
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
        elif response.status_code == 401:
            print("❌ Erro de autenticação - Token inválido")
        elif response.status_code == 400:
            try:
                error_data = response.json()
                print(f"❌ Erro de validação: {error_data}")
            except:
                print(f"❌ Erro inesperado: {response.text}")
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            print(f"Resposta: {response.text[:200]}")
                
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando teste com token real...")
    test_com_token_real()
    print("\n✅ Teste concluído!") 