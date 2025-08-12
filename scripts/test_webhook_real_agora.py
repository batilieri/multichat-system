#!/usr/bin/env python3
"""
🔧 TESTE WEBHOOK REAL AGORA
Verifica por que o download automático não está sendo chamado no último webhook
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

def verificar_ultimo_webhook():
    """Verifica o último webhook e tenta processar o download manualmente"""
    print("🔧 VERIFICANDO ÚLTIMO WEBHOOK")
    print("=" * 80)
    
    from webhook.models import WebhookEvent
    from webhook.media_downloader import processar_midias_automaticamente
    
    # Pegar o último webhook
    ultimo_webhook = WebhookEvent.objects.all().order_by('-timestamp').first()
    
    if not ultimo_webhook:
        print("❌ Nenhum webhook encontrado")
        return
    
    print(f"✅ Último webhook: {ultimo_webhook.timestamp}")
    print(f"   📧 Event ID: {ultimo_webhook.event_id}")
    print(f"   👤 Cliente: {ultimo_webhook.cliente.nome}")
    print(f"   📱 Instance ID: {ultimo_webhook.instance_id}")
    print(f"   ⚙️ Processado: {ultimo_webhook.processed}")
    
    # Verificar dados do webhook
    data = ultimo_webhook.raw_data
    msg_content = data.get('msgContent', {})
    message_id = data.get('messageId')
    chat_id = data.get('chat', {}).get('id')
    
    print(f"\n📋 DADOS DO WEBHOOK:")
    print(f"   📧 messageId: {message_id}")
    print(f"   📞 chat_id: {chat_id}")
    print(f"   🎵 tem_audio: {'audioMessage' in msg_content}")
    print(f"   🔑 mediaKey: {'✅' if msg_content.get('audioMessage', {}).get('mediaKey') else '❌'}")
    
    # Verificar se tem chat_id no webhook_event
    print(f"\n🔍 WEBHOOK EVENT ANALYSIS:")
    print(f"   webhook.chat_id: {ultimo_webhook.chat_id}")
    print(f"   data.chat.id: {data.get('chat', {}).get('id')}")
    
    # Tentar processar download manualmente
    if 'audioMessage' in msg_content:
        print(f"\n🧪 TESTANDO DOWNLOAD MANUAL...")
        try:
            print(f"   Chamando processar_midias_automaticamente...")
            processar_midias_automaticamente(ultimo_webhook)
            print(f"   ✅ Função executada")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            import traceback
            traceback.print_exc()
        
        # Verificar se arquivo foi criado
        print(f"\n📂 VERIFICANDO SE ARQUIVO FOI CRIADO:")
        cliente = ultimo_webhook.cliente
        instance_id = ultimo_webhook.instance_id
        
        # Nome do cliente normalizado
        cliente_nome = "".join(c for c in cliente.nome if c.isalnum() or c in (' ', '-', '_')).strip()
        cliente_nome = cliente_nome.replace(' ', '_')
        
        # Verificar estrutura
        audio_path = Path(__file__).parent / "multichat_system" / "media_storage" / cliente_nome / f"instance_{instance_id}" / "chats" / str(chat_id) / "audio"
        
        print(f"   Pasta: {audio_path}")
        print(f"   Existe: {'✅' if audio_path.exists() else '❌'}")
        
        if audio_path.exists():
            arquivos = list(audio_path.glob("*.ogg"))
            print(f"   Arquivos .ogg: {len(arquivos)}")
            for arquivo in arquivos:
                print(f"     📁 {arquivo.name}")
                
            arquivos_mp3 = list(audio_path.glob("*.mp3"))
            print(f"   Arquivos .mp3: {len(arquivos_mp3)}")
            for arquivo in arquivos_mp3:
                print(f"     📁 {arquivo.name}")

def verificar_se_funcao_sendo_chamada():
    """Verifica se a função processar_midias_automaticamente está sendo chamada"""
    print("\n🔍 VERIFICANDO SE FUNÇÃO ESTÁ SENDO CHAMADA")
    print("=" * 80)
    
    from webhook.models import WebhookEvent
    import logging
    
    # Configurar logging mais verboso
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('webhook.media_downloader')
    logger.setLevel(logging.DEBUG)
    
    # Pegar último webhook com áudio
    ultimo_webhook = None
    for webhook in WebhookEvent.objects.all().order_by('-timestamp')[:5]:
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
        
    print(f"✅ Webhook com áudio: {ultimo_webhook.timestamp}")
    
    # Verificar se função de download está sendo chamada corretamente
    print(f"\n🧪 SIMULANDO CHAMADA DO PROCESSOR...")
    
    try:
        # Simular exatamente o que o processor faz
        from webhook.processors import WhatsAppWebhookProcessor
        from webhook.media_downloader import processar_midias_automaticamente
        
        print(f"   1. Criando processor...")
        processor = WhatsAppWebhookProcessor(ultimo_webhook.cliente)
        
        print(f"   2. Verificando se função existe...")
        print(f"      processar_midias_automaticamente: {'✅' if processar_midias_automaticamente else '❌'}")
        
        print(f"   3. Chamando função diretamente...")
        resultado = processar_midias_automaticamente(ultimo_webhook)
        print(f"      Resultado: {resultado}")
        
    except Exception as e:
        print(f"   ❌ Erro na simulação: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    print("🔧 TESTE WEBHOOK REAL AGORA")
    print("=" * 100)
    print("OBJETIVO: Descobrir por que o download não está funcionando no webhook real")
    print("=" * 100)
    
    # 1. Verificar último webhook
    verificar_ultimo_webhook()
    
    # 2. Verificar se função está sendo chamada
    verificar_se_funcao_sendo_chamada()
    
    print("\n" + "=" * 100)
    print("🎯 INVESTIGAÇÃO:")
    print("Se a função manual funciona mas automática não → problema na integração")
    print("Se nem a função manual funciona → problema na função")
    print("Se logs não aparecem → função não está sendo chamada")

if __name__ == "__main__":
    main() 