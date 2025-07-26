#!/usr/bin/env python3
"""
Script para testar a API via HTTP
MultiChat System - Teste da API HTTP

Este script:
1. Testa a API de mensagens via HTTP
2. Verifica se as mensagens estão sendo retornadas corretamente
3. Testa a autenticação
"""

import requests
import json
from datetime import datetime

class APITester:
    """Testador da API via HTTP"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.token = None
        self.setup_auth()
    
    def setup_auth(self):
        """Configura autenticação"""
        try:
            # Tentar fazer login
            login_data = {
                "email": "admin@multichat.com",
                "password": "admin123"
            }
            
            response = requests.post(f"{self.base_url}/api/auth/login/", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access')
                print(f"✅ Autenticação bem-sucedida")
            else:
                print(f"❌ Erro na autenticação: {response.status_code}")
                print(f"Resposta: {response.text}")
        except Exception as e:
            print(f"❌ Erro ao configurar autenticação: {e}")
    
    def test_chats_api(self):
        """Testa a API de chats"""
        print("🔍 Testando API de chats...")
        print("=" * 50)
        
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            response = requests.get(f"{self.base_url}/api/chats/", headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chats encontrados: {len(data.get('results', data))}")
                
                # Mostrar alguns chats
                chats = data.get('results', data)
                for chat in chats[:3]:
                    print(f"   📱 {chat.get('chat_id')} - {chat.get('chat_name')} - {chat.get('total_mensagens')} mensagens")
            else:
                print(f"❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro ao testar API de chats: {e}")
    
    def test_mensagens_api(self):
        """Testa a API de mensagens"""
        print("\n🔍 Testando API de mensagens...")
        print("=" * 50)
        
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        # Primeiro, buscar um chat
        try:
            response = requests.get(f"{self.base_url}/api/chats/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                chats = data.get('results', data)
                
                if chats:
                    # Buscar um chat com mais mensagens
                    chat_com_mensagens = None
                    for c in chats:
                        if c.get('total_mensagens', 0) > 10:
                            chat_com_mensagens = c
                            break
                    
                    chat = chat_com_mensagens or chats[0]
                    chat_id = chat.get('chat_id')
                    total_mensagens = chat.get('total_mensagens', 0)
                    print(f"📱 Testando mensagens do chat: {chat_id} ({total_mensagens} mensagens)")
                    
                    # Buscar mensagens do chat
                    response = requests.get(
                        f"{self.base_url}/api/mensagens/?chat_id={chat_id}", 
                        headers=headers
                    )
                    
                    print(f"Status: {response.status_code}")
                    
                    if response.status_code == 200:
                        data = response.json()
                        mensagens = data.get('results', data)
                        print(f"✅ Mensagens encontradas: {len(mensagens)}")
                        
                        # Mostrar algumas mensagens
                        for msg in mensagens[:3]:
                            print(f"   💬 {msg.get('id')} - {msg.get('conteudo', '')[:50]}... - FromMe: {msg.get('from_me')}")
                    else:
                        print(f"❌ Erro: {response.text}")
                else:
                    print("❌ Nenhum chat encontrado")
            else:
                print(f"❌ Erro ao buscar chats: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro ao testar API de mensagens: {e}")
    
    def test_public_endpoint(self):
        """Testa endpoint público"""
        print("\n🔍 Testando endpoint público...")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.base_url}/api/test-chats/")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Endpoint público funcionando")
                print(f"   Chats: {data.get('total_chats')}")
            else:
                print(f"❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro ao testar endpoint público: {e}")
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("🧪 MultiChat System - Teste da API HTTP")
        print("=" * 60)
        
        self.test_public_endpoint()
        self.test_chats_api()
        self.test_mensagens_api()
        
        print("\n" + "=" * 60)
        print("🏁 Teste concluído!")

def main():
    """Função principal"""
    tester = APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 