#!/usr/bin/env python3
"""
Script para testar a configuração HTTPS do webhook
"""

import requests
import json
import time
from datetime import datetime

def testar_webhook_https():
    """Testa a configuração HTTPS do webhook"""
    
    print("🔒 TESTANDO CONFIGURAÇÃO HTTPS DO WEBHOOK")
    print("=" * 60)
    
    # URLs de teste
    urls_teste = [
        "https://localhost:5000/webhook",
        "https://localhost:5000/status",
        "https://localhost:5000/test"
    ]
    
    # Dados de teste para webhook
    dados_teste = {
        "instanceId": "test_instance_123",
        "event": "message",
        "fromMe": True,
        "messageId": "test_msg_456",
        "sender": {
            "id": "5511999999999@c.us",
            "name": "Teste Cliente"
        },
        "chat": {
            "id": "5511888888888@c.us",
            "name": "Contato Teste"
        },
        "msgContent": {
            "type": "text",
            "text": "Teste de mensagem HTTPS"
        },
        "timestamp": datetime.now().isoformat()
    }
    
    for url in urls_teste:
        print(f"\n🌐 Testando: {url}")
        print("-" * 40)
        
        try:
            # Teste GET
            response = requests.get(url, timeout=10, verify=False)
            print(f"✅ GET: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"📄 Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"📄 Resposta: {response.text[:200]}...")
            
        except requests.exceptions.SSLError as e:
            print(f"⚠️ SSL Error: {e}")
            print("💡 Isso é normal para localhost com HTTPS")
            
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection Error: {e}")
            print("💡 Servidor não está rodando ou porta incorreta")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    # Teste POST para webhook
    print(f"\n📤 Testando POST para webhook...")
    print("-" * 40)
    
    try:
        response = requests.post(
            "https://localhost:5000/webhook",
            json=dados_teste,
            headers={"Content-Type": "application/json"},
            timeout=10,
            verify=False
        )
        
        print(f"✅ POST: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📄 Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except:
                print(f"📄 Resposta: {response.text[:200]}...")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except requests.exceptions.SSLError as e:
        print(f"⚠️ SSL Error: {e}")
        print("💡 Isso é normal para localhost com HTTPS")
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("💡 Servidor não está rodando")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

def verificar_ngrok_https():
    """Verifica se o ngrok está criando túnel HTTPS"""
    
    print(f"\n🔍 VERIFICANDO CONFIGURAÇÃO NGROK HTTPS")
    print("=" * 60)
    
    try:
        import requests
        
        # Tentar acessar a API do ngrok
        response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
        
        if response.status_code == 200:
            tunnels = response.json()
            
            print(f"📊 Túneis ativos: {len(tunnels.get('tunnels', []))}")
            
            for tunnel in tunnels.get('tunnels', []):
                public_url = tunnel.get('public_url', '')
                protocol = tunnel.get('proto', '')
                
                print(f"🌐 URL: {public_url}")
                print(f"🔒 Protocolo: {protocol}")
                
                if public_url.startswith('https://'):
                    print("✅ HTTPS configurado corretamente!")
                else:
                    print("⚠️ URL não é HTTPS!")
                    
        else:
            print("❌ Não foi possível acessar API do ngrok")
            
    except Exception as e:
        print(f"❌ Erro ao verificar ngrok: {e}")
        print("💡 Verifique se o ngrok está rodando")

def main():
    """Função principal"""
    
    print("🚀 TESTE DE CONFIGURAÇÃO HTTPS - MULTICHAT WEBHOOK")
    print("=" * 60)
    print("🔒 Verificando protocolo HTTPS")
    print("🌐 Testando túnel ngrok")
    print("📱 Validando webhook")
    print("=" * 60)
    
    # Verificar ngrok
    verificar_ngrok_https()
    
    # Testar webhook
    testar_webhook_https()
    
    print(f"\n✅ TESTE CONCLUÍDO!")
    print("=" * 60)
    print("💡 Se todos os testes passaram, o webhook está funcionando com HTTPS")
    print("📱 Configure a URL HTTPS no WhatsApp Business API")
    print("🔒 O protocolo HTTPS garante segurança nas comunicações")

if __name__ == "__main__":
    main() 