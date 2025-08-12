#!/usr/bin/env python3
"""
🔍 DEBUG WEBHOOK LOGS
Verifica se os logs da função process_media_automatically estão aparecendo
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

def analisar_webhook_recente():
    """Analisa o webhook mais recente para debug"""
    print("🔍 ANÁLISE DO WEBHOOK MAIS RECENTE")
    print("=" * 60)
    
    # Buscar webhook mais recente com áudio
    webhook = WebhookEvent.objects.filter(
        raw_data__contains="audioMessage"
    ).order_by('-timestamp').first()
    
    if not webhook:
        print("❌ Nenhum webhook com áudio encontrado")
        return
    
    print(f"📧 Event ID: {webhook.event_id}")
    print(f"🕒 Timestamp: {webhook.timestamp}")
    print(f"👤 Cliente: {webhook.cliente.nome}")
    print(f"✅ Processed: {webhook.processed}")
    print(f"🏷️ Event Type: {webhook.event_type}")
    
    data = webhook.raw_data
    print(f"\n📊 DADOS DO WEBHOOK:")
    print(f"   Message ID: {data.get('messageId', 'N/A')}")
    print(f"   From Me: {data.get('fromMe', 'N/A')}")
    print(f"   Instance ID: {data.get('instanceId', 'N/A')}")
    
    # Analisar dados do áudio
    msg_content = data.get('msgContent', {})
    audio_data = msg_content.get('audioMessage', {})
    
    print(f"\n🎵 DADOS DO ÁUDIO:")
    print(f"   MediaKey: {'✅' if audio_data.get('mediaKey') else '❌'} ({len(audio_data.get('mediaKey', ''))} chars)")
    print(f"   DirectPath: {'✅' if audio_data.get('directPath') else '❌'} {audio_data.get('directPath', 'N/A')[:50]}...")
    print(f"   Mimetype: {'✅' if audio_data.get('mimetype') else '❌'} {audio_data.get('mimetype', 'N/A')}")
    print(f"   File Length: {audio_data.get('fileLength', 'N/A')}")
    
    # Verificar se dados são válidos para download
    media_key = audio_data.get('mediaKey', '')
    direct_path = audio_data.get('directPath', '')
    mimetype = audio_data.get('mimetype', '')
    
    print(f"\n🔍 VALIDAÇÃO PARA DOWNLOAD:")
    print(f"   MediaKey válida: {'✅' if media_key else '❌'}")
    print(f"   DirectPath válido: {'✅' if direct_path else '❌'}")
    print(f"   Mimetype válido: {'✅' if mimetype else '❌'}")
    
    if media_key and direct_path and mimetype:
        print(f"   🎯 TODOS OS DADOS VÁLIDOS - deveria baixar!")
    else:
        print(f"   ❌ DADOS INVÁLIDOS - não vai baixar")
        return
    
    # Verificar instância
    from core.models import WhatsappInstance
    try:
        instance = WhatsappInstance.objects.get(instance_id=data.get('instanceId'))
        print(f"\n📱 INSTÂNCIA ENCONTRADA:")
        print(f"   ID: {instance.instance_id}")
        print(f"   Cliente: {instance.cliente.nome}")
        print(f"   Token: {'✅' if instance.token else '❌'} {instance.token[:20] if instance.token else 'AUSENTE'}...")
        print(f"   Status: {instance.status}")
    except:
        print(f"\n❌ INSTÂNCIA NÃO ENCONTRADA: {data.get('instanceId')}")
        return
    
    # Simular a chamada da função
    print(f"\n🧪 SIMULANDO CHAMADA process_media_automatically...")
    try:
        from webhook.views import process_media_automatically
        resultado = process_media_automatically(data, webhook.cliente, instance)
        print(f"   ✅ Resultado: {resultado}")
    except Exception as e:
        print(f"   ❌ Erro na simulação: {e}")
        import traceback
        traceback.print_exc()

def testar_funcao_download():
    """Testa diretamente a função de download"""
    print(f"\n🧪 TESTE DIRETO DA FUNÇÃO DOWNLOAD")
    print("=" * 60)
    
    # Buscar webhook recente
    webhook = WebhookEvent.objects.filter(
        raw_data__contains="audioMessage"
    ).order_by('-timestamp').first()
    
    if not webhook:
        print("❌ Nenhum webhook encontrado")
        return
    
    data = webhook.raw_data
    audio_data = data.get('msgContent', {}).get('audioMessage', {})
    
    # Preparar dados para teste
    media_data = {
        'mediaKey': audio_data.get('mediaKey', ''),
        'directPath': audio_data.get('directPath', ''),
        'type': 'audio',
        'mimetype': audio_data.get('mimetype', '')
    }
    
    print(f"📊 Dados para teste:")
    for key, value in media_data.items():
        if isinstance(value, str) and len(value) > 50:
            print(f"   {key}: {value[:50]}...")
        else:
            print(f"   {key}: {value}")
    
    # Buscar instância
    from core.models import WhatsappInstance
    try:
        instance = WhatsappInstance.objects.get(instance_id=data.get('instanceId'))
        
        print(f"\n🔄 Testando download_media_via_wapi...")
        
        from webhook.views import download_media_via_wapi
        resultado = download_media_via_wapi(
            instance.instance_id,
            instance.token,
            media_data
        )
        
        print(f"✅ Resultado: {type(resultado)} - {resultado}")
        
        if isinstance(resultado, str):
            from pathlib import Path
            if Path(resultado).exists():
                print(f"✅ Arquivo existe: {resultado}")
            else:
                print(f"❌ Arquivo não existe: {resultado}")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    print("🔍 DEBUG WEBHOOK LOGS - INVESTIGAÇÃO DETALHADA")
    print("=" * 80)
    
    analisar_webhook_recente()
    testar_funcao_download()
    
    print(f"\n💡 CONCLUSÕES:")
    print("✅ Se os dados estão válidos mas o arquivo não baixa:")
    print("   - Problema pode estar na função download_media_via_wapi")
    print("   - Ou na W-API (token, rede, etc.)")
    print("❌ Se os dados estão inválidos:")
    print("   - Problema está na estrutura do webhook")
    print("   - Ou na extração dos dados")

if __name__ == "__main__":
    main() 