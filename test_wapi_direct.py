import json
import requests

def test_wapi_direct():
    """
    Teste direto da WAPI para verificar se está funcionando
    """
    # Configurações da API - dados fornecidos pelo usuário
    INSTANCE_ID = "3B6XIW-ZTS923-GEAY6V"
    API_TOKEN = "Q8EOH07SJkXhg4iT6Qmhz1BJdLl8nL9WF"
    BASE_URL = "https://api.w-api.app/v1/"
    
    print("🔍 Testando conexão direta com a WAPI...")
    print(f"Instance ID: {INSTANCE_ID}")
    print(f"Base URL: {BASE_URL}")
    
    # 1. Testar status da instância
    print("\n📊 1. Testando status da instância...")
    try:
        status_url = f"{BASE_URL}instance/status-instance"
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        params = {"instanceId": INSTANCE_ID}
        
        response = requests.get(status_url, headers=headers, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            print("✅ Status da instância obtido com sucesso!")
        else:
            print("❌ Erro ao obter status da instância")
            
    except Exception as e:
        print(f"❌ Erro ao testar status: {str(e)}")
    
    # 2. Testar envio de mensagem de texto
    print("\n📤 2. Testando envio de mensagem de texto...")
    try:
        message_url = f"{BASE_URL}message/send-text"
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "instanceId": INSTANCE_ID,
            "phone": "5569999267344",  # Número de teste
            "message": "Teste de mensagem via API direta",
            "delay": 1
        }
        
        response = requests.post(message_url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            print("✅ Mensagem enviada com sucesso!")
        else:
            print("❌ Erro ao enviar mensagem")
            
    except Exception as e:
        print(f"❌ Erro ao testar envio de mensagem: {str(e)}")
    
    # 3. Testar webhook (endpoint não existe na WAPI oficial)
    print("\n🔗 3. Testando webhook...")
    print("⚠️  Endpoint /webhooks/test não existe na WAPI oficial")
    print("   O teste de webhook deve ser feito através do nosso backend Flask")
    
    # 4. Testar QR Code
    print("\n📱 4. Testando geração de QR Code...")
    try:
        qr_url = f"{BASE_URL}instance/qr-code"
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        params = {
            "instanceId": INSTANCE_ID,
            "syncContacts": "disable",
            "image": "enable"
        }
        
        response = requests.get(qr_url, headers=headers, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            if 'image/png' in response.headers.get('content-type', ''):
                print("✅ QR Code gerado com sucesso (imagem PNG)!")
            else:
                print(f"✅ QR Code gerado com sucesso! Response: {response.text[:200]}")
        else:
            print("❌ Erro ao gerar QR Code")
            
    except Exception as e:
        print(f"❌ Erro ao testar QR Code: {str(e)}")

if __name__ == "__main__":
    test_wapi_direct() 