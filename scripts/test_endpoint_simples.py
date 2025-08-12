#!/usr/bin/env python3
"""
Teste simples do endpoint de envio de imagem
"""

import requests
import json

def test_endpoint():
    """Testa o endpoint de envio de imagem"""
    
    # Configurações
    API_BASE_URL = "http://localhost:8000"
    chat_id = 21  # ID do chat que está dando erro
    
    print(f"🧪 Testando endpoint de envio de imagem...")
    print(f"🌐 API URL: {API_BASE_URL}")
    print(f"📱 Chat ID: {chat_id}")
    
    # Teste 1: Verificar se o servidor está rodando
    try:
        response = requests.get(f"{API_BASE_URL}/api/", timeout=5)
        print(f"✅ Servidor respondendo: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando na porta 8000")
        return False
    except Exception as e:
        print(f"❌ Erro ao conectar com servidor: {e}")
        return False
    
    # Teste 2: Verificar se o endpoint existe (sem autenticação)
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chats/{chat_id}/enviar-imagem/",
            json={
                'image_data': 'teste',
                'image_type': 'base64',
                'caption': 'Teste'
            }
        )
        print(f"📸 Endpoint imagem status: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Endpoint existe (erro esperado - sem autenticação)")
        elif response.status_code == 404:
            print("❌ Endpoint não encontrado (404)")
            print("🔍 Verificando se o servidor Django está rodando...")
            
            # Verificar se o servidor Django está rodando
            try:
                response = requests.get(f"{API_BASE_URL}/admin/", timeout=5)
                print(f"📊 Admin Django status: {response.status_code}")
            except Exception as e:
                print(f"❌ Erro ao acessar admin Django: {e}")
                
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            print(f"Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando teste simples do endpoint...")
    success = test_endpoint()
    
    if success:
        print("\n✅ Teste concluído!")
    else:
        print("\n❌ Teste falhou!") 