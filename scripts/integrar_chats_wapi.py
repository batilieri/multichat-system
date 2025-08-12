#!/usr/bin/env python3
"""
Script para integrar a busca de chats ativos da W-API com o sistema MultiChat.

Este script:
1. Busca chats ativos da W-API
2. Sincroniza com o banco de dados do MultiChat
3. Atualiza informações dos chats existentes
4. Cria novos chats se necessário

Autor: Sistema MultiChat
Data: 2025-01-09
"""

import os
import sys
import django
from datetime import datetime
from typing import Dict, Any, List

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

import requests
from core.models import Cliente, WhatsappInstance, Chat
from authentication.models import Usuario


class WApiChatsIntegrator:
    """
    Classe para integrar chats da W-API com o sistema MultiChat
    """
    
    def __init__(self, instance_id: str, token: str, cliente_id: int = None):
        """
        Inicializa o integrador
        
        Args:
            instance_id (str): ID da instância do WhatsApp
            token (str): Token de autenticação
            cliente_id (int, opcional): ID do cliente no sistema MultiChat
        """
        self.instance_id = instance_id
        self.token = token
        self.cliente_id = cliente_id
        self.base_url = "https://api.w-api.app/v1"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Buscar cliente se não fornecido
        if not self.cliente_id:
            self.cliente_id = self._buscar_cliente_por_instancia()
    
    def _buscar_cliente_por_instancia(self) -> int:
        """
        Busca o cliente associado à instância
        
        Returns:
            int: ID do cliente
        """
        try:
            instancia = WhatsappInstance.objects.get(instance_id=self.instance_id)
            return instancia.cliente.id
        except WhatsappInstance.DoesNotExist:
            print(f"❌ Instância {self.instance_id} não encontrada no sistema MultiChat")
            return None
    
    def buscar_chats_wapi(self, per_page: int = 50, page: int = 1) -> Dict[str, Any]:
        """
        Busca chats da W-API
        
        Args:
            per_page (int): Número de chats por página
            page (int): Número da página
            
        Returns:
            Dict[str, Any]: Dados dos chats
        """
        url = f"{self.base_url}/chats/fetch-chats"
        params = {
            "instanceId": self.instance_id,
            "perPage": per_page,
            "page": page
        }
        
        try:
            print(f"🔍 Buscando chats da W-API (página {page})...")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
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
    
    def obter_chat_detalhado_wapi(self, chat_id: str) -> Dict[str, Any]:
        """
        Obtém informações detalhadas de um chat da W-API
        
        Args:
            chat_id (str): ID do chat
            
        Returns:
            Dict[str, Any]: Informações do chat
        """
        url = f"{self.base_url}/chats/chat"
        params = {
            "instanceId": self.instance_id,
            "phoneNumber": chat_id
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
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
    
    def sincronizar_chats(self, max_pages: int = 5) -> Dict[str, Any]:
        """
        Sincroniza todos os chats da W-API com o banco de dados
        
        Args:
            max_pages (int): Número máximo de páginas para buscar
            
        Returns:
            Dict[str, Any]: Resultado da sincronização
        """
        if not self.cliente_id:
            return {
                "success": False,
                "message": "Cliente não encontrado para esta instância"
            }
        
        try:
            cliente = Cliente.objects.get(id=self.cliente_id)
        except Cliente.DoesNotExist:
            return {
                "success": False,
                "message": f"Cliente com ID {self.cliente_id} não encontrado"
            }
        
        total_chats_processados = 0
        total_chats_criados = 0
        total_chats_atualizados = 0
        erros = []
        
        print(f"🔄 Iniciando sincronização de chats para cliente: {cliente.nome}")
        
        # Buscar todas as páginas
        for page in range(1, max_pages + 1):
            resultado = self.buscar_chats_wapi(per_page=50, page=page)
            
            if not resultado.get("success"):
                erros.append(f"Página {page}: {resultado.get('message')}")
                continue
            
            dados = resultado["data"]
            chats = dados.get('chats', [])
            
            if not chats:
                print(f"📭 Página {page}: Nenhum chat encontrado")
                break
            
            print(f"📱 Página {page}: Processando {len(chats)} chats...")
            
            # Processar cada chat
            for chat_wapi in chats:
                try:
                    resultado_processamento = self._processar_chat_individual(
                        chat_wapi, cliente
                    )
                    
                    if resultado_processamento["success"]:
                        total_chats_processados += 1
                        if resultado_processamento["criado"]:
                            total_chats_criados += 1
                        else:
                            total_chats_atualizados += 1
                    else:
                        erros.append(f"Chat {chat_wapi.get('id')}: {resultado_processamento['message']}")
                        
                except Exception as e:
                    erros.append(f"Chat {chat_wapi.get('id')}: Erro inesperado - {str(e)}")
            
            # Verificar se há mais páginas
            current_page = dados.get('currentPage', page)
            total_pages = dados.get('totalPages', 1)
            
            if current_page >= total_pages:
                break
        
        return {
            "success": True,
            "total_processados": total_chats_processados,
            "total_criados": total_chats_criados,
            "total_atualizados": total_chats_atualizados,
            "erros": erros,
            "cliente": cliente.nome
        }
    
    def _processar_chat_individual(self, chat_wapi: Dict[str, Any], cliente: Cliente) -> Dict[str, Any]:
        """
        Processa um chat individual da W-API
        
        Args:
            chat_wapi (Dict[str, Any]): Dados do chat da W-API
            cliente (Cliente): Cliente do sistema MultiChat
            
        Returns:
            Dict[str, Any]: Resultado do processamento
        """
        chat_id = chat_wapi.get('id')
        chat_name = chat_wapi.get('name', 'Sem Nome')
        
        # Converter timestamp para datetime
        last_message_time = None
        if chat_wapi.get('lastMessageTime'):
            try:
                last_message_time = datetime.fromtimestamp(chat_wapi['lastMessageTime'])
            except:
                pass
        
        # Verificar se o chat já existe
        try:
            chat_existente = Chat.objects.get(
                chat_id=chat_id,
                cliente=cliente
            )
            
            # Atualizar informações
            atualizacoes = {}
            
            if chat_name and chat_name != chat_existente.chat_name:
                chat_existente.chat_name = chat_name
                atualizacoes['chat_name'] = chat_name
            
            if last_message_time and (
                not chat_existente.last_message_at or 
                last_message_time > chat_existente.last_message_at
            ):
                chat_existente.last_message_at = last_message_time
                atualizacoes['last_message_at'] = last_message_time
            
            # Atualizar foto de perfil se disponível
            if chat_wapi.get('profilePictureUrl'):
                chat_existente.foto_perfil = chat_wapi['profilePictureUrl']
                atualizacoes['foto_perfil'] = chat_wapi['profilePictureUrl']
            
            if atualizacoes:
                chat_existente.save()
                print(f"  ✅ Chat atualizado: {chat_name}")
            
            return {
                "success": True,
                "criado": False,
                "message": "Chat atualizado"
            }
            
        except Chat.DoesNotExist:
            # Criar novo chat
            novo_chat = Chat.objects.create(
                chat_id=chat_id,
                cliente=cliente,
                chat_name=chat_name,
                is_group=chat_id.endswith('@g.us'),  # Grupos terminam com @g.us
                canal='whatsapp',
                status='active',
                last_message_at=last_message_time,
                foto_perfil=chat_wapi.get('profilePictureUrl')
            )
            
            print(f"  ➕ Chat criado: {chat_name}")
            
            return {
                "success": True,
                "criado": True,
                "message": "Chat criado"
            }
    
    def exibir_estatisticas(self) -> None:
        """
        Exibe estatísticas dos chats no sistema MultiChat
        """
        if not self.cliente_id:
            print("❌ Cliente não encontrado")
            return
        
        try:
            cliente = Cliente.objects.get(id=self.cliente_id)
            total_chats = Chat.objects.filter(cliente=cliente).count()
            chats_ativos = Chat.objects.filter(cliente=cliente, status='active').count()
            chats_grupos = Chat.objects.filter(cliente=cliente, is_group=True).count()
            chats_individual = Chat.objects.filter(cliente=cliente, is_group=False).count()
            
            print(f"\n📊 ESTATÍSTICAS DOS CHATS - {cliente.nome}")
            print("=" * 50)
            print(f"Total de Chats: {total_chats}")
            print(f"Chats Ativos: {chats_ativos}")
            print(f"Chats de Grupo: {chats_grupos}")
            print(f"Chats Individuais: {chats_individual}")
            
            # Últimos chats com atividade
            ultimos_chats = Chat.objects.filter(
                cliente=cliente,
                last_message_at__isnull=False
            ).order_by('-last_message_at')[:5]
            
            if ultimos_chats:
                print(f"\n🕒 ÚLTIMOS CHATS COM ATIVIDADE:")
                for chat in ultimos_chats:
                    print(f"  • {chat.chat_name} - {chat.last_message_at.strftime('%d/%m/%Y %H:%M')}")
            
        except Cliente.DoesNotExist:
            print(f"❌ Cliente com ID {self.cliente_id} não encontrado")


def main():
    """
    Função principal para demonstrar a integração
    """
    print("🚀 INTEGRAÇÃO DE CHATS W-API COM MULTICHAT")
    print("=" * 60)
    
    # Configurações - SUBSTITUA pelos seus dados reais
    INSTANCE_ID = "3B6XIW-ZTS923-GEAY6V"  # Seu Instance ID
    TOKEN = "Q8EOH07SJkXhg4iT6Qmhz1BJdLl8nL9WF"  # Seu Token
    CLIENTE_ID = None  # Será buscado automaticamente se None
    
    # Criar integrador
    integrator = WApiChatsIntegrator(INSTANCE_ID, TOKEN, CLIENTE_ID)
    
    if not integrator.cliente_id:
        print("❌ Não foi possível encontrar o cliente para esta instância")
        return
    
    # 1. Exibir estatísticas atuais
    print("\n1️⃣ ESTATÍSTICAS ATUAIS")
    print("-" * 40)
    integrator.exibir_estatisticas()
    
    # 2. Sincronizar chats
    print("\n2️⃣ SINCRONIZANDO CHATS")
    print("-" * 40)
    
    resultado = integrator.sincronizar_chats(max_pages=3)
    
    if resultado.get("success"):
        print(f"\n✅ SINCRONIZAÇÃO CONCLUÍDA!")
        print(f"Total processados: {resultado['total_processados']}")
        print(f"Chats criados: {resultado['total_criados']}")
        print(f"Chats atualizados: {resultado['total_atualizados']}")
        
        if resultado['erros']:
            print(f"\n⚠️  ERROS ENCONTRADOS:")
            for erro in resultado['erros'][:5]:  # Mostrar apenas os primeiros 5
                print(f"  • {erro}")
            if len(resultado['erros']) > 5:
                print(f"  ... e mais {len(resultado['erros']) - 5} erros")
    else:
        print(f"❌ Erro na sincronização: {resultado.get('message')}")
    
    # 3. Exibir estatísticas finais
    print("\n3️⃣ ESTATÍSTICAS FINAIS")
    print("-" * 40)
    integrator.exibir_estatisticas()
    
    print(f"\n✅ Integração concluída!")
    print("💡 Os chats agora estão sincronizados no sistema MultiChat")


if __name__ == "__main__":
    main() 