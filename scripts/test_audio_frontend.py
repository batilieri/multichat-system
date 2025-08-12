#!/usr/bin/env python3
"""
Script para testar se os áudios estão sendo processados e exibidos corretamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente
from webhook.models import Message, WebhookEvent
import json

def test_audio_messages():
    """Testa se as mensagens de áudio estão sendo processadas corretamente"""
    print("🧪 TESTANDO MENSAGENS DE ÁUDIO")
    print("=" * 60)
    
    # Buscar mensagens de áudio
    audio_messages_core = Mensagem.objects.filter(tipo='audio')
    audio_messages_webhook = Message.objects.filter(message_type='audio')
    
    print(f"📊 Mensagens de áudio no core: {audio_messages_core.count()}")
    print(f"📊 Mensagens de áudio no webhook: {audio_messages_webhook.count()}")
    
    # Verificar mensagens do core
    print("\n🔍 Mensagens de áudio no core:")
    for msg in audio_messages_core[:5]:
        print(f"  ID: {msg.id}")
        print(f"  Tipo: {msg.tipo}")
        print(f"  Conteúdo: {msg.conteudo}")
        print(f"  From Me: {msg.from_me}")
        print(f"  Data: {msg.data_envio}")
        print("  ---")
    
    # Verificar mensagens do webhook
    print("\n🔍 Mensagens de áudio no webhook:")
    for msg in audio_messages_webhook[:5]:
        print(f"  ID: {msg.id}")
        print(f"  Tipo: {msg.message_type}")
        print(f"  Conteúdo: {msg.text_content}")
        print(f"  From Me: {msg.from_me}")
        print(f"  Media URL: {msg.media_url}")
        print(f"  Media Type: {msg.media_type}")
        print(f"  Media Size: {msg.media_size}")
        print(f"  Data: {msg.timestamp}")
        print("  ---")
    
    # Verificar se há áudios com URLs
    audio_with_url = audio_messages_webhook.filter(media_url__isnull=False).exclude(media_url='')
    print(f"\n📊 Áudios com URL: {audio_with_url.count()}")
    
    for audio in audio_with_url[:3]:
        print(f"  URL: {audio.media_url}")
        print(f"  Tamanho: {audio.media_size}")
        print(f"  Tipo: {audio.media_type}")
        print("  ---")

def test_audio_processing():
    """Testa o processamento de áudios"""
    print("\n🧪 TESTANDO PROCESSAMENTO DE ÁUDIOS")
    print("=" * 60)
    
    # Dados de teste de áudio
    test_audio_data = {
        "fromMe": False,
        "chat": {
            "id": "556999267344",
            "profilePicture": "https://example.com/chat.jpg"
        },
        "sender": {
            "id": "556993291093",
            "profilePicture": "https://example.com/sender.jpg",
            "pushName": "Teste"
        },
        "msgContent": {
            "audioMessage": {
                "url": "https://example.com/audio.mp3",
                "mimetype": "audio/mpeg",
                "fileLength": 1024000,
                "duration": 30,
                "ptt": False,
                "mediaKey": "test_key",
                "directPath": "/test/audio.mp3",
                "mediaKeyTimestamp": "1748872244"
            }
        },
        "messageTimestamp": "1748872244"
    }
    
    print("📤 Dados de teste de áudio:")
    print(json.dumps(test_audio_data, indent=2))
    
    # Verificar se o tipo seria detectado corretamente
    if 'audioMessage' in test_audio_data['msgContent']:
        print("✅ Tipo de áudio detectado corretamente")
    else:
        print("❌ Tipo de áudio não detectado")

def check_audio_frontend_display():
    """Verifica se os áudios estão sendo exibidos no frontend"""
    print("\n🧪 VERIFICANDO EXIBIÇÃO NO FRONTEND")
    print("=" * 60)
    
    # Buscar áudios com URLs válidas
    audio_messages = Message.objects.filter(
        message_type='audio',
        media_url__isnull=False
    ).exclude(media_url='')
    
    print(f"📊 Áudios disponíveis para exibição: {audio_messages.count()}")
    
    for audio in audio_messages[:3]:
        print(f"\n🎵 Áudio ID: {audio.id}")
        print(f"  URL: {audio.media_url}")
        print(f"  Tamanho: {audio.media_size} bytes")
        print(f"  Tipo: {audio.media_type}")
        print(f"  From Me: {audio.from_me}")
        print(f"  Chat: {audio.chat.chat_name}")
        
        # Verificar se a URL é acessível
        import requests
        try:
            response = requests.head(audio.media_url, timeout=5)
            if response.status_code == 200:
                print(f"  ✅ URL acessível (Status: {response.status_code})")
            else:
                print(f"  ⚠️ URL não acessível (Status: {response.status_code})")
        except Exception as e:
            print(f"  ❌ Erro ao acessar URL: {e}")

def main():
    """Função principal"""
    print("🔧 TESTE DE ÁUDIOS NO FRONTEND")
    print("=" * 60)
    
    try:
        # Testar mensagens de áudio
        test_audio_messages()
        
        # Testar processamento
        test_audio_processing()
        
        # Verificar exibição no frontend
        check_audio_frontend_display()
        
        print("\n✅ Testes concluídos!")
        
    except Exception as e:
        print(f"❌ Erro nos testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 