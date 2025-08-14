#!/usr/bin/env python3
"""
Script para diagnosticar o sistema de áudio completo
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

def verificar_mensagens_audio():
    """Verifica mensagens de áudio no sistema"""
    print("🎵 DIAGNÓSTICO COMPLETO DO SISTEMA DE ÁUDIO")
    print("=" * 60)
    
    # 1. Verificar mensagens de áudio no webhook
    print("\n🔍 VERIFICANDO MENSAGENS DE ÁUDIO NO WEBHOOK:")
    try:
        audio_messages_webhook = Message.objects.filter(message_type='audio')
        print(f"Total encontrado: {audio_messages_webhook.count()}")
        
        if audio_messages_webhook.exists():
            for msg in audio_messages_webhook[:3]:
                print(f"\nID: {msg.id}")
                print(f"  Tipo: {msg.message_type}")
                print(f"  Conteúdo: {msg.content[:200] if msg.content else 'N/A'}...")
                print(f"  Chat ID: {msg.chat_id}")
                print(f"  Timestamp: {msg.timestamp}")
        else:
            print("❌ Nenhuma mensagem de áudio encontrada no webhook")
    except Exception as e:
        print(f"❌ Erro ao verificar webhook: {e}")
    
    # 2. Verificar mensagens de áudio na tabela core
    print("\n🔍 VERIFICANDO MENSAGENS DE ÁUDIO NA TABELA CORE:")
    try:
        audio_messages_core = Mensagem.objects.filter(tipo='audio')
        print(f"Total encontrado: {audio_messages_core.count()}")
        
        if audio_messages_core.exists():
            for msg in audio_messages_core[:3]:
                print(f"\nID: {msg.id}")
                print(f"  Tipo: {msg.tipo}")
                print(f"  Conteúdo: {msg.conteudo[:200] if msg.conteudo else 'N/A'}...")
                print(f"  Chat ID: {msg.chat_id}")
                print(f"  Data Envio: {msg.data_envio}")
                print(f"  From Me: {msg.from_me}")
        else:
            print("❌ Nenhuma mensagem de áudio encontrada na tabela core")
    except Exception as e:
        print(f"❌ Erro ao verificar tabela core: {e}")
    
    # 3. Verificar estrutura dos dados
    print("\n🔍 VERIFICANDO ESTRUTURA DOS DADOS:")
    try:
        sample_msg = audio_messages_core.first()
        if sample_msg:
            print(f"Exemplo de mensagem:")
            print(f"  ID: {sample_msg.id}")
            print(f"  Tipo: {sample_msg.tipo}")
            print(f"  Conteúdo: {sample_msg.conteudo}")
            
            # Verificar campos adicionais
            campos_disponiveis = [field.name for field in sample_msg._meta.fields]
            print(f"  Campos disponíveis: {campos_disponiveis}")
            
            # Verificar se tem campos de mídia
            if hasattr(sample_msg, 'media_url'):
                print(f"  Media URL: {sample_msg.media_url}")
            if hasattr(sample_msg, 'media_type'):
                print(f"  Media Type: {sample_msg.media_type}")
        else:
            print("❌ Nenhuma mensagem de áudio para verificar estrutura")
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
    
    # 4. Verificar arquivos de áudio
    print("\n🔍 VERIFICANDO ARQUIVOS DE ÁUDIO:")
    audio_path = "D:/multiChat/multichat_system/media_storage/Elizeu_Batiliere_Dos_Santos/instance_3B6XIW-ZTS923-GEAY6V/chats/556993258212/audio"
    
    if os.path.exists(audio_path):
        try:
            files = os.listdir(audio_path)
            print(f"📁 Caminho encontrado: {audio_path}")
            print(f"🎵 Arquivos de áudio encontrados: {len(files)}")
            
            for file in files[:10]:  # Mostrar apenas os primeiros 10
                file_path = os.path.join(audio_path, file)
                file_size = os.path.getsize(file_path)
                print(f"  - {file} ({file_size} bytes)")
                
            if len(files) > 10:
                print(f"  ... e mais {len(files) - 10} arquivos")
        except Exception as e:
            print(f"❌ Erro ao listar arquivos: {e}")
    else:
        print(f"❌ Caminho não encontrado: {audio_path}")
    
    # 5. Verificar chats
    print("\n🔍 VERIFICANDO CHATS:")
    try:
        chat_especifico = Chat.objects.filter(chat_id='556993258212').first()
        if chat_especifico:
            print(f"✅ Chat encontrado: {chat_especifico.chat_id}")
            print(f"  Nome: {chat_especifico.nome}")
            print(f"  Tipo: {chat_especifico.tipo}")
            
            # Verificar mensagens deste chat
            mensagens_chat = Mensagem.objects.filter(chat=chat_especifico)
            print(f"  Total de mensagens: {mensagens_chat.count()}")
            
            # Verificar mensagens de áudio deste chat
            audio_chat = mensagens_chat.filter(tipo='audio')
            print(f"  Mensagens de áudio: {audio_chat.count()}")
        else:
            print("❌ Chat 556993258212 não encontrado")
    except Exception as e:
        print(f"❌ Erro ao verificar chat: {e}")
    
    # 6. Verificar banco de dados
    print("\n🔍 VERIFICANDO BANCO DE DADOS:")
    try:
        with connection.cursor() as cursor:
            # Verificar tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"📊 Tabelas encontradas: {len(tables)}")
            
            # Verificar mensagens de áudio em todas as tabelas
            for table in tables:
                table_name = table[0]
                if 'message' in table_name.lower() or 'mensagem' in table_name.lower():
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE tipo='audio' OR message_type='audio'")
                        count = cursor.fetchone()[0]
                        if count > 0:
                            print(f"  {table_name}: {count} mensagens de áudio")
                    except:
                        pass
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
    
    print("\n" + "=" * 60)
    print("🎵 DIAGNÓSTICO CONCLUÍDO!")

if __name__ == "__main__":
    verificar_mensagens_audio() 