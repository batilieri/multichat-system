#!/usr/bin/env python3
"""
Script para testar o sistema completo de webhook com download automático
"""

import os
import sys
import django
import json
import requests
from pathlib import Path

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import MediaFile, WhatsappInstance
from webhook.views import process_webhook_message

def testar_webhook_completo():
    """Testa o sistema completo de webhook"""
    print("🧪 Testando sistema completo de webhook...")
    
    # Dados reais do webhook de áudio
    webhook_data = {
        "instanceId": "3B6XIW-ZTS923-GEAY6V",
        "messageId": "B80D865264B9CA985108F695BEF5B564",
        "fromMe": True,
        "sender": {
            "id": "556992962392@c.us",
            "pushName": "Elizeu"
        },
        "msgContent": {
            "audioMessage": {
                "url": "https://mmg.whatsapp.net/v/t62.7117-24/19083661_1303226854859439_3997981883652895124_n.enc?ccb=11-4&oh=01_Q5Aa2AHv1g25E-1H3jqetiO5I0A7GCCp1SbCxNT7hCJBPKZhJw&oe=68BB4268&_nc_sid=5e03e0&mms3=true",
                "mediaKey": "rwyoaVpbrjfFQ3X1YKt7Y1+pnun0a2536qDKOnT2HuQ=",
                "mimetype": "audio/ogg; codecs=opus",
                "fileLength": "5067",
                "seconds": 2,
                "ptt": True,
                "directPath": "/v/t62.7117-24/19083661_1303226854859439_3997981883652895124_n.enc?ccb=11-4&oh=01_Q5Aa2AHv1g25E-1H3jqetiO5I0A7GCCp1SbCxNT7hCJBPKZhJw&oe=68BB4268&_nc_sid=5e03e0",
                "fileSha256": "muLcy0C+OrTMaciGKHUeYxzc/UKCYHgRUVbbf+46b7U=",
                "fileEncSha256": "cG50b/Z+hq/Re57fT/W1n0pNI2ZdHsZe1KaiP6EeI/4=",
                "mediaKeyTimestamp": "1754510999",
                "waveform": "JSo2SlFTU05GTlJPTUpFQ0RBNh4TEjBBS0lIRURDQTw3REtGNCY1QEc/Mx8wRkxMSTs7TVFPSkA1QEU+OjlCRg=="
            }
        }
    }
    
    print("📋 Dados do webhook:")
    print(f"   Instance ID: {webhook_data['instanceId']}")
    print(f"   Message ID: {webhook_data['messageId']}")
    print(f"   From Me: {webhook_data['fromMe']}")
    print(f"   Sender: {webhook_data['sender']['pushName']}")
    print(f"   Tipo de mídia: Audio")
    
    # Testar processamento completo
    print("\n🔄 Processando webhook completo...")
    
    try:
        resultado = process_webhook_message(webhook_data, 'message')
        
        if resultado:
            print("✅ Webhook processado com sucesso!")
        else:
            print("❌ Falha no processamento do webhook")
            
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        import traceback
        traceback.print_exc()

def verificar_resultado_download():
    """Verifica o resultado do download"""
    print("\n📁 Verificando resultado do download...")
    
    # Verificar arquivos na pasta
    audio_path = Path(__file__).parent / "media_storage" / "cliente_2" / "instance_3B6XIW-ZTS923-GEAY6V" / "audio"
    
    if audio_path.exists():
        arquivos = list(audio_path.glob('*'))
        print(f"📊 Arquivos na pasta audio: {len(arquivos)}")
        
        for arquivo in arquivos:
            tamanho = arquivo.stat().st_size
            print(f"   📎 {arquivo.name} ({tamanho} bytes)")
    else:
        print("❌ Pasta de áudio não existe!")
    
    # Verificar registros no banco
    midias_recentes = MediaFile.objects.filter(
        message_id="B80D865264B9CA985108F695BEF5B564"
    ).order_by('-created_at')
    
    if midias_recentes.exists():
        print(f"\n📊 Registros no banco para esta mensagem: {midias_recentes.count()}")
        
        for midia in midias_recentes:
            print(f"   📎 ID: {midia.id}")
            print(f"      Status: {midia.download_status}")
            print(f"      Arquivo: {midia.file_name}")
            print(f"      Caminho: {midia.file_path}")
            if midia.file_path:
                existe = os.path.exists(midia.file_path)
                print(f"      Existe: {'✅' if existe else '❌'}")
    else:
        print("❌ Nenhum registro encontrado no banco!")

def testar_diferentes_tipos_midia():
    """Testa diferentes tipos de mídia"""
    print("\n🧪 Testando diferentes tipos de mídia...")
    
    tipos_teste = [
        {
            "nome": "Imagem",
            "msgContent": {
                "imageMessage": {
                    "mediaKey": "test_image_key",
                    "directPath": "/test/image/path.jpg",
                    "mimetype": "image/jpeg",
                    "fileLength": "1024"
                }
            }
        },
        {
            "nome": "Vídeo",
            "msgContent": {
                "videoMessage": {
                    "mediaKey": "test_video_key",
                    "directPath": "/test/video/path.mp4",
                    "mimetype": "video/mp4",
                    "fileLength": "2048"
                }
            }
        },
        {
            "nome": "Documento",
            "msgContent": {
                "documentMessage": {
                    "mediaKey": "test_doc_key",
                    "directPath": "/test/doc/path.pdf",
                    "mimetype": "application/pdf",
                    "fileLength": "512"
                }
            }
        }
    ]
    
    for tipo in tipos_teste:
        print(f"\n📎 Testando {tipo['nome']}...")
        
        webhook_data = {
            "instanceId": "3B6XIW-ZTS923-GEAY6V",
            "messageId": f"TEST_{tipo['nome']}_123",
            "sender": {
                "id": "556992962392@c.us",
                "pushName": "Teste"
            },
            "msgContent": tipo["msgContent"]
        }
        
        try:
            from webhook.views import process_media_automatically
            
            instancia = WhatsappInstance.objects.get(instance_id="3B6XIW-ZTS923-GEAY6V")
            cliente = instancia.cliente
            
            resultado = process_media_automatically(webhook_data, cliente, instancia)
            
            if resultado:
                print(f"   ✅ {tipo['nome']} processado com sucesso!")
            else:
                print(f"   ❌ {tipo['nome']} falhou!")
                
        except Exception as e:
            print(f"   ❌ Erro no teste de {tipo['nome']}: {e}")

def main():
    """Função principal"""
    print("🚀 Testando sistema completo de webhook...")
    print("=" * 60)
    
    # Testar webhook completo
    testar_webhook_completo()
    
    # Verificar resultado
    verificar_resultado_download()
    
    # Testar diferentes tipos
    testar_diferentes_tipos_midia()
    
    print("\n" + "=" * 60)
    print("✅ Teste completo concluído!")

if __name__ == "__main__":
    main() 