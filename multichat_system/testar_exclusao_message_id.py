#!/usr/bin/env python
"""
Script para testar a exclusão de mensagens usando message_id correto.
"""

import os
import sys
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente

def testar_exclusao_message_id():
    """Testa a exclusão de mensagens usando message_id correto"""
    
    print("🧪 Testando exclusão com message_id correto...")
    
    # 1. Buscar uma mensagem que pode ser excluída (from_me=True e com message_id)
    mensagem_test = Mensagem.objects.filter(
        from_me=True,
        message_id__isnull=False
    ).exclude(message_id='').first()
    
    if not mensagem_test:
        print("❌ Nenhuma mensagem encontrada com from_me=True e message_id")
        return
    
    print(f"✅ Mensagem encontrada para teste:")
    print(f"   - ID interno: {mensagem_test.id}")
    print(f"   - message_id: {mensagem_test.message_id}")
    print(f"   - from_me: {mensagem_test.from_me}")
    print(f"   - chat_id: {mensagem_test.chat.chat_id}")
    
    # 2. Testar endpoint da API
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/mensagens/{mensagem_test.id}/"
    
    print(f"\n🌐 Testando endpoint: {endpoint}")
    
    try:
        # Primeiro, fazer login para obter token
        login_data = {
            "email": "admin@multichat.com",
            "password": "admin123"
        }
        
        login_response = requests.post(
            f"{base_url}/api/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            print(f"   Resposta: {login_response.text}")
            return
        
        token_data = login_response.json()
        access_token = token_data.get('access')
        
        if not access_token:
            print("❌ Token de acesso não encontrado na resposta")
            return
        
        print(f"✅ Login realizado com sucesso")
        
        # 3. Testar exclusão
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        delete_response = requests.delete(endpoint, headers=headers)
        
        print(f"📡 Status da resposta: {delete_response.status_code}")
        
        try:
            response_data = delete_response.json()
            print(f"📡 Dados da resposta: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"📡 Resposta não é JSON: {delete_response.text}")
        
        if delete_response.status_code == 200:
            print("✅ Exclusão realizada com sucesso!")
            
            # Verificar se a mensagem foi realmente excluída
            try:
                Mensagem.objects.get(id=mensagem_test.id)
                print("⚠️ Mensagem ainda existe no banco (pode ser normal se a exclusão foi apenas na W-API)")
            except Mensagem.DoesNotExist:
                print("✅ Mensagem foi excluída do banco de dados")
                
        elif delete_response.status_code == 404:
            print("❌ Endpoint não encontrado (404)")
        elif delete_response.status_code == 400:
            print("❌ Erro de validação (400)")
        else:
            print(f"❌ Erro inesperado: {delete_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - verificar se o servidor está rodando")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    testar_exclusao_message_id() 