#!/usr/bin/env python3
"""
Script de teste simples para o endpoint de áudio
"""

import requests
import json

def test_endpoint_simple():
    """Testa o endpoint de áudio de forma simples"""
    
    # Testar endpoint básico
    print("🎵 Testando endpoint básico...")
    try:
        response = requests.get("http://localhost:8000/api/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API básica funcionando")
        else:
            print(f"   ⚠️ API retornou: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Testar endpoint de mensagens
    print("\n🎵 Testando endpoint de mensagens...")
    try:
        response = requests.get("http://localhost:8000/api/mensagens/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Mensagens: {len(data)} encontradas")
            
            # Procurar por mensagens de áudio
            audio_msgs = [m for m in data if m.get('tipo') == 'audio']
            print(f"   🎵 Áudios: {len(audio_msgs)} encontrados")
            
            if audio_msgs:
                print("   📋 Primeira mensagem de áudio:")
                msg = audio_msgs[0]
                print(f"      ID: {msg.get('id')}")
                print(f"      Tipo: {msg.get('tipo')}")
                print(f"      Conteúdo: {str(msg.get('conteudo', ''))[:100]}...")
                print(f"      Media URL: {msg.get('media_url', 'N/A')}")
        else:
            print(f"   ⚠️ Retornou: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Testar endpoint específico de áudio
    print("\n🎵 Testando endpoint específico de áudio...")
    try:
        # Primeiro, buscar uma mensagem de áudio
        response = requests.get("http://localhost:8000/api/mensagens/")
        if response.status_code == 200:
            data = response.json()
            audio_msgs = [m for m in data if m.get('tipo') == 'audio']
            
            if audio_msgs:
                msg = audio_msgs[0]
                msg_id = msg.get('id')
                chat_id = msg.get('chat_id') or '556999267344'  # Fallback
                
                print(f"   🎯 Testando com mensagem ID: {msg_id}, Chat: {chat_id}")
                
                # Testar endpoint inteligente
                url = f"http://localhost:8000/api/whatsapp-audio-smart/2/3B6XIW-ZTS923-GEAY6V/{chat_id}/{msg_id}/"
                print(f"   🔗 URL: {url}")
                
                response = requests.get(url)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Endpoint funcionando!")
                else:
                    print(f"   ⚠️ Retornou: {response.text[:200]}")
            else:
                print("   ❌ Nenhuma mensagem de áudio encontrada para testar")
        else:
            print("   ❌ Não foi possível buscar mensagens")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    test_endpoint_simple() 