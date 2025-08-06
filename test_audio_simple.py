#!/usr/bin/env python3
"""
Teste simplificado do sistema de áudio
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
django.setup()

from webhook.audio_processor_simple import SimpleAudioProcessor, process_audio_from_webhook_simple
from core.models import Cliente
import json

def test_simple_audio_processor():
    """Testa o processador de áudio simplificado"""
    print("🧪 TESTANDO PROCESSADOR DE ÁUDIO SIMPLIFICADO")
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
    processor = SimpleAudioProcessor(cliente)
    
    # Testar processamento
    message_id = f"test_audio_simple_{int(django.utils.timezone.now().timestamp())}"
    result = processor.process_audio_message(test_audio_data, message_id)
    
    if result:
        print(f"✅ Áudio processado com sucesso!")
        print(f"  📁 Arquivo: {result['file_path']}")
        print(f"  📏 Tamanho: {result['file_size']} bytes")
        print(f"  ⏱️ Duração: {result['duration']} segundos")
        print(f"  🎤 PTT: {result['ptt']}")
        print(f"  📄 MimeType: {result['mimetype']}")
        print(f"  📝 Nota: {result.get('note', 'N/A')}")
    else:
        print("❌ Falha ao processar áudio")

def test_webhook_processing_simple():
    """Testa o processamento de áudio via webhook (versão simplificada)"""
    print("\n🧪 TESTANDO PROCESSAMENTO VIA WEBHOOK (SIMPLIFICADO)")
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
        "messageId": f"webhook_test_simple_{int(django.utils.timezone.now().timestamp())}"
    }
    
    print("📤 Dados de webhook:")
    print(json.dumps(webhook_data, indent=2))
    
    # Processar via webhook
    result = process_audio_from_webhook_simple(webhook_data, cliente)
    
    if result:
        print(f"✅ Áudio processado via webhook!")
        print(f"  📁 Arquivo: {result['file_path']}")
        print(f"  📏 Tamanho: {result['file_size']} bytes")
        print(f"  ⏱️ Duração: {result['duration']} segundos")
        print(f"  🎤 PTT: {result['ptt']}")
        print(f"  📄 MimeType: {result['mimetype']}")
        print(f"  ✅ Status: {result['status']}")
        print(f"  📝 Nota: {result.get('note', 'N/A')}")
    else:
        print("❌ Falha ao processar áudio via webhook")

def check_media_directory():
    """Verifica se o diretório de mídia está configurado corretamente"""
    print("\n🔍 VERIFICANDO DIRETÓRIO DE MÍDIA")
    print("=" * 60)
    
    from django.conf import settings
    
    media_root = settings.MEDIA_ROOT
    print(f"📁 Media Root: {media_root}")
    
    if os.path.exists(media_root):
        print("✅ Diretório de mídia existe")
        
        # Verificar permissões
        if os.access(media_root, os.W_OK):
            print("✅ Diretório de mídia é gravável")
        else:
            print("❌ Diretório de mídia não é gravável")
    else:
        print("❌ Diretório de mídia não existe")
        print("💡 Criando diretório...")
        try:
            os.makedirs(media_root, exist_ok=True)
            print("✅ Diretório criado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao criar diretório: {e}")

def main():
    """Função principal"""
    print("🔧 TESTE DO SISTEMA DE ÁUDIO SIMPLIFICADO")
    print("=" * 60)
    
    try:
        # Verificar diretório de mídia
        check_media_directory()
        
        # Testar processador de áudio
        test_simple_audio_processor()
        
        # Testar processamento via webhook
        test_webhook_processing_simple()
        
        print("\n✅ Testes concluídos!")
        print("\n💡 Para instalar FFmpeg e usar o processador completo:")
        print("   Execute: .\\install_ffmpeg_windows.ps1")
        
    except Exception as e:
        print(f"❌ Erro nos testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 