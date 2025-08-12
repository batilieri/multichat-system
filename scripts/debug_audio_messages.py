#!/usr/bin/env python3
"""
Script para debugar mensagens de áudio
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
django.setup()

from webhook.models import Message
from core.models import Mensagem
import json

def debug_audio_messages():
    """Debuga mensagens de áudio no sistema"""
    print("🔍 DEBUGANDO MENSAGENS DE ÁUDIO")
    print("=" * 60)
    
    # Buscar mensagens de áudio no webhook
    webhook_audio_messages = Message.objects.filter(message_type='audio')
    print(f"📊 Mensagens de áudio no webhook: {webhook_audio_messages.count()}")
    
    for msg in webhook_audio_messages[:5]:
        print(f"\n🎵 Webhook Message ID: {msg.id}")
        print(f"  Tipo: {msg.message_type}")
        print(f"  Conteúdo: {msg.text_content}")
        print(f"  Media URL: {msg.media_url}")
        print(f"  Media Type: {msg.media_type}")
        print(f"  From Me: {msg.from_me}")
        print(f"  Data: {msg.timestamp}")
        print(f"  JSON Content: {msg.json_content}")
    
    # Buscar mensagens de áudio no core
    core_audio_messages = Mensagem.objects.filter(tipo='audio')
    print(f"\n📊 Mensagens de áudio no core: {core_audio_messages.count()}")
    
    for msg in core_audio_messages[:5]:
        print(f"\n🎵 Core Message ID: {msg.id}")
        print(f"  Tipo: {msg.tipo}")
        print(f"  Conteúdo: {msg.conteudo}")
        print(f"  From Me: {msg.from_me}")
        print(f"  Data: {msg.data_envio}")
        print(f"  JSON Content: {msg.json_content if hasattr(msg, 'json_content') else 'N/A'}")

def create_test_audio_message():
    """Cria uma mensagem de áudio de teste"""
    print("\n🧪 CRIANDO MENSAGEM DE ÁUDIO DE TESTE")
    print("=" * 60)
    
    from core.models import Cliente, Chat, Mensagem
    from django.utils import timezone
    
    # Obter cliente e chat
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado")
        return
    
    chat = Chat.objects.filter(cliente=cliente).first()
    if not chat:
        print("❌ Nenhum chat encontrado")
        return
    
    # Dados de teste de áudio
    test_audio_data = {
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
    
    # Criar mensagem de teste
    test_message = Mensagem.objects.create(
        chat=chat,
        remetente="556993291093",
        conteudo=json.dumps(test_audio_data),
        tipo='audio',
        from_me=False,
        data_envio=timezone.now(),
        json_content=test_audio_data
    )
    
    print(f"✅ Mensagem de teste criada: {test_message.id}")
    print(f"  Tipo: {test_message.tipo}")
    print(f"  Conteúdo: {test_message.conteudo}")
    print(f"  From Me: {test_message.from_me}")
    
    return test_message

def check_frontend_display():
    """Verifica como as mensagens apareceriam no frontend"""
    print("\n🖥️ VERIFICANDO EXIBIÇÃO NO FRONTEND")
    print("=" * 60)
    
    # Buscar mensagens de áudio
    audio_messages = Mensagem.objects.filter(tipo='audio')
    
    for msg in audio_messages[:3]:
        print(f"\n🎵 Mensagem ID: {msg.id}")
        
        # Simular dados que o frontend receberia
        frontend_data = {
            id: msg.id,
            tipo: msg.tipo,
            type: msg.tipo,
            content: msg.conteudo,
            fromMe: msg.from_me,
            from_me: msg.from_me,
            timestamp: msg.data_envio.isoformat(),
            mediaUrl: None,
            mediaType: 'audio',
            duration: None
        }
        
        # Tentar extrair dados do JSON
        try:
            if msg.json_content:
                json_data = msg.json_content
                if 'audioMessage' in json_data:
                    audio_data = json_data['audioMessage']
                    frontend_data.mediaUrl = audio_data.get('url')
                    frontend_data.duration = audio_data.get('seconds')
                    print(f"  ✅ Dados extraídos do JSON")
            else:
                print(f"  ⚠️ Sem dados JSON")
        except Exception as e:
            print(f"  ❌ Erro ao extrair dados: {e}")
        
        print(f"  Frontend Data: {json.dumps(frontend_data, indent=2, default=str)}")
        
        # Verificar se seria renderizado como áudio
        if frontend_data.tipo == 'audio':
            print(f"  ✅ Seria renderizado como áudio")
        else:
            print(f"  ❌ NÃO seria renderizado como áudio")

def main():
    """Função principal"""
    print("🔧 DEBUG DE MENSAGENS DE ÁUDIO")
    print("=" * 60)
    
    try:
        # Debug mensagens existentes
        debug_audio_messages()
        
        # Criar mensagem de teste
        test_message = create_test_audio_message()
        
        # Verificar exibição no frontend
        check_frontend_display()
        
        print("\n✅ Debug concluído!")
        
    except Exception as e:
        print(f"❌ Erro no debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 