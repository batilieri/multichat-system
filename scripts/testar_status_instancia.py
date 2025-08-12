#!/usr/bin/env python3
"""
Script para testar o status da instância W-API antes de buscar chats.
"""

import requests

def testar_status_instancia():
    """Testa o status da instância W-API"""
    
    # Configurações
    INSTANCE_ID = "3B6XIW-ZTS923-GEAY6V"
    TOKEN = "Q8EOH07SJkXhg4iT6Qmhz1BJdLl8nL9WF"
    
    base_url = "https://api.w-api.app/v1"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("🔍 TESTANDO STATUS DA INSTÂNCIA W-API")
    print("=" * 50)
    
    # 1. Testar status da instância
    print("\n1️⃣ Verificando status da instância...")
    url_status = f"{base_url}/instance/status-instance"
    params_status = {"instanceId": INSTANCE_ID}
    
    try:
        response = requests.get(url_status, headers=headers, params=params_status, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Instância conectada: {data.get('connected', False)}")
        else:
            print(f"❌ Erro ao verificar status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {str(e)}")
    
    # 2. Testar geração de QR Code
    print("\n2️⃣ Testando geração de QR Code...")
    url_qr = f"{base_url}/instance/qr-code"
    params_qr = {"instanceId": INSTANCE_ID}
    
    try:
        response = requests.get(url_qr, headers=headers, params=params_qr, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('qrcode'):
                print("✅ QR Code gerado com sucesso")
            else:
                print("⚠️ QR Code não disponível (pode estar conectado)")
        else:
            print(f"❌ Erro ao gerar QR Code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {str(e)}")
    
    # 3. Testar endpoint de chats com diferentes formatos
    print("\n3️⃣ Testando endpoint de chats...")
    url_chats = f"{base_url}/chats/fetch-chats"
    params_chats = {
        "instanceId": INSTANCE_ID,
        "perPage": 5,
        "page": 1
    }
    
    try:
        response = requests.get(url_chats, headers=headers, params=params_chats, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            total_chats = data.get('totalChats', 0)
            print(f"✅ Chats encontrados: {total_chats}")
        else:
            print(f"❌ Erro ao buscar chats: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {str(e)}")

if __name__ == "__main__":
    testar_status_instancia() 