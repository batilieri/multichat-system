#!/usr/bin/env python3
"""
Script para verificar e obter token válido da W-API.

Este script ajuda a:
1. Verificar se o token atual é válido
2. Gerar novo QR Code se necessário
3. Testar diferentes formatos de autenticação
4. Verificar status da instância

Autor: Sistema MultiChat
Data: 2025-01-09
"""

import requests
import json

def verificar_token_atual():
    """Verifica se o token atual é válido"""
    
    # Configurações atuais
    INSTANCE_ID = "3B6XIW-ZTS923-GEAY6V"
    TOKEN_ATUAL = "Q8EOH07SJkXhg4iT6Qmhz1BJdLl8nL9WF"
    
    base_url = "https://api.w-api.app/v1"
    
    print("🔍 VERIFICANDO TOKEN ATUAL")
    print("=" * 50)
    print(f"Instance ID: {INSTANCE_ID}")
    print(f"Token: {TOKEN_ATUAL}")
    print("-" * 50)
    
    # Testar diferentes formatos de headers
    headers_formats = [
        {"Authorization": f"Bearer {TOKEN_ATUAL}"},
        {"Authorization": f"token {TOKEN_ATUAL}"},
        {"Authorization": TOKEN_ATUAL},
        {"X-API-Key": TOKEN_ATUAL},
        {"api-key": TOKEN_ATUAL}
    ]
    
    for i, headers in enumerate(headers_formats, 1):
        print(f"\n{i}️⃣ Testando formato: {list(headers.keys())[0]}")
        
        try:
            # Testar endpoint de status
            url = f"{base_url}/instance/status-instance"
            params = {"instanceId": INSTANCE_ID}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCESSO! Instância conectada: {data.get('connected', False)}")
                return {"success": True, "headers": headers, "data": data}
            else:
                print(f"   ❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Erro na requisição: {str(e)}")
    
    return {"success": False, "message": "Nenhum formato de autenticação funcionou"}

def gerar_novo_qr_code():
    """Tenta gerar um novo QR Code"""
    
    INSTANCE_ID = "3B6XIW-ZTS923-GEAY6V"
    TOKEN = "Q8EOH07SJkXhg4iT6Qmhz1BJdLl8nL9WF"
    
    base_url = "https://api.w-api.app/v1"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    print("\n🔄 TENTANDO GERAR NOVO QR CODE")
    print("=" * 50)
    
    try:
        url = f"{base_url}/instance/qr-code"
        params = {"instanceId": INSTANCE_ID}
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('qrcode'):
                print("✅ QR Code gerado! Você pode precisar escanear novamente.")
                return True
            else:
                print("⚠️ QR Code não disponível - pode estar conectado")
                return False
        else:
            print(f"❌ Erro ao gerar QR Code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {str(e)}")
        return False

def verificar_instancia_existe():
    """Verifica se a instância existe"""
    
    INSTANCE_ID = "3B6XIW-ZTS923-GEAY6V"
    
    print("\n🔍 VERIFICANDO SE A INSTÂNCIA EXISTE")
    print("=" * 50)
    print(f"Instance ID: {INSTANCE_ID}")
    
    # Tentar sem autenticação primeiro
    base_url = "https://api.w-api.app/v1"
    
    try:
        url = f"{base_url}/instance/status-instance"
        params = {"instanceId": INSTANCE_ID}
        
        response = requests.get(url, params=params, timeout=10)
        print(f"Status sem autenticação: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ Instância existe, mas precisa de autenticação")
            return True
        elif response.status_code == 404:
            print("❌ Instância não encontrada")
            return False
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {str(e)}")
        return None

def instrucoes_solucao():
    """Fornece instruções para resolver o problema"""
    
    print("\n💡 INSTRUÇÕES PARA RESOLVER O PROBLEMA")
    print("=" * 60)
    
    print("""
1️⃣ VERIFICAR CREDENCIAIS:
   - Acesse o painel da W-API (https://w-api.app)
   - Verifique se a instância {INSTANCE_ID} ainda existe
   - Confirme se o token está correto e não expirou

2️⃣ SE A INSTÂNCIA NÃO EXISTE:
   - Crie uma nova instância no painel da W-API
   - Anote o novo Instance ID e Token
   - Use as novas credenciais

3️⃣ SE O TOKEN EXPIROU:
   - Gere um novo token no painel da W-API
   - Substitua o token antigo pelo novo

4️⃣ SE A INSTÂNCIA ESTÁ DESCONECTADA:
   - Gere um novo QR Code
   - Escaneie com o WhatsApp
   - Aguarde a conexão

5️⃣ TESTAR NOVAMENTE:
   - Execute este script novamente
   - Verifique se a autenticação funciona

6️⃣ ALTERNATIVA - CRIAR NOVA INSTÂNCIA:
   - Se nada funcionar, crie uma nova instância
   - Use as novas credenciais no sistema MultiChat
""")

def main():
    """Função principal"""
    
    print("🚀 VERIFICADOR DE TOKEN W-API")
    print("=" * 60)
    
    # 1. Verificar se a instância existe
    instancia_existe = verificar_instancia_existe()
    
    # 2. Verificar token atual
    resultado_token = verificar_token_atual()
    
    # 3. Se o token não funcionou, tentar gerar QR Code
    if not resultado_token.get("success"):
        print("\n🔄 Token inválido, tentando gerar QR Code...")
        qr_sucesso = gerar_novo_qr_code()
        
        if qr_sucesso:
            print("\n✅ QR Code gerado! Tente escanear e testar novamente.")
        else:
            print("\n❌ Não foi possível gerar QR Code.")
    
    # 4. Fornecer instruções
    instrucoes_solucao()
    
    # 5. Resumo
    print("\n📋 RESUMO")
    print("=" * 30)
    if resultado_token.get("success"):
        print("✅ Token válido! Você pode usar as funcionalidades de chat.")
    else:
        print("❌ Token inválido. Siga as instruções acima para resolver.")

if __name__ == "__main__":
    main() 