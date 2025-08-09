#!/usr/bin/env python3
"""
🔍 DEBUG WEBHOOK DETALHADO
Monitora logs específicos para identificar onde está falhando o download
"""

import os
import sys
import django
import time
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

def verificar_webhooks_processados():
    """Verifica últimos webhooks com áudio que foram processados"""
    print("🔍 ANÁLISE DETALHADA DOS WEBHOOKS")
    print("=" * 80)
    
    from webhook.models import WebhookEvent
    from core.models import Mensagem, Chat, Cliente, WhatsappInstance
    
    # Buscar últimos webhooks com áudio
    webhooks_audio = []
    
    for webhook in WebhookEvent.objects.all().order_by('-timestamp')[:10]:
        try:
            data = webhook.raw_data
            msg_content = data.get('msgContent', {})
            
            if 'audioMessage' in msg_content:
                webhooks_audio.append(webhook)
                
                if len(webhooks_audio) >= 3:  # Analisar últimos 3
                    break
        except:
            continue
    
    print(f"📊 Analisando últimos {len(webhooks_audio)} webhooks com áudio:")
    print()
    
    for i, webhook in enumerate(webhooks_audio, 1):
        print(f"🎵 WEBHOOK {i} - {webhook.timestamp}")
        print("=" * 60)
        
        data = webhook.raw_data
        msg_content = data.get('msgContent', {})
        audio_msg = msg_content.get('audioMessage', {})
        
        # Informações do webhook
        print(f"📧 messageId: {data.get('messageId')}")
        print(f"👤 fromMe: {data.get('fromMe')}")
        print(f"⚙️ processed: {webhook.processed}")
        print(f"📞 chatId: {data.get('chatId')}")
        
        # Informações do áudio
        print(f"🎵 Audio dados:")
        print(f"   🔑 mediaKey: {'✅' if audio_msg.get('mediaKey') else '❌'}")
        print(f"   📂 directPath: {'✅' if audio_msg.get('directPath') else '❌'}")
        print(f"   🎭 mimetype: {audio_msg.get('mimetype', 'N/A')}")
        
        # Verificar se mensagem foi salva no banco
        message_id = data.get('messageId')
        mensagem = None
        try:
            mensagem = Mensagem.objects.filter(message_id=message_id).first()
            if mensagem:
                print(f"💾 Mensagem no banco: ✅ ID {mensagem.id}")
                print(f"   📁 Arquivo: {mensagem.arquivo_midia or 'N/A'}")
                print(f"   📂 Caminho: {mensagem.direct_path or 'N/A'}")
            else:
                print(f"💾 Mensagem no banco: ❌ Não encontrada")
        except Exception as e:
            print(f"💾 Erro ao verificar mensagem: {e}")
        
        # Verificar instância
        instance_id = data.get('instanceId')
        if instance_id:
            try:
                instance = WhatsappInstance.objects.get(instance_id=instance_id)
                print(f"📱 Instância: ✅ {instance.instance_id} - {instance.cliente.nome}")
                print(f"   🔑 Token: {'✅' if instance.token else '❌'}")
            except Exception as e:
                print(f"📱 Instância: ❌ {e}")
        
        print()

def simular_download_manual():
    """Simula o download manual de um áudio recente"""
    print("🧪 SIMULAÇÃO DE DOWNLOAD MANUAL")
    print("=" * 80)
    
    from webhook.models import WebhookEvent
    from core.models import WhatsappInstance
    
    # Pegar último webhook com áudio
    ultimo_webhook = None
    
    for webhook in WebhookEvent.objects.all().order_by('-timestamp')[:20]:
        try:
            data = webhook.raw_data
            msg_content = data.get('msgContent', {})
            
            if 'audioMessage' in msg_content:
                ultimo_webhook = webhook
                break
        except:
            continue
    
    if not ultimo_webhook:
        print("❌ Nenhum webhook com áudio encontrado")
        return
    
    print(f"🎵 Usando webhook: {ultimo_webhook.timestamp}")
    
    data = ultimo_webhook.raw_data
    msg_content = data.get('msgContent', {})
    audio_msg = msg_content.get('audioMessage', {})
    
    # Verificar dados necessários
    media_key = audio_msg.get('mediaKey')
    direct_path = audio_msg.get('directPath')
    mimetype = audio_msg.get('mimetype')
    instance_id = data.get('instanceId')
    
    print(f"📋 Dados para download:")
    print(f"   🔑 mediaKey: {media_key[:20] if media_key else 'AUSENTE'}...")
    print(f"   📂 directPath: {direct_path[:50] if direct_path else 'AUSENTE'}...")
    print(f"   🎭 mimetype: {mimetype}")
    print(f"   📱 instanceId: {instance_id}")
    
    if not all([media_key, direct_path, mimetype, instance_id]):
        print("❌ Dados insuficientes para download")
        return
    
    # Pegar instância e token
    try:
        instance = WhatsappInstance.objects.get(instance_id=instance_id)
        token = instance.token
        cliente = instance.cliente
        
        print(f"✅ Instância encontrada: {cliente.nome}")
        print(f"   🔑 Token: {token[:20] if token else 'AUSENTE'}...")
        
        if not token:
            print("❌ Token não encontrado")
            return
            
    except Exception as e:
        print(f"❌ Erro ao buscar instância: {e}")
        return
    
    # Preparar dados para download
    media_data = {
        'mediaKey': media_key,
        'directPath': direct_path,
        'type': 'audio',
        'mimetype': mimetype
    }
    
    print(f"\n🔄 Iniciando download manual...")
    
    # Importar função de download
    from webhook.views import download_media_via_wapi
    
    # Fazer download
    try:
        resultado = download_media_via_wapi(instance_id, token, media_data)
        
        print(f"\n📋 RESULTADO DO DOWNLOAD:")
        print(f"   Tipo: {type(resultado)}")
        print(f"   Valor: {resultado}")
        
        if resultado:
            print(f"✅ Download realizado com sucesso!")
            print(f"📁 Caminho: {resultado}")
            
            # Verificar se arquivo existe
            if os.path.exists(resultado):
                print(f"✅ Arquivo existe no sistema")
                print(f"📏 Tamanho: {os.path.getsize(resultado)} bytes")
            else:
                print(f"❌ Arquivo não existe no sistema")
        else:
            print(f"❌ Download falhou")
            
    except Exception as e:
        print(f"❌ Erro durante download: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    print("🔍 DEBUG WEBHOOK DETALHADO")
    print("=" * 100)
    print("OBJETIVO: Identificar exatamente onde está falhando o download")
    print("=" * 100)
    
    # 1. Verificar webhooks processados
    verificar_webhooks_processados()
    
    # 2. Simular download manual
    print("\n" + "=" * 100)
    simular_download_manual()
    
    print("\n" + "=" * 100)
    print("🎯 PRÓXIMOS PASSOS:")
    print("1. Se webhooks têm processed=True mas não há arquivo → problema no download")
    print("2. Se dados de mídia estão ausentes → problema no webhook")
    print("3. Se download manual falha → problema na API W-API")
    print("4. Se download manual funciona → problema na lógica automática")

if __name__ == "__main__":
    main() 