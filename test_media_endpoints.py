#!/usr/bin/env python3
"""
Script para testar os endpoints de mídia do backend MultiChat
"""

import requests
import json
import os
from pathlib import Path

# Configurações
API_BASE_URL = "http://localhost:8000"
TEST_MESSAGE_ID = 1  # ID de uma mensagem existente

def test_wapi_media_endpoint():
    """Testa o endpoint wapi-media"""
    print("🧪 Testando endpoint wapi-media...")
    
    # Tipos de mídia para testar
    media_types = ['audios', 'imagens', 'videos', 'documentos', 'stickers']
    
    for media_type in media_types:
        print(f"\n📁 Testando {media_type}...")
        
        # Verificar se a pasta existe
        wapi_path = Path(f"wapi/midias/{media_type}")
        if wapi_path.exists():
            # Listar arquivos na pasta
            files = list(wapi_path.glob("*"))
            if files:
                # Testar com o primeiro arquivo encontrado
                test_file = files[0].name
                url = f"{API_BASE_URL}/api/wapi-media/{media_type}/{test_file}"
                
                print(f"  📄 Testando arquivo: {test_file}")
                print(f"  🔗 URL: {url}")
                
                try:
                    response = requests.get(url, timeout=10)
                    print(f"  📊 Status: {response.status_code}")
                    print(f"  📋 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                    
                    if response.status_code == 200:
                        print(f"  ✅ Sucesso! Tamanho: {len(response.content)} bytes")
                    else:
                        print(f"  ❌ Erro: {response.text[:200]}")
                        
                except Exception as e:
                    print(f"  ❌ Erro na requisição: {e}")
            else:
                print(f"  ⚠️ Pasta {media_type} existe mas está vazia")
        else:
            print(f"  ⚠️ Pasta {media_type} não existe")

def test_message_media_endpoints():
    """Testa os endpoints de mídia por ID da mensagem"""
    print("\n🧪 Testando endpoints de mídia por ID da mensagem...")
    
    # Endpoints para testar
    endpoints = [
        ('audio', 'audio/message'),
        ('image', 'image/message'),
        ('video', 'video/message'),
        ('sticker', 'sticker/message'),
        ('document', 'document/message')
    ]
    
    for media_type, endpoint in endpoints:
        print(f"\n📁 Testando {media_type}...")
        url = f"{API_BASE_URL}/api/{endpoint}/{TEST_MESSAGE_ID}/"
        
        print(f"  🔗 URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"  📊 Status: {response.status_code}")
            print(f"  📋 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            if response.status_code == 200:
                print(f"  ✅ Sucesso! Tamanho: {len(response.content)} bytes")
            else:
                print(f"  ❌ Erro: {response.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ Erro na requisição: {e}")

def test_audio_endpoint():
    """Testa o endpoint de áudio específico"""
    print("\n🧪 Testando endpoint de áudio...")
    
    # Verificar se existem áudios na pasta media
    media_path = Path("multichat_system/media/audios")
    if media_path.exists():
        audio_files = list(media_path.glob("*.mp3"))
        if audio_files:
            test_file = audio_files[0].name
            url = f"{API_BASE_URL}/api/audio/{test_file}/"
            
            print(f"  📄 Testando arquivo: {test_file}")
            print(f"  🔗 URL: {url}")
            
            try:
                response = requests.get(url, timeout=10)
                print(f"  📊 Status: {response.status_code}")
                print(f"  📋 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                
                if response.status_code == 200:
                    print(f"  ✅ Sucesso! Tamanho: {len(response.content)} bytes")
                else:
                    print(f"  ❌ Erro: {response.text[:200]}")
                    
            except Exception as e:
                print(f"  ❌ Erro na requisição: {e}")
        else:
            print("  ⚠️ Nenhum arquivo de áudio encontrado")
    else:
        print("  ⚠️ Pasta de áudios não existe")

def check_media_folders():
    """Verifica as pastas de mídia existentes"""
    print("\n📁 Verificando pastas de mídia...")
    
    # Pastas para verificar
    folders = [
        "wapi/midias/audios",
        "wapi/midias/imagens", 
        "wapi/midias/videos",
        "wapi/midias/documentos",
        "wapi/midias/stickers",
        "multichat_system/media/audios",
        "multichat_system/media/images"
    ]
    
    for folder in folders:
        path = Path(folder)
        if path.exists():
            files = list(path.glob("*"))
            print(f"  ✅ {folder}: {len(files)} arquivos")
            if files:
                print(f"     📄 Exemplos: {', '.join([f.name for f in files[:3]])}")
        else:
            print(f"  ❌ {folder}: não existe")

def test_backend_connection():
    """Testa se o backend está rodando"""
    print("🧪 Testando conexão com o backend...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/", timeout=5)
        if response.status_code == 200:
            print("  ✅ Backend está rodando")
            return True
        else:
            print(f"  ❌ Backend respondeu com status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Erro ao conectar com o backend: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando testes dos endpoints de mídia...")
    
    # Verificar se o backend está rodando
    if not test_backend_connection():
        print("\n❌ Backend não está rodando. Inicie o servidor Django primeiro.")
        return
    
    # Verificar pastas de mídia
    check_media_folders()
    
    # Testar endpoints
    test_wapi_media_endpoint()
    test_message_media_endpoints()
    test_audio_endpoint()
    
    print("\n✅ Testes concluídos!")

if __name__ == "__main__":
    main() 