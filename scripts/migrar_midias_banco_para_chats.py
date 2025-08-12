#!/usr/bin/env python3
"""
🔄 MIGRAÇÃO COMPLETA DE MÍDIAS DO BANCO PARA CHATS
Busca todas as mídias armazenadas no banco e faz download para seus respectivos chats
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

def listar_midias_pendentes():
    """Lista todas as mídias que precisam ser baixadas"""
    print("📋 LISTANDO MÍDIAS PENDENTES PARA DOWNLOAD")
    print("=" * 80)
    
    from core.models import MediaFile
    from webhook.models import WebhookEvent, MessageMedia
    
    # Verificar MediaFile (modelo principal)
    print("1. VERIFICANDO MediaFile...")
    medias_pendentes = MediaFile.objects.filter(
        download_status__in=['pending', 'failed']
    ).exclude(
        media_key__isnull=True
    ).exclude(
        direct_path__isnull=True
    )
    
    print(f"   📊 Mídias pendentes no MediaFile: {medias_pendentes.count()}")
    
    # Verificar MessageMedia (modelo secundário)
    print("2. VERIFICANDO MessageMedia...")
    message_medias_pendentes = MessageMedia.objects.filter(
        download_status__in=['pending', 'failed']
    ).exclude(
        media_key__isnull=True
    ).exclude(
        direct_path__isnull=True
    )
    
    print(f"   📊 Mídias pendentes no MessageMedia: {message_medias_pendentes.count()}")
    
    # Verificar mídias em WebhookEvent que podem não ter sido processadas
    print("3. VERIFICANDO WebhookEvents com mídias...")
    webhooks_com_midia = WebhookEvent.objects.filter(
        raw_data__msgContent__icontains='"audioMessage"'
    ).exclude(
        raw_data__msgContent__audioMessage__mediaKey__isnull=True
    )
    
    webhooks_audio = webhooks_com_midia.filter(raw_data__msgContent__icontains='"audioMessage"')
    webhooks_image = webhooks_com_midia.filter(raw_data__msgContent__icontains='"imageMessage"')
    webhooks_video = webhooks_com_midia.filter(raw_data__msgContent__icontains='"videoMessage"')
    
    print(f"   📊 Webhooks com audioMessage: {webhooks_audio.count()}")
    print(f"   📊 Webhooks com imageMessage: {webhooks_image.count()}")
    print(f"   📊 Webhooks com videoMessage: {webhooks_video.count()}")
    
    total_estimado = medias_pendentes.count() + message_medias_pendentes.count()
    print(f"\n🎯 TOTAL ESTIMADO PARA MIGRAÇÃO: {total_estimado}")
    
    return medias_pendentes, message_medias_pendentes, webhooks_com_midia

def migrar_mediafile():
    """Migra mídias do modelo MediaFile"""
    print("\n🔄 MIGRANDO MediaFile")
    print("=" * 80)
    
    from core.models import MediaFile
    from webhook.media_downloader import MultiChatMediaDownloader
    
    medias_pendentes = MediaFile.objects.filter(
        download_status__in=['pending', 'failed']
    ).exclude(
        media_key__isnull=True
    ).exclude(
        direct_path__isnull=True
    )
    
    print(f"📊 Processando {medias_pendentes.count()} mídias do MediaFile...")
    
    sucessos = 0
    falhas = 0
    
    for i, media in enumerate(medias_pendentes, 1):
        try:
            print(f"\n📄 [{i}/{medias_pendentes.count()}] Processando: {media.message_id}")
            print(f"   👤 Cliente: {media.cliente.nome}")
            print(f"   🎵 Tipo: {media.media_type}")
            print(f"   📞 Chat: {getattr(media.chat, 'chat_id', 'N/A') if media.chat else 'N/A'}")
            
            # Criar downloader
            downloader = MultiChatMediaDownloader(media.cliente)
            
            # Preparar dados de mídia
            info_midia = {
                'type': media.media_type,
                'mimetype': media.mimetype,
                'mediaKey': media.media_key,
                'directPath': media.direct_path,
                'fileSha256': media.file_sha256,
                'fileEncSha256': media.file_enc_sha256,
                'mediaKeyTimestamp': media.media_key_timestamp,
                'fileLength': media.file_size,
                'seconds': media.duration_seconds,
                'ptt': media.is_ptt,
                'caption': media.caption,
                'width': media.width,
                'height': media.height
            }
            
            # Determinar chat_id
            chat_id = 'unknown'
            if media.chat and hasattr(media.chat, 'chat_id'):
                chat_id = media.chat.chat_id
            elif media.sender_id:
                chat_id = media.sender_id
            
            # Definir chat_id no downloader
            downloader._current_chat_id = chat_id
            
            # Tentar download
            caminho_arquivo = downloader.descriptografar_e_baixar_midia(
                info_midia, 
                media.message_id, 
                media.sender_name or 'Usuario'
            )
            
            if caminho_arquivo and os.path.exists(caminho_arquivo):
                # Atualizar status
                media.file_path = caminho_arquivo
                media.download_status = 'success'
                media.download_timestamp = django.utils.timezone.now()
                media.save()
                
                print(f"   ✅ Sucesso: {os.path.basename(caminho_arquivo)}")
                sucessos += 1
            else:
                print(f"   ❌ Falha no download")
                media.download_status = 'failed'
                media.save()
                falhas += 1
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            falhas += 1
            try:
                media.download_status = 'failed'
                media.save()
            except:
                pass
    
    print(f"\n📊 RESULTADOS MediaFile:")
    print(f"   ✅ Sucessos: {sucessos}")
    print(f"   ❌ Falhas: {falhas}")
    
    return sucessos, falhas

def migrar_webhooks_pendentes():
    """Migra mídias de webhooks que podem não ter sido processados"""
    print("\n🔄 MIGRANDO WEBHOOKS COM MÍDIAS PENDENTES")
    print("=" * 80)
    
    from webhook.models import WebhookEvent
    from webhook.media_downloader import processar_midias_automaticamente
    
    # Buscar webhooks com mídias que podem não ter sido processados
    webhooks_com_midia = WebhookEvent.objects.filter(
        raw_data__msgContent__icontains='"Message"'
    ).order_by('-timestamp')[:50]  # Últimos 50 para não sobrecarregar
    
    print(f"📊 Verificando {webhooks_com_midia.count()} webhooks recentes...")
    
    sucessos = 0
    falhas = 0
    processados = 0
    
    for i, webhook in enumerate(webhooks_com_midia, 1):
        try:
            data = webhook.raw_data
            msg_content = data.get('msgContent', {})
            
            # Verificar se tem mídia
            tipos_midia = ['audioMessage', 'imageMessage', 'videoMessage', 'documentMessage', 'stickerMessage']
            tem_midia = any(tipo in msg_content for tipo in tipos_midia)
            
            if not tem_midia:
                continue
                
            processados += 1
            print(f"\n📄 [{processados}] Webhook: {webhook.timestamp}")
            print(f"   📧 Message ID: {data.get('messageId')}")
            print(f"   👤 Cliente: {webhook.cliente.nome}")
            
            # Tentar processar
            resultado = processar_midias_automaticamente(webhook)
            
            if resultado:
                print(f"   ✅ Processado com sucesso")
                sucessos += 1
            else:
                print(f"   ⚠️ Processado sem resultado")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            falhas += 1
    
    print(f"\n📊 RESULTADOS Webhooks:")
    print(f"   🔄 Processados: {processados}")
    print(f"   ✅ Sucessos: {sucessos}")
    print(f"   ❌ Falhas: {falhas}")
    
    return sucessos, falhas

def verificar_estrutura_final():
    """Verifica a estrutura final após a migração"""
    print("\n📂 VERIFICANDO ESTRUTURA FINAL")
    print("=" * 80)
    
    base_path = Path(__file__).parent / "multichat_system" / "media_storage"
    
    if not base_path.exists():
        print("❌ Pasta media_storage não encontrada")
        return
    
    total_arquivos = 0
    
    for cliente_folder in base_path.iterdir():
        if cliente_folder.is_dir() and not cliente_folder.name.startswith('.'):
            print(f"\n👤 Cliente: {cliente_folder.name}")
            
            for instance_folder in cliente_folder.iterdir():
                if instance_folder.is_dir() and instance_folder.name.startswith('instance_'):
                    print(f"   📱 {instance_folder.name}")
                    
                    # Verificar estrutura de chats
                    chats_folder = instance_folder / "chats"
                    if chats_folder.exists():
                        for chat_folder in chats_folder.iterdir():
                            if chat_folder.is_dir():
                                chat_total = 0
                                for tipo_folder in chat_folder.iterdir():
                                    if tipo_folder.is_dir():
                                        arquivos = list(tipo_folder.glob("*"))
                                        if arquivos:
                                            chat_total += len(arquivos)
                                            print(f"     📞 {chat_folder.name}/{tipo_folder.name}: {len(arquivos)} arquivo(s)")
                                
                                total_arquivos += chat_total
    
    print(f"\n🎯 TOTAL DE ARQUIVOS MIGRADOS: {total_arquivos}")

def main():
    """Função principal"""
    print("🔄 MIGRAÇÃO COMPLETA DE MÍDIAS DO BANCO PARA CHATS")
    print("=" * 100)
    print("OBJETIVO: Buscar todas as mídias no banco e fazer download para chats")
    print("=" * 100)
    
    # Importar dentro da função para evitar problemas de import
    import django.utils.timezone
    globals()['django'] = django
    
    inicio = datetime.now()
    
    # 1. Listar mídias pendentes
    medias_pendentes, message_medias_pendentes, webhooks_com_midia = listar_midias_pendentes()
    
    input("\n⏸️ Pressione ENTER para continuar com a migração...")
    
    total_sucessos = 0
    total_falhas = 0
    
    # 2. Migrar MediaFile
    if medias_pendentes.exists():
        sucessos, falhas = migrar_mediafile()
        total_sucessos += sucessos
        total_falhas += falhas
    
    # 3. Migrar webhooks pendentes
    sucessos, falhas = migrar_webhooks_pendentes()
    total_sucessos += sucessos
    total_falhas += falhas
    
    # 4. Verificar estrutura final
    verificar_estrutura_final()
    
    # Resumo final
    fim = datetime.now()
    duracao = fim - inicio
    
    print("\n" + "=" * 100)
    print("📋 RESUMO FINAL DA MIGRAÇÃO")
    print("=" * 100)
    print(f"⏱️ Duração: {duracao}")
    print(f"✅ Total de sucessos: {total_sucessos}")
    print(f"❌ Total de falhas: {total_falhas}")
    print(f"📊 Taxa de sucesso: {(total_sucessos/(total_sucessos+total_falhas)*100):.1f}%" if (total_sucessos+total_falhas) > 0 else "N/A")
    print("\n🎯 MIGRAÇÃO CONCLUÍDA!")
    print("💡 Agora todas as mídias do banco foram migradas para seus chats corretos")

if __name__ == "__main__":
    main() 