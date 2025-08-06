#!/usr/bin/env python3
"""
Script para testar e diagnosticar o problema com download automático de mídias
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

from core.models import Cliente, WhatsappInstance, MediaFile
from webhook.views import process_media_automatically, download_media_via_wapi, save_media_file

def testar_instancias_ativas():
    """Testa instâncias ativas e suas configurações"""
    print("🔍 Verificando instâncias ativas...")
    
    instancias = WhatsappInstance.objects.all()
    
    if not instancias.exists():
        print("❌ Nenhuma instância encontrada!")
        return None
    
    for instancia in instancias:
        print(f"\n📱 Instância: {instancia.instance_id}")
        print(f"   Cliente: {instancia.cliente.nome}")
        print(f"   Status: {instancia.status}")
        print(f"   Token: {'✅' if instancia.token else '❌'}")
        
        # Verificar se a pasta existe
        media_path = Path(__file__).parent / "media_storage" / f"cliente_{instancia.cliente.id}" / f"instance_{instancia.instance_id}"
        print(f"   Pasta mídia: {'✅' if media_path.exists() else '❌'} - {media_path}")
        
        return instancia
    
    return None

def testar_webhook_midia_exemplo():
    """Testa com dados de webhook de exemplo"""
    print("\n🧪 Testando com dados de webhook de exemplo...")
    
    # Dados de exemplo de uma mensagem com imagem
    webhook_exemplo = {
        "instanceId": "3B6XIW-ZTS923-GEAY6V",
        "messageId": "test_message_123",
        "sender": {
            "id": "5511999999999@c.us",
            "pushName": "Teste Usuário"
        },
        "msgContent": {
            "imageMessage": {
                "mediaKey": "test_media_key_123",
                "directPath": "/test/direct/path/image.jpg",
                "mimetype": "image/jpeg",
                "fileLength": 1024,
                "caption": "Teste de imagem"
            }
        }
    }
    
    # Buscar instância
    try:
        instancia = WhatsappInstance.objects.get(instance_id="3B6XIW-ZTS923-GEAY6V")
        cliente = instancia.cliente
        
        print(f"✅ Instância encontrada: {instancia.instance_id}")
        print(f"✅ Cliente: {cliente.nome}")
        
        # Testar processamento automático
        resultado = process_media_automatically(webhook_exemplo, cliente, instancia)
        
        if resultado:
            print("✅ Processamento automático funcionou!")
        else:
            print("❌ Processamento automático falhou!")
            
    except WhatsappInstance.DoesNotExist:
        print("❌ Instância não encontrada!")
    except Exception as e:
        print(f"❌ Erro: {e}")

def testar_download_wapi_direto():
    """Testa download direto via W-API"""
    print("\n🌐 Testando download direto via W-API...")
    
    try:
        instancia = WhatsappInstance.objects.get(instance_id="3B6XIW-ZTS923-GEAY6V")
        
        # Dados de teste
        media_data = {
            'mediaKey': 'test_key_123',
            'directPath': '/test/path/image.jpg',
            'type': 'image',
            'mimetype': 'image/jpeg'
        }
        
        print(f"🔄 Testando download com:")
        print(f"   Instance ID: {instancia.instance_id}")
        print(f"   Token: {'✅' if instancia.token else '❌'}")
        print(f"   Media Data: {json.dumps(media_data, indent=2)}")
        
        resultado = download_media_via_wapi(
            instancia.instance_id,
            instancia.token,
            media_data
        )
        
        if resultado:
            print("✅ Download W-API funcionou!")
            print(f"   File Link: {resultado.get('fileLink', 'N/A')}")
        else:
            print("❌ Download W-API falhou!")
            
    except WhatsappInstance.DoesNotExist:
        print("❌ Instância não encontrada!")
    except Exception as e:
        print(f"❌ Erro: {e}")

def verificar_midias_existentes():
    """Verifica mídias já baixadas"""
    print("\n📁 Verificando mídias existentes...")
    
    midias = MediaFile.objects.all()
    
    if not midias.exists():
        print("❌ Nenhuma mídia encontrada no banco!")
        return
    
    print(f"📊 Total de mídias: {midias.count()}")
    
    for midia in midias[:5]:  # Mostrar apenas as 5 primeiras
        print(f"\n📎 Mídia ID: {midia.id}")
        print(f"   Tipo: {midia.media_type}")
        print(f"   Status: {midia.download_status}")
        print(f"   Arquivo: {midia.file_name}")
        print(f"   Caminho: {midia.file_path}")
        print(f"   Existe: {'✅' if (midia.file_path and os.path.exists(midia.file_path)) else '❌'}")

def criar_estrutura_pastas():
    """Cria estrutura de pastas necessária"""
    print("\n📂 Criando estrutura de pastas...")
    
    try:
        instancia = WhatsappInstance.objects.get(instance_id="3B6XIW-ZTS923-GEAY6V")
        cliente = instancia.cliente
        
        # Criar estrutura base
        base_path = Path(__file__).parent / "media_storage" / f"cliente_{cliente.id}" / f"instance_{instancia.instance_id}"
        
        # Criar pastas para cada tipo de mídia
        tipos_midia = ['image', 'video', 'audio', 'document', 'sticker']
        
        for tipo in tipos_midia:
            tipo_path = base_path / tipo
            tipo_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Pasta criada: {tipo_path}")
        
        print(f"✅ Estrutura criada em: {base_path}")
        
    except WhatsappInstance.DoesNotExist:
        print("❌ Instância não encontrada!")
    except Exception as e:
        print(f"❌ Erro ao criar pastas: {e}")

def testar_salvamento_arquivo():
    """Testa salvamento de arquivo"""
    print("\n💾 Testando salvamento de arquivo...")
    
    try:
        instancia = WhatsappInstance.objects.get(instance_id="3B6XIW-ZTS923-GEAY6V")
        cliente = instancia.cliente
        
        # URL de teste (pode ser qualquer imagem)
        file_link = "https://via.placeholder.com/150x150.png"
        
        resultado = save_media_file(
            file_link,
            'image',
            'test_message_456',
            'Teste Usuário',
            cliente,
            instancia
        )
        
        if resultado:
            print("✅ Salvamento funcionou!")
            print(f"   Arquivo: {resultado}")
        else:
            print("❌ Salvamento falhou!")
            
    except WhatsappInstance.DoesNotExist:
        print("❌ Instância não encontrada!")
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    print("🚀 Iniciando diagnóstico de download automático de mídias...")
    print("=" * 60)
    
    # Testar instâncias
    instancia = testar_instancias_ativas()
    
    if not instancia:
        print("❌ Nenhuma instância ativa encontrada!")
        return
    
    # Verificar mídias existentes
    verificar_midias_existentes()
    
    # Criar estrutura de pastas
    criar_estrutura_pastas()
    
    # Testar salvamento
    testar_salvamento_arquivo()
    
    # Testar webhook de exemplo
    testar_webhook_midia_exemplo()
    
    # Testar download W-API
    testar_download_wapi_direto()
    
    print("\n" + "=" * 60)
    print("✅ Diagnóstico concluído!")

if __name__ == "__main__":
    main() 