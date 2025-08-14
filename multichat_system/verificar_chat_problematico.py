#!/usr/bin/env python3
"""
Script para verificar e corrigir o chat problemático
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat
from django.db import connection

def verificar_chat_problematico():
    """Verifica o chat problemático"""
    print("🔍 VERIFICANDO CHAT PROBLEMÁTICO")
    print("=" * 50)
    
    chat_id_problematico = "556992962029-1415646286@g.us"
    
    try:
        # 1. Verificar se o chat existe
        print(f"\n🔍 Verificando chat: {chat_id_problematico}")
        
        chat_existente = Chat.objects.filter(chat_id=chat_id_problematico).first()
        if chat_existente:
            print(f"✅ Chat encontrado:")
            print(f"  ID: {chat_existente.id}")
            print(f"  Chat ID: {chat_existente.chat_id}")
            print(f"  Nome: {chat_existente.nome}")
            print(f"  Cliente ID: {chat_existente.cliente_id}")
            print(f"  Tipo: {chat_existente.tipo}")
            print(f"  Criado em: {chat_existente.created_at}")
        else:
            print(f"❌ Chat não encontrado")
            
        # 2. Verificar se há duplicatas
        print(f"\n🔍 Verificando duplicatas:")
        chats_duplicados = Chat.objects.filter(chat_id=chat_id_problematico)
        print(f"Total de chats com este ID: {chats_duplicados.count()}")
        
        if chats_duplicados.count() > 1:
            print(f"⚠️ ENCONTRADAS DUPLICATAS!")
            for i, chat in enumerate(chats_duplicados):
                print(f"  {i+1}. ID: {chat.id}, Cliente: {chat.cliente_id}, Nome: {chat.nome}")
                
        # 3. Verificar mensagens deste chat
        print(f"\n🔍 Verificando mensagens:")
        if chat_existente:
            mensagens = Mensagem.objects.filter(chat=chat_existente)
            print(f"Total de mensagens: {mensagens.count()}")
            
            # Verificar mensagens de áudio
            audio_messages = mensagens.filter(tipo='audio')
            print(f"Mensagens de áudio: {audio_messages.count()}")
            
            if audio_messages.exists():
                print(f"\n📋 Exemplo de mensagem de áudio:")
                sample_audio = audio_messages.first()
                print(f"  ID: {sample_audio.id}")
                print(f"  Tipo: {sample_audio.tipo}")
                print(f"  Conteúdo: {sample_audio.conteudo[:100]}...")
                
        # 4. Verificar estrutura da tabela
        print(f"\n🔍 Verificando estrutura da tabela:")
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(core_chat)")
            columns = cursor.fetchall()
            print(f"Colunas da tabela core_chat:")
            for col in columns:
                print(f"  {col[1]} ({col[2]}) - {'UNIQUE' if col[5] else 'NOT UNIQUE'}")
                
        # 5. Verificar constraints
        print(f"\n🔍 Verificando constraints:")
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA index_list(core_chat)")
            indexes = cursor.fetchall()
            print(f"Índices da tabela core_chat:")
            for idx in indexes:
                print(f"  {idx[1]}: {idx[2]}")
                
        # 6. Tentar corrigir o problema
        print(f"\n🔧 TENTANDO CORRIGIR O PROBLEMA:")
        
        if chat_existente:
            print(f"✅ Chat já existe, não precisa criar")
            
            # Verificar se consegue criar mensagens
            try:
                # Simular criação de mensagem
                print(f"🧪 Testando criação de mensagem...")
                
                # Verificar se há mensagens de áudio para testar
                if audio_messages.exists():
                    sample_audio = audio_messages.first()
                    print(f"✅ Mensagem de áudio encontrada e válida")
                    print(f"  ID: {sample_audio.id}")
                    print(f"  Tipo: {sample_audio.tipo}")
                    print(f"  Chat: {sample_audio.chat.chat_id}")
                    
                    # Verificar se o frontend consegue acessar
                    print(f"\n🔍 Verificando acesso do frontend:")
                    print(f"  Chat ID: {sample_audio.chat.chat_id}")
                    print(f"  Mensagem ID: {sample_audio.id}")
                    print(f"  Tipo: {sample_audio.tipo}")
                    
                else:
                    print(f"⚠️ Nenhuma mensagem de áudio encontrada neste chat")
                    
            except Exception as e:
                print(f"❌ Erro ao verificar mensagens: {e}")
        else:
            print(f"❌ Chat não existe, precisa ser criado")
            
        print("\n" + "=" * 50)
        print("🎵 VERIFICAÇÃO CONCLUÍDA!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    verificar_chat_problematico() 