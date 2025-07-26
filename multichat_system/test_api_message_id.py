#!/usr/bin/env python
"""
Script para testar a API e verificar se message_id está sendo retornado.
"""

import requests
import json

def test_api_message_id():
    """Testa a API para verificar se message_id está sendo retornado"""
    
    print("🧪 Testando API para message_id...")
    
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
        
        token_data = login_response.json()
        access_token = token_data.get('access')
        
        print("✅ Login realizado com sucesso")
        
        # 2. Buscar mensagens
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Testar endpoint de listagem
        list_response = requests.get(f"{base_url}/api/mensagens/", headers=headers)
        
        print(f"📡 Lista Status: {list_response.status_code}")
        
        if list_response.status_code == 200:
            response_data = list_response.json()
            
            if 'results' in response_data:
                mensagens = response_data['results']
            else:
                mensagens = response_data
            
            print(f"📊 Total de mensagens retornadas: {len(mensagens)}")
            
            # Verificar as primeiras mensagens
            for i, msg in enumerate(mensagens[:5]):
                print(f"\n📋 Mensagem {i+1}:")
                print(f"   - id: {msg.get('id')}")
                print(f"   - message_id: '{msg.get('message_id')}'")
                print(f"   - from_me: {msg.get('from_me')}")
                print(f"   - fromMe: {msg.get('fromMe')}")
                print(f"   - Campos: {list(msg.keys())}")
                
                # Verificar se message_id está presente
                if 'message_id' in msg:
                    if msg['message_id']:
                        print("   ✅ message_id presente e não vazio")
                    else:
                        print("   ⚠️ message_id presente mas vazio/null")
                else:
                    print("   ❌ message_id não presente")
            
            # 3. Testar mensagem específica
            if mensagens:
                primeira_msg = mensagens[0]
                msg_id = primeira_msg.get('id')
                
                if msg_id:
                    print(f"\n🧪 Testando mensagem específica ID: {msg_id}")
                    
                    detail_response = requests.get(
                        f"{base_url}/api/mensagens/{msg_id}/", 
                        headers=headers
                    )
                    
                    print(f"📡 Detail Status: {detail_response.status_code}")
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        print(f"📋 Dados da mensagem:")
                        print(f"   - id: {detail_data.get('id')}")
                        print(f"   - message_id: '{detail_data.get('message_id')}'")
                        print(f"   - from_me: {detail_data.get('from_me')}")
                        print(f"   - fromMe: {detail_data.get('fromMe')}")
                        print(f"   - Campos: {list(detail_data.keys())}")
                        
                        if 'message_id' in detail_data:
                            if detail_data['message_id']:
                                print("   ✅ message_id presente e não vazio")
                            else:
                                print("   ⚠️ message_id presente mas vazio/null")
                        else:
                            print("   ❌ message_id não presente")
                    else:
                        print(f"❌ Erro no detail: {detail_response.status_code}")
                        print(f"   Resposta: {detail_response.text}")
        else:
            print(f"❌ Erro na listagem: {list_response.status_code}")
            print(f"   Resposta: {list_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - verificar se o servidor está rodando na porta 8000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_api_message_id() 