#!/usr/bin/env python3
"""
🧪 TESTE DA CORREÇÃO - download_media_via_wapi
Verifica se as correções baseadas na documentação W-API funcionaram
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

from core.models import Cliente, WhatsappInstance
from webhook.views import download_media_via_wapi

def test_download_corrigido():
    """Testa a função corrigida de download"""
    print("🧪 TESTE DA FUNÇÃO CORRIGIDA - download_media_via_wapi")
    print("=" * 80)
    
    # Obter credenciais do banco
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado!")
        return
    
    instancia = WhatsappInstance.objects.filter(cliente=cliente).first()
    if not instancia:
        print("❌ Nenhuma instância encontrada!")
        return
    
    print(f"✅ Cliente: {cliente.nome}")
    print(f"✅ Instância: {instancia.instance_id}")
    print(f"✅ Token: {instancia.token[:20]}...")
    
    print("\n🧪 TESTE 1: Dados válidos reais do webhook")
    print("-" * 60)
    
    # Usar dados reais de um webhook capturado
    dados_reais = {
        'mediaKey': 'O9DM61a9JCpaYl3hkzAGE6yiEDL0R1fmR68SXFJsCU4=',
        'directPath': '/o1/v/t24/f2/m233/AQNKUg_ba9qqNjq8a29zPrI8IwDMynEsYjBJoLdqoGW8cFn2-FxFSlpNs2GfqGzUJbsF8WoyBt8gew',
        'type': 'image',
        'mimetype': 'image/jpeg'
    }
    
    print("Dados do teste:")
    print(json.dumps(dados_reais, indent=2))
    
    resultado = download_media_via_wapi(
        instancia.instance_id,
        instancia.token,
        dados_reais
    )
    
    if resultado:
        print(f"✅ SUCESSO! Download realizado")
        print(f"   fileLink: {resultado.get('fileLink')}")
        print(f"   expires: {resultado.get('expires')}")
    else:
        print(f"❌ FALHA no download")
    
    print("\n🧪 TESTE 2: Dados com campos ausentes (deve falhar na validação)")
    print("-" * 60)
    
    dados_incompletos = {
        'mediaKey': 'TEST_KEY',
        # 'directPath' ausente - deve falhar
        'type': 'audio',
        'mimetype': 'audio/ogg'
    }
    
    print("Dados do teste (incompletos):")
    print(json.dumps(dados_incompletos, indent=2))
    
    resultado2 = download_media_via_wapi(
        instancia.instance_id,
        instancia.token,
        dados_incompletos
    )
    
    if resultado2 is None:
        print(f"✅ VALIDAÇÃO FUNCIONOU! Dados incompletos rejeitados corretamente")
    else:
        print(f"❌ VALIDAÇÃO FALHOU! Dados incompletos foram aceitos")
    
    print("\n🧪 TESTE 3: Dados de teste simples")
    print("-" * 60)
    
    dados_teste = {
        'mediaKey': 'TEST_MEDIA_KEY_123',
        'directPath': '/v/test-path',
        'type': 'audio',
        'mimetype': 'audio/ogg'
    }
    
    print("Dados do teste:")
    print(json.dumps(dados_teste, indent=2))
    
    resultado3 = download_media_via_wapi(
        instancia.instance_id,
        instancia.token,
        dados_teste
    )
    
    if resultado3:
        print(f"✅ SUCESSO! Download realizado")
        print(f"   fileLink: {resultado3.get('fileLink')}")
        print(f"   expires: {resultado3.get('expires')}")
    else:
        print(f"❌ FALHA no download (pode ser normal com dados de teste)")

def test_webhook_automatico():
    """Testa envio de webhook para verificar processamento automático"""
    print("\n🌐 TESTE WEBHOOK AUTOMÁTICO COM CORREÇÃO")
    print("=" * 80)
    
    import requests
    
    # Dados de webhook com mídia real
    webhook_data = {
        "instanceId": "3B6XIW-ZTS923-GEAY6V",
        "event": "messages.upsert",
        "messageId": "TEST_CORRIGIDO_001",
        "fromMe": False,
        "sender": {
            "id": "556999211347",
            "pushName": "Teste Corrigido"
        },
        "chat": {
            "id": "556999211347",
            "name": "Teste Corrigido"
        },
        "msgContent": {
            "imageMessage": {
                "mediaKey": "O9DM61a9JCpaYl3hkzAGE6yiEDL0R1fmR68SXFJsCU4=",
                "directPath": "/o1/v/t24/f2/m233/AQNKUg_ba9qqNjq8a29zPrI8IwDMynEsYjBJoLdqoGW8cFn2-FxFSlpNs2GfqGzUJbsF8WoyBt8gew",
                "mimetype": "image/jpeg",
                "fileLength": "45123",
                "width": 720,
                "height": 1280
            }
        }
    }
    
    try:
        print("Enviando webhook com dados corrigidos...")
        response = requests.post(
            'http://localhost:8000/webhook/receive/',
            json=webhook_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📡 Status da resposta: {response.status_code}")
        print(f"📋 Resposta: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Webhook processado com sucesso!")
            print("   Verifique os logs do Django para ver se o download automático funcionou")
        else:
            print("❌ Erro ao processar webhook")
            
    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {e}")
        print("   Certifique-se de que o servidor Django está rodando")

def main():
    """Função principal"""
    print("🔧 TESTE COMPLETO DA CORREÇÃO W-API")
    print("=" * 80)
    print("Testando as correções implementadas:")
    print("1. Validação prévia de campos obrigatórios")
    print("2. Correção da lógica de verificação de erro")
    print("3. Logs mais detalhados")
    print("4. Remoção de .get() com valores padrão vazios")
    print("=" * 80)
    
    try:
        # Testar função corrigida
        test_download_corrigido()
        
        # Testar webhook automático
        test_webhook_automatico()
        
        print("\n" + "=" * 80)
        print("✅ TESTES CONCLUÍDOS!")
        print("\n💡 ANÁLISE DOS RESULTADOS:")
        print("   1. Se validação funcionou: ✅ Correção da validação OK")
        print("   2. Se download com dados reais funcionou: ✅ Problema resolvido!")
        print("   3. Se ainda falha: ⚠️ Problema pode ser nos dados ou na API")
        print("   4. Se webhook automático funcionou: ✅ Sistema totalmente corrigido!")
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 