#!/usr/bin/env python3
"""
Script para testar o serializer corrigido
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem
from api.serializers import MensagemSerializer

def testar_serializer_corrigido():
    """Testa o serializer corrigido"""
    print("🔧 Testando serializer corrigido...")
    
    # Buscar mensagem de áudio que tem arquivo
    mensagem = Mensagem.objects.filter(
        tipo='audio',
        chat__chat_id='556999211347'  # Chat que tem o arquivo
    ).first()
    
    if not mensagem:
        print("❌ Nenhuma mensagem de áudio encontrada no chat 556999211347!")
        return
    
    print(f"📋 Testando mensagem ID: {mensagem.id}")
    print(f"   Tipo: {mensagem.tipo}")
    print(f"   Message ID: {mensagem.message_id}")
    print(f"   Chat: {mensagem.chat.chat_id}")
    
    # Testar serializer
    serializer = MensagemSerializer(mensagem)
    data = serializer.data
    
    print("\n✅ Dados serializados:")
    print(f"   Tipo: {data.get('tipo')}")
    print(f"   From Me: {data.get('fromMe')}")
    print(f"   Media URL: {data.get('media_url')}")
    print(f"   Conteúdo: {data.get('conteudo', '')[:100]}...")
    
    # Verificar se media_url foi encontrada
    if data.get('media_url'):
        print("✅ Media URL encontrada!")
        
        # Testar se o arquivo existe
        media_url = data.get('media_url')
        if media_url.startswith('/media/'):
            # Converter para caminho local
            file_path = media_url.replace('/media/', 'media_storage/')
            full_path = os.path.join(os.path.dirname(__file__), file_path)
            
            if os.path.exists(full_path):
                print(f"✅ Arquivo existe: {full_path}")
                print(f"📏 Tamanho: {os.path.getsize(full_path)} bytes")
            else:
                print(f"❌ Arquivo não existe: {full_path}")
        else:
            print(f"⚠️ Media URL não é um caminho local: {media_url}")
    else:
        print("❌ Media URL não encontrada")

def verificar_arquivos_audio():
    """Verifica arquivos de áudio existentes"""
    print("\n📁 Verificando arquivos de áudio...")
    
    # Buscar pasta de áudio
    audio_path = Path(__file__).parent / "media_storage" / "cliente_2" / "instance_3B6XIW-ZTS923-GEAY6V" / "chats" / "556999211347" / "audio"
    
    if audio_path.exists():
        print(f"✅ Pasta de áudio existe: {audio_path}")
        
        # Listar arquivos
        arquivos = list(audio_path.glob("*"))
        print(f"📊 Total de arquivos: {len(arquivos)}")
        
        for arquivo in arquivos:
            print(f"   📄 {arquivo.name} ({arquivo.stat().st_size} bytes)")
    else:
        print(f"❌ Pasta de áudio não existe: {audio_path}")

def main():
    """Função principal"""
    print("🚀 Testando serializer corrigido...")
    print("=" * 60)
    
    # Verificar arquivos
    verificar_arquivos_audio()
    
    # Testar serializer
    testar_serializer_corrigido()
    
    print("\n" + "=" * 60)
    print("✅ Teste do serializer concluído!")

if __name__ == "__main__":
    main() 