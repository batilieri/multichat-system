#!/usr/bin/env python3
"""
Script para criar pastas de áudio para todos os chats que têm mensagens de áudio
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

def verificar_chats_com_audio():
    """Verifica todos os chats que têm mensagens de áudio"""
    print("🎵 Verificando chats com mensagens de áudio...")
    
    # Buscar todos os chats que têm mensagens de áudio
    chats_com_audio = Chat.objects.filter(
        mensagens__tipo='audio'
    ).distinct()
    
    if not chats_com_audio.exists():
        print("❌ Nenhum chat com mensagens de áudio encontrado!")
        return []
    
    print(f"📊 Total de chats com áudio: {chats_com_audio.count()}")
    
    chats_info = []
    for chat in chats_com_audio:
        # Contar mensagens de áudio
        mensagens_audio = chat.mensagens.filter(tipo='audio')
        print(f"\n📱 Chat: {chat.chat_id}")
        print(f"   Cliente: {chat.cliente.nome}")
        print(f"   Mensagens de áudio: {mensagens_audio.count()}")
        
        chats_info.append({
            'chat': chat,
            'audio_count': mensagens_audio.count(),
            'mensagens': mensagens_audio
        })
    
    return chats_info

def criar_pastas_audio(chats_info):
    """Cria pastas de áudio para todos os chats"""
    print("\n📁 Criando pastas de áudio...")
    
    for info in chats_info:
        chat = info['chat']
        audio_count = info['audio_count']
        
        print(f"\n📱 Processando chat: {chat.chat_id}")
        print(f"   Mensagens de áudio: {audio_count}")
        
        # Buscar instância do WhatsApp
        try:
            instance = chat.cliente.whatsapp_instances.first()
            if not instance:
                print(f"   ❌ Nenhuma instância encontrada para cliente {chat.cliente.nome}")
                continue
                
            cliente_id = chat.cliente.id
            instance_id = instance.instance_id
            chat_id = chat.chat_id
            
            # Criar estrutura de pastas
            base_path = Path(__file__).parent / "media_storage" / f"cliente_{cliente_id}" / f"instance_{instance_id}" / "chats" / str(chat_id) / "audio"
            
            print(f"   📁 Criando pasta: {base_path}")
            
            # Criar pasta se não existir
            base_path.mkdir(parents=True, exist_ok=True)
            
            if base_path.exists():
                print(f"   ✅ Pasta criada/existe: {base_path}")
                
                # Verificar se já tem arquivos
                arquivos = list(base_path.glob("*"))
                print(f"   📄 Arquivos existentes: {len(arquivos)}")
                
                for arquivo in arquivos:
                    print(f"      📄 {arquivo.name} ({arquivo.stat().st_size} bytes)")
            else:
                print(f"   ❌ Erro ao criar pasta: {base_path}")
                
        except Exception as e:
            print(f"   ❌ Erro ao processar chat {chat.chat_id}: {e}")

def verificar_estrutura_completa():
    """Verifica se a estrutura está completa"""
    print("\n🔍 Verificando estrutura completa...")
    
    # Buscar pasta base
    base_path = Path(__file__).parent / "media_storage"
    
    if not base_path.exists():
        print(f"❌ Pasta base não existe: {base_path}")
        return
    
    print(f"✅ Pasta base existe: {base_path}")
    
    # Listar clientes
    clientes_path = base_path / "cliente_2"
    if clientes_path.exists():
        print(f"✅ Cliente existe: {clientes_path}")
        
        # Listar instâncias
        instancias = list(clientes_path.glob("instance_*"))
        print(f"📊 Instâncias encontradas: {len(instancias)}")
        
        for instancia in instancias:
            print(f"   📱 {instancia.name}")
            
            # Listar chats
            chats_path = instancia / "chats"
            if chats_path.exists():
                chats = list(chats_path.glob("*"))
                print(f"      📊 Chats encontrados: {len(chats)}")
                
                for chat in chats:
                    if chat.is_dir():
                        audio_path = chat / "audio"
                        if audio_path.exists():
                            arquivos = list(audio_path.glob("*"))
                            print(f"         🎵 {chat.name}/audio: {len(arquivos)} arquivos")
                        else:
                            print(f"         ⚠️ {chat.name}/audio: pasta não existe")

def main():
    """Função principal"""
    print("🚀 Criando pastas de áudio para todos os chats...")
    print("=" * 60)
    
    # Verificar chats com áudio
    chats_info = verificar_chats_com_audio()
    
    if not chats_info:
        print("❌ Nenhum chat com áudio encontrado!")
        return
    
    # Criar pastas
    criar_pastas_audio(chats_info)
    
    # Verificar estrutura
    verificar_estrutura_completa()
    
    print("\n" + "=" * 60)
    print("✅ Criação de pastas concluída!")

if __name__ == "__main__":
    main() 