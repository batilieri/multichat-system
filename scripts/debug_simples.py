#!/usr/bin/env python3
"""
🔍 DEBUG SIMPLES WEBHOOK
Análise sem usar contains do Django
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

from webhook.models import WebhookEvent

def debug_webhook_simples():
    """Debug simples dos webhooks"""
    print("🔍 DEBUG SIMPLES - ÚLTIMOS WEBHOOKS")
    print("=" * 60)
    
    # Buscar últimos webhooks sem filtro contains
    webhooks = WebhookEvent.objects.all().order_by('-timestamp')[:10]
    
    webhook_com_audio = None
    
    for webhook in webhooks:
        try:
            data = webhook.raw_data
            msg_content = data.get('msgContent', {})
            
            if 'audioMessage' in msg_content:
                webhook_com_audio = webhook
                break
        except:
            continue
    
    if not webhook_com_audio:
        print("❌ Nenhum webhook com áudio encontrado")
        return
    
    print(f"📧 Webhook com áudio encontrado:")
    print(f"   Event ID: {webhook_com_audio.event_id}")
    print(f"   Timestamp: {webhook_com_audio.timestamp}")
    print(f"   Cliente: {webhook_com_audio.cliente.nome}")
    
    data = webhook_com_audio.raw_data
    audio_data = data.get('msgContent', {}).get('audioMessage', {})
    
    print(f"\n🎵 DADOS DO ÁUDIO:")
    print(f"   MediaKey: {len(audio_data.get('mediaKey', ''))} chars")
    print(f"   DirectPath: {audio_data.get('directPath', 'N/A')[:50]}...")
    print(f"   Mimetype: {audio_data.get('mimetype', 'N/A')}")
    
    # Testar download direto
    testar_download_direto(webhook_com_audio.cliente, data, audio_data)

def testar_download_direto(cliente, webhook_data, audio_data):
    """Testa download direto"""
    print(f"\n🧪 TESTE DIRETO DE DOWNLOAD")
    print("=" * 60)
    
    try:
        from core.models import WhatsappInstance
        instance = WhatsappInstance.objects.get(instance_id=webhook_data.get('instanceId'))
        
        print(f"📱 Instância: {instance.instance_id}")
        print(f"🔑 Token disponível: {'✅' if instance.token else '❌'}")
        
        # Preparar dados
        media_data = {
            'mediaKey': audio_data.get('mediaKey', ''),
            'directPath': audio_data.get('directPath', ''),
            'type': 'audio',
            'mimetype': audio_data.get('mimetype', '')
        }
        
        print(f"📊 Dados para W-API:")
        for key, value in media_data.items():
            if key in ['mediaKey', 'directPath'] and len(str(value)) > 30:
                print(f"   {key}: {str(value)[:30]}...")
            else:
                print(f"   {key}: {value}")
        
        # Simular process_media_automatically
        print(f"\n🔄 Simulando process_media_automatically...")
        from webhook.views import process_media_automatically
        resultado = process_media_automatically(webhook_data, cliente, instance)
        
        print(f"✅ Resultado: {resultado}")
        
        if not resultado:
            print("❌ Função retornou False - investigar por quê")
            
            # Testar download_media_via_wapi diretamente
            print(f"\n🔧 Testando download_media_via_wapi diretamente...")
            from webhook.views import download_media_via_wapi
            
            resultado_wapi = download_media_via_wapi(
                instance.instance_id,
                instance.token,
                media_data
            )
            
            print(f"📋 Resultado W-API: {type(resultado_wapi)} - {resultado_wapi}")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    print("🔍 DEBUG SIMPLES WEBHOOK - SEM DJANGO CONTAINS")
    print("=" * 80)
    
    debug_webhook_simples()
    
    print(f"\n💡 SE O TESTE MOSTRAR QUE A FUNÇÃO ESTÁ SENDO CHAMADA:")
    print("   1. Verificar se os prints aparecem no console do Django")
    print("   2. Se não aparecem = logs não estão sendo exibidos")
    print("   3. Se aparecem = verificar onde está falhando")

if __name__ == "__main__":
    main() 