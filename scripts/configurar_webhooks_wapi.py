#!/usr/bin/env python3
"""
Script para configurar webhooks do WhatsApp na W-API
MultiChat System - Configuração Automática de Webhooks

Uso:
    python configurar_webhooks_wapi.py --instance-id INSTANCE_ID --token TOKEN
"""

import argparse
import requests
import json
import sys
from typing import Dict, Any

class WApiWebhookConfigurator:
    """Configurador de webhooks para W-API"""
    
    def __init__(self, base_url: str = "https://api.w-api.app"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def configure_webhooks(self, instance_id: str, token: str, webhook_urls: Dict[str, str]) -> Dict[str, Any]:
        """
        Configura webhooks para uma instância específica
        
        Args:
            instance_id: ID da instância do WhatsApp
            token: Token de autenticação da W-API
            webhook_urls: Dicionário com URLs dos webhooks
            
        Returns:
            Dict com resultado da configuração
        """
        try:
            # Headers de autenticação
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
            
            # Payload para configuração dos webhooks
            payload = {
                "instanceId": instance_id,
                "webhooks": webhook_urls
            }
            
            # URL do endpoint de configuração de webhooks
            url = f"{self.base_url}/webhook/set"
            
            print(f"🔧 Configurando webhooks para instância: {instance_id}")
            print(f"📡 URL da API: {url}")
            print(f"🔗 Webhooks a configurar:")
            for event, webhook_url in webhook_urls.items():
                print(f"   - {event}: {webhook_url}")
            
            # Fazer requisição para configurar webhooks
            response = self.session.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Webhooks configurados com sucesso!")
                print(f"📊 Resposta: {json.dumps(result, indent=2)}")
                return {
                    "success": True,
                    "message": "Webhooks configurados com sucesso",
                    "data": result
                }
            else:
                print(f"❌ Erro ao configurar webhooks: {response.status_code}")
                print(f"📄 Resposta: {response.text}")
                return {
                    "success": False,
                    "message": f"Erro HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {e}")
            return {
                "success": False,
                "message": f"Erro de conexão: {str(e)}"
            }
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            return {
                "success": False,
                "message": f"Erro inesperado: {str(e)}"
            }
    
    def test_webhook_connectivity(self, webhook_url: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Testa conectividade de um webhook específico
        
        Args:
            webhook_url: URL do webhook a testar
            test_data: Dados de teste para enviar
            
        Returns:
            Dict com resultado do teste
        """
        try:
            print(f"🧪 Testando conectividade: {webhook_url}")
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = self.session.post(webhook_url, headers=headers, json=test_data, timeout=10)
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ Webhook respondendo corretamente: {response.status_code}")
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response": response.text
                }
            else:
                print(f"⚠️ Webhook retornou status inesperado: {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "response": response.text
                }
                
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout ao testar webhook: {webhook_url}")
            return {
                "success": False,
                "message": "Timeout"
            }
        except requests.exceptions.ConnectionError:
            print(f"🔌 Erro de conexão ao testar webhook: {webhook_url}")
            return {
                "success": False,
                "message": "Connection Error"
            }
        except Exception as e:
            print(f"❌ Erro ao testar webhook: {e}")
            return {
                "success": False,
                "message": str(e)
            }

def get_default_webhook_urls(base_url: str = "https://ac70b57623e8.ngrok-free.app") -> Dict[str, str]:
    """
    Retorna as URLs padrão dos webhooks conforme especificação
    
    Args:
        base_url: URL base do sistema MultiChat
        
    Returns:
        Dict com URLs dos webhooks
    """
    return {
        "connection": "https://meulink.com/webhook/connect/",
        "disconnection": "https://meulink.com/webhook/disconnect/",
        "send_message": f"{base_url}/webhook/send-message/",
        "receive_message": f"{base_url}/webhook/receive-message/",
        "chat_presence": "https://meulink.com/webhook/chat-presence/",
        "message_status": f"{base_url}/webhook/message-status/",
        "fallback": f"{base_url}/webhook/"
    }

def main():
    """Função principal do script"""
    parser = argparse.ArgumentParser(description="Configurar webhooks do WhatsApp na W-API")
    parser.add_argument("--instance-id", required=True, help="ID da instância do WhatsApp")
    parser.add_argument("--token", required=True, help="Token de autenticação da W-API")
    parser.add_argument("--base-url", default="https://ac70b57623e8.ngrok-free.app", 
                       help="URL base do sistema MultiChat")
    parser.add_argument("--wapi-url", default="https://api.w-api.app",
                       help="URL base da W-API")
    parser.add_argument("--test", action="store_true", 
                       help="Testar conectividade dos webhooks após configuração")
    
    args = parser.parse_args()
    
    print("🚀 MultiChat System - Configurador de Webhooks W-API")
    print("=" * 60)
    
    # Obter URLs dos webhooks
    webhook_urls = get_default_webhook_urls(args.base_url)
    
    # Criar configurador
    configurator = WApiWebhookConfigurator(args.wapi_url)
    
    # Configurar webhooks
    result = configurator.configure_webhooks(args.instance_id, args.token, webhook_urls)
    
    if result["success"]:
        print("\n✅ Configuração concluída com sucesso!")
        
        if args.test:
            print("\n🧪 Testando conectividade dos webhooks...")
            
            # Dados de teste para cada tipo de webhook
            test_data = {
                "connection": {
                    "instanceId": args.instance_id,
                    "event": "connection",
                    "status": "connected",
                    "timestamp": "2025-01-15T10:30:00Z"
                },
                "send_message": {
                    "instanceId": args.instance_id,
                    "event": "message",
                    "fromMe": True,
                    "messageId": "test_msg_123",
                    "sender": {"id": "5511999999999@c.us", "name": "Teste"},
                    "msgContent": {"type": "text", "text": "Teste de mensagem"}
                },
                "receive_message": {
                    "instanceId": args.instance_id,
                    "event": "message",
                    "fromMe": False,
                    "messageId": "test_msg_456",
                    "sender": {"id": "5511888888888@c.us", "name": "Contato Teste"},
                    "msgContent": {"type": "text", "text": "Mensagem de teste"}
                }
            }
            
            # Testar webhooks principais
            for webhook_type, test_payload in test_data.items():
                if webhook_type in webhook_urls:
                    test_result = configurator.test_webhook_connectivity(
                        webhook_urls[webhook_type], 
                        test_payload
                    )
                    if test_result["success"]:
                        print(f"✅ {webhook_type}: OK")
                    else:
                        print(f"❌ {webhook_type}: FALHOU - {test_result.get('message', 'Erro desconhecido')}")
        
        print(f"\n📋 Resumo da configuração:")
        print(f"   - Instância: {args.instance_id}")
        print(f"   - Webhooks configurados: {len(webhook_urls)}")
        print(f"   - Status: {'✅ Sucesso' if result['success'] else '❌ Falha'}")
        
    else:
        print(f"\n❌ Falha na configuração: {result['message']}")
        sys.exit(1)

if __name__ == "__main__":
    main() 