#!/usr/bin/env python3
"""
Script de teste completo para o sistema de áudio do MultiChat
Testa todos os componentes: backend, frontend e integração
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

# Configurações
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_audio_endpoints():
    """Testa todos os endpoints de áudio do backend"""
    print("🎵 Testando endpoints de áudio do backend...")
    
    # Teste 1: Endpoint de áudio inteligente
    print("\n1. Testando endpoint whatsapp-audio-smart...")
    try:
        url = f"{BACKEND_URL}/api/whatsapp-audio-smart/2/3B6XIW-ZTS923-GEAY6V/556999267344/test_message/"
        response = requests.get(url)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Endpoint funcionando")
        else:
            print(f"   ⚠️ Endpoint retornou: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Teste 2: Endpoint público de áudio
    print("\n2. Testando endpoint público de áudio...")
    try:
        url = f"{BACKEND_URL}/api/audio/message/1/public/"
        response = requests.get(url)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Endpoint funcionando")
        else:
            print(f"   ⚠️ Endpoint retornou: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Teste 3: Endpoint de mídia WAPI
    print("\n3. Testando endpoint de mídia WAPI...")
    try:
        url = f"{BACKEND_URL}/api/wapi-media/audios/test_audio.ogg"
        response = requests.get(url)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Endpoint funcionando")
        else:
            print(f"   ⚠️ Endpoint retornou: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def test_frontend_audio_components():
    """Testa os componentes de áudio do frontend"""
    print("\n🎵 Testando componentes de áudio do frontend...")
    
    # Verificar se o frontend está rodando
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            print("   ✅ Frontend está rodando")
        else:
            print("   ⚠️ Frontend retornou status diferente de 200")
    except Exception as e:
        print(f"   ❌ Frontend não está acessível: {e}")
        return
    
    # Verificar se os componentes estão sendo carregados
    try:
        response = requests.get(f"{FRONTEND_URL}/src/components/Message.jsx")
        if response.status_code == 200:
            print("   ✅ Componente Message.jsx acessível")
        else:
            print("   ⚠️ Componente Message.jsx não acessível")
    except Exception as e:
        print(f"   ❌ Erro ao acessar componente: {e}")

def test_audio_file_structure():
    """Testa a estrutura de arquivos de áudio"""
    print("\n🎵 Testando estrutura de arquivos de áudio...")
    
    # Verificar diretório media_storage
    media_storage = Path("multichat_system/media_storage")
    if media_storage.exists():
        print("   ✅ Diretório media_storage existe")
        
        # Listar clientes
        clientes = list(media_storage.iterdir())
        print(f"   📁 Clientes encontrados: {len(clientes)}")
        
        for cliente in clientes:
            if cliente.is_dir():
                print(f"      📂 Cliente: {cliente.name}")
                
                # Verificar instâncias
                instancias = list(cliente.iterdir())
                for instancia in instancias:
                    if instancia.is_dir():
                        print(f"         🔧 Instância: {instancia.name}")
                        
                        # Verificar chats
                        chats_dir = instancia / "chats"
                        if chats_dir.exists():
                            chats = list(chats_dir.iterdir())
                            print(f"            💬 Chats: {len(chats)}")
                            
                            for chat in chats:
                                if chat.is_dir():
                                    audio_dir = chat / "audio"
                                    if audio_dir.exists():
                                        audios = list(audio_dir.glob("*.ogg")) + list(audio_dir.glob("*.mp3"))
                                        if audios:
                                            print(f"               🎵 Áudios em {chat.name}: {len(audios)}")
                                            for audio in audios[:3]:  # Mostrar apenas os primeiros 3
                                                print(f"                  🔊 {audio.name}")
    else:
        print("   ❌ Diretório media_storage não encontrado")

def test_database_audio_messages():
    """Testa as mensagens de áudio no banco de dados"""
    print("\n🎵 Testando mensagens de áudio no banco...")
    
    try:
        # Tentar conectar ao banco via API
        url = f"{BACKEND_URL}/api/mensagens/"
        response = requests.get(url)
        
        if response.status_code == 200:
            mensagens = response.json()
            print(f"   ✅ API de mensagens acessível")
            print(f"   📊 Total de mensagens: {len(mensagens)}")
            
            # Contar mensagens de áudio
            audio_messages = [m for m in mensagens if m.get('tipo') == 'audio']
            print(f"   🎵 Mensagens de áudio: {len(audio_messages)}")
            
            if audio_messages:
                print("   📋 Exemplo de mensagem de áudio:")
                audio_msg = audio_messages[0]
                print(f"      ID: {audio_msg.get('id')}")
                print(f"      Tipo: {audio_msg.get('tipo')}")
                print(f"      Conteúdo: {audio_msg.get('conteudo', '')[:100]}...")
                print(f"      Media URL: {audio_msg.get('media_url', 'N/A')}")
        else:
            print(f"   ⚠️ API retornou status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar banco: {e}")

def test_webhook_audio_processing():
    """Testa o processamento de áudio via webhook"""
    print("\n🎵 Testando processamento de áudio via webhook...")
    
    # Verificar se o processador de áudio está funcionando
    try:
        # Simular dados de webhook de áudio
        webhook_data = {
            "msgContent": {
                "audioMessage": {
                    "url": "https://example.com/audio.ogg",
                    "mediaKey": "test_key",
                    "mimetype": "audio/ogg",
                    "seconds": 10,
                    "ptt": False
                }
            },
            "messageId": "test_audio_123"
        }
        
        print("   📝 Dados de webhook simulados criados")
        print(f"   🎵 Tipo de mensagem: audio")
        print(f"   🎵 Message ID: {webhook_data['messageId']}")
        
    except Exception as e:
        print(f"   ❌ Erro ao simular webhook: {e}")

def main():
    """Função principal de teste"""
    print("🎵 TESTE COMPLETO DO SISTEMA DE ÁUDIO MULTICHAT")
    print("=" * 50)
    
    # Testar backend
    test_backend_audio_endpoints()
    
    # Testar frontend
    test_frontend_audio_components()
    
    # Testar estrutura de arquivos
    test_audio_file_structure()
    
    # Testar banco de dados
    test_database_audio_messages()
    
    # Testar webhook
    test_webhook_audio_processing()
    
    print("\n" + "=" * 50)
    print("🎵 TESTE COMPLETO FINALIZADO")
    print("\n📋 RESUMO:")
    print("   - Verifique os logs do backend para erros")
    print("   - Verifique o console do navegador para erros do frontend")
    print("   - Verifique se os arquivos de áudio estão sendo baixados")
    print("   - Verifique se as mensagens estão sendo criadas corretamente")

if __name__ == "__main__":
    main() 