#!/usr/bin/env python3
"""
Teste de envio de imagens via W-API
"""

import sys
import os
import json
import base64
import requests

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enviar_imagem_url():
    """Testa envio de imagem via URL"""
    print("🧪 Testando envio de imagem via URL...")
    
    # Configurações
    instance_id = "T34398-VYR3QD-MS29SL"  # Substitua pelo seu instance_id
    token = "seu_token_aqui"  # Substitua pelo seu token
    
    # URL de teste (imagem pública)
    image_url = "https://via.placeholder.com/300x200/FF0000/FFFFFF?text=Teste+Imagem"
    
    # Dados da requisição
    url = f"https://api.w-api.app/v1/message/send-image"
    params = {"instanceId": instance_id}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "phone": "5569999267344",  # Substitua pelo número de teste
        "image": image_url,
        "caption": "Teste de envio de imagem via URL",
        "delayMessage": 1
    }
    
    try:
        response = requests.post(url, headers=headers, params=params, json=payload)
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

def test_enviar_imagem_base64():
    """Testa envio de imagem via Base64"""
    print("\n🧪 Testando envio de imagem via Base64...")
    
    # Configurações
    instance_id = "T34398-VYR3QD-MS29SL"  # Substitua pelo seu instance_id
    token = "seu_token_aqui"  # Substitua pelo seu token
    
    # Criar uma imagem simples em Base64 (1x1 pixel vermelho)
    # Esta é uma imagem PNG de 1x1 pixel vermelho em Base64
    image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # Dados da requisição
    url = f"https://api.w-api.app/v1/message/send-image"
    params = {"instanceId": instance_id}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "phone": "5569999267344",  # Substitua pelo número de teste
        "image": image_base64,
        "caption": "Teste de envio de imagem via Base64",
        "delayMessage": 1
    }
    
    try:
        response = requests.post(url, headers=headers, params=params, json=payload)
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

def test_classe_enviar_imagem():
    """Testa a classe EnviarImagem"""
    print("\n🧪 Testando classe EnviarImagem...")
    
    try:
        from wapi.mensagem.enviosMensagensDocs.enviarImagem import EnviarImagem
        
        # Configurações
        instance_id = "T34398-VYR3QD-MS29SL"  # Substitua pelo seu instance_id
        token = "seu_token_aqui"  # Substitua pelo seu token
        
        # Criar instância
        imagem_wapi = EnviarImagem(instance_id, token)
        
        # Testar envio via URL
        print("📤 Testando envio via URL...")
        result_url = imagem_wapi.enviar_imagem_url(
            phone="5569999267344",
            image_url="https://via.placeholder.com/300x200/00FF00/FFFFFF?text=Teste+Classe",
            caption="Teste da classe EnviarImagem - URL",
            delay=1
        )
        
        print(f"📡 Resultado URL: {json.dumps(result_url, indent=2)}")
        
        # Testar envio via Base64
        print("\n📤 Testando envio via Base64...")
        image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        result_base64 = imagem_wapi.enviar_imagem_base64(
            phone="5569999267344",
            image_base64=image_base64,
            caption="Teste da classe EnviarImagem - Base64",
            delay=1
        )
        
        print(f"📡 Resultado Base64: {json.dumps(result_base64, indent=2)}")
        
        # Testar método simples
        print("\n📤 Testando método simples...")
        result_simples = imagem_wapi.enviar_imagem_simples(
            phone="5569999267344",
            image_data="https://via.placeholder.com/300x200/0000FF/FFFFFF?text=Teste+Simples",
            caption="Teste do método simples",
            delay=1
        )
        
        print(f"📡 Resultado Simples: {json.dumps(result_simples, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar classe: {e}")
        return False

def test_endpoint_backend():
    """Testa o endpoint do backend"""
    print("\n🧪 Testando endpoint do backend...")
    
    try:
        # Configurações
        API_BASE_URL = "http://localhost:8000"
        token = "seu_token_aqui"  # Substitua pelo seu token de acesso
        
        # Dados do teste
        chat_id = 1  # Substitua pelo ID do chat de teste
        image_data = "https://via.placeholder.com/300x200/FF00FF/FFFFFF?text=Teste+Backend"
        
        # Fazer requisição para o endpoint
        url = f"{API_BASE_URL}/api/chats/{chat_id}/enviar-imagem/"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "image_data": image_data,
            "image_type": "url",
            "caption": "Teste do endpoint do backend"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso! {result.get('mensagem')}")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando testes de envio de imagens...")
    print("=" * 50)
    
    # Testes
    tests = [
        ("Envio via URL", test_enviar_imagem_url),
        ("Envio via Base64", test_enviar_imagem_base64),
        ("Classe EnviarImagem", test_classe_enviar_imagem),
        ("Endpoint Backend", test_endpoint_backend)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram!")
    else:
        print("⚠️ Alguns testes falharam. Verifique as configurações.")

if __name__ == "__main__":
    main() 