#!/usr/bin/env python3
"""
Script para testar a integração completa de áudios:
1. Webhook → Processador → Django
2. Django → Frontend 
3. Frontend → Player de áudio
"""

import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
sys.path.append('multichat_system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente

def main():
    print("TESTE INTEGRAÇÃO COMPLETA - ÁUDIOS")
    print("=" * 50)
    
    # 1. Verificar mensagens de áudio existentes
    print("\n1. MENSAGENS DE ÁUDIO EXISTENTES:")
    mensagens_audio = Mensagem.objects.filter(tipo='audio').order_by('-data_envio')
    
    print(f"Total de mensagens de áudio: {mensagens_audio.count()}")
    
    for msg in mensagens_audio[:5]:
        print(f"\nMensagem ID: {msg.id}")
        print(f"   Data: Data: {msg.data_envio}")
        print(f"   Remetente: Remetente: {msg.remetente}")
        print(f"   Chat: Chat: {msg.chat.chat_name}")
        print(f"   FromMe: From Me: {msg.from_me}")
        print(f"   Conteudo: Conteúdo: {msg.conteudo[:100]}...")
        
        # Verificar se o conteúdo é JSON estruturado
        try:
            if msg.conteudo and msg.conteudo.startswith('{'):
                conteudo_json = json.loads(msg.conteudo)
                if 'audioMessage' in conteudo_json:
                    audio_data = conteudo_json['audioMessage']
                    print(f"   OK JSON estruturado encontrado:")
                    print(f"      - URL: {audio_data.get('url', 'N/A')[:50]}...")
                    print(f"      - Mimetype: {audio_data.get('mimetype', 'N/A')}")
                    print(f"      - Duração: {audio_data.get('seconds', 'N/A')}s")
                    print(f"      - PTT: {audio_data.get('ptt', 'N/A')}")
                else:
                    print(f"   AVISO JSON sem audioMessage")
            else:
                print(f"   AVISO Conteúdo não é JSON estruturado")
        except json.JSONDecodeError as e:
            print(f"   ERRO Erro ao decodificar JSON: {e}")
    
    # 2. Simular dados de webhook de áudio (baseado no log real)
    print(f"\n2. SIMULANDO PROCESSAMENTO DE WEBHOOK:")
    
    webhook_data = {
        "event": "webhookDelivery",
        "instanceId": "3B6XIW-ZTS923-GEAY6V",
        "messageId": "TESTE_AUDIO_" + str(int(datetime.now().timestamp())),
        "fromMe": True,
        "chat": {"id": "556999267344"},
        "sender": {
            "id": "556993291093",
            "pushName": "Elizeu"
        },
        "moment": int(datetime.now().timestamp()),
        "msgContent": {
            "audioMessage": {
                "url": "https://mmg.whatsapp.net/v/t62.7117-24/11252069_TESTE.enc",
                "mimetype": "audio/ogg; codecs=opus",
                "fileSha256": "5DlaY4przrGL/ASNz5lM5oonk6+blnsEHBTCmrM7XLM=",
                "fileLength": "5237",
                "seconds": 5,
                "ptt": True,
                "mediaKey": "sRadDqIFGL9DQtMs1iCrHH89YJAOCQwwH2qXsDgSQy4=",
                "fileEncSha256": "VP/8lJ+jNSf9PFMsTQEQM9it2osoDe0yr+Z0JFFTCBk=",
                "directPath": "/v/t62.7117-24/11252069_TESTE.enc",
                "mediaKeyTimestamp": str(int(datetime.now().timestamp())),
                "waveform": "AAAAAAAAAAALKUZZWFZQPjk4ODUxLjZETlJSUU5KQjQiISMpJyIaCgAAAAAAAAA="
            }
        }
    }
    
    print("Dados Dados do webhook simulado:")
    print(f"   Message ID: {webhook_data['messageId']}")
    print(f"   From Me: {webhook_data['fromMe']}")
    print(f"   Audio Duration: {webhook_data['msgContent']['audioMessage']['seconds']}s")
    print(f"   Audio Mimetype: {webhook_data['msgContent']['audioMessage']['mimetype']}")
    
    # 3. Criar mensagem manualmente como o processador faria
    print(f"\n3. CRIANDO MENSAGEM COMO O PROCESSADOR:")
    
    try:
        # Buscar cliente
        cliente = Cliente.objects.first()
        if not cliente:
            print("ERRO Nenhum cliente encontrado")
            return
            
        # Buscar chat
        chat = Chat.objects.filter(cliente=cliente).first()
        if not chat:
            print("ERRO Nenhum chat encontrado")
            return
        
        # Criar JSON estruturado para o frontend
        audio_data = webhook_data['msgContent']['audioMessage']
        conteudo_json = json.dumps({
            "audioMessage": {
                "url": audio_data.get('url', ''),
                "mediaKey": audio_data.get('mediaKey', ''),
                "mimetype": audio_data.get('mimetype', 'audio/ogg'),
                "fileLength": audio_data.get('fileLength', ''),
                "seconds": audio_data.get('seconds', 0),
                "ptt": audio_data.get('ptt', False),
                "directPath": audio_data.get('directPath', ''),
                "fileSha256": audio_data.get('fileSha256', ''),
                "fileEncSha256": audio_data.get('fileEncSha256', ''),
                "mediaKeyTimestamp": audio_data.get('mediaKeyTimestamp', ''),
                "waveform": audio_data.get('waveform', '')
            }
        }, ensure_ascii=False)
        
        # Criar mensagem
        mensagem = Mensagem.objects.create(
            chat=chat,
            remetente=webhook_data['sender']['pushName'],
            conteudo=conteudo_json,
            tipo='audio',
            from_me=webhook_data['fromMe'],
            message_id=webhook_data['messageId'],
            data_envio=datetime.now()
        )
        
        print(f"OK Mensagem criada com sucesso!")
        print(f"   ID: {mensagem.id}")
        print(f"   Tipo: {mensagem.tipo}")
        print(f"   JSON estruturado: {len(conteudo_json)} chars")
        
    except Exception as e:
        print(f"ERRO Erro ao criar mensagem: {e}")
    
    # 4. Verificar endpoints de teste
    print(f"\n4. ENDPOINTS DE TESTE DISPONÍVEIS:")
    
    if mensagens_audio.exists():
        primeira_mensagem = mensagens_audio.first()
        print(f"OK Endpoints para mensagem ID {primeira_mensagem.id}:")
        print(f"   - Por ID: http://localhost:8000/api/audio/message/{primeira_mensagem.id}/")
        
        # Verificar se há áudio em /wapi/midias/
        import glob
        audio_files = glob.glob("wapi/midias/audios/*.mp3")
        if audio_files:
            filename = os.path.basename(audio_files[0])
            print(f"   - Via arquivo: http://localhost:8000/api/wapi-media/audios/{filename}")
    
    print(f"\n5. INSTRUÇÕES PARA TESTE COMPLETO:")
    print("   1. Iniciar backend: cd multichat_system && python manage.py runserver")
    print("   2. Iniciar frontend: cd multichat-frontend && npm start")  
    print("   3. Acessar: http://localhost:3000")
    print("   4. Procurar mensagens de áudio nos chats")
    print("   5. Verificar se aparecem players de áudio interativos")
    print("   6. Console do navegador deve mostrar logs '🎵 DEBUG AudioPlayer'")
    
    print("\n" + "=" * 50)
    print("TESTE CONCLUÍDO")

if __name__ == '__main__':
    main()