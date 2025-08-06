#!/usr/bin/env python3
"""
Script para testar com dados reais do webhook de áudio
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

from core.models import WhatsappInstance, MediaFile
from webhook.views import process_media_automatically, download_media_via_wapi, save_media_file

def testar_webhook_audio_real():
    """Testa com dados reais do webhook de áudio"""
    print("🧪 Testando com dados reais do webhook de áudio...")
    
    # Dados reais do webhook fornecido
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
    
    try:
        # Buscar instância
        instancia = WhatsappInstance.objects.get(instance_id="3B6XIW-ZTS923-GEAY6V")
        cliente = instancia.cliente
        
        print(f"✅ Instância encontrada: {instancia.instance_id}")
        print(f"✅ Cliente: {cliente.nome}")
        print(f"✅ Token: {'✅' if instancia.token else '❌'}")
        
        # Testar processamento automático
        print("\n🔄 Testando processamento automático...")
        resultado = process_media_automatically(webhook_data, cliente, instancia)
        
        if resultado:
            print("✅ Processamento automático funcionou!")
        else:
            print("❌ Processamento automático falhou!")
            
    except WhatsappInstance.DoesNotExist:
        print("❌ Instância não encontrada!")
    except Exception as e:
        print(f"❌ Erro: {e}")

def testar_download_direto_audio():
    """Testa download direto do áudio"""
    print("\n🌐 Testando download direto do áudio...")
    
    try:
        instancia = WhatsappInstance.objects.get(instance_id="3B6XIW-ZTS923-GEAY6V")
        
        # Dados reais do áudio
        media_data = {
            'mediaKey': 'rwyoaVpbrjfFQ3X1YKt7Y1+pnun0a2536qDKOnT2HuQ=',
            'directPath': '/v/t62.7117-24/19083661_1303226854859439_3997981883652895124_n.enc?ccb=11-4&oh=01_Q5Aa2AHv1g25E-1H3jqetiO5I0A7GCCp1SbCxNT7hCJBPKZhJw&oe=68BB4268&_nc_sid=5e03e0',
            'type': 'audio',
            'mimetype': 'audio/ogg; codecs=opus'
        }
        
        print(f"🔄 Testando download com dados reais:")
        print(f"   Media Key: {media_data['mediaKey']}")
        print(f"   Direct Path: {media_data['directPath']}")
        print(f"   Type: {media_data['type']}")
        print(f"   Mimetype: {media_data['mimetype']}")
        
        resultado = download_media_via_wapi(
            instancia.instance_id,
            instancia.token,
            media_data
        )
        
        if resultado and resultado.get('fileLink'):
            print("✅ Download direto funcionou!")
            print(f"   File Link: {resultado['fileLink']}")
            
            # Testar salvamento
            file_path = save_media_file(
                resultado['fileLink'],
                'audio',
                'B80D865264B9CA985108F695BEF5B564',
                'Elizeu',
                instancia.cliente,
                instancia
            )
            
            if file_path:
                print(f"✅ Arquivo salvo: {file_path}")
            else:
                print("❌ Falha ao salvar arquivo")
        else:
            print("❌ Download direto falhou!")
            
    except WhatsappInstance.DoesNotExist:
        print("❌ Instância não encontrada!")
    except Exception as e:
        print(f"❌ Erro: {e}")

def verificar_midias_audio():
    """Verifica mídias de áudio existentes"""
    print("\n📁 Verificando mídias de áudio existentes...")
    
    midias_audio = MediaFile.objects.filter(media_type='audio')
    
    if not midias_audio.exists():
        print("❌ Nenhuma mídia de áudio encontrada!")
        return
    
    print(f"📊 Total de mídias de áudio: {midias_audio.count()}")
    
    for midia in midias_audio[:3]:  # Mostrar apenas as 3 primeiras
        print(f"\n📎 Mídia ID: {midia.id}")
        print(f"   Message ID: {midia.message_id}")
        print(f"   Sender: {midia.sender_name}")
        print(f"   Status: {midia.download_status}")
        print(f"   Arquivo: {midia.file_name}")
        print(f"   Caminho: {midia.file_path}")
        if midia.file_path:
            existe = os.path.exists(midia.file_path)
            print(f"   Existe: {'✅' if existe else '❌'}")

def criar_estrutura_audio():
    """Cria estrutura específica para áudios"""
    print("\n📂 Criando estrutura para áudios...")
    
    try:
        instancia = WhatsappInstance.objects.get(instance_id="3B6XIW-ZTS923-GEAY6V")
        cliente = instancia.cliente
        
        # Criar pasta de áudio
        audio_path = Path(__file__).parent / "media_storage" / f"cliente_{cliente.id}" / f"instance_{instancia.instance_id}" / "audio"
        audio_path.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Pasta de áudio criada: {audio_path}")
        
        # Verificar se a pasta existe
        if audio_path.exists():
            print("✅ Pasta de áudio existe e está acessível")
        else:
            print("❌ Pasta de áudio não foi criada")
            
    except Exception as e:
        print(f"❌ Erro ao criar estrutura: {e}")

def main():
    """Função principal"""
    print("🚀 Testando webhook de áudio real...")
    print("=" * 60)
    
    # Criar estrutura
    criar_estrutura_audio()
    
    # Verificar mídias existentes
    verificar_midias_audio()
    
    # Testar com dados reais
    testar_webhook_audio_real()
    
    # Testar download direto
    testar_download_direto_audio()
    
    print("\n" + "=" * 60)
    print("✅ Teste concluído!")

if __name__ == "__main__":
    main() 