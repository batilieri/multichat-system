#!/usr/bin/env python3
"""
Script para diagnóstico completo do sistema de áudio
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from webhook.models import Message
from core.models import Mensagem, Chat
from django.db import connection

def verificar_arquivos_audio():
    """Verifica arquivos de áudio no sistema"""
    print("🎵 VERIFICANDO ARQUIVOS DE ÁUDIO")
    print("=" * 50)
    
    # Caminho dos arquivos de áudio
    audio_path = "D:/multiChat/multichat_system/media_storage/Elizeu_Batiliere_Dos_Santos/instance_3B6XIW-ZTS923-GEAY6V/chats/556993258212/audio"
    
    if os.path.exists(audio_path):
        try:
            files = os.listdir(audio_path)
            print(f"📁 Caminho encontrado: {audio_path}")
            print(f"🎵 Total de arquivos de áudio: {len(files)}")
            
            # Mostrar todos os arquivos
            for i, file in enumerate(files, 1):
                file_path = os.path.join(audio_path, file)
                file_size = os.path.getsize(file_path)
                print(f"  {i:2d}. {file} ({file_size:,} bytes)")
                
        except Exception as e:
            print(f"❌ Erro ao listar arquivos: {e}")
    else:
        print(f"❌ Caminho não encontrado: {audio_path}")

def verificar_mensagens_audio_chat():
    """Verifica mensagens de áudio de um chat específico"""
    print("\n🔍 VERIFICANDO MENSAGENS DE ÁUDIO DO CHAT 556993258212:")
    
    try:
        # Buscar chat específico
        chat = Chat.objects.filter(chat_id='556993258212').first()
        if chat:
            print(f"✅ Chat encontrado: {chat.chat_id}")
            print(f"  Nome: {chat.nome}")
            print(f"  Tipo: {chat.tipo}")
            
            # Buscar mensagens deste chat
            mensagens = Mensagem.objects.filter(chat=chat)
            print(f"  Total de mensagens: {mensagens.count()}")
            
            # Buscar mensagens de áudio
            audio_messages = mensagens.filter(tipo='audio')
            print(f"  Mensagens de áudio: {audio_messages.count()}")
            
            if audio_messages.exists():
                print("\n📋 Mensagens de áudio encontradas:")
                for msg in audio_messages[:5]:  # Mostrar apenas as primeiras 5
                    print(f"\n  ID: {msg.id}")
                    print(f"    Tipo: {msg.tipo}")
                    print(f"    From Me: {msg.from_me}")
                    print(f"    Data: {msg.data_envio}")
                    print(f"    Conteúdo: {msg.conteudo[:100]}...")
                    
                    # Verificar se tem dados de áudio válidos
                    try:
                        import json
                        content = json.loads(msg.conteudo)
                        if 'audioMessage' in content:
                            audio_data = content['audioMessage']
                            print(f"    🎵 Dados do áudio:")
                            print(f"      URL: {audio_data.get('url', 'N/A')}")
                            print(f"      Segundos: {audio_data.get('seconds', 'N/A')}")
                            print(f"      Tamanho: {audio_data.get('fileLength', 'N/A')}")
                            print(f"      Mime: {audio_data.get('mimetype', 'N/A')}")
                    except Exception as e:
                        print(f"    ❌ Erro ao parsear JSON: {e}")
            else:
                print("❌ Nenhuma mensagem de áudio encontrada neste chat")
        else:
            print("❌ Chat 556993258212 não encontrado")
    except Exception as e:
        print(f"❌ Erro ao verificar chat: {e}")

def verificar_api_mensagens():
    """Verifica se a API está retornando mensagens corretamente"""
    print("\n🔍 VERIFICANDO API DE MENSAGENS:")
    
    try:
        # Buscar mensagens de áudio recentes
        audio_messages = Mensagem.objects.filter(tipo='audio').order_by('-data_envio')[:10]
        print(f"📊 Últimas 10 mensagens de áudio:")
        
        for msg in audio_messages:
            print(f"\n  ID: {msg.id}")
            print(f"    Chat ID: {msg.chat.chat_id if msg.chat else 'N/A'}")
            print(f"    Tipo: {msg.tipo}")
            print(f"    Conteúdo: {msg.conteudo[:80]}...")
            
            # Verificar se tem campos necessários para o frontend
            campos_necessarios = ['id', 'tipo', 'conteudo', 'chat_id']
            for campo in campos_necessarios:
                valor = getattr(msg, campo, None)
                if campo == 'chat_id':
                    valor = msg.chat.chat_id if msg.chat else None
                print(f"    {campo}: {valor}")
                
    except Exception as e:
        print(f"❌ Erro ao verificar API: {e}")

def verificar_estrutura_frontend():
    """Verifica se a estrutura está correta para o frontend"""
    print("\n🔍 VERIFICANDO ESTRUTURA PARA O FRONTEND:")
    
    try:
        # Buscar uma mensagem de áudio para verificar estrutura
        sample_msg = Mensagem.objects.filter(tipo='audio').first()
        if sample_msg:
            print(f"📋 Exemplo de mensagem para o frontend:")
            print(f"  ID: {sample_msg.id}")
            print(f"  Tipo: {sample_msg.tipo}")
            print(f"  Conteúdo: {sample_msg.conteudo}")
            
            # Verificar se o JSON é válido
            try:
                import json
                content = json.loads(sample_msg.conteudo)
                print(f"  ✅ JSON válido")
                print(f"  🎵 audioMessage presente: {'audioMessage' in content}")
                
                if 'audioMessage' in content:
                    audio_data = content['audioMessage']
                    print(f"  🎵 Campos do áudio:")
                    for key, value in audio_data.items():
                        print(f"    {key}: {value}")
                        
            except Exception as e:
                print(f"  ❌ JSON inválido: {e}")
        else:
            print("❌ Nenhuma mensagem de áudio para verificar")
            
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")

if __name__ == "__main__":
    verificar_arquivos_audio()
    verificar_mensagens_audio_chat()
    verificar_api_mensagens()
    verificar_estrutura_frontend()
    
    print("\n" + "=" * 50)
    print("🎵 DIAGNÓSTICO COMPLETO FINALIZADO!") 