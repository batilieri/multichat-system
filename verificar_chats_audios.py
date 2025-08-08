#!/usr/bin/env python3
"""
Verificação completa de todos os chats e suas mensagens de áudio
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
django.setup()

from core.models import Cliente, Chat, Mensagem
import json
from pathlib import Path

def verificar_todos_chats():
    """Verifica todos os chats e suas mensagens de áudio"""
    print("🔍 VERIFICANDO TODOS OS CHATS")
    print("=" * 60)
    
    # Buscar todos os chats
    chats = Chat.objects.all()
    print(f"📊 Total de chats encontrados: {chats.count()}")
    
    for chat in chats:
        print(f"\n📱 Chat ID: {chat.chat_id}")
        print(f"   Nome: {chat.chat_name}")
        print(f"   Cliente: {chat.cliente.nome}")
        print(f"   Status: {chat.status}")
        print(f"   Última mensagem: {chat.last_message_at}")
        
        # Contar mensagens por tipo
        mensagens = chat.mensagens.all()
        print(f"   Total de mensagens: {mensagens.count()}")
        
        # Contar mensagens de áudio
        audio_messages = mensagens.filter(tipo='audio')
        print(f"   Mensagens de áudio: {audio_messages.count()}")
        
        if audio_messages.count() > 0:
            print(f"   🎵 ÁUDIOS ENCONTRADOS!")
            for msg in audio_messages[:3]:  # Mostrar primeiros 3
                print(f"      - ID: {msg.id}, Data: {msg.data_envio}")
                try:
                    json_data = json.loads(msg.conteudo)
                    if 'audioMessage' in json_data:
                        audio_data = json_data['audioMessage']
                        print(f"        URL: {audio_data.get('url', 'N/A')}")
                        print(f"        MediaKey: {audio_data.get('mediaKey', 'N/A')}")
                except:
                    print(f"        ⚠️ Erro ao processar JSON")
        else:
            print(f"   ⚠️ Nenhuma mensagem de áudio encontrada")

def verificar_pastas_audio():
    """Verifica as pastas de áudio de todos os chats"""
    print("\n📁 VERIFICANDO PASTAS DE ÁUDIO")
    print("=" * 60)
    
    media_path = Path("multichat_system/media_storage/cliente_2/instance_3B6XIW-ZTS923-GEAY6V/chats")
    
    if not media_path.exists():
        print("❌ Pasta de chats não encontrada!")
        return
    
    # Verificar cada chat
    for chat_dir in media_path.glob("*"):
        if chat_dir.is_dir():
            print(f"\n📱 Chat: {chat_dir.name}")
            
            # Verificar pasta de áudio
            audio_dir = chat_dir / "audio"
            if audio_dir.exists():
                files = list(audio_dir.glob("*"))
                print(f"   🎵 Áudios encontrados: {len(files)}")
                for file in files:
                    size_kb = file.stat().st_size / 1024
                    print(f"      - {file.name} ({size_kb:.1f} KB)")
            else:
                print(f"   ⚠️ Pasta de áudio não existe")

def verificar_mensagens_audio_banco():
    """Verifica mensagens de áudio no banco de dados"""
    print("\n🗄️ VERIFICANDO MENSAGENS DE ÁUDIO NO BANCO")
    print("=" * 60)
    
    # Buscar todas as mensagens de áudio
    audio_messages = Mensagem.objects.filter(tipo='audio')
    print(f"📊 Total de mensagens de áudio no banco: {audio_messages.count()}")
    
    if audio_messages.count() == 0:
        print("❌ Nenhuma mensagem de áudio encontrada no banco!")
        return
    
    # Agrupar por chat
    chats_com_audio = {}
    for msg in audio_messages:
        chat_id = msg.chat.chat_id
        if chat_id not in chats_com_audio:
            chats_com_audio[chat_id] = []
        chats_com_audio[chat_id].append(msg)
    
    print(f"📱 Chats com áudio: {len(chats_com_audio)}")
    
    for chat_id, messages in chats_com_audio.items():
        print(f"\n🎵 Chat {chat_id}: {len(messages)} áudios")
        for msg in messages:
            print(f"   - ID: {msg.id}, Data: {msg.data_envio}")
            try:
                json_data = json.loads(msg.conteudo)
                if 'audioMessage' in json_data:
                    audio_data = json_data['audioMessage']
                    print(f"     URL: {audio_data.get('url', 'N/A')}")
                    print(f"     MediaKey: {audio_data.get('mediaKey', 'N/A')}")
            except:
                print(f"     ⚠️ Erro ao processar JSON")

def verificar_webhooks_audio():
    """Verifica webhooks que contêm áudio"""
    print("\n📡 VERIFICANDO WEBHOOKS COM ÁUDIO")
    print("=" * 60)
    
    try:
        from webhook.models import WebhookEvent
        
        # Buscar webhooks recentes
        webhooks = WebhookEvent.objects.all().order_by('-timestamp')[:20]
        print(f"📊 Webhooks analisados: {webhooks.count()}")
        
        webhooks_com_audio = 0
        for webhook in webhooks:
            try:
                data = json.loads(webhook.raw_data)
                if 'msgContent' in data:
                    msg_content = data['msgContent']
                    if 'audioMessage' in msg_content:
                        webhooks_com_audio += 1
                        print(f"   🎵 Webhook ID {webhook.id}: CONTÉM ÁUDIO")
                        audio_data = msg_content['audioMessage']
                        print(f"      URL: {audio_data.get('url', 'N/A')}")
                        print(f"      MediaKey: {audio_data.get('mediaKey', 'N/A')}")
            except:
                continue
        
        print(f"\n📊 Total de webhooks com áudio: {webhooks_com_audio}")
        
    except ImportError:
        print("❌ Modelo WebhookEvent não encontrado")

def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO COMPLETA DE CHATS E ÁUDIOS")
    print("=" * 80)
    
    try:
        # Verificar todos os chats
        verificar_todos_chats()
        
        # Verificar pastas de áudio
        verificar_pastas_audio()
        
        # Verificar mensagens no banco
        verificar_mensagens_audio_banco()
        
        # Verificar webhooks
        verificar_webhooks_audio()
        
        print("\n" + "=" * 80)
        print("✅ VERIFICAÇÃO CONCLUÍDA!")
        
        print("\n💡 ANÁLISE:")
        print("   - Verificar se há mensagens de áudio no banco")
        print("   - Confirmar se webhooks estão chegando")
        print("   - Verificar se download automático está ativo")
        print("   - Testar com áudios reais no WhatsApp")
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 