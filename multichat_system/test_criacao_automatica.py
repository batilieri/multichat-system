#!/usr/bin/env python3
"""
Script para testar a criação automática de pastas de mídia
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat
from webhook.views import (
    criar_pasta_audio_automatica,
    criar_pasta_imagem_automatica,
    criar_pasta_video_automatica,
    criar_pasta_documento_automatica,
    criar_pasta_sticker_automatica
)

def testar_criacao_automatica():
    """Testa a criação automática de pastas"""
    print("🧪 Testando criação automática de pastas...")
    
    # Buscar chat e instância
    chat = Chat.objects.filter(mensagens__tipo='audio').first()
    if not chat:
        print("❌ Nenhum chat com áudio encontrado!")
        return
    
    instance = chat.cliente.whatsapp_instances.first()
    if not instance:
        print("❌ Nenhuma instância encontrada!")
        return
    
    print(f"📱 Chat: {chat.chat_id}")
    print(f"📱 Instância: {instance.instance_id}")
    print(f"👤 Cliente: {chat.cliente.nome}")
    
    # Testar criação de pastas para diferentes tipos de mídia
    message_id = "test_auto_creation"
    
    print("\n🎵 Testando criação de pasta de áudio...")
    pasta_audio = criar_pasta_audio_automatica(chat, instance, message_id)
    if pasta_audio:
        print(f"✅ Pasta de áudio criada: {pasta_audio}")
        # Verificar se existe
        if os.path.exists(pasta_audio):
            print("✅ Pasta existe no sistema de arquivos")
        else:
            print("❌ Pasta não existe no sistema de arquivos")
    else:
        print("❌ Falha ao criar pasta de áudio")
    
    print("\n🖼️ Testando criação de pasta de imagem...")
    pasta_imagem = criar_pasta_imagem_automatica(chat, instance, message_id)
    if pasta_imagem:
        print(f"✅ Pasta de imagem criada: {pasta_imagem}")
        if os.path.exists(pasta_imagem):
            print("✅ Pasta existe no sistema de arquivos")
        else:
            print("❌ Pasta não existe no sistema de arquivos")
    else:
        print("❌ Falha ao criar pasta de imagem")
    
    print("\n🎬 Testando criação de pasta de vídeo...")
    pasta_video = criar_pasta_video_automatica(chat, instance, message_id)
    if pasta_video:
        print(f"✅ Pasta de vídeo criada: {pasta_video}")
        if os.path.exists(pasta_video):
            print("✅ Pasta existe no sistema de arquivos")
        else:
            print("❌ Pasta não existe no sistema de arquivos")
    else:
        print("❌ Falha ao criar pasta de vídeo")
    
    print("\n📄 Testando criação de pasta de documento...")
    pasta_documento = criar_pasta_documento_automatica(chat, instance, message_id)
    if pasta_documento:
        print(f"✅ Pasta de documento criada: {pasta_documento}")
        if os.path.exists(pasta_documento):
            print("✅ Pasta existe no sistema de arquivos")
        else:
            print("❌ Pasta não existe no sistema de arquivos")
    else:
        print("❌ Falha ao criar pasta de documento")
    
    print("\n😀 Testando criação de pasta de sticker...")
    pasta_sticker = criar_pasta_sticker_automatica(chat, instance, message_id)
    if pasta_sticker:
        print(f"✅ Pasta de sticker criada: {pasta_sticker}")
        if os.path.exists(pasta_sticker):
            print("✅ Pasta existe no sistema de arquivos")
        else:
            print("❌ Pasta não existe no sistema de arquivos")
    else:
        print("❌ Falha ao criar pasta de sticker")

def verificar_estrutura_criada():
    """Verifica a estrutura criada"""
    print("\n🔍 Verificando estrutura criada...")
    
    # Buscar pasta base
    base_path = Path(__file__).parent / "media_storage"
    
    if not base_path.exists():
        print(f"❌ Pasta base não existe: {base_path}")
        return
    
    print(f"✅ Pasta base existe: {base_path}")
    
    # Listar estrutura completa
    for cliente_path in base_path.glob("cliente_*"):
        print(f"\n👤 {cliente_path.name}")
        
        for instance_path in cliente_path.glob("instance_*"):
            print(f"   📱 {instance_path.name}")
            
            chats_path = instance_path / "chats"
            if chats_path.exists():
                for chat_path in chats_path.glob("*"):
                    if chat_path.is_dir():
                        print(f"      📱 {chat_path.name}")
                        
                        # Verificar pastas de mídia
                        for media_type in ["audio", "imagens", "videos", "documentos", "stickers"]:
                            media_path = chat_path / media_type
                            if media_path.exists():
                                arquivos = list(media_path.glob("*"))
                                print(f"         📁 {media_type}: {len(arquivos)} arquivos")
                            else:
                                print(f"         ⚠️ {media_type}: pasta não existe")

def simular_webhook_audio():
    """Simula o processamento de um webhook de áudio"""
    print("\n🎵 Simulando webhook de áudio...")
    
    # Dados simulados de webhook
    webhook_data = {
        "messageId": "test_webhook_audio",
        "sender": {
            "id": "556999211347@c.us",
            "pushName": "Teste Áudio"
        },
        "msgContent": {
            "audioMessage": {
                "url": "https://mmg.whatsapp.net/v/test.enc",
                "mediaKey": "test_key",
                "directPath": "/v/test.enc",
                "mimetype": "audio/ogg",
                "fileLength": "1000"
            }
        }
    }
    
    # Buscar cliente e instância
    from core.models import Cliente
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado!")
        return
    
    instance = cliente.whatsapp_instances.first()
    if not instance:
        print("❌ Nenhuma instância encontrada!")
        return
    
    print(f"👤 Cliente: {cliente.nome}")
    print(f"📱 Instância: {instance.instance_id}")
    
    # Simular processamento
    from webhook.views import process_media_automatically
    
    print("🔄 Processando mídia automaticamente...")
    resultado = process_media_automatically(webhook_data, cliente, instance)
    
    if resultado:
        print("✅ Processamento automático funcionou!")
    else:
        print("❌ Processamento automático falhou!")

def main():
    """Função principal"""
    print("🚀 Testando criação automática de pastas...")
    print("=" * 60)
    
    # Testar criação automática
    testar_criacao_automatica()
    
    # Verificar estrutura
    verificar_estrutura_criada()
    
    # Simular webhook
    simular_webhook_audio()
    
    print("\n" + "=" * 60)
    print("✅ Teste de criação automática concluído!")

if __name__ == "__main__":
    main() 