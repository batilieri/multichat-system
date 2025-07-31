#!/usr/bin/env python3
"""
Teste do endpoint de envio de imagem
"""

import requests
import json
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_endpoint_imagem():
    """Testa o endpoint de envio de imagem"""
    print("🧪 Testando endpoint de envio de imagem...")
    
    # Configurações
    API_BASE_URL = "http://localhost:8000"
    token = "seu_token_aqui"  # Substitua pelo seu token
    
    # Dados do teste
    chat_id = 24  # ID do chat que está dando erro
    image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="  # Imagem 1x1 pixel
    
    # Fazer requisição para o endpoint
    url = f"{API_BASE_URL}/api/chats/{chat_id}/enviar-imagem/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "image_data": image_data,
        "image_type": "base64",
        "caption": "Teste do endpoint"
    }
    
    print(f"📡 URL: {url}")
    print(f"📄 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        print(f"📄 Response Text: {response.text[:500]}...")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso! {result.get('mensagem')}")
            return True
        elif response.status_code == 404:
            print("❌ Endpoint não encontrado (404)")
            print("🔍 Verificando se o servidor está rodando...")
            return False
        else:
            print(f"❌ Erro: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - Servidor não está rodando")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")
        return False

def test_chat_exists():
    """Testa se o chat existe"""
    print("\n🔍 Testando se o chat existe...")
    
    API_BASE_URL = "http://localhost:8000"
    token = "seu_token_aqui"  # Substitua pelo seu token
    
    # Testar listagem de chats
    url = f"{API_BASE_URL}/api/chats/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            chats = response.json()
            print(f"📄 Chats encontrados: {len(chats.get('results', []))}")
            
            # Procurar pelo chat ID 24
            chat_24 = None
            for chat in chats.get('results', []):
                if chat.get('id') == 24:
                    chat_24 = chat
                    break
            
            if chat_24:
                print(f"✅ Chat 24 encontrado: {chat_24.get('chat_id')}")
                return True
            else:
                print("❌ Chat 24 não encontrado")
                return False
        else:
            print(f"❌ Erro ao listar chats: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar chats: {e}")
        return False

def test_server_status():
    """Testa se o servidor está rodando"""
    print("\n🔍 Testando status do servidor...")
    
    API_BASE_URL = "http://localhost:8000"
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/")
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Servidor está rodando")
            return True
        else:
            print(f"❌ Servidor retornou: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar servidor: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando testes do endpoint de imagem...")
    print("=" * 50)
    
    # Testes
    tests = [
        ("Status do Servidor", test_server_status),
        ("Chat Existe", test_chat_exists),
        ("Endpoint de Imagem", test_endpoint_imagem)
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
        print("⚠️ Alguns testes falharam. Verifique:")
        print("1. Se o servidor está rodando (python manage.py runserver)")
        print("2. Se o token está correto")
        print("3. Se o chat ID 24 existe")

if __name__ == "__main__":
    main() 