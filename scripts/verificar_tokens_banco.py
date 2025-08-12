#!/usr/bin/env python3
"""
🔍 VERIFICAÇÃO DE TOKENS NO BANCO DE DADOS
Compara tokens no script vs banco de dados
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

from core.models import Cliente, WhatsappInstance

def verificar_tokens():
    """Verifica tokens armazenados no banco"""
    print("🔍 VERIFICAÇÃO DE TOKENS NO BANCO DE DADOS")
    print("=" * 60)
    
    # Token usado no script
    token_script = "Q8EOH07SJkXhg4iT6Qmhz1BJdLl8nL9WF"
    instance_script = "3B6XIW-ZTS923-GEAY6V"
    
    print(f"🔧 Token usado no script: {token_script}")
    print(f"🔧 Instance usado no script: {instance_script}")
    
    print(f"\n📋 VERIFICANDO CLIENTES:")
    print("-" * 40)
    
    clientes = Cliente.objects.all()
    for cliente in clientes:
        print(f"\n👤 Cliente: {cliente.nome}")
        print(f"   Instance ID: {cliente.wapi_instance_id}")
        print(f"   Token: {cliente.wapi_token}")
        
        # Comparar com script
        if cliente.wapi_token == token_script:
            print("   ✅ Token IGUAL ao do script")
        else:
            print("   ❌ Token DIFERENTE do script")
        
        if cliente.wapi_instance_id == instance_script:
            print("   ✅ Instance ID IGUAL ao do script")
        else:
            print("   ❌ Instance ID DIFERENTE do script")
    
    print(f"\n📋 VERIFICANDO INSTÂNCIAS WhatsApp:")
    print("-" * 40)
    
    instancias = WhatsappInstance.objects.all()
    for instancia in instancias:
        print(f"\n📱 Instância: {instancia.instance_id}")
        print(f"   Cliente: {instancia.cliente.nome}")
        print(f"   Token: {instancia.token}")
        print(f"   Status: {instancia.status}")
        
        # Comparar com script
        if instancia.token == token_script:
            print("   ✅ Token IGUAL ao do script")
        else:
            print("   ❌ Token DIFERENTE do script")
        
        if instancia.instance_id == instance_script:
            print("   ✅ Instance ID IGUAL ao do script")
        else:
            print("   ❌ Instance ID DIFERENTE do script")

def testar_token_correto():
    """Testa usando o token do banco de dados"""
    print(f"\n🧪 TESTANDO COM TOKEN DO BANCO")
    print("=" * 60)
    
    import requests
    
    # Pegar token e instance do banco
    instancia = WhatsappInstance.objects.first()
    if not instancia:
        print("❌ Nenhuma instância encontrada no banco")
        return
    
    token_banco = instancia.token
    instance_banco = instancia.instance_id
    
    print(f"🔧 Usando token do banco: {token_banco[:20]}...")
    print(f"🔧 Usando instance do banco: {instance_banco}")
    
    # Testar status da instância
    url = f"https://api.w-api.app/v1/instance/status-instance"
    headers = {
        'Authorization': f'Bearer {token_banco}',
        'Content-Type': 'application/json'
    }
    params = {'instanceId': instance_banco}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        print(f"\n📡 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conectada: {data.get('connected', 'N/A')}")
            print(f"✅ Status: {data.get('status', 'N/A')}")
            
            # Se funcionar, testar download
            if data.get('connected'):
                testar_download_com_token_correto(instance_banco, token_banco)
            
        elif response.status_code == 403:
            print("❌ Token do banco também é inválido!")
        else:
            print(f"❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def testar_download_com_token_correto(instance_id, token):
    """Testa download com token correto do banco"""
    print(f"\n🎯 TESTANDO DOWNLOAD COM TOKEN CORRETO")
    print("-" * 40)
    
    import requests
    import json
    
    # Dados de teste
    info_midia = {
        'mediaKey': 'O9DM61a9JCpaYl3hkzAGE6yiEDL0R1fmR68SXFJsCU4=',
        'directPath': '/o1/v/t24/f2/m233/AQNKUg_ba9qqNjq8a29zPrI8IwDMynEsYjBJoLdqoGW8cFn2-FxFSlpNs2GfqGzUJbsF8WoyBt8gew',
        'type': 'image',
        'mimetype': 'image/jpeg'
    }
    
    # Teste 1: Método do sistema atual
    url = f"https://api.w-api.app/v1/message/download-media?instanceId={instance_id}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'mediaKey': info_midia['mediaKey'],
        'directPath': info_midia['directPath'],
        'type': info_midia['type'],
        'mimetype': info_midia['mimetype']
    }
    
    print(f"🔄 Testando download com token correto...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"\n📡 Status: {response.status_code}")
        print(f"📄 Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("🎉 SUCESSO! O problema era realmente o token!")
        else:
            print("❌ Ainda falha mesmo com token correto")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    print("🔍 DIAGNÓSTICO FINAL - VERIFICAÇÃO DE TOKENS")
    print("=" * 80)
    
    verificar_tokens()
    testar_token_correto()
    
    print("\n" + "=" * 80)
    print("🎯 CONCLUSÃO")
    print("=" * 80)
    print("Se o teste com token do banco funcionou:")
    print("   ✅ Problema identificado: Token hardcoded estava desatualizado")
    print("   🔧 Solução: Usar sempre tokens do banco de dados")
    print("   📋 Sistema deve buscar credenciais dinamicamente")
    
    print("\nSe ainda falha:")
    print("   ❌ Problema na W-API ou nos dados de mídia")
    print("   📞 Contatar suporte W-API")

if __name__ == "__main__":
    main() 