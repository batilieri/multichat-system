#!/usr/bin/env python3
"""
Teste detalhado do problema de envio de imagem
Analisa cada componente individualmente para identificar a causa raiz
"""

import requests
import json
import base64
import time

def testar_wapi_direto():
    """Testa a W-API diretamente sem o backend"""
    print("🔍 Testando W-API diretamente...")
    
    # Configurações de teste (substitua pelos seus dados reais)
    instance_id = "T34398-VYR3QD-MS29SL"  # Substitua pelo seu instance_id
    token = "seu_token_aqui"  # Substitua pelo seu token
    
    # URL da W-API
    url = "https://api.w-api.app/v1/message/send-image"
    
    # Headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Parâmetros
    params = {"instanceId": instance_id}
    
    # Imagem de teste (1x1 pixel vermelho)
    test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # Payload
    payload = {
        "phone": "5569999267344",  # Substitua pelo número de teste
        "image": test_image_base64,
        "caption": "Teste direto W-API",
        "delayMessage": 1
    }
    
    print(f"📤 URL: {url}")
    print(f"🔑 Instance ID: {instance_id}")
    print(f"📱 Phone: {payload['phone']}")
    print(f"🖼️ Image size: {len(test_image_base64)} chars")
    
    try:
        response = requests.post(url, headers=headers, params=params, json=payload, timeout=30)
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso! Message ID: {result.get('messageId')}")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def testar_backend_local():
    """Testa o backend local"""
    print("\n🌐 Testando backend local...")
    
    # Token de teste (substitua por um token válido)
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM1NzI4MDAwLCJpYXQiOjE3MzU3MjQ0MDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoxfQ.example"
    
    # Dados do teste
    chat_id = 21
    image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # Testar diferentes endpoints
    endpoints = [
        "/api/mensagens/enviar-imagem/",
        "/api/chats/21/enviar-imagem/"
    ]
    
    for endpoint in endpoints:
        print(f"\n📤 Testando endpoint: {endpoint}")
        
        url = f"http://localhost:8000{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "chat_id": chat_id,
            "image_data": image_data,
            "image_type": "base64",
            "caption": "Teste detalhado"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            print(f"📡 Status Code: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Sucesso! {result}")
                return True
            else:
                print(f"❌ Erro: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro na requisição: {e}")
    
    return False

def testar_formatos_imagem():
    """Testa diferentes formatos de imagem"""
    print("\n🖼️ Testando diferentes formatos de imagem...")
    
    # Base64 simples
    base64_simples = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # Base64 com data URL
    base64_data_url = f"data:image/png;base64,{base64_simples}"
    
    # Base64 com data URL JPEG
    base64_jpeg = f"data:image/jpeg;base64,{base64_simples}"
    
    formatos = [
        ("Base64 simples", base64_simples),
        ("Data URL PNG", base64_data_url),
        ("Data URL JPEG", base64_jpeg)
    ]
    
    for nome, formato in formatos:
        print(f"\n📝 Testando: {nome}")
        print(f"   Tamanho: {len(formato)} caracteres")
        print(f"   Inicia com: {formato[:30]}...")
        
        # Verificar se é base64 válido
        try:
            if formato.startswith('data:'):
                base64_part = formato.split(',')[1]
                decoded = base64.b64decode(base64_part)
                print(f"   ✅ Base64 válido ({len(decoded)} bytes)")
            else:
                decoded = base64.b64decode(formato)
                print(f"   ✅ Base64 válido ({len(decoded)} bytes)")
        except Exception as e:
            print(f"   ❌ Base64 inválido: {e}")
    
    return True

def testar_autenticacao():
    """Testa a autenticação do backend"""
    print("\n🔐 Testando autenticação...")
    
    # Testar sem token
    url = "http://localhost:8000/api/mensagens/enviar-imagem/"
    payload = {
        "chat_id": 21,
        "image_data": "teste",
        "image_type": "base64"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"📡 Sem token - Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Erro sem token: {e}")
    
    # Testar com token inválido
    headers = {"Authorization": "Bearer token_invalido"}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"📡 Token inválido - Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Erro com token inválido: {e}")
    
    return True

def verificar_erro_especifico():
    """Verifica o erro específico mencionado"""
    print("\n🎯 Analisando erro específico...")
    
    # O erro mencionado é: "Formato de imagem inválido. Forneça uma imagem em base64 ou URL."
    
    # Este erro vem da linha 1615 do arquivo views.py:
    # if image_type not in ['url', 'base64']:
    
    print("🔍 O erro indica que o 'image_type' não está sendo enviado corretamente")
    print("📋 Valores aceitos: 'url' ou 'base64'")
    
    # Testar com image_type ausente
    print("\n📤 Testando sem image_type...")
    
    url = "http://localhost:8000/api/mensagens/enviar-imagem/"
    headers = {"Content-Type": "application/json"}
    payload = {
        "chat_id": 21,
        "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        # image_type ausente
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Testar com image_type inválido
    print("\n📤 Testando com image_type inválido...")
    
    payload["image_type"] = "invalid"
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    return True

def main():
    """Função principal"""
    print("🔬 TESTE DETALHADO - PROBLEMA DE ENVIO DE IMAGEM")
    print("=" * 60)
    
    # Testes
    testes = [
        ("Testar W-API diretamente", testar_wapi_direto),
        ("Testar backend local", testar_backend_local),
        ("Testar formatos de imagem", testar_formatos_imagem),
        ("Testar autenticação", testar_autenticacao),
        ("Verificar erro específico", verificar_erro_especifico)
    ]
    
    for nome, teste in testes:
        print(f"\n{'='*20} {nome} {'='*20}")
        try:
            teste()
        except Exception as e:
            print(f"❌ Erro no teste {nome}: {e}")
    
    print("\n" + "=" * 60)
    print("📊 ANÁLISE DO PROBLEMA")
    print("=" * 60)
    
    print("""
🔍 POSSÍVEIS CAUSAS DO ERRO:

1. **image_type ausente ou inválido**
   - O frontend não está enviando o campo 'image_type'
   - O valor enviado não é 'url' ou 'base64'

2. **Token de autenticação inválido**
   - O token JWT está expirado ou inválido
   - O usuário não tem permissão

3. **Instância do WhatsApp não configurada**
   - Não há instância ativa
   - Token da W-API inválido

4. **Formato de imagem incorreto**
   - Base64 malformado
   - URL inválida

5. **Backend não está rodando**
   - Servidor Django não iniciado
   - Porta 8000 não disponível

💡 SOLUÇÕES SUGERIDAS:

1. Verifique se o frontend está enviando 'image_type' corretamente
2. Gere um novo token JWT válido
3. Configure uma instância do WhatsApp ativa
4. Teste com uma imagem base64 válida
5. Inicie o backend Django na porta 8000
""")

if __name__ == "__main__":
    main() 