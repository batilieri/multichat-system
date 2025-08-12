#!/usr/bin/env python3
"""
Teste sem autenticação para verificar validação
"""

import requests
import json

def test_sem_auth():
    """Testa o endpoint sem autenticação para ver a validação"""
    
    API_BASE_URL = "http://localhost:8000"
    
    # Chat ID de teste
    chat_id = 21
    
    # Payload que o frontend envia
    payload = {
        'chat_id': chat_id,
        'image_data': 'teste_base64_aqui',
        'image_type': 'base64',
        'caption': 'Teste de imagem'
    }
    
    print(f"🧪 Testando sem autenticação...")
    print(f"📦 Payload enviado: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/mensagens/enviar-imagem/",
            headers={
                'Content-Type': 'application/json'
            },
            json=payload,
            timeout=10
        )
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Endpoint protegido (autenticação necessária)")
        elif response.status_code == 400:
            try:
                error_data = response.json()
                print(f"✅ Validação funcionando: {error_data}")
            except:
                print(f"❌ Erro inesperado: {response.text}")
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            print(f"Resposta: {response.text[:200]}")
                
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando teste sem autenticação...")
    test_sem_auth()
    print("\n✅ Teste concluído!") 