#!/usr/bin/env python3
"""
Script para testar o sistema completo de áudio
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from webhook.audio_processor import WhatsAppAudioProcessor, process_audio_from_webhook
from core.models import Cliente
import json

def test_audio_processor():
    """Testa o processador de áudio"""
    print("🧪 TESTANDO PROCESSADOR DE ÁUDIO")
    print("=" * 60)
    
    # Obter cliente de teste
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado")
        return
    
    # Dados de teste de áudio (baseados no seu exemplo)
    test_audio_data = {
        "url": "https://mmg.whatsapp.net/v/t62.7117-24/11418572_639123605874985_2074276734782391920_n.enc?ccb=11-4&oh=01_Q5Aa2AH90VmSBOTtBIXsGxf0r5vMtkmkC4BsJLVg9s4HdByRdQ&oe=68B5B693&_nc_sid=5e03e0&mms3=true",
        "mimetype": "audio/ogg; codecs=opus",
        "fileSha256": "+ylX/pg8Tsa+zRJ8fgO0rpPycxdXtmLUZvZeZybjRAE=",
        "fileLength": "20718",
        "seconds": 8,
        "ptt": True,
        "mediaKey": "FnIfz9Ka/QzEPkAzlOQ9x0m3WBwUQaG265dvhLjnFl0=",
        "fileEncSha256": "bjXRtF2x2Xo1VCIBUVfKn7eQq6BUXSNVX7Z6JyUAdbs=",
        "directPath": "/v/t62.7117-24/11418572_639123605874985_2074276734782391920_n.enc?ccb=11-4&oh=01_Q5Aa2AH90VmSBOTtBIXsGxf0r5vMtkmkC4BsJLVg9s4HdByRdQ&oe=68B5B693&_nc_sid=5e03e0",
        "mediaKeyTimestamp": "1754149705",
        "waveform": "SCVgUxslRjNMUFpWOxgAAAA/NlNdQQ8/UFRbUjhLVDoSBwFENDodRSkpWl9VRx48QTZUTiECAABCRDUAFU49VA=="
    }
    
    print("📤 Dados de teste:")
    print(json.dumps(test_audio_data, indent=2))
    
    # Criar processador
    processor = WhatsAppAudioProcessor(cliente)
    
    # Testar processamento
    message_id = f"test_audio_{int(django.utils.timezone.now().timestamp())}"
    result = processor.process_audio_message(test_audio_data, message_id)
    
    if result:
        print(f"✅ Áudio processado com sucesso!")
        print(f"  📁 Arquivo: {result['file_path']}")
        print(f"  📏 Tamanho: {result['file_size']} bytes")
        print(f"  ⏱️ Duração: {result['duration']} segundos")
        print(f"  🎤 PTT: {result['ptt']}")
        print(f"  📄 MimeType: {result['mimetype']}")
    else:
        print("❌ Falha ao processar áudio")

def test_webhook_processing():
    """Testa o processamento de áudio via webhook"""
    print("\n🧪 TESTANDO PROCESSAMENTO VIA WEBHOOK")
    print("=" * 60)
    
    # Obter cliente de teste
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado")
        return
    
    # Dados de webhook de teste
    webhook_data = {
        "fromMe": False,
        "chat": {
            "id": "556999267344",
            "profilePicture": "https://example.com/chat.jpg"
        },
        "sender": {
            "id": "556993291093",
            "profilePicture": "https://example.com/sender.jpg",
            "pushName": "Teste"
        },
        "msgContent": {
            "audioMessage": {
                "url": "https://mmg.whatsapp.net/v/t62.7117-24/11418572_639123605874985_2074276734782391920_n.enc?ccb=11-4&oh=01_Q5Aa2AH90VmSBOTtBIXsGxf0r5vMtkmkC4BsJLVg9s4HdByRdQ&oe=68B5B693&_nc_sid=5e03e0&mms3=true",
                "mimetype": "audio/ogg; codecs=opus",
                "fileSha256": "+ylX/pg8Tsa+zRJ8fgO0rpPycxdXtmLUZvZeZybjRAE=",
                "fileLength": "20718",
                "seconds": 8,
                "ptt": True,
                "mediaKey": "FnIfz9Ka/QzEPkAzlOQ9x0m3WBwUQaG265dvhLjnFl0=",
                "fileEncSha256": "bjXRtF2x2Xo1VCIBUVfKn7eQq6BUXSNVX7Z6JyUAdbs=",
                "directPath": "/v/t62.7117-24/11418572_639123605874985_2074276734782391920_n.enc?ccb=11-4&oh=01_Q5Aa2AH90VmSBOTtBIXsGxf0r5vMtkmkC4BsJLVg9s4HdByRdQ&oe=68B5B693&_nc_sid=5e03e0",
                "mediaKeyTimestamp": "1754149705",
                "waveform": "SCVgUxslRjNMUFpWOxgAAAA/NlNdQQ8/UFRbUjhLVDoSBwFENDodRSkpWl9VRx48QTZUTiECAABCRDUAFU49VA=="
            }
        },
        "messageId": f"webhook_test_{int(django.utils.timezone.now().timestamp())}"
    }
    
    print("📤 Dados de webhook:")
    print(json.dumps(webhook_data, indent=2))
    
    # Processar via webhook
    result = process_audio_from_webhook(webhook_data, cliente)
    
    if result:
        print(f"✅ Áudio processado via webhook!")
        print(f"  📁 Arquivo: {result['file_path']}")
        print(f"  📏 Tamanho: {result['file_size']} bytes")
        print(f"  ⏱️ Duração: {result['duration']} segundos")
        print(f"  🎤 PTT: {result['ptt']}")
        print(f"  📄 MimeType: {result['mimetype']}")
        print(f"  ✅ Status: {result['status']}")
    else:
        print("❌ Falha ao processar áudio via webhook")

def check_ffmpeg():
    """Verifica se o ffmpeg está instalado"""
    print("\n🔍 VERIFICANDO FFMPEG")
    print("=" * 60)
    
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ FFmpeg está instalado e funcionando")
            print(f"  📋 Versão: {result.stdout.split('ffmpeg version')[1].split(' ')[1]}")
        else:
            print("❌ FFmpeg não está funcionando corretamente")
            print(f"  📄 Erro: {result.stderr}")
    except FileNotFoundError:
        print("❌ FFmpeg não está instalado")
        print("💡 Instale o FFmpeg para converter áudios")
    except Exception as e:
        print(f"❌ Erro ao verificar FFmpeg: {e}")

def main():
    """Função principal"""
    print("🔧 TESTE DO SISTEMA DE ÁUDIO")
    print("=" * 60)
    
    try:
        # Verificar FFmpeg
        check_ffmpeg()
        
        # Testar processador de áudio
        test_audio_processor()
        
        # Testar processamento via webhook
        test_webhook_processing()
        
        print("\n✅ Testes concluídos!")
        
    except Exception as e:
        print(f"❌ Erro nos testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 