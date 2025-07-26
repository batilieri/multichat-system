#!/usr/bin/env python
"""
Script para testar se o frontend está recebendo message_id corretamente.
"""

import requests
import json

def test_frontend_message_id():
    """Testa se o frontend está recebendo message_id corretamente"""
    
    print("🧪 Testando frontend message_id...")
    
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
        
        # 2. Buscar chats primeiro
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        chats_response = requests.get(f"{base_url}/api/chats/", headers=headers)
        
        if chats_response.status_code != 200:
            print(f"❌ Erro ao buscar chats: {chats_response.status_code}")
            return
        
        chats_data = chats_response.json()
        chats = chats_data.get('results', chats_data)
        
        if not chats:
            print("❌ Nenhum chat encontrado")
            return
        
        # 3. Buscar mensagens do primeiro chat
        primeiro_chat = chats[0]
        chat_id = primeiro_chat.get('chat_id')
        
        print(f"📱 Testando chat: {chat_id}")
        
        mensagens_response = requests.get(
            f"{base_url}/api/mensagens/?chat_id={chat_id}&limit=10", 
            headers=headers
        )
        
        if mensagens_response.status_code != 200:
            print(f"❌ Erro ao buscar mensagens: {mensagens_response.status_code}")
            return
        
        mensagens_data = mensagens_response.json()
        mensagens = mensagens_data.get('results', mensagens_data)
        
        print(f"📊 Total de mensagens: {len(mensagens)}")
        
        # 4. Verificar cada mensagem
        for i, msg in enumerate(mensagens):
            print(f"\n📋 Mensagem {i+1}:")
            print(f"   - id: {msg.get('id')}")
            print(f"   - message_id: '{msg.get('message_id')}'")
            print(f"   - from_me: {msg.get('from_me')}")
            print(f"   - fromMe: {msg.get('fromMe')}")
            print(f"   - remetente: {msg.get('remetente')}")
            print(f"   - tipo: {msg.get('tipo')}")
            
            # Verificar se message_id está presente
            if 'message_id' in msg:
                if msg['message_id']:
                    print("   ✅ message_id presente e não vazio")
                else:
                    print("   ⚠️ message_id presente mas vazio/null")
            else:
                print("   ❌ message_id não presente")
        
        # 5. Testar mensagem específica para exclusão
        mensagens_com_message_id = [msg for msg in mensagens if msg.get('message_id')]
        
        if mensagens_com_message_id:
            msg_teste = mensagens_com_message_id[0]
            print(f"\n🧪 Testando mensagem para exclusão:")
            print(f"   - ID interno: {msg_teste.get('id')}")
            print(f"   - message_id: {msg_teste.get('message_id')}")
            print(f"   - from_me: {msg_teste.get('from_me')}")
            
            if msg_teste.get('from_me'):
                print("   ✅ Mensagem pode ser excluída (from_me=True)")
            else:
                print("   ⚠️ Mensagem não pode ser excluída (from_me=False)")
        else:
            print("\n❌ Nenhuma mensagem com message_id encontrada")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - verificar se o servidor está rodando na porta 8000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_frontend_message_id() 