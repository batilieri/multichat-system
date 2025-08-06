#!/usr/bin/env python3
"""
Script para testar download real com W-API
"""

import os
import sys
import django
import json
import requests
from pathlib import Path

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import WhatsappInstance, MediaFile
from webhook.views import download_media_via_wapi, save_media_file

def testar_download_real():
    """Testa download com dados reais"""
    print("🧪 Testando download real com W-API...")
    
    try:
        instancia = WhatsappInstance.objects.get(instance_id="3B6XIW-ZTS923-GEAY6V")
        
        # Dados reais de teste (substitua pelos dados reais do webhook)
        media_data = {
            'mediaKey': 'REAL_MEDIA_KEY_HERE',
            'directPath': '/REAL/DIRECT/PATH',
            'type': 'image',
            'mimetype': 'image/jpeg'
        }
        
        print(f"📱 Instância: {instancia.instance_id}")
        print(f"🔑 Token: {'✅' if instancia.token else '❌'}")
        
        # Testar download
        resultado = download_media_via_wapi(
            instancia.instance_id,
            instancia.token,
            media_data
        )
        
        if resultado and resultado.get('fileLink'):
            print("✅ Download funcionou!")
            print(f"📎 File Link: {resultado['fileLink']}")
            
            # Testar salvamento
            file_path = save_media_file(
                resultado['fileLink'],
                'image',
                'test_real_message',
                'Teste Real',
                instancia.cliente,
                instancia
            )
            
            if file_path:
                print(f"✅ Arquivo salvo: {file_path}")
            else:
                print("❌ Falha ao salvar arquivo")
        else:
            print("❌ Download falhou!")
            
    except WhatsappInstance.DoesNotExist:
        print("❌ Instância não encontrada!")
    except Exception as e:
        print(f"❌ Erro: {e}")

def verificar_webhook_recente():
    """Verifica webhooks recentes para dados reais"""
    print("\n🔍 Verificando webhooks recentes...")
    
    # Buscar eventos de webhook recentes
    from webhook.models import WebhookEvent
    
    eventos = WebhookEvent.objects.filter(
        event_type='message'
    ).order_by('-received_at')[:5]
    
    if not eventos.exists():
        print("❌ Nenhum evento de webhook encontrado!")
        return
    
    for evento in eventos:
        print(f"\n📋 Evento: {evento.event_id}")
        print(f"   Tipo: {evento.event_type}")
        print(f"   Data: {evento.received_at}")
        
        # Analisar payload
        payload = evento.payload
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except:
                pass
        
        # Extrair dados de mídia
        msg_content = payload.get('msgContent', {})
        media_types = ['imageMessage', 'videoMessage', 'audioMessage', 'documentMessage']
        
        for media_type in media_types:
            if media_type in msg_content:
                media_data = msg_content[media_type]
                print(f"   📎 Mídia encontrada: {media_type}")
                print(f"      Media Key: {media_data.get('mediaKey', 'N/A')}")
                print(f"      Direct Path: {media_data.get('directPath', 'N/A')}")
                print(f"      Mimetype: {media_data.get('mimetype', 'N/A')}")
                
                # Testar download com dados reais
                testar_download_com_dados_reais(payload, media_data, media_type)

def testar_download_com_dados_reais(webhook_data, media_data, media_type):
    """Testa download com dados reais do webhook"""
    try:
        instancia = WhatsappInstance.objects.get(instance_id=webhook_data.get('instanceId'))
        
        # Preparar dados para download
        download_data = {
            'mediaKey': media_data.get('mediaKey', ''),
            'directPath': media_data.get('directPath', ''),
            'type': media_type.replace('Message', ''),
            'mimetype': media_data.get('mimetype', '')
        }
        
        print(f"🔄 Testando download com dados reais...")
        
        resultado = download_media_via_wapi(
            instancia.instance_id,
            instancia.token,
            download_data
        )
        
        if resultado and resultado.get('fileLink'):
            print("✅ Download real funcionou!")
            return resultado
        else:
            print("❌ Download real falhou!")
            return None
            
    except Exception as e:
        print(f"❌ Erro no teste real: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Testando download real com W-API...")
    print("=" * 50)
    
    verificar_webhook_recente()
    testar_download_real() 