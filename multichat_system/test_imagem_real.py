#!/usr/bin/env python3
"""
Script para testar download de imagem com dados reais
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

def testar_imagem_real():
    """Testa com dados reais de imagem"""
    print("🧪 Testando download de imagem com dados reais...")
    
    # Dados reais de imagem (substitua pelos dados reais do seu webhook)
    webhook_data = {
        "instanceId": "3B6XIW-ZTS923-GEAY6V",
        "messageId": "TEST_IMAGE_123",
        "sender": {
            "id": "556992962392@c.us",
            "pushName": "Elizeu"
        },
        "msgContent": {
            "imageMessage": {
                "url": "https://mmg.whatsapp.net/v/t62.7117-24/19083661_1303226854859439_3997981883652895124_n.enc?ccb=11-4&oh=01_Q5Aa2AHv1g25E-1H3jqetiO5I0A7GCCp1SbCxNT7hCJBPKZhJw&oe=68BB4268&_nc_sid=5e03e0&mms3=true",
                "mediaKey": "REAL_IMAGE_MEDIA_KEY_HERE",
                "mimetype": "image/jpeg",
                "fileLength": "1024",
                "directPath": "/v/t62.7117-24/19083661_1303226854859439_3997981883652895124_n.enc?ccb=11-4&oh=01_Q5Aa2AHv1g25E-1H3jqetiO5I0A7GCCp1SbCxNT7hCJBPKZhJw&oe=68BB4268&_nc_sid=5e03e0",
                "fileSha256": "REAL_SHA256_HERE",
                "fileEncSha256": "REAL_ENC_SHA256_HERE",
                "mediaKeyTimestamp": "1754510999"
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

def verificar_webhooks_reais_imagens():
    """Verifica webhooks reais com imagens"""
    print("\n🔍 Verificando webhooks reais com imagens...")
    
    # Buscar eventos de webhook recentes com imagens
    from webhook.models import WebhookEvent
    
    eventos = WebhookEvent.objects.filter(
        event_type='message'
    ).order_by('-timestamp')[:10]
    
    if not eventos.exists():
        print("❌ Nenhum evento de webhook encontrado!")
        return
    
    for evento in eventos:
        print(f"\n📋 Evento: {evento.event_id}")
        print(f"   Data: {evento.received_at}")
        
        # Analisar payload
        payload = evento.payload
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except:
                pass
        
        # Verificar se tem imagem
        msg_content = payload.get('msgContent', {})
        if 'imageMessage' in msg_content:
            print("   📎 IMAGEM ENCONTRADA!")
            media_data = msg_content['imageMessage']
            print(f"      Media Key: {media_data.get('mediaKey', 'N/A')}")
            print(f"      Direct Path: {media_data.get('directPath', 'N/A')}")
            print(f"      Mimetype: {media_data.get('mimetype', 'N/A')}")
            
            # Testar download com dados reais
            testar_download_imagem_real(payload, media_data)
        else:
            print("   ❌ Nenhuma imagem encontrada")

def testar_download_imagem_real(webhook_data, media_data):
    """Testa download de imagem com dados reais"""
    try:
        instancia = WhatsappInstance.objects.get(instance_id=webhook_data.get('instanceId'))
        
        # Preparar dados para download
        download_data = {
            'mediaKey': media_data.get('mediaKey', ''),
            'directPath': media_data.get('directPath', ''),
            'type': 'image',
            'mimetype': media_data.get('mimetype', '')
        }
        
        print(f"🔄 Testando download de imagem com dados reais...")
        
        resultado = download_media_via_wapi(
            instancia.instance_id,
            instancia.token,
            download_data
        )
        
        if resultado and resultado.get('fileLink'):
            print("✅ Download de imagem funcionou!")
            print(f"   File Link: {resultado['fileLink']}")
            
            # Testar salvamento
            file_path = save_media_file(
                resultado['fileLink'],
                'image',
                webhook_data.get('messageId', 'test_image'),
                'Teste Imagem',
                instancia.cliente,
                instancia
            )
            
            if file_path:
                print(f"✅ Imagem salva: {file_path}")
            else:
                print("❌ Falha ao salvar imagem")
        else:
            print("❌ Download de imagem falhou!")
            
    except Exception as e:
        print(f"❌ Erro no teste de imagem: {e}")

def criar_estrutura_imagem():
    """Cria estrutura específica para imagens"""
    print("\n📂 Criando estrutura para imagens...")
    
    try:
        instancia = WhatsappInstance.objects.get(instance_id="3B6XIW-ZTS923-GEAY6V")
        cliente = instancia.cliente
        
        # Criar pasta de imagem
        image_path = Path(__file__).parent / "media_storage" / f"cliente_{cliente.id}" / f"instance_{instancia.instance_id}" / "image"
        image_path.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Pasta de imagem criada: {image_path}")
        
        # Verificar se a pasta existe
        if image_path.exists():
            print("✅ Pasta de imagem existe e está acessível")
        else:
            print("❌ Pasta de imagem não foi criada")
            
    except Exception as e:
        print(f"❌ Erro ao criar estrutura: {e}")

def verificar_midias_imagem():
    """Verifica mídias de imagem existentes"""
    print("\n📁 Verificando mídias de imagem existentes...")
    
    midias_imagem = MediaFile.objects.filter(media_type='image')
    
    if not midias_imagem.exists():
        print("❌ Nenhuma mídia de imagem encontrada!")
        return
    
    print(f"📊 Total de mídias de imagem: {midias_imagem.count()}")
    
    for midia in midias_imagem[:3]:  # Mostrar apenas as 3 primeiras
        print(f"\n📎 Mídia ID: {midia.id}")
        print(f"   Message ID: {midia.message_id}")
        print(f"   Sender: {midia.sender_name}")
        print(f"   Status: {midia.download_status}")
        print(f"   Arquivo: {midia.file_name}")
        print(f"   Caminho: {midia.file_path}")
        if midia.file_path:
            existe = os.path.exists(midia.file_path)
            print(f"   Existe: {'✅' if existe else '❌'}")

def main():
    """Função principal"""
    print("🚀 Testando download de imagem...")
    print("=" * 60)
    
    # Criar estrutura
    criar_estrutura_imagem()
    
    # Verificar mídias existentes
    verificar_midias_imagem()
    
    # Verificar webhooks reais
    verificar_webhooks_reais_imagens()
    
    # Testar com dados reais
    testar_imagem_real()
    
    print("\n" + "=" * 60)
    print("✅ Teste de imagem concluído!")

if __name__ == "__main__":
    main() 