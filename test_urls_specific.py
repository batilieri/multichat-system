#!/usr/bin/env python3
"""
Teste específico das URLs da API
"""

import requests
import json

def test_api_urls():
    """Testa URLs específicas da API"""
    
    API_BASE_URL = "http://localhost:8000"
    
    print("🔍 Testando URLs da API...")
    
    # URLs para testar
    urls_to_test = [
        "/api/",
        "/api/chats/",
        "/api/chats/21/",
        "/api/chats/21/enviar-imagem/",
        "/api/mensagens/",
        "/api/mensagens/1/reagir/",
        "/api/mensagens/1/remover-reacao/",
    ]
    
    for url in urls_to_test:
        try:
            response = requests.get(f"{API_BASE_URL}{url}", timeout=5)
            print(f"🔗 {url}: {response.status_code}")
            
            if response.status_code == 404:
                print(f"   ❌ 404 - URL não encontrada")
            elif response.status_code == 401:
                print(f"   ✅ 401 - URL existe (autenticação necessária)")
            elif response.status_code == 200:
                print(f"   ✅ 200 - URL funciona")
            else:
                print(f"   ⚠️ {response.status_code} - Status inesperado")
                
        except Exception as e:
            print(f"🔗 {url}: ERRO - {e}")
    
    # Teste específico do endpoint de imagem
    print("\n📸 Teste específico do endpoint de imagem:")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chats/21/enviar-imagem/",
            json={"test": "data"},
            timeout=5
        )
        print(f"POST /api/chats/21/enviar-imagem/: {response.status_code}")
        
        if response.status_code == 404:
            print("❌ Endpoint não encontrado - problema de registro de URL")
        elif response.status_code == 401:
            print("✅ Endpoint existe - autenticação necessária")
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando teste de URLs...")
    test_api_urls()
    print("\n✅ Teste concluído!") 