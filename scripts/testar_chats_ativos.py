#!/usr/bin/env python3
"""
Script para testar a busca de chats ativos no WhatsApp usando a API W-API.

Este script demonstra como:
1. Buscar todos os chats ativos de uma instância
2. Obter informações detalhadas de um chat específico
3. Verificar presença/status de um chat

Autor: Sistema MultiChat
Data: 2025-01-09
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, List

class WApiChatsTester:
    """
    Classe para testar funcionalidades de chats da W-API
    """
    
    def __init__(self, instance_id: str, token: str):
        """
        Inicializa o tester com credenciais da W-API
        
        Args:
            instance_id (str): ID da instância do WhatsApp
            token (str): Token de autenticação
        """
        self.instance_id = instance_id
        self.token = token
        self.base_url = "https://api.w-api.app/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def buscar_chats_ativos(self, per_page: int = 20, page: int = 1) -> Dict[str, Any]:
        """
        Busca todos os chats ativos da instância
        
        Args:
            per_page (int): Número de chats por página
            page (int): Número da página
            
        Returns:
            Dict[str, Any]: Dados dos chats encontrados
        """
        url = f"{self.base_url}/chats/fetch-chats"
        params = {
            "instanceId": self.instance_id,
            "perPage": per_page,
            "page": page
        }
        
        try:
            print(f"🔍 Buscando chats ativos... (página {page})")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                dados = response.json()
                return {
                    "success": True,
                    "data": dados,
                    "message": "Chats encontrados com sucesso"
                }
            else:
                return {
                    "success": False,
                    "message": f"Erro {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro na requisição: {str(e)}"
            }
    
    def obter_chat_especifico(self, phone_number: str) -> Dict[str, Any]:
        """
        Obtém informações detalhadas de um chat específico
        
        Args:
            phone_number (str): Número do telefone ou ID do chat
            
        Returns:
            Dict[str, Any]: Informações do chat
        """
        url = f"{self.base_url}/chats/chat"
        params = {
            "instanceId": self.instance_id,
            "phoneNumber": phone_number
        }
        
        try:
            print(f"🔍 Buscando informações do chat: {phone_number}")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                dados = response.json()
                return {
                    "success": True,
                    "data": dados,
                    "message": "Chat encontrado com sucesso"
                }
            else:
                return {
                    "success": False,
                    "message": f"Erro {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro na requisição: {str(e)}"
            }
    
    def verificar_presenca_chat(self, phone_number: str, presence: str = "composing", delay: int = 15) -> Dict[str, Any]:
        """
        Envia sinal de presença para um chat (digitando, gravando, etc.)
        
        Args:
            phone_number (str): Número do telefone
            presence (str): Tipo de presença ('composing', 'recording')
            delay (int): Duração da presença em segundos
            
        Returns:
            Dict[str, Any]: Resultado da operação
        """
        url = f"{self.base_url}/chats/send-presence"
        params = {"instanceId": self.instance_id}
        payload = {
            "phone": phone_number,
            "presence": presence,
            "delay": delay
        }
        
        try:
            print(f"🔍 Enviando presença '{presence}' para: {phone_number}")
            response = requests.post(url, headers=self.headers, params=params, json=payload, timeout=30)
            
            if response.status_code == 200:
                dados = response.json()
                return {
                    "success": True,
                    "data": dados,
                    "message": "Presença enviada com sucesso"
                }
            else:
                return {
                    "success": False,
                    "message": f"Erro {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro na requisição: {str(e)}"
            }
    
    def exibir_chats_formatados(self, dados_chats: Dict[str, Any]) -> None:
        """
        Exibe os chats de forma formatada e legível
        
        Args:
            dados_chats (Dict[str, Any]): Dados dos chats retornados pela API
        """
        if not dados_chats.get("success"):
            print(f"❌ Erro: {dados_chats.get('message')}")
            return
        
        data = dados_chats["data"]
        total_chats = data.get('totalChats', 0)
        current_page = data.get('currentPage', 1)
        total_pages = data.get('totalPages', 1)
        
        print(f"\n📊 RESUMO DOS CHATS")
        print(f"Total de Chats: {total_chats}")
        print(f"Página Atual: {current_page} de {total_pages}")
        print("=" * 60)
        
        chats = data.get('chats', [])
        if not chats:
            print("📭 Nenhum chat encontrado")
            return
        
        for idx, chat in enumerate(chats, start=1):
            chat_id = chat.get('id', 'Sem ID')
            name = chat.get('name', 'Sem Nome')
            
            # Converter timestamp para data legível
            last_msg_time = chat.get('lastMessageTime')
            if last_msg_time:
                try:
                    last_msg_time = datetime.fromtimestamp(last_msg_time).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    last_msg_time = 'Data inválida'
            else:
                last_msg_time = 'Sem mensagens'
            
            print(f"\n{idx}. 📱 {name}")
            print(f"   ID: {chat_id}")
            print(f"   Última Mensagem: {last_msg_time}")
            
            # Informações adicionais se disponíveis
            if chat.get('profilePictureUrl'):
                print(f"   📸 Tem foto de perfil")
            
            if chat.get('about'):
                print(f"   ℹ️  Sobre: {chat.get('about')}")
    
    def exibir_chat_detalhado(self, dados_chat: Dict[str, Any]) -> None:
        """
        Exibe informações detalhadas de um chat específico
        
        Args:
            dados_chat (Dict[str, Any]): Dados do chat retornados pela API
        """
        if not dados_chat.get("success"):
            print(f"❌ Erro: {dados_chat.get('message')}")
            return
        
        data = dados_chat["data"]
        chat_info = data.get('chat', {})
        
        print(f"\n📋 INFORMAÇÕES DETALHADAS DO CHAT")
        print("=" * 50)
        
        for chave, valor in chat_info.items():
            if chave == 'lastMessageTime' and valor:
                try:
                    valor = datetime.fromtimestamp(valor).strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            
            print(f"{chave}: {valor}")


def main():
    """
    Função principal para demonstrar o uso das funcionalidades
    """
    print("🚀 TESTE DE BUSCA DE CHATS ATIVOS - W-API")
    print("=" * 60)
    
    # Configurações - Credenciais reais fornecidas pelo usuário
    INSTANCE_ID = "3B6XIW-ZTS923-GEAY6V"
    TOKEN = "Q8EOH07SJkXhg4iT6Qmhz1BJdLl8nL9WF"
    
    # Criar instância do tester
    tester = WApiChatsTester(INSTANCE_ID, TOKEN)
    
    # 1. Buscar todos os chats ativos
    print("\n1️⃣ BUSCANDO TODOS OS CHATS ATIVOS")
    print("-" * 40)
    
    resultado_chats = tester.buscar_chats_ativos(per_page=10, page=1)
    tester.exibir_chats_formatados(resultado_chats)
    
    # 2. Se encontrou chats, buscar informações detalhadas do primeiro
    if resultado_chats.get("success") and resultado_chats["data"].get('chats'):
        primeiro_chat = resultado_chats["data"]['chats'][0]
        chat_id = primeiro_chat.get('id')
        
        print(f"\n2️⃣ INFORMAÇÕES DETALHADAS DO PRIMEIRO CHAT")
        print("-" * 40)
        
        resultado_detalhado = tester.obter_chat_especifico(chat_id)
        tester.exibir_chat_detalhado(resultado_detalhado)
        
        # 3. Testar envio de presença (opcional)
        print(f"\n3️⃣ TESTE DE PRESENÇA (OPCIONAL)")
        print("-" * 40)
        
        resposta = input("Deseja testar envio de presença? (s/n): ").lower()
        if resposta == 's':
            resultado_presenca = tester.verificar_presenca_chat(chat_id, "composing", 5)
            if resultado_presenca.get("success"):
                print("✅ Presença enviada com sucesso!")
            else:
                print(f"❌ Erro ao enviar presença: {resultado_presenca.get('message')}")
    
    print(f"\n✅ Teste concluído!")
    print("💡 Dica: Use estas funcionalidades no seu sistema MultiChat para sincronizar chats")


if __name__ == "__main__":
    main() 