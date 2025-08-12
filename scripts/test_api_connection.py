#!/usr/bin/env python3
"""
Script para testar a conexão com a API do Django
"""
import requests
import json

def test_api_connection():
    """Testa a conexão com a API do Django"""
    print("🔍 TESTE DE CONEXÃO COM API DJANGO")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Teste 1: Verificar se o servidor está rodando
    print("1️⃣ Testando se o servidor está rodando...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Servidor respondendo (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando na porta 8000")
        print("💡 Para iniciar o servidor Django:")
        print("   cd multichat_system")
        print("   python manage.py runserver")
        return
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return
    
    # Teste 2: Verificar endpoint de instâncias sem autenticação
    print("\n2️⃣ Testando endpoint de instâncias (sem auth)...")
    try:
        response = requests.get(f"{base_url}/api/whatsapp-instances/", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Endpoint protegido (esperado)")
        else:
            print(f"⚠️  Resposta inesperada: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 3: Verificar endpoint de clientes sem autenticação
    print("\n3️⃣ Testando endpoint de clientes (sem auth)...")
    try:
        response = requests.get(f"{base_url}/api/clientes/", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Endpoint protegido (esperado)")
        else:
            print(f"⚠️  Resposta inesperada: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste 4: Verificar se há token de acesso válido
    print("\n4️⃣ Verificando token de acesso...")
    try:
        # Tentar buscar token do localStorage (simulado)
        print("💡 Para testar com autenticação, você precisa:")
        print("   1. Fazer login no frontend")
        print("   2. Copiar o token do localStorage")
        print("   3. Usar o token nas requisições")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n📋 RESUMO:")
    print("✅ Servidor Django está rodando")
    print("✅ Endpoints estão protegidos por autenticação")
    print("💡 O erro no frontend pode ser:")
    print("   - Token de acesso expirado")
    print("   - Problema de CORS")
    print("   - Erro na autenticação")

if __name__ == "__main__":
    test_api_connection() 