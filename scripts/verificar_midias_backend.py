#!/usr/bin/env python3
"""
Script para verificar se as mídias estão sendo processadas corretamente no backend
"""

import os
import sys
import django
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent / "multichat_system"
sys.path.append(str(project_root))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, MediaFile
from webhook.models import MessageMedia
from django.db.models import Q

def verificar_mensagens_com_midia():
    """Verifica mensagens que contêm mídia"""
    print("🔍 Verificando mensagens com mídia...")
    
    # Buscar mensagens que não são de texto
    mensagens_midia = Mensagem.objects.exclude(
        Q(tipo='texto') | Q(tipo='text')
    ).order_by('-data_envio')[:10]
    
    print(f"📊 Encontradas {mensagens_midia.count()} mensagens com mídia:")
    
    for msg in mensagens_midia:
        print(f"\n📱 Mensagem ID: {msg.id}")
        print(f"   Tipo: {msg.tipo}")
        print(f"   Chat: {msg.chat.chat_id}")
        print(f"   Data: {msg.data_envio}")
        print(f"   Conteúdo: {msg.conteudo[:100]}...")
        
        # Verificar se tem MediaFile associado
        try:
            media_file = MediaFile.objects.get(message_id=msg.message_id)
            print(f"   ✅ MediaFile encontrado: {media_file.media_type}")
            print(f"   📁 Caminho: {media_file.file_path}")
            print(f"   📊 Status: {media_file.download_status}")
        except MediaFile.DoesNotExist:
            print(f"   ❌ MediaFile não encontrado")
        
        # Verificar se tem MessageMedia associado
        try:
            message_media = MessageMedia.objects.get(message_id=msg.message_id)
            print(f"   ✅ MessageMedia encontrado: {message_media.media_type}")
            print(f"   📁 Caminho: {message_media.media_path}")
            print(f"   📊 Status: {message_media.download_status}")
        except MessageMedia.DoesNotExist:
            print(f"   ❌ MessageMedia não encontrado")

def verificar_media_files():
    """Verifica arquivos MediaFile no banco"""
    print("\n📁 Verificando MediaFiles no banco...")
    
    media_files = MediaFile.objects.all().order_by('-created_at')[:10]
    
    print(f"📊 Encontrados {media_files.count()} MediaFiles:")
    
    for mf in media_files:
        print(f"\n📄 MediaFile ID: {mf.id}")
        print(f"   Tipo: {mf.media_type}")
        print(f"   Message ID: {mf.message_id}")
        print(f"   Cliente: {mf.cliente.nome}")
        print(f"   Instância: {mf.instance.instance_id}")
        print(f"   Status: {mf.download_status}")
        print(f"   Caminho: {mf.file_path}")
        
        # Verificar se o arquivo físico existe
        if mf.file_path:
            file_path = Path(mf.file_path)
            if file_path.exists():
                print(f"   ✅ Arquivo físico existe: {file_path.stat().st_size} bytes")
            else:
                print(f"   ❌ Arquivo físico não existe: {file_path}")

def verificar_message_media():
    """Verifica MessageMedia no banco"""
    print("\n📁 Verificando MessageMedia no banco...")
    
    message_medias = MessageMedia.objects.all().order_by('-created_at')[:10]
    
    print(f"📊 Encontrados {message_medias.count()} MessageMedia:")
    
    for mm in message_medias:
        print(f"\n📄 MessageMedia ID: {mm.id}")
        print(f"   Tipo: {mm.media_type}")
        print(f"   Message ID: {mm.message_id}")
        print(f"   Status: {mm.download_status}")
        print(f"   Caminho: {mm.media_path}")
        
        # Verificar se o arquivo físico existe
        if mm.media_path:
            file_path = Path(mm.media_path)
            if file_path.exists():
                print(f"   ✅ Arquivo físico existe: {file_path.stat().st_size} bytes")
            else:
                print(f"   ❌ Arquivo físico não existe: {file_path}")

def verificar_pastas_midia():
    """Verifica as pastas de mídia no sistema de arquivos"""
    print("\n📁 Verificando pastas de mídia...")
    
    # Pastas para verificar
    pastas = [
        "wapi/midias/audios",
        "wapi/midias/imagens",
        "wapi/midias/videos", 
        "wapi/midias/documentos",
        "wapi/midias/stickers",
        "multichat_system/media/audios",
        "multichat_system/media/images"
    ]
    
    for pasta in pastas:
        path = Path(pasta)
        if path.exists():
            arquivos = list(path.glob("*"))
            print(f"✅ {pasta}: {len(arquivos)} arquivos")
            if arquivos:
                for arquivo in arquivos[:3]:  # Mostrar apenas os 3 primeiros
                    print(f"   📄 {arquivo.name} ({arquivo.stat().st_size} bytes)")
        else:
            print(f"❌ {pasta}: não existe")

def verificar_endpoints_midia():
    """Verifica se os endpoints de mídia estão funcionando"""
    print("\n🔗 Verificando endpoints de mídia...")
    
    import requests
    
    # Testar endpoint wapi-media
    try:
        response = requests.get("http://localhost:8000/api/wapi-media/imagens/test.jpg", timeout=5)
        print(f"✅ Endpoint wapi-media responde: {response.status_code}")
    except Exception as e:
        print(f"❌ Endpoint wapi-media não responde: {e}")
    
    # Testar endpoint de áudio
    try:
        response = requests.get("http://localhost:8000/api/audio/message/1/", timeout=5)
        print(f"✅ Endpoint audio/message responde: {response.status_code}")
    except Exception as e:
        print(f"❌ Endpoint audio/message não responde: {e}")

def main():
    """Função principal"""
    print("🚀 Iniciando verificação de mídias no backend...")
    
    # Verificar mensagens com mídia
    verificar_mensagens_com_midia()
    
    # Verificar MediaFiles
    verificar_media_files()
    
    # Verificar MessageMedia
    verificar_message_media()
    
    # Verificar pastas de mídia
    verificar_pastas_midia()
    
    # Verificar endpoints
    verificar_endpoints_midia()
    
    print("\n✅ Verificação concluída!")

if __name__ == "__main__":
    main() 