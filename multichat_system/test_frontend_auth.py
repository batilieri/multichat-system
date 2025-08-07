#!/usr/bin/env python3
"""
Script para testar a autenticação do frontend
"""

import requests
import json

def testar_auth_frontend():
    """Testa se o frontend consegue acessar a API com autenticação"""
    print("🔐 Testando autenticação do frontend...")
    
    # URL da API
    base_url = "http://localhost:8000/api"
    
    # Testar endpoint público primeiro
    print("\n📋 Testando endpoint público...")
    try:
        response = requests.get(f"{base_url}/test/mensagens/public/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Endpoint público funcionando!")
            print(f"📊 Total de mensagens: {data.get('total', 0)}")
            
            # Verificar primeira mensagem
            if data.get('mensagens'):
                msg = data['mensagens'][0]
                print(f"📋 Primeira mensagem:")
                print(f"   ID: {msg.get('id')}")
                print(f"   Tipo: {msg.get('tipo')}")
                print(f"   From Me: {msg.get('fromMe')}")
                print(f"   Conteúdo: {msg.get('conteudo', '')[:100]}...")
        else:
            print(f"❌ Erro no endpoint público: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar endpoint público: {e}")
    
    # Testar endpoint com autenticação
    print("\n🔐 Testando endpoint com autenticação...")
    try:
        # Simular token do frontend (você pode substituir por um token real)
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM1NzE5MjAwLCJpYXQiOjE3MzU3MTU2MDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoxfQ.example"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{base_url}/mensagens/906/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Autenticação funcionando!")
            print(f"📋 Mensagem:")
            print(f"   ID: {data.get('id')}")
            print(f"   Tipo: {data.get('tipo')}")
            print(f"   From Me: {data.get('fromMe')}")
        elif response.status_code == 401:
            print("❌ Token inválido ou expirado")
            print("💡 O frontend precisa fazer login novamente")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro ao testar autenticação: {e}")

def testar_login():
    """Testa o processo de login"""
    print("\n🔑 Testando processo de login...")
    
    # Dados de login (substitua pelos dados reais)
    login_data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login bem-sucedido!")
            print(f"🔑 Access Token: {data.get('access', '')[:50]}...")
            print(f"👤 Usuário: {data.get('user', {}).get('username', 'N/A')}")
            
            # Testar acesso com o token
            token = data.get('access')
            if token:
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get("http://localhost:8000/api/mensagens/906/", headers=headers)
                
                if response.status_code == 200:
                    print("✅ Acesso com token funcionando!")
                else:
                    print(f"❌ Erro ao acessar com token: {response.status_code}")
                    
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar login: {e}")

def main():
    """Função principal"""
    print("🚀 Testando autenticação do frontend...")
    print("=" * 60)
    
    # Testar endpoint público
    testar_auth_frontend()
    
    # Testar login
    testar_login()
    
    print("\n" + "=" * 60)
    print("✅ Teste de autenticação concluído!")

if __name__ == "__main__":
    main() 