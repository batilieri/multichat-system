#!/usr/bin/env python3
"""
Script simples para migrar áudios para o frontend
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
django.setup()

from core.models import Mensagem
from django.utils import timezone
import json

def migrar_audios():
    """Migra mensagens de áudio existentes"""
    print("🔄 MIGRANDO ÁUDIOS PARA O FRONTEND")
    print("=" * 60)
    
    # Buscar todas as mensagens
    mensagens = Mensagem.objects.all()
    print(f"📊 Total de mensagens: {mensagens.count()}")
    
    migradas = 0
    
    for msg in mensagens:
        # Verificar se é um áudio
        if msg.conteudo and 'audioMessage' in msg.conteudo:
            print(f"\n🎵 Encontrada mensagem de áudio ID: {msg.id}")
            
            # Definir tipo como áudio se não estiver
            if msg.tipo != 'audio':
                msg.tipo = 'audio'
                msg.save()
                print(f"  ✅ Tipo alterado para 'audio'")
                migradas += 1
            else:
                print(f"  ✅ Já é do tipo 'audio'")
            
            # Extrair dados do áudio
            try:
                json_data = json.loads(msg.conteudo)
                if 'audioMessage' in json_data:
                    audio_data = json_data['audioMessage']
                    url = audio_data.get('url', 'N/A')
                    duration = audio_data.get('seconds', 0)
                    print(f"  📁 URL: {url}")
                    print(f"  ⏱️ Duração: {duration} segundos")
            except:
                print(f"  ⚠️ Erro ao extrair dados JSON")
    
    print(f"\n✅ Migração concluída!")
    print(f"📊 Mensagens migradas: {migradas}")

def criar_audio_teste():
    """Cria uma mensagem de áudio de teste"""
    print("\n🧪 CRIANDO MENSAGEM DE ÁUDIO DE TESTE")
    print("=" * 60)
    
    # Buscar primeiro chat
    from core.models import Chat
    chat = Chat.objects.first()
    
    if not chat:
        print("❌ Nenhum chat encontrado")
        return
    
    # Dados de teste
    test_audio = {
        "audioMessage": {
            "url": "https://mmg.whatsapp.net/v/t62.7117-24/11418572_639123605874985_2074276734782391920_n.enc?ccb=11-4&oh=01_Q5Aa2AH90VmSBOTtBIXsGxf0r5vMtkmkC4BsJLVg9s4HdByRdQ&oe=68B5B693&_nc_sid=5e03e0&mms3=true",
            "mimetype": "audio/ogg; codecs=opus",
            "fileSha256": "+ylX/pg8Tsa+zRJ8fgO0rpPycxdXtmLUZvZeZybjRAE=",
            "fileLength": "20718",
            "seconds": 8,
            "ptt": True,
            "mediaKey": "FnIfz9Ka/QzEPkAzlOQ9x0m3WBwUQaG265dvhLjnFl0="
        }
    }
    
    # Criar mensagem
    test_message = Mensagem.objects.create(
        chat=chat,
        remetente="556993291093",
        conteudo=json.dumps(test_audio),
        tipo='audio',
        from_me=False,
        data_envio=timezone.now()
    )
    
    print(f"✅ Mensagem de teste criada: {test_message.id}")
    print(f"  Tipo: {test_message.tipo}")
    print(f"  Chat: {chat.chat_name}")

def verificar_audios():
    """Verifica áudios existentes"""
    print("\n🔍 VERIFICANDO ÁUDIOS EXISTENTES")
    print("=" * 60)
    
    # Buscar mensagens de áudio
    audio_messages = Mensagem.objects.filter(tipo='audio')
    print(f"📊 Mensagens de áudio: {audio_messages.count()}")
    
    for msg in audio_messages[:3]:
        print(f"\n🎵 Mensagem ID: {msg.id}")
        print(f"  Tipo: {msg.tipo}")
        print(f"  From Me: {msg.from_me}")
        print(f"  Data: {msg.data_envio}")
        
        # Verificar dados JSON
        try:
            json_data = json.loads(msg.conteudo)
            if 'audioMessage' in json_data:
                audio_data = json_data['audioMessage']
                print(f"  ✅ Dados de áudio encontrados")
                print(f"  📁 URL: {audio_data.get('url', 'N/A')}")
                print(f"  ⏱️ Duração: {audio_data.get('seconds', 0)} segundos")
                print(f"  🎤 PTT: {audio_data.get('ptt', False)}")
        except:
            print(f"  ⚠️ Erro ao processar JSON")

def main():
    """Função principal"""
    print("🎵 MIGRAÇÃO DE ÁUDIOS")
    print("=" * 60)
    
    try:
        # Migrar áudios existentes
        migrar_audios()
        
        # Criar áudio de teste
        criar_audio_teste()
        
        # Verificar áudios
        verificar_audios()
        
        print("\n✅ Migração concluída!")
        print("\n💡 Para testar no frontend:")
        print("   1. Inicie o backend: python manage.py runserver")
        print("   2. Inicie o frontend: npm start")
        print("   3. Acesse um chat com mensagens de áudio")
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 