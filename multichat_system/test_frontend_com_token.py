#!/usr/bin/env python3
"""
Script para testar o frontend com token válido
"""

import requests
import json

def obter_token_valido():
    """Obtém um token válido fazendo login"""
    print("🔑 Obtendo token válido...")
    
    login_data = {
        "email": "admin@multichat.com",
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
            token = data.get('access')
            print("✅ Token obtido com sucesso!")
            return token
        else:
            print(f"❌ Erro no login: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao obter token: {e}")
        return None

def testar_frontend_com_token(token):
    """Testa o frontend com token válido"""
    print(f"\n🎯 Testando frontend com token...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Testar diferentes endpoints
    endpoints = [
        "/api/mensagens/906/",
        "/api/chats/",
        "/api/clientes/",
        "/api/whatsapp-instances/"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔗 Testando: {endpoint}")
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sucesso!")
                
                # Se for mensagem, verificar tipo
                if 'tipo' in data:
                    print(f"   Tipo: {data.get('tipo')}")
                    print(f"   From Me: {data.get('fromMe')}")
                    if data.get('tipo') == 'audio':
                        print("   🎵 É uma mensagem de áudio!")
                        
            else:
                print(f"❌ Erro {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ Erro: {e}")

def testar_chats_com_audio(token):
    """Testa chats que têm mensagens de áudio"""
    print(f"\n📱 Testando chats com áudio...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Buscar chats
        response = requests.get("http://localhost:8000/api/chats/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            chats = data.get('results', [])
            
            print(f"📊 Total de chats: {len(chats)}")
            
            # Verificar chats com mensagens de áudio
            for chat in chats[:3]:  # Primeiros 3 chats
                chat_id = chat.get('id')
                chat_name = chat.get('chat_name', 'N/A')
                
                print(f"\n📱 Chat: {chat_name} (ID: {chat_id})")
                
                # Buscar mensagens do chat
                try:
                    msg_response = requests.get(f"http://localhost:8000/api/chats/{chat_id}/mensagens/", headers=headers)
                    
                    if msg_response.status_code == 200:
                        msg_data = msg_response.json()
                        mensagens = msg_data.get('results', [])
                        
                        # Contar mensagens de áudio
                        audio_count = sum(1 for msg in mensagens if msg.get('tipo') == 'audio')
                        print(f"   🎵 Mensagens de áudio: {audio_count}")
                        
                        if audio_count > 0:
                            print("   ✅ Chat tem mensagens de áudio!")
                            
                    else:
                        print(f"   ❌ Erro ao buscar mensagens: {msg_response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Erro: {e}")
                    
        else:
            print(f"❌ Erro ao buscar chats: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def simular_frontend_request(token):
    """Simula uma requisição do frontend"""
    print(f"\n🌐 Simulando requisição do frontend...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Origin': 'http://localhost:3000',
        'Referer': 'http://localhost:3000/'
    }
    
    try:
        # Simular requisição de mensagens
        response = requests.get("http://localhost:8000/api/mensagens/906/", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Frontend consegue acessar mensagem!")
            print(f"📋 Dados da mensagem:")
            print(f"   ID: {data.get('id')}")
            print(f"   Tipo: {data.get('tipo')}")
            print(f"   From Me: {data.get('fromMe')}")
            print(f"   Conteúdo: {data.get('conteudo', '')[:100]}...")
            
            # Verificar se é áudio
            if data.get('tipo') == 'audio':
                print("   🎵 Mensagem de áudio detectada!")
                
                # Verificar se tem media_url
                media_url = data.get('media_url')
                if media_url:
                    print(f"   📁 Media URL: {media_url}")
                else:
                    print("   ⚠️ Media URL não encontrada")
                    
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📄 Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    print("🚀 Testando frontend com token válido...")
    print("=" * 60)
    
    # Obter token válido
    token = obter_token_valido()
    
    if not token:
        print("❌ Não foi possível obter token válido!")
        return
    
    # Testar frontend com token
    testar_frontend_com_token(token)
    
    # Testar chats com áudio
    testar_chats_com_audio(token)
    
    # Simular requisição do frontend
    simular_frontend_request(token)
    
    print("\n" + "=" * 60)
    print("✅ Teste do frontend concluído!")

if __name__ == "__main__":
    main() 