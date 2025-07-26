#!/usr/bin/env python
"""
Script para debugar especificamente o problema do message_id no frontend.
"""

import requests
import json

def debug_frontend_message_id():
    """Debuga especificamente o problema do message_id no frontend"""
    
    print("🔍 Debugando message_id no frontend...")
    
    base_url = "http://localhost:8000"
    
    try:
        # 1. Login
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
            return
        
        token = login_response.json().get('access')
        print("✅ Login realizado com sucesso")
        
        # 2. Buscar mensagens
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Buscar mensagens que podem ser excluídas (from_me=True)
        response = requests.get(
            f"{base_url}/api/mensagens/?from_me=true&limit=5",
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Erro ao buscar mensagens: {response.status_code}")
            return
        
        data = response.json()
        messages = data.get('results', data)
        
        print(f"📊 Total de mensagens: {len(messages)}")
        
        # 3. Verificar cada mensagem
        for i, msg in enumerate(messages[:3]):
            print(f"\n📋 Mensagem {i+1}:")
            print(f"   - id: {msg.get('id')}")
            print(f"   - message_id: {msg.get('message_id')}")
            print(f"   - from_me: {msg.get('from_me')}")
            print(f"   - fromMe: {msg.get('fromMe')}")
            
            # Verificar se message_id está presente
            if msg.get('message_id'):
                print(f"   ✅ message_id presente: {msg.get('message_id')}")
                
                # Testar exclusão
                print(f"   🧪 Testando exclusão...")
                delete_response = requests.delete(
                    f"{base_url}/api/mensagens/{msg.get('message_id')}/",
                    headers=headers
                )
                
                print(f"   📡 Status da exclusão: {delete_response.status_code}")
                if delete_response.status_code == 204:
                    print(f"   ✅ Exclusão bem-sucedida!")
                else:
                    print(f"   ❌ Erro na exclusão: {delete_response.text}")
            else:
                print(f"   ❌ message_id ausente ou vazio")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    debug_frontend_message_id() 