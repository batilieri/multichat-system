#!/usr/bin/env python3
"""
Verificação simples de todos os chats e suas pastas de áudio
"""

import os
import json
from pathlib import Path

def verificar_pastas_chats():
    """Verifica as pastas de todos os chats"""
    print("🔍 VERIFICANDO TODOS OS CHATS")
    print("=" * 60)
    
    # Caminho base dos chats
    base_path = Path("multichat_system/media_storage/cliente_2/instance_3B6XIW-ZTS923-GEAY6V/chats")
    
    if not base_path.exists():
        print("❌ Pasta de chats não encontrada!")
        return
    
    # Listar todos os chats
    chats = [d for d in base_path.iterdir() if d.is_dir()]
    print(f"📊 Total de chats encontrados: {len(chats)}")
    
    for chat_dir in chats:
        chat_id = chat_dir.name
        print(f"\n📱 Chat ID: {chat_id}")
        
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
        
        # Verificar outros tipos de mídia
        for media_type in ['imagens', 'videos', 'documentos', 'stickers']:
            media_dir = chat_dir / media_type
            if media_dir.exists():
                files = list(media_dir.glob("*"))
                if len(files) > 0:
                    print(f"   📎 {media_type}: {len(files)} arquivos")

def verificar_estrutura_completa():
    """Verifica a estrutura completa de mídia"""
    print("\n📁 ESTRUTURA COMPLETA DE MÍDIA")
    print("=" * 60)
    
    base_path = Path("multichat_system/media_storage")
    
    if not base_path.exists():
        print("❌ Pasta media_storage não encontrada!")
        return
    
    # Verificar estrutura completa
    for cliente_dir in base_path.glob("cliente_*"):
        print(f"\n👤 Cliente: {cliente_dir.name}")
        
        for instance_dir in cliente_dir.glob("instance_*"):
            print(f"   📱 Instância: {instance_dir.name}")
            
            # Verificar chats
            chats_dir = instance_dir / "chats"
            if chats_dir.exists():
                chats = [d for d in chats_dir.iterdir() if d.is_dir()]
                print(f"      📱 Chats: {len(chats)}")
                
                for chat_dir in chats:
                    chat_id = chat_dir.name
                    print(f"         Chat {chat_id}:")
                    
                    # Contar arquivos por tipo
                    for media_type in ['audio', 'imagens', 'videos', 'documentos', 'stickers']:
                        media_dir = chat_dir / media_type
                        if media_dir.exists():
                            files = list(media_dir.glob("*"))
                            if len(files) > 0:
                                print(f"            {media_type}: {len(files)} arquivos")
                                for file in files[:2]:  # Mostrar primeiros 2
                                    size_kb = file.stat().st_size / 1024
                                    print(f"               - {file.name} ({size_kb:.1f} KB)")

def verificar_arquivos_audio():
    """Verifica especificamente arquivos de áudio"""
    print("\n🎵 VERIFICANDO ARQUIVOS DE ÁUDIO")
    print("=" * 60)
    
    base_path = Path("multichat_system/media_storage")
    audio_files = []
    
    # Buscar todos os arquivos de áudio
    for audio_file in base_path.rglob("*.ogg"):
        audio_files.append(audio_file)
    
    for audio_file in base_path.rglob("*.mp3"):
        audio_files.append(audio_file)
    
    for audio_file in base_path.rglob("*.m4a"):
        audio_files.append(audio_file)
    
    for audio_file in base_path.rglob("*.wav"):
        audio_files.append(audio_file)
    
    print(f"📊 Total de arquivos de áudio encontrados: {len(audio_files)}")
    
    if len(audio_files) == 0:
        print("❌ Nenhum arquivo de áudio encontrado!")
        return
    
    # Agrupar por chat
    audios_por_chat = {}
    for audio_file in audio_files:
        # Extrair chat_id do caminho
        parts = audio_file.parts
        for i, part in enumerate(parts):
            if part == "chats" and i + 1 < len(parts):
                chat_id = parts[i + 1]
                if chat_id not in audios_por_chat:
                    audios_por_chat[chat_id] = []
                audios_por_chat[chat_id].append(audio_file)
                break
    
    print(f"📱 Chats com áudio: {len(audios_por_chat)}")
    
    for chat_id, files in audios_por_chat.items():
        print(f"\n🎵 Chat {chat_id}: {len(files)} áudios")
        for file in files:
            size_kb = file.stat().st_size / 1024
            print(f"   - {file.name} ({size_kb:.1f} KB)")

def verificar_documentacao_audios():
    """Verifica documentação sobre áudios"""
    print("\n📋 VERIFICANDO DOCUMENTAÇÃO SOBRE ÁUDIOS")
    print("=" * 60)
    
    docs_files = [
        "SOLUCAO_FINAL_AUDIOS.md",
        "RELATORIO_TESTE_DOWNLOAD_REAL_MIDIAS.md",
        "SISTEMA_DOWNLOAD_ATIVO.md",
        "RELATORIO_ANALISE_DOWNLOAD_AUDIOS.md"
    ]
    
    for doc_file in docs_files:
        doc_path = Path(doc_file)
        if doc_path.exists():
            print(f"✅ {doc_file} encontrado")
            
            # Verificar se menciona múltiplos chats
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if '556999211347' in content:
                    print(f"   📱 Menciona chat 556999211347")
                if '556999267344' in content:
                    print(f"   📱 Menciona chat 556999267344")
                if '556992962392' in content:
                    print(f"   📱 Menciona chat 556992962392")
                if 'audio' in content.lower():
                    print(f"   🎵 Menciona áudio")
        else:
            print(f"❌ {doc_file} não encontrado")

def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO COMPLETA DE CHATS E ÁUDIOS")
    print("=" * 80)
    
    try:
        # Verificar pastas de chats
        verificar_pastas_chats()
        
        # Verificar estrutura completa
        verificar_estrutura_completa()
        
        # Verificar arquivos de áudio
        verificar_arquivos_audio()
        
        # Verificar documentação
        verificar_documentacao_audios()
        
        print("\n" + "=" * 80)
        print("✅ VERIFICAÇÃO CONCLUÍDA!")
        
        print("\n💡 ANÁLISE:")
        print("   - Verificar se há áudios em todos os 3 chats")
        print("   - Confirmar se download automático está funcionando")
        print("   - Verificar se webhooks estão chegando")
        print("   - Testar com áudios reais no WhatsApp")
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 