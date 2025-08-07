#!/usr/bin/env python3
"""
Script para testar a API de mensagens e verificar como os dados estão sendo retornados
"""

import os
import sys
import django
import requests
import json
from pathlib import Path

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat

def testar_api_mensagens():
    """Testa a API de mensagens para ver como os dados estão sendo retornados"""
    print("🔍 Testando API de mensagens...")
    
    # Buscar mensagens de áudio no banco
    mensagens_audio = Mensagem.objects.filter(tipo='audio').order_by('-data_envio')[:3]
    
    if not mensagens_audio.exists():
        print("❌ Nenhuma mensagem de áudio encontrada no banco!")
        return
    
    print(f"📊 Encontradas {mensagens_audio.count()} mensagens de áudio")
    
    for mensagem in mensagens_audio:
        print(f"\n📋 Mensagem ID: {mensagem.id}")
        print(f"   Chat: {mensagem.chat.chat_id}")
        print(f"   Tipo: {mensagem.tipo}")
        print(f"   From Me: {mensagem.from_me}")
        print(f"   Conteúdo: {mensagem.conteudo[:100]}...")
        
        # Testar API
        url = f"http://localhost:8000/api/mensagens/{mensagem.id}/"
        print(f"🔗 Testando URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ API retornou dados:")
                print(f"   ID: {data.get('id')}")
                print(f"   Tipo: {data.get('tipo')}")
                print(f"   From Me: {data.get('fromMe')}")
                print(f"   Conteúdo: {data.get('conteudo', '')[:100]}...")
                print(f"   Media URL: {data.get('media_url')}")
                
                # Verificar se o tipo está correto
                if data.get('tipo') == 'audio':
                    print("✅ Tipo correto: audio")
                else:
                    print(f"❌ Tipo incorreto: {data.get('tipo')}")
                    
            else:
                print(f"❌ Erro HTTP: {response.status_code}")
                print(f"📄 Resposta: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Erro ao testar API: {e}")

def testar_api_chat():
    """Testa a API de chat para ver as mensagens"""
    print("\n📱 Testando API de chat...")
    
    # Buscar chat com mensagens de áudio
    chat_com_audio = Chat.objects.filter(
        mensagens__tipo='audio'
    ).first()
    
    if not chat_com_audio:
        print("❌ Nenhum chat com áudio encontrado!")
        return
    
    print(f"📱 Chat: {chat_com_audio.chat_id}")
    
    # Testar API de mensagens do chat
    url = f"http://localhost:8000/api/chats/{chat_com_audio.id}/mensagens/"
    print(f"🔗 Testando URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API retornou dados do chat:")
            print(f"   Total de mensagens: {len(data.get('results', []))}")
            
            # Verificar mensagens de áudio
            mensagens_audio = [msg for msg in data.get('results', []) if msg.get('tipo') == 'audio']
            print(f"   Mensagens de áudio: {len(mensagens_audio)}")
            
            for msg in mensagens_audio[:2]:  # Mostrar apenas as 2 primeiras
                print(f"   📋 ID: {msg.get('id')}, Tipo: {msg.get('tipo')}")
                
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")

def verificar_serializer():
    """Verifica como o serializer está processando as mensagens"""
    print("\n🔧 Verificando serializer...")
    
    from api.serializers import MensagemSerializer
    
    # Buscar mensagem de áudio
    mensagem = Mensagem.objects.filter(tipo='audio').first()
    
    if not mensagem:
        print("❌ Nenhuma mensagem de áudio encontrada!")
        return
    
    print(f"📋 Testando serializer com mensagem ID: {mensagem.id}")
    print(f"   Tipo original: {mensagem.tipo}")
    print(f"   Conteúdo: {mensagem.conteudo[:100]}...")
    
    # Testar serializer
    serializer = MensagemSerializer(mensagem)
    data = serializer.data
    
    print("✅ Dados serializados:")
    print(f"   Tipo: {data.get('tipo')}")
    print(f"   From Me: {data.get('fromMe')}")
    print(f"   Conteúdo: {data.get('conteudo', '')[:100]}...")
    print(f"   Media URL: {data.get('media_url')}")

def main():
    """Função principal"""
    print("🚀 Testando API de mensagens...")
    print("=" * 60)
    
    # Verificar serializer
    verificar_serializer()
    
    # Testar API individual
    testar_api_mensagens()
    
    # Testar API de chat
    testar_api_chat()
    
    print("\n" + "=" * 60)
    print("✅ Teste da API concluído!")

if __name__ == "__main__":
    main() 