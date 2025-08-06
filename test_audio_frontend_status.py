#!/usr/bin/env python3
"""
Script para testar o status dos áudios no frontend
Verifica se existem mensagens de áudio e como estão sendo processadas
"""

import os
import sys
import django

# Configurar Django
sys.path.append('multichat_system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente
from webhook.models import Message

def main():
    print("🎵 TESTE STATUS ÁUDIO FRONTEND")
    print("=" * 50)
    
    # 1. Verificar mensagens de áudio no Core
    print("\n📊 MENSAGENS DE ÁUDIO (Core):")
    audio_messages_core = Mensagem.objects.filter(media_type='audio')
    print(f"Total de mensagens de áudio: {audio_messages_core.count()}")
    
    for msg in audio_messages_core[:5]:  # Mostrar só as primeiras 5
        print(f"  🎵 ID: {msg.id}")
        print(f"     Tipo: {msg.media_type}")
        print(f"     URL: {msg.media_url}")
        print(f"     Conteúdo: {msg.conteudo[:100] if msg.conteudo else 'N/A'}...")
        print(f"     Chat: {msg.chat_id}")
        print()
    
    # 2. Verificar mensagens de áudio no Webhook
    print("\n📊 MENSAGENS DE ÁUDIO (Webhook):")
    try:
        audio_messages_webhook = Message.objects.filter(
            message_type='audio'
        ).exclude(media_url__isnull=True).exclude(media_url='')
        print(f"Total de mensagens de áudio processadas: {audio_messages_webhook.count()}")
        
        for msg in audio_messages_webhook[:5]:  # Mostrar só as primeiras 5
            print(f"  🎵 ID: {msg.id}")
            print(f"     Tipo: {msg.message_type}")
            print(f"     URL: {msg.media_url}")
            print(f"     Chat: {msg.chat.remote_jid if msg.chat else 'N/A'}")
            print()
    except Exception as e:
        print(f"❌ Erro ao acessar webhook messages: {e}")
    
    # 3. Verificar arquivos de áudio no sistema
    print("\n📁 ARQUIVOS DE ÁUDIO NO SISTEMA:")
    media_root = os.path.join('multichat_system', 'media', 'audios')
    if os.path.exists(media_root):
        audio_count = 0
        for root, dirs, files in os.walk(media_root):
            for file in files:
                if file.endswith(('.mp3', '.ogg', '.wav', '.m4a')):
                    audio_count += 1
                    if audio_count <= 5:  # Mostrar só os primeiros 5
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, 'multichat_system/media')
                        file_size = os.path.getsize(file_path)
                        print(f"  🎵 {relative_path} ({file_size} bytes)")
        
        print(f"\nTotal de arquivos de áudio: {audio_count}")
    else:
        print("❌ Pasta de áudios não encontrada")
    
    # 4. Teste de dados para frontend
    print("\n🖥️ DADOS PARA FRONTEND:")
    print("Exemplo de mensagem que o frontend deveria receber:")
    
    if audio_messages_core.exists():
        msg = audio_messages_core.first()
        frontend_data = {
            'id': msg.id,
            'tipo': 'audio',
            'type': 'audio',
            'content': msg.conteudo or '[Áudio]',
            'conteudo': msg.conteudo or '[Áudio]',
            'mediaUrl': msg.media_url,
            'mediaType': 'audio',
            'fromMe': msg.from_me,
            'timestamp': str(msg.timestamp)
        }
        
        print("Dados JSON:")
        import json
        print(json.dumps(frontend_data, indent=2, ensure_ascii=False))
        
        print(f"\n✅ URL do áudio: http://localhost:8000{msg.media_url}")
        print(f"✅ URL alternativa: http://localhost:8000/api/audio/message/{msg.id}/")
    else:
        print("❌ Nenhuma mensagem de áudio encontrada")
    
    print("\n" + "=" * 50)
    print("🎵 TESTE CONCLUÍDO")

if __name__ == '__main__':
    main()