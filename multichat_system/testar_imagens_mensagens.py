#!/usr/bin/env python
"""
Script para testar se as imagens estão sendo processadas corretamente
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem, Cliente
from webhook.views import extract_message_content, detect_message_type

def testar_processamento_imagens():
    """Testa o processamento de imagens"""
    print("🔍 Testando processamento de imagens...")
    print("=" * 50)
    
    # Buscar mensagens com imagens
    mensagens_imagem = Mensagem.objects.filter(tipo='image')
    print(f"Total de mensagens de imagem: {mensagens_imagem.count()}")
    
    for i, msg in enumerate(mensagens_imagem[:5]):  # Testar apenas as primeiras 5
        print(f"\n📸 Mensagem {i+1}:")
        print(f"   ID: {msg.id}")
        print(f"   Message ID: {msg.message_id}")
        print(f"   Tipo: {msg.tipo}")
        print(f"   Conteúdo: {msg.conteudo[:100]}...")
        
        # Verificar se o conteúdo é JSON
        if msg.conteudo and msg.conteudo.startswith('{'):
            try:
                json_content = json.loads(msg.conteudo)
                print(f"   ✅ Conteúdo JSON válido")
                
                if 'imageMessage' in json_content:
                    image_data = json_content['imageMessage']
                    print(f"   📷 URL da imagem: {image_data.get('url', 'N/A')}")
                    print(f"   📝 Caption: {image_data.get('caption', 'N/A')}")
                    print(f"   📏 Dimensões: {image_data.get('width', 'N/A')}x{image_data.get('height', 'N/A')}")
                    print(f"   📦 Tamanho: {image_data.get('fileLength', 'N/A')}")
                else:
                    print(f"   ❌ Não é uma mensagem de imagem")
            except json.JSONDecodeError:
                print(f"   ❌ JSON inválido")
        else:
            print(f"   📝 Conteúdo texto simples")
    
    # Testar função de extração
    print(f"\n🧪 Testando função extract_message_content...")
    
    # Simular dados de webhook de imagem
    test_payload = {
        'message': {
            'imageMessage': {
                'url': 'https://mmg.whatsapp.net/v/t62.7109-24/1234567890/image.jpg',
                'caption': 'Teste de imagem',
                'mimetype': 'image/jpeg',
                'fileLength': '12345',
                'height': 800,
                'width': 600,
                'jpegThumbnail': 'data:image/jpeg;base64,...',
                'mediaKey': 'test_key',
                'directPath': '/v/t62.7109-24/1234567890/image.jpg',
                'fileSha256': 'test_sha256',
                'fileEncSha256': 'test_enc_sha256',
                'mediaKeyTimestamp': '1234567890'
            }
        }
    }
    
    message_type = detect_message_type(test_payload)
    content = extract_message_content(test_payload, message_type)
    
    print(f"   Tipo detectado: {message_type}")
    print(f"   Conteúdo extraído: {content[:100]}...")
    
    # Verificar se é JSON válido
    try:
        json_content = json.loads(content)
        print(f"   ✅ JSON válido gerado")
        if 'imageMessage' in json_content:
            print(f"   📷 URL preservada: {json_content['imageMessage'].get('url', 'N/A')}")
    except json.JSONDecodeError:
        print(f"   ❌ JSON inválido gerado")

if __name__ == "__main__":
    testar_processamento_imagens() 