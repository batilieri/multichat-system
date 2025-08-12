#!/usr/bin/env python3
"""
🧪 TESTE COMPARATIVO - Dados que funcionaram vs dados que falharam
"""

import os
import sys
import django
import json
import requests

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

from core.models import Cliente, WhatsappInstance

def testar_dados_que_funcionaram():
    """Testa com dados de áudio que funcionaram no diagnóstico"""
    print("🧪 TESTE COM DADOS QUE FUNCIONARAM")
    print("=" * 60)
    
    # Dados que funcionaram (áudio do diagnóstico)
    # Usando dados reais de webhook que retornaram Status 200
    
    instancia = WhatsappInstance.objects.first()
    token = instancia.token
    instance_id = instancia.instance_id
    
    # Dados de áudio que funcionaram
    dados_audio_ok = {
        'mediaKey': 'real_audio_key_from_working_webhook',  # Substituir por dados reais
        'directPath': '/real/audio/path',
        'type': 'audio',
        'mimetype': 'audio/ogg; codecs=opus'
    }
    
    print("📊 Dados de áudio que funcionaram:")
    print(json.dumps(dados_audio_ok, indent=2))
    
    # Fazer requisição
    url = f"https://api.w-api.app/v1/message/download-media?instanceId={instance_id}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, json=dados_audio_ok, timeout=30)
        print(f"\n📡 Status: {response.status_code}")
        print(f"📄 Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ CONFIRMADO: Dados de áudio funcionam!")
        else:
            print("❌ Falhou mesmo sendo dados que funcionaram antes")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def testar_dados_que_falharam():
    """Testa com dados que falharam nos testes anteriores"""
    print("\n🧪 TESTE COM DADOS QUE FALHARAM")
    print("=" * 60)
    
    instancia = WhatsappInstance.objects.first()
    token = instancia.token
    instance_id = instancia.instance_id
    
    # Dados que falharam (imagem dos testes anteriores)
    dados_imagem_falha = {
        'mediaKey': 'O9DM61a9JCpaYl3hkzAGE6yiEDL0R1fmR68SXFJsCU4=',
        'directPath': '/o1/v/t24/f2/m233/AQNKUg_ba9qqNjq8a29zPrI8IwDMynEsYjBJoLdqoGW8cFn2-FxFSlpNs2GfqGzUJbsF8WoyBt8gew',
        'type': 'image',
        'mimetype': 'image/jpeg'
    }
    
    print("📊 Dados de imagem que falharam:")
    print(json.dumps(dados_imagem_falha, indent=2))
    
    # Fazer requisição
    url = f"https://api.w-api.app/v1/message/download-media?instanceId={instance_id}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, json=dados_imagem_falha, timeout=30)
        print(f"\n📡 Status: {response.status_code}")
        print(f"📄 Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("🎉 SUCESSO: Dados de imagem agora funcionam!")
        else:
            print("❌ CONFIRMADO: Dados de imagem ainda falham")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def testar_dados_de_teste_simples():
    """Testa com dados de teste simples"""
    print("\n🧪 TESTE COM DADOS DE TESTE SIMPLES")
    print("=" * 60)
    
    instancia = WhatsappInstance.objects.first()
    token = instancia.token
    instance_id = instancia.instance_id
    
    # Dados de teste simples
    dados_teste = {
        'mediaKey': 'TEST_MEDIA_KEY_123',
        'directPath': '/v/test-path',
        'type': 'audio',
        'mimetype': 'audio/ogg'
    }
    
    print("📊 Dados de teste simples:")
    print(json.dumps(dados_teste, indent=2))
    
    # Fazer requisição
    url = f"https://api.w-api.app/v1/message/download-media?instanceId={instance_id}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, json=dados_teste, timeout=30)
        print(f"\n📡 Status: {response.status_code}")
        print(f"📄 Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Dados de teste funcionam!")
        else:
            print("❌ Dados de teste falham (esperado)")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def obter_dados_reais_de_webhook():
    """Obtém dados reais de webhook para teste"""
    print("\n🔍 OBTENDO DADOS REAIS DE WEBHOOK")
    print("=" * 60)
    
    from webhook.models import WebhookEvent
    
    # Buscar webhook com áudio mais recente
    for webhook in WebhookEvent.objects.all().order_by('-timestamp')[:10]:
        try:
            if isinstance(webhook.raw_data, dict):
                data = webhook.raw_data
            else:
                data = json.loads(webhook.raw_data)
            
            msg_content = data.get('msgContent', {})
            
            if 'audioMessage' in msg_content:
                audio_data = msg_content['audioMessage']
                
                print(f"✅ Webhook com áudio encontrado: {webhook.event_id}")
                print(f"   Timestamp: {webhook.timestamp}")
                print(f"   MediaKey: {audio_data.get('mediaKey', 'N/A')[:20]}...")
                print(f"   DirectPath: {audio_data.get('directPath', 'N/A')[:50]}...")
                print(f"   Mimetype: {audio_data.get('mimetype', 'N/A')}")
                
                return {
                    'mediaKey': audio_data.get('mediaKey'),
                    'directPath': audio_data.get('directPath'),
                    'type': 'audio',
                    'mimetype': audio_data.get('mimetype')
                }
                
        except Exception as e:
            continue
    
    print("❌ Nenhum webhook com áudio encontrado")
    return None

def main():
    """Função principal"""
    print("🧪 TESTE COMPARATIVO - DADOS QUE FUNCIONARAM VS FALHARAM")
    print("=" * 80)
    
    # Obter dados reais de webhook
    dados_reais = obter_dados_reais_de_webhook()
    
    if dados_reais:
        print("\n🧪 TESTANDO COM DADOS REAIS DE WEBHOOK")
        print("=" * 60)
        
        instancia = WhatsappInstance.objects.first()
        token = instancia.token
        instance_id = instancia.instance_id
        
        print(f"📊 Dados reais obtidos do webhook:")
        print(json.dumps(dados_reais, indent=2))
        
        # Fazer requisição
        url = f"https://api.w-api.app/v1/message/download-media?instanceId={instance_id}"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, json=dados_reais, timeout=30)
            print(f"\n📡 Status: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("🎉 SUCESSO: Dados reais de webhook funcionam!")
                
                # Se funcionou, verificar se há dados de imagem para comparar
                print("\n🔍 Buscando dados de imagem para comparar...")
                
                from webhook.models import WebhookEvent
                for webhook in WebhookEvent.objects.all().order_by('-timestamp')[:10]:
                    try:
                        if isinstance(webhook.raw_data, dict):
                            data = webhook.raw_data
                        else:
                            data = json.loads(webhook.raw_data)
                        
                        msg_content = data.get('msgContent', {})
                        
                        if 'imageMessage' in msg_content:
                            image_data = msg_content['imageMessage']
                            
                            dados_imagem = {
                                'mediaKey': image_data.get('mediaKey'),
                                'directPath': image_data.get('directPath'),
                                'type': 'image',
                                'mimetype': image_data.get('mimetype')
                            }
                            
                            print(f"\n🖼️ Testando dados reais de imagem:")
                            print(json.dumps(dados_imagem, indent=2))
                            
                            response_img = requests.post(url, headers=headers, json=dados_imagem, timeout=30)
                            print(f"📡 Status imagem: {response_img.status_code}")
                            
                            if response_img.status_code == 200:
                                print("🎉 Imagens também funcionam!")
                            else:
                                print("❌ Imagens falham - problema específico de imagens")
                            
                            break
                            
                    except Exception as e:
                        continue
                        
            else:
                print("❌ Dados reais falham")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    # Testar dados que falharam antes
    testar_dados_que_falharam()
    
    # Testar dados de teste
    testar_dados_de_teste_simples()
    
    print("\n" + "=" * 80)
    print("🎯 CONCLUSÃO")
    print("=" * 80)
    print("Se dados reais funcionam mas dados antigos falham:")
    print("   ✅ Problema era dados expirados/inválidos")
    print("   🔧 Sistema funcionando corretamente")
    print("\nSe todos falham:")
    print("   ❌ Problema persiste na W-API")
    print("\nSe apenas alguns tipos funcionam:")
    print("   ⚠️ Problema específico por tipo de mídia")

if __name__ == "__main__":
    main() 