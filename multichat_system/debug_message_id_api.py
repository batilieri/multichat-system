#!/usr/bin/env python
"""
Script para debugar o problema do message_id na API.
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

def debug_message_id_api():
    """Debuga o problema do message_id na API"""
    
    print("🔍 Debugando message_id na API...")
    print("=" * 60)
    
    # 1. Verificar mensagens no banco
    print("📊 Mensagens no banco:")
    total_mensagens = Mensagem.objects.count()
    mensagens_com_message_id = Mensagem.objects.filter(message_id__isnull=False).exclude(message_id='').count()
    mensagens_sem_message_id = Mensagem.objects.filter(message_id__isnull=True).count()
    mensagens_message_id_vazio = Mensagem.objects.filter(message_id='').count()
    
    print(f"   - Total: {total_mensagens}")
    print(f"   - Com message_id: {mensagens_com_message_id}")
    print(f"   - Sem message_id (null): {mensagens_sem_message_id}")
    print(f"   - message_id vazio: {mensagens_message_id_vazio}")
    
    # 2. Mostrar algumas mensagens com message_id
    print("\n📋 Mensagens com message_id:")
    mensagens_com_id = Mensagem.objects.filter(
        message_id__isnull=False
    ).exclude(
        message_id=''
    ).order_by('-data_envio')[:5]
    
    for msg in mensagens_com_id:
        print(f"   - ID: {msg.id}, message_id: '{msg.message_id}', from_me: {msg.from_me}")
    
    # 3. Mostrar algumas mensagens sem message_id
    print("\n📋 Mensagens sem message_id:")
    mensagens_sem_id = Mensagem.objects.filter(
        message_id__isnull=True
    ).order_by('-data_envio')[:5]
    
    for msg in mensagens_sem_id:
        print(f"   - ID: {msg.id}, message_id: {msg.message_id}, from_me: {msg.from_me}")
    
    # 4. Testar API diretamente
    if mensagens_com_id.exists():
        mensagem_teste = mensagens_com_id.first()
        print(f"\n🧪 Testando API para mensagem ID: {mensagem_teste.id}")
        
        base_url = "http://localhost:8000"
        endpoint = f"{base_url}/api/mensagens/{mensagem_teste.id}/"
        
        try:
            # Login
            login_data = {
                "email": "admin@multichat.com",
                "password": "admin123"
            }
            
            login_response = requests.post(
                f"{base_url}/api/auth/login/",
                json=login_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get('access')
                
                # Testar GET da mensagem
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                get_response = requests.get(endpoint, headers=headers)
                
                print(f"📡 GET Status: {get_response.status_code}")
                
                if get_response.status_code == 200:
                    response_data = get_response.json()
                    print(f"📡 Dados da resposta:")
                    print(f"   - id: {response_data.get('id')}")
                    print(f"   - message_id: '{response_data.get('message_id')}'")
                    print(f"   - from_me: {response_data.get('from_me')}")
                    print(f"   - fromMe: {response_data.get('fromMe')}")
                    print(f"   - Campos disponíveis: {list(response_data.keys())}")
                    
                    # Verificar se message_id está presente
                    if 'message_id' in response_data:
                        if response_data['message_id']:
                            print("✅ message_id está presente e não é vazio")
                        else:
                            print("⚠️ message_id está presente mas é vazio/null")
                    else:
                        print("❌ message_id não está presente na resposta")
                else:
                    print(f"❌ Erro no GET: {get_response.status_code}")
                    print(f"   Resposta: {get_response.text}")
                    
            else:
                print(f"❌ Erro no login: {login_response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Erro de conexão - verificar se o servidor está rodando")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
    
    # 5. Verificar se há mensagens com ID específico do erro
    print(f"\n🔍 Verificando mensagem ID: 1753569616123")
    try:
        mensagem_erro = Mensagem.objects.get(id=1753569616123)
        print(f"   - Encontrada: Sim")
        print(f"   - message_id: '{mensagem_erro.message_id}'")
        print(f"   - from_me: {mensagem_erro.from_me}")
        print(f"   - chat_id: {mensagem_erro.chat.chat_id}")
    except Mensagem.DoesNotExist:
        print(f"   - Encontrada: Não (não existe no banco)")

if __name__ == "__main__":
    debug_message_id_api() 