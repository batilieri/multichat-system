#!/usr/bin/env python3
"""
🔧 DEBUG DOWNLOAD AUTOMÁTICO
Testa por que o download automático de mídias não está funcionando
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

def testar_download_automatico():
    """Testa o download automático com um webhook real"""
    print("🔧 TESTE DOWNLOAD AUTOMÁTICO")
    print("=" * 80)
    
    from webhook.models import WebhookEvent
    from webhook.media_downloader import processar_midias_automaticamente
    
    # Pegar último webhook com áudio
    ultimo_webhook = None
    
    for webhook in WebhookEvent.objects.all().order_by('-timestamp')[:10]:
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
    
    print(f"✅ Webhook encontrado: {ultimo_webhook.timestamp}")
    print(f"   📧 Event ID: {ultimo_webhook.event_id}")
    print(f"   👤 Cliente: {ultimo_webhook.cliente.nome}")
    print(f"   📱 Instance ID: {ultimo_webhook.instance_id}")
    
    # Verificar dados do webhook
    data = ultimo_webhook.raw_data
    msg_content = data.get('msgContent', {})
    audio_msg = msg_content.get('audioMessage', {})
    
    print(f"\n📋 DADOS DO ÁUDIO:")
    print(f"   🔑 mediaKey: {'✅' if audio_msg.get('mediaKey') else '❌'}")
    print(f"   📂 directPath: {'✅' if audio_msg.get('directPath') else '❌'}")
    print(f"   🎭 mimetype: {audio_msg.get('mimetype', 'N/A')}")
    print(f"   📏 fileLength: {audio_msg.get('fileLength', 'N/A')}")
    print(f"   ⏱️ seconds: {audio_msg.get('seconds', 'N/A')}")
    
    # Verificar se WebhookEvent tem chat_id
    print(f"\n🔍 CHAT ID ANALYSIS:")
    print(f"   webhook.chat_id: {ultimo_webhook.chat_id}")
    print(f"   data.chat.id: {data.get('chat', {}).get('id')}")
    
    # Testar função processar_midias_automaticamente
    print(f"\n🧪 TESTANDO DOWNLOAD AUTOMÁTICO...")
    try:
        processar_midias_automaticamente(ultimo_webhook)
        print(f"✅ Função executada sem erro")
    except Exception as e:
        print(f"❌ Erro na função: {e}")
        import traceback
        traceback.print_exc()
    
    # Verificar se arquivo foi criado
    print(f"\n📂 VERIFICANDO ESTRUTURA DE ARQUIVOS:")
    
    cliente = ultimo_webhook.cliente
    instance_id = ultimo_webhook.instance_id
    chat_id = data.get('chat', {}).get('id', 'unknown')
    
    # Nome do cliente normalizado
    cliente_nome = "".join(c for c in cliente.nome if c.isalnum() or c in (' ', '-', '_')).strip()
    cliente_nome = cliente_nome.replace(' ', '_')
    
    # Verificar estrutura nova
    nova_estrutura = Path(__file__).parent / "multichat_system" / "media_storage" / cliente_nome / f"instance_{instance_id}" / "chats" / str(chat_id) / "audio"
    print(f"   Nova estrutura: {nova_estrutura}")
    print(f"   Existe: {'✅' if nova_estrutura.exists() else '❌'}")
    
    if nova_estrutura.exists():
        arquivos = list(nova_estrutura.glob("*.mp3"))
        print(f"   Arquivos: {len(arquivos)}")
        for arquivo in arquivos[-3:]:
            print(f"     📁 {arquivo.name}")
    
    # Verificar estrutura antiga
    estrutura_antiga = Path(__file__).parent / "multichat_system" / "media_storage" / f"cliente_{cliente.id}" / f"instance_{instance_id}" / "audio"
    print(f"\n   Estrutura antiga: {estrutura_antiga}")
    print(f"   Existe: {'✅' if estrutura_antiga.exists() else '❌'}")
    
    if estrutura_antiga.exists():
        arquivos = list(estrutura_antiga.glob("*.mp3"))
        print(f"   Arquivos: {len(arquivos)}")
        for arquivo in arquivos[-3:]:
            print(f"     📁 {arquivo.name}")

def testar_downloader_diretamente():
    """Testa o MultiChatMediaDownloader diretamente"""
    print("\n🧪 TESTE DIRETO DO DOWNLOADER")
    print("=" * 80)
    
    from webhook.models import WebhookEvent
    from webhook.media_downloader import MultiChatMediaDownloader
    from core.models import Cliente
    
    # Pegar último webhook com áudio
    ultimo_webhook = None
    
    for webhook in WebhookEvent.objects.all().order_by('-timestamp')[:10]:
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
    
    cliente = ultimo_webhook.cliente
    data = ultimo_webhook.raw_data
    
    print(f"✅ Testando downloader para cliente: {cliente.nome}")
    
    # Criar downloader
    downloader = MultiChatMediaDownloader(cliente)
    
    print(f"📋 CONFIGURAÇÕES DO DOWNLOADER:")
    print(f"   Instance ID: {downloader.instance_id}")
    print(f"   Bearer Token: {'✅' if downloader.bearer_token else '❌'}")
    print(f"   Cliente: {downloader.cliente.nome}")
    
    # Definir chat_id
    chat_id = data.get('chat', {}).get('id', 'unknown')
    downloader._current_chat_id = chat_id
    print(f"   Chat ID: {chat_id}")
    
    # Tentar processar
    try:
        resultado = downloader.processar_mensagem_com_midia(ultimo_webhook, data)
        print(f"📋 Resultado: {resultado}")
    except Exception as e:
        print(f"❌ Erro no downloader: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    print("🔧 DEBUG DOWNLOAD AUTOMÁTICO")
    print("=" * 100)
    print("OBJETIVO: Identificar por que o download automático não está funcionando")
    print("=" * 100)
    
    # 1. Testar função processar_midias_automaticamente
    testar_download_automatico()
    
    # 2. Testar downloader diretamente
    testar_downloader_diretamente()
    
    print("\n" + "=" * 100)
    print("🎯 CONCLUSÕES:")
    print("1. Se a função executa sem erro mas não baixa → problema no downloader")
    print("2. Se dá erro na função → problema na configuração")
    print("3. Se downloader direto funciona → problema na integração")

if __name__ == "__main__":
    main() 