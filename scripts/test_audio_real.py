#!/usr/bin/env python3
"""
Teste simples para verificar áudios
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
django.setup()

from core.models import Mensagem, Cliente, Chat
import json

def check_audio_messages():
    """Verifica mensagens de áudio existentes"""
    print("🔍 VERIFICANDO MENSAGENS DE ÁUDIO")
    print("=" * 60)
    
    # Buscar mensagens de áudio
    audio_messages = Mensagem.objects.filter(tipo='audio')
    print(f"📊 Mensagens de áudio encontradas: {audio_messages.count()}")
    
    if audio_messages.count() == 0:
        print("⚠️ Nenhuma mensagem de áudio encontrada")
        print("💡 Criando mensagem de teste...")
        create_test_audio()
    else:
        for msg in audio_messages[:3]:
            print(f"\n🎵 Mensagem ID: {msg.id}")
            print(f"  Tipo: {msg.tipo}")
            print(f"  Conteúdo: {msg.conteudo[:100]}...")
            print(f"  From Me: {msg.from_me}")
            print(f"  Data: {msg.data_envio}")

def create_test_audio():
    """Cria uma mensagem de áudio de teste"""
    print("\n🧪 CRIANDO MENSAGEM DE ÁUDIO DE TESTE")
    print("=" * 60)
    
    # Obter cliente e chat
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado")
        return
    
    chat = Chat.objects.filter(cliente=cliente).first()
    if not chat:
        print("❌ Nenhum chat encontrado")
        return
    
    # Dados de teste
    test_data = {
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
    from django.utils import timezone
    test_message = Mensagem.objects.create(
        chat=chat,
        remetente="556993291093",
        conteudo=json.dumps(test_data),
        tipo='audio',
        from_me=False,
        data_envio=timezone.now()
    )
    
    print(f"✅ Mensagem de teste criada: {test_message.id}")
    print(f"  Tipo: {test_message.tipo}")
    print(f"  Cliente: {cliente.nome}")
    print(f"  Chat: {chat.chat_name}")

def check_frontend_data():
    """Verifica como os dados apareceriam no frontend"""
    print("\n🖥️ DADOS PARA O FRONTEND")
    print("=" * 60)
    
    audio_messages = Mensagem.objects.filter(tipo='audio')
    
    for msg in audio_messages[:2]:
        print(f"\n🎵 Mensagem ID: {msg.id}")
        
        # Dados que o frontend deve receber
        frontend_data = {
            'id': msg.id,
            'tipo': msg.tipo,
            'type': msg.tipo,
            'content': msg.conteudo,
            'fromMe': msg.from_me,
            'from_me': msg.from_me,
            'timestamp': msg.data_envio.isoformat(),
            'mediaUrl': None,
            'mediaType': 'audio',
            'duration': None
        }
        
        # Extrair dados do JSON
        try:
            json_data = json.loads(msg.conteudo)
            if 'audioMessage' in json_data:
                audio_data = json_data['audioMessage']
                frontend_data['mediaUrl'] = audio_data.get('url')
                frontend_data['duration'] = audio_data.get('seconds')
                print(f"  ✅ Dados extraídos do JSON")
        except:
            print(f"  ⚠️ Erro ao extrair dados JSON")
        
        print(f"  Frontend Data: {json.dumps(frontend_data, indent=2)}")
        
        # Verificar se seria renderizado
        if frontend_data['tipo'] == 'audio':
            print(f"  ✅ Seria renderizado como áudio no frontend")
        else:
            print(f"  ❌ NÃO seria renderizado como áudio")

def main():
    """Função principal"""
    print("🔧 TESTE DE ÁUDIOS NO FRONTEND")
    print("=" * 60)
    
    try:
        # Verificar mensagens existentes
        check_audio_messages()
        
        # Verificar dados para frontend
        check_frontend_data()
        
        print("\n✅ Teste concluído!")
        print("\n💡 Para testar no frontend:")
        print("   1. Inicie o backend: python manage.py runserver")
        print("   2. Inicie o frontend: npm start")
        print("   3. Acesse um chat com mensagens de áudio")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 