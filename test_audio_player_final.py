#!/usr/bin/env python3
"""
Teste final do sistema de áudio após migração
Verifica se os áudios estão sendo servidos corretamente
"""

import os
import sys
import django
import requests
import json

# Configurar Django
sys.path.append('multichat_system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente

def test_audio_system():
    """Testa o sistema de áudio completo"""
    print("🎵 TESTE FINAL DO SISTEMA DE ÁUDIO")
    print("=" * 60)
    
    # 1. Verificar mensagens de áudio
    print("\n📊 VERIFICANDO MENSAGENS DE ÁUDIO")
    audio_messages = Mensagem.objects.filter(tipo='audio')
    print(f"Total de mensagens de áudio: {audio_messages.count()}")
    
    if audio_messages.count() == 0:
        print("❌ Nenhuma mensagem de áudio encontrada!")
        return
    
    # 2. Verificar algumas mensagens específicas
    print("\n🔍 VERIFICANDO MENSAGENS ESPECÍFICAS")
    for msg in audio_messages[:5]:
        print(f"\n🎵 Mensagem ID: {msg.id}")
        print(f"  Message ID: {msg.message_id}")
        print(f"  Chat: {msg.chat.chat_id}")
        print(f"  From Me: {msg.from_me}")
        print(f"  Data: {msg.data_envio}")
        
        try:
            content = json.loads(msg.conteudo)
            if 'audioMessage' in content:
                audio_data = content['audioMessage']
                print(f"  ✅ Dados de áudio encontrados:")
                print(f"     FileName: {audio_data.get('fileName', 'N/A')}")
                print(f"     LocalPath: {audio_data.get('localPath', 'N/A')}")
                print(f"     DirectPath: {audio_data.get('directPath', 'N/A')}")
                print(f"     Seconds: {audio_data.get('seconds', 'N/A')}")
                print(f"     FileLength: {audio_data.get('fileLength', 'N/A')}")
            else:
                print(f"  ❌ Dados de áudio não encontrados")
        except Exception as e:
            print(f"  ❌ Erro ao processar conteúdo: {e}")
    
    # 3. Testar endpoints da API
    print("\n🌐 TESTANDO ENDPOINTS DA API")
    
    # Testar endpoint de áudio por message_id
    test_message = audio_messages.first()
    if test_message and test_message.message_id:
        print(f"\n🧪 Testando endpoint para message_id: {test_message.message_id}")
        
        # Construir URL do endpoint
        chat_id = test_message.chat.chat_id
        cliente_id = test_message.chat.cliente.id
        instance_id = "3B6XIW-ZTS923-GEAY6V"
        
        url = f"http://localhost:8000/api/whatsapp-audio/{cliente_id}/{instance_id}/{chat_id}/{test_message.message_id}/"
        print(f"  URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"  Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                print(f"  ✅ Áudio servido com sucesso!")
            else:
                print(f"  ❌ Erro ao servir áudio: {response.text}")
        except Exception as e:
            print(f"  ❌ Erro na requisição: {e}")
    
    # 4. Verificar estrutura de arquivos
    print("\n📁 VERIFICANDO ESTRUTURA DE ARQUIVOS")
    
    # Verificar se os arquivos existem
    for msg in audio_messages[:3]:
        try:
            content = json.loads(msg.conteudo)
            if 'audioMessage' in content:
                audio_data = content['audioMessage']
                local_path = audio_data.get('localPath')
                
                if local_path and os.path.exists(local_path):
                    file_size = os.path.getsize(local_path)
                    print(f"  ✅ Arquivo existe: {os.path.basename(local_path)} ({file_size} bytes)")
                else:
                    print(f"  ❌ Arquivo não encontrado: {local_path}")
        except Exception as e:
            print(f"  ❌ Erro ao verificar arquivo: {e}")
    
    # 5. Resumo final
    print("\n📋 RESUMO FINAL")
    print("=" * 60)
    
    total_audios = audio_messages.count()
    audios_com_arquivo = 0
    audios_com_message_id = 0
    
    for msg in audio_messages:
        if msg.message_id:
            audios_com_message_id += 1
        
        try:
            content = json.loads(msg.conteudo)
            if 'audioMessage' in content:
                audio_data = content['audioMessage']
                local_path = audio_data.get('localPath')
                if local_path and os.path.exists(local_path):
                    audios_com_arquivo += 1
        except:
            pass
    
    print(f"📊 Total de mensagens de áudio: {total_audios}")
    print(f"📊 Áudios com message_id: {audios_com_message_id}")
    print(f"📊 Áudios com arquivo existente: {audios_com_arquivo}")
    print(f"📊 Taxa de sucesso: {(audios_com_arquivo/total_audios)*100:.1f}%")
    
    if audios_com_arquivo > 0:
        print("\n✅ SISTEMA DE ÁUDIO FUNCIONANDO!")
        print("💡 Para testar no frontend:")
        print("   1. Backend já está rodando em http://localhost:8000")
        print("   2. Frontend deve estar rodando em http://localhost:3000")
        print("   3. Acesse um chat com mensagens de áudio")
        print("   4. Os áudios devem aparecer com player interativo do WhatsApp")
    else:
        print("\n❌ SISTEMA DE ÁUDIO COM PROBLEMAS!")
        print("💡 Verifique:")
        print("   1. Se os arquivos existem nas pastas corretas")
        print("   2. Se as permissões estão corretas")
        print("   3. Se os caminhos estão sendo construídos corretamente")

if __name__ == "__main__":
    test_audio_system() 