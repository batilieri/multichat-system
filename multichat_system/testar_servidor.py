#!/usr/bin/env python
"""
Script para testar se o servidor está rodando
"""

import requests
import time

def testar_servidor():
    """Testa se o servidor está rodando"""
    print("🔍 Testando servidor...")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Aguardar um pouco para o servidor iniciar
    print("⏳ Aguardando servidor iniciar...")
    time.sleep(3)
    
    try:
        # Testar endpoint público
        print("📡 Testando endpoint público...")
        response = requests.get(f"{base_url}/api/test-chats/", timeout=10)
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Resposta: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Servidor está funcionando!")
            return True
        else:
            print(f"❌ Servidor retornou status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor")
        print("💡 Verifique se o servidor está rodando em http://localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout na requisição")
        print("💡 O servidor pode estar sobrecarregado ou não iniciou corretamente")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    testar_servidor() 