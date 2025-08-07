#!/usr/bin/env python3
"""
Script para testar o áudio real encontrado no sistema
"""

import os
import sys
import django
import requests
from pathlib import Path

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

def testar_audio_real():
    """Testa o áudio real encontrado no sistema"""
    print("🎵 Testando áudio real encontrado no sistema...")
    
    # Dados do áudio real encontrado
    cliente_id = 2
    instance_id = "3B6XIW-ZTS923-GEAY6V"
    chat_id = "556999211347"
    filename = "msg_8E0BFC85_20250806_165649.ogg"
    
    # Verificar se o arquivo existe
    audio_path = f"media_storage/cliente_{cliente_id}/instance_{instance_id}/chats/{chat_id}/audio/{filename}"
    
    if not os.path.exists(audio_path):
        print(f"❌ Arquivo não encontrado: {audio_path}")
        return False
    
    print(f"✅ Arquivo encontrado: {audio_path}")
    print(f"📏 Tamanho: {os.path.getsize(audio_path)} bytes")
    
    # Testar endpoint público
    url = f"http://localhost:8000/api/whatsapp-audio/{cliente_id}/{instance_id}/{chat_id}/{filename}"
    print(f"🔗 Testando URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Endpoint funcionando!")
            print(f"📊 Content-Type: {response.headers.get('content-type')}")
            print(f"📏 Tamanho da resposta: {len(response.content)} bytes")
            
            # Verificar se o conteúdo é válido
            if len(response.content) > 0:
                print("✅ Conteúdo válido recebido!")
                return True
            else:
                print("❌ Conteúdo vazio!")
                return False
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")
        return False

def testar_endpoint_publico():
    """Testa o endpoint público de áudio"""
    print("\n🔗 Testando endpoint público...")
    
    # Usar o áudio real encontrado
    cliente_id = 2
    instance_id = "3B6XIW-ZTS923-GEAY6V"
    chat_id = "556999211347"
    filename = "msg_8E0BFC85_20250806_165649.ogg"
    
    url = f"http://localhost:8000/api/whatsapp-audio/{cliente_id}/{instance_id}/{chat_id}/{filename}"
    print(f"🔗 Testando URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Endpoint público funcionando!")
            print(f"📊 Content-Type: {response.headers.get('content-type')}")
            print(f"📏 Tamanho da resposta: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint público: {e}")
        return False

def verificar_estrutura_arquivos():
    """Verifica a estrutura de arquivos de áudio"""
    print("\n📁 Verificando estrutura de arquivos...")
    
    base_path = "media_storage"
    
    if not os.path.exists(base_path):
        print("❌ Pasta media_storage não encontrada!")
        return False
    
    # Procurar por arquivos de áudio
    audio_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(('.ogg', '.mp3', '.m4a', '.wav')):
                audio_files.append(os.path.join(root, file))
    
    if audio_files:
        print(f"✅ Encontrados {len(audio_files)} arquivos de áudio:")
        for audio_file in audio_files:
            size = os.path.getsize(audio_file)
            print(f"   📄 {audio_file} ({size} bytes)")
        return True
    else:
        print("❌ Nenhum arquivo de áudio encontrado!")
        return False

def main():
    """Função principal"""
    print("🚀 Testando sistema de áudio real...")
    print("=" * 60)
    
    # Verificar estrutura
    verificar_estrutura_arquivos()
    
    # Testar endpoint público
    testar_endpoint_publico()
    
    # Testar áudio real
    resultado = testar_audio_real()
    
    print("\n" + "=" * 60)
    if resultado:
        print("✅ Teste de áudio concluído com sucesso!")
    else:
        print("❌ Teste de áudio falhou!")

if __name__ == "__main__":
    main() 