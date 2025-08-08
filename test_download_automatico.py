#!/usr/bin/env python3
"""
Teste do Download Automático de Áudios
"""

import os
import sys
import django
import json
import requests
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
django.setup()

from core.models import Cliente, Chat, Mensagem
from webhook.models import WebhookEvent

def testar_webhook_audio():
    """Testa envio de webhook com áudio"""
    print("🧪 TESTANDO WEBHOOK COM ÁUDIO")
    print("=" * 60)
    
    # Dados de teste de áudio
    webhook_data = {
        "instanceId": "3B6XIW-ZTS923-GEAY6V",
        "event": "messages.upsert",
        "messageId": "TEST_AUDIO_001",
        "fromMe": False,
        "sender": {
            "id": "556999211347",
            "pushName": "Teste Áudio"
        },
        "chat": {
            "id": "556999211347",
            "name": "Teste Áudio"
        },
        "msgContent": {
            "audioMessage": {
                "url": "https://mmg.whatsapp.net/v/t62.7117-24/19083661_1303226854859439_3997981883652895124_n.enc?ccb=11-4&oh=01_Q5Aa2AHv1g25E-1H3jqetiO5I0A7GCCp1SbCxNT7hCJBPKZhJw&oe=68BB4268&_nc_sid=5e03e0&mms3=true",
                "mediaKey": "TEST_MEDIA_KEY_123",
                "directPath": "/v/t62.7117-24/19083661_1303226854859439_3997981883652895124_n.enc?ccb=11-4&oh=01_Q5Aa2AHv1g25E-1H3jqetiO5I0A7GCCp1SbCxNT7hCJBPKZhJw&oe=68BB4268&_nc_sid=5e03e0",
                "mimetype": "audio/ogg; codecs=opus",
                "fileLength": "4478",
                "seconds": 5,
                "isPtt": True,
                "fileSha256": "TEST_SHA256",
                "fileEncSha256": "TEST_ENC_SHA256"
            }
        }
    }
    
    try:
        # Enviar webhook para o sistema
        response = requests.post(
            'http://localhost:8000/webhook/receive/',
            json=webhook_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📡 Status da resposta: {response.status_code}")
        print(f"📋 Resposta: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook processado com sucesso!")
        else:
            print("❌ Erro ao processar webhook")
            
    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {e}")

def verificar_processamento_automatico():
    """Verifica se o processamento automático está sendo chamado"""
    print("\n🔍 VERIFICANDO PROCESSAMENTO AUTOMÁTICO")
    print("=" * 60)
    
    # Buscar webhooks recentes
    webhooks = WebhookEvent.objects.all().order_by('-timestamp')[:5]
    print(f"📊 Webhooks recentes: {webhooks.count()}")
    
    for webhook in webhooks:
        print(f"\n📡 Webhook ID: {webhook.id}")
        print(f"   Tipo: {webhook.event_type}")
        print(f"   Data: {webhook.timestamp}")
        
        # Verificar se contém áudio
        try:
            data = json.loads(webhook.raw_data)
            if 'msgContent' in data:
                msg_content = data['msgContent']
                if 'audioMessage' in msg_content:
                    print(f"   🎵 CONTÉM ÁUDIO!")
                    audio_data = msg_content['audioMessage']
                    print(f"      URL: {audio_data.get('url', 'N/A')}")
                    print(f"      MediaKey: {audio_data.get('mediaKey', 'N/A')}")
                    print(f"      DirectPath: {audio_data.get('directPath', 'N/A')}")
                else:
                    print(f"   ⚠️ Não contém áudio")
        except:
            print(f"   ❌ Erro ao processar dados")

def verificar_configuracao_wapi():
    """Verifica configuração da W-API"""
    print("\n🔧 VERIFICANDO CONFIGURAÇÃO W-API")
    print("=" * 60)
    
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado!")
        return
    
    print(f"✅ Cliente: {cliente.nome}")
    print(f"   WAPI Instance ID: {cliente.wapi_instance_id}")
    print(f"   WAPI Token: {cliente.wapi_token[:20] if cliente.wapi_token else 'Nenhum'}...")
    
    # Testar conexão com W-API
    if cliente.wapi_token and cliente.wapi_instance_id:
        try:
            url = f"https://api.w-api.app/v1/instance/status?instanceId={cliente.wapi_instance_id}"
            headers = {'Authorization': f'Bearer {cliente.wapi_token}'}
            
            response = requests.get(url, headers=headers, timeout=10)
            print(f"📡 Status da instância: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Status: {data.get('status', 'N/A')}")
                print(f"   Conectado: {data.get('connected', 'N/A')}")
            else:
                print(f"   ❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Erro ao conectar com W-API: {e}")
    else:
        print("❌ Configuração W-API incompleta!")

def verificar_estrutura_pastas():
    """Verifica estrutura de pastas após teste"""
    print("\n📁 VERIFICANDO ESTRUTURA DE PASTAS")
    print("=" * 60)
    
    media_path = Path("multichat_system/media_storage/cliente_2/instance_3B6XIW-ZTS923-GEAY6V/chats")
    
    if not media_path.exists():
        print("❌ Pasta de chats não encontrada!")
        return
    
    # Verificar cada chat
    for chat_dir in media_path.glob("*"):
        if chat_dir.is_dir():
            print(f"\n📱 Chat: {chat_dir.name}")
            
            # Verificar pasta de áudio
            audio_dir = chat_dir / "audio"
            if audio_dir.exists():
                files = list(audio_dir.glob("*"))
                print(f"   🎵 Áudios encontrados: {len(files)}")
                for file in files:
                    size_kb = file.stat().st_size / 1024
                    print(f"      - {file.name} ({size_kb:.1f} KB)")
            else:
                print(f"   ⚠️ Pasta de áudio não existe")

def testar_download_manual():
    """Testa download manual para comparar"""
    print("\n🧪 TESTANDO DOWNLOAD MANUAL")
    print("=" * 60)
    
    # Dados de teste
    media_data = {
        'mediaKey': 'TEST_MEDIA_KEY_123',
        'directPath': '/v/t62.7117-24/19083661_1303226854859439_3997981883652895124_n.enc',
        'type': 'audio',
        'mimetype': 'audio/ogg'
    }
    
    cliente = Cliente.objects.first()
    if not cliente or not cliente.wapi_token:
        print("❌ Cliente ou token não encontrado!")
        return
    
    try:
        # Testar download via W-API
        url = f"https://api.w-api.app/v1/message/download-media?instanceId={cliente.wapi_instance_id}"
        headers = {
            'Authorization': f'Bearer {cliente.wapi_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, json=media_data, timeout=30)
        print(f"📡 Status da resposta W-API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Download manual funcionou!")
            print(f"   fileLink: {data.get('fileLink', 'N/A')}")
        else:
            print(f"❌ Erro no download manual: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro no download manual: {e}")

def main():
    """Função principal"""
    print("🔍 TESTE COMPLETO DO DOWNLOAD AUTOMÁTICO")
    print("=" * 80)
    
    try:
        # Verificar configuração
        verificar_configuracao_wapi()
        
        # Testar download manual
        testar_download_manual()
        
        # Verificar processamento automático
        verificar_processamento_automatico()
        
        # Testar webhook
        testar_webhook_audio()
        
        # Verificar estrutura
        verificar_estrutura_pastas()
        
        print("\n" + "=" * 80)
        print("✅ TESTE CONCLUÍDO!")
        
        print("\n💡 DIAGNÓSTICO:")
        print("   1. Se W-API não conecta: problema de configuração")
        print("   2. Se download manual falha: problema de credenciais")
        print("   3. Se webhook não processa: problema no receiver")
        print("   4. Se arquivo não baixa: problema no processamento automático")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 