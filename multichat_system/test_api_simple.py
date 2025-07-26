#!/usr/bin/env python3
"""
Script simples para testar a API de chats
"""

import os
import sys
import django
import requests
import json

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

def test_api():
    """
    Testa a API de chats
    """
    print("🌐 Testando API de chats...")
    
    try:
        # Fazer requisição para o endpoint público
        response = requests.get('http://localhost:8000/api/test-chats/', timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API funcionando!")
            print(f"Status: {data.get('status')}")
            print(f"Mensagem: {data.get('message')}")
            print(f"Total de chats: {data.get('total_chats', 0)}")
            
            # Mostrar informações dos chats
            chats = data.get('chats', [])
            for i, chat in enumerate(chats[:3]):
                print(f"\n💬 Chat {i+1}:")
                print(f"   Nome: {chat.get('chat_name', 'N/A')}")
                print(f"   ID: {chat.get('chat_id', 'N/A')}")
                print(f"   Foto de perfil: {chat.get('foto_perfil', 'N/A')}")
                print(f"   Profile picture: {chat.get('profile_picture', 'N/A')}")
                print(f"   É grupo: {chat.get('is_group', False)}")
                print(f"   Cliente: {chat.get('cliente_nome', 'N/A')}")
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"Conteúdo: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API. Verifique se o servidor está rodando.")
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")

if __name__ == "__main__":
    test_api() 