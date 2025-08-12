#!/usr/bin/env python3
"""
Script para iniciar o backend e testar envio de imagem
"""

import subprocess
import time
import requests
import json
import os
import sys

def iniciar_backend():
    """Inicia o backend Django"""
    print("🚀 Iniciando backend Django...")
    
    try:
        # Navegar para o diretório do projeto
        os.chdir("multichat_system")
        
        # Iniciar o servidor em background
        process = subprocess.Popen([
            "python", "manage.py", "runserver", "8000"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguardar um pouco para o servidor inicializar
        time.sleep(5)
        
        print("✅ Backend iniciado na porta 8000")
        return process
        
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")
        return None

def gerar_token_valido():
    """Gera um token JWT válido"""
    print("🔑 Gerando token JWT válido...")
    
    try:
        # Fazer login para obter token
        url = "http://localhost:8000/api/auth/login/"
        
        # Dados de login (substitua pelos dados reais)
        login_data = {
            "username": "admin",  # Substitua pelo usuário real
            "password": "admin123"  # Substitua pela senha real
        }
        
        response = requests.post(url, json=login_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access')
            print(f"✅ Token gerado: {token[:50]}...")
            return token
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao gerar token: {e}")
        return None

def testar_envio_imagem_com_token(token):
    """Testa o envio de imagem com token válido"""
    print("🧪 Testando envio de imagem com token válido...")
    
    if not token:
        print("❌ Token não disponível")
        return False
    
    # Dados do teste
    chat_id = 21  # Substitua pelo ID do chat real
    image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # Testar endpoint de mensagens
    url = "http://localhost:8000/api/mensagens/enviar-imagem/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "chat_id": chat_id,
        "image_data": image_data,
        "image_type": "base64",  # IMPORTANTE: Este campo é obrigatório
        "caption": "Teste com token válido"
    }
    
    print(f"📤 Enviando para: {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Envio bem-sucedido!")
            return True
        else:
            print(f"❌ Erro no envio: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def verificar_endpoints():
    """Verifica se os endpoints estão funcionando"""
    print("🔍 Verificando endpoints...")
    
    endpoints = [
        "http://localhost:8000/api/",
        "http://localhost:8000/api/mensagens/",
        "http://localhost:8000/api/chats/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

def main():
    """Função principal"""
    print("🔬 INICIANDO BACKEND E TESTANDO ENVIO DE IMAGEM")
    print("=" * 60)
    
    # Iniciar backend
    process = iniciar_backend()
    
    if not process:
        print("❌ Não foi possível iniciar o backend")
        return
    
    try:
        # Aguardar um pouco mais
        time.sleep(3)
        
        # Verificar endpoints
        verificar_endpoints()
        
        # Gerar token
        token = gerar_token_valido()
        
        if token:
            # Testar envio de imagem
            testar_envio_imagem_com_token(token)
        else:
            print("⚠️ Não foi possível gerar token válido")
            print("💡 Tente fazer login manualmente no frontend")
        
        # Aguardar input do usuário
        input("\n⏸️ Pressione Enter para parar o backend...")
        
    finally:
        # Parar o backend
        print("🛑 Parando backend...")
        process.terminate()
        process.wait()
        print("✅ Backend parado")

if __name__ == "__main__":
    main() 