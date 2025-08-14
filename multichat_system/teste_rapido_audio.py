#!/usr/bin/env python3
"""
Teste rápido do sistema de áudio
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat
from django.db import connection
from django.db.models import Count

def teste_rapido():
    """Teste rápido do sistema"""
    print("🎵 TESTE RÁPIDO DO SISTEMA DE ÁUDIO")
    print("=" * 50)
    
    try:
        # 1. Verificar mensagens de áudio
        print("\n🔍 VERIFICANDO MENSAGENS DE ÁUDIO:")
        audio_messages = Mensagem.objects.filter(tipo='audio')
        total_audio = audio_messages.count()
        print(f"📊 Total de mensagens de áudio: {total_audio}")
        
        if total_audio > 0:
            # Verificar estrutura
            sample_msg = audio_messages.first()
            print(f"\n📋 Exemplo de mensagem:")
            print(f"  ID: {sample_msg.id}")
            print(f"  Tipo: {sample_msg.tipo}")
            print(f"  Chat ID: {sample_msg.chat.chat_id if sample_msg.chat else 'N/A'}")
            
            # Verificar JSON
            try:
                import json
                content = json.loads(sample_msg.conteudo)
                if 'audioMessage' in content:
                    audio_data = content['audioMessage']
                    print(f"  ✅ JSON válido com audioMessage")
                    print(f"  🎵 Segundos: {audio_data.get('seconds', 'N/A')}")
                    print(f"  🎵 Tamanho: {audio_data.get('fileLength', 'N/A')}")
                    print(f"  🎵 Mime: {audio_data.get('mimetype', 'N/A')}")
                else:
                    print(f"  ❌ JSON não contém audioMessage")
            except Exception as e:
                print(f"  ❌ Erro no JSON: {e}")
                
            # Verificar distribuição por chat
            print(f"\n📊 Distribuição por chat:")
            chat_stats = audio_messages.values('chat__chat_id').annotate(count=Count('id')).order_by('-count')[:5]
            for stat in chat_stats:
                chat_id = stat['chat__chat_id']
                count = stat['count']
                print(f"  Chat {chat_id}: {count} áudios")
                
        else:
            print("❌ Nenhuma mensagem de áudio encontrada")
            
        # 2. Verificar arquivos de áudio
        print("\n🔍 VERIFICANDO ARQUIVOS DE ÁUDIO:")
        audio_path = "D:/multiChat/multichat_system/media_storage/Elizeu_Batiliere_Dos_Santos/instance_3B6XIW-ZTS923-GEAY6V/chats/556993258212/audio"
        
        if os.path.exists(audio_path):
            files = os.listdir(audio_path)
            print(f"📁 Caminho encontrado: {audio_path}")
            print(f"🎵 Total de arquivos: {len(files)}")
            
            # Mostrar arquivos
            for i, file in enumerate(files, 1):
                file_path = os.path.join(audio_path, file)
                file_size = os.path.getsize(file_path)
                print(f"  {i:2d}. {file} ({file_size:,} bytes)")
                
        else:
            print(f"❌ Caminho não encontrado: {audio_path}")
            
        # 3. Verificar API
        print("\n🔍 VERIFICANDO API:")
        try:
            import requests
            response = requests.get('http://localhost:8000/api/mensagens/?chat_id=556993258212&limit=5', timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("✅ API funcionando")
                
                # Verificar mensagens de áudio na API
                if 'results' in data:
                    audio_in_api = [msg for msg in data['results'] if msg.get('tipo') == 'audio']
                    print(f"🎵 Mensagens de áudio na API: {len(audio_in_api)}")
                    
                    if audio_in_api:
                        sample_api = audio_in_api[0]
                        print(f"📋 Exemplo da API:")
                        print(f"  ID: {sample_api.get('id')}")
                        print(f"  Tipo: {sample_api.get('tipo')}")
                        print(f"  Chat ID: {sample_api.get('chat_id')}")
            else:
                print(f"❌ API retornou status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Servidor não está rodando na porta 8000")
            print("💡 Execute: python manage.py runserver")
        except Exception as e:
            print(f"❌ Erro ao testar API: {e}")
            
        print("\n" + "=" * 50)
        print("🎵 TESTE RÁPIDO FINALIZADO!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    teste_rapido() 