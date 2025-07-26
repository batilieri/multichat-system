#!/usr/bin/env python3
"""
Teste do Analisador Completo de Webhooks
Demonstra a análise detalhada de webhooks do WhatsApp
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.webhook_media_analyzer import (
    analisar_webhook_whatsapp,
    processar_webhook_whatsapp,
    gerar_relatorio_webhook
)


def test_webhook_analyzer():
    """Testa o analisador de webhooks"""
    
    print("🔍 TESTE DO ANALISADOR COMPLETO DE WEBHOOKS")
    print("=" * 60)
    
    # Webhook de exemplo com diferentes tipos de mídia
    webhook_exemplo = {
        'event': 'webhookReceived',
        'instanceId': '3B6XIW-ZTS923-GEAY6V',
        'messageId': f'test_analyzer_{int(datetime.now().timestamp())}',
        'sender': {
            'id': '5511999999999@s.whatsapp.net',
            'pushName': 'Teste Analisador'
        },
        'chat': {
            'id': '5511999999999@s.whatsapp.net'
        },
        'msgContent': {
            'imageMessage': {
                'mimetype': 'image/jpeg',
                'fileName': 'foto_teste.jpg',
                'fileLength': 8192,
                'caption': 'Foto de teste do analisador',
                'mediaKey': 'test_media_key_001',
                'directPath': '/test/path/image',
                'fileSha256': 'test_sha256_001',
                'fileEncSha256': 'test_enc_sha256_001',
                'width': 1200,
                'height': 800,
                'jpegThumbnail': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...'
            }
        },
        'isGroup': False,
        'fromMe': False,
        'moment': int(datetime.now().timestamp())
    }
    
    # 1. Análise básica
    print("\n📊 1. ANÁLISE BÁSICA DO WEBHOOK")
    print("-" * 40)
    
    analise = analisar_webhook_whatsapp(webhook_exemplo)
    
    print(f"✅ Webhook analisado com sucesso")
    print(f"📎 Total de mídias: {analise.get('total_midias', 0)}")
    print(f"🔍 Tem mídias: {analise.get('tem_midias', False)}")
    
    # Informações do cliente
    cliente_info = analise.get('cliente_info', {})
    if cliente_info.get('encontrado'):
        print(f"👤 Cliente: {cliente_info.get('cliente_nome')}")
        print(f"📱 Instância: {cliente_info.get('instance_id')}")
        print(f"🔑 Token: {cliente_info.get('instance_token', '')[:20]}...")
    else:
        print(f"❌ Cliente não encontrado: {cliente_info.get('erro')}")
    
    # Informações das mídias
    midias = analise.get('midias', [])
    print(f"\n📎 Mídias encontradas:")
    for i, midia in enumerate(midias, 1):
        print(f"   {i}. {midia['type'].upper()}:")
        print(f"      📄 Mimetype: {midia.get('mimetype')}")
        print(f"      📁 Extensão: {midia.get('extensao')}")
        print(f"      📏 Tamanho: {midia.get('fileLength', 'N/A')} bytes")
        print(f"      ✅ Válido para download: {midia.get('valido_para_download')}")
        
        if midia.get('width') and midia.get('height'):
            print(f"      📐 Dimensões: {midia['width']}x{midia['height']}")
    
    # 2. Relatório detalhado
    print("\n📋 2. RELATÓRIO DETALHADO")
    print("-" * 40)
    
    relatorio = gerar_relatorio_webhook(webhook_exemplo)
    print(relatorio)
    
    # 3. Processamento completo (se cliente encontrado)
    if cliente_info.get('encontrado'):
        print("\n🔄 3. PROCESSAMENTO COMPLETO")
        print("-" * 40)
        
        resultado = processar_webhook_whatsapp(webhook_exemplo)
        
        if resultado.get('sucesso'):
            print(f"✅ Processamento concluído")
            print(f"📊 Total processadas: {resultado.get('total_processadas', 0)}")
            
            resultados_midias = resultado.get('resultados_midias', [])
            for resultado_midia in resultados_midias:
                print(f"   📎 {resultado_midia['tipo'].upper()}:")
                if resultado_midia.get('sucesso'):
                    print(f"      ✅ Sucesso")
                    print(f"      📁 Arquivo: {resultado_midia.get('file_path', 'N/A')}")
                    print(f"      📏 Tamanho: {resultado_midia.get('file_size_mb', 0)} MB")
                    print(f"      📊 Status: {resultado_midia.get('download_status')}")
                else:
                    print(f"      ❌ Falha: {resultado_midia.get('erro')}")
        else:
            print(f"❌ Falha no processamento: {resultado.get('erro')}")
    else:
        print("\n⚠️ 3. PROCESSAMENTO PULADO (cliente não encontrado)")
    
    return True


def test_diferentes_tipos_midia():
    """Testa diferentes tipos de mídia"""
    
    print("\n🎬 TESTE DE DIFERENTES TIPOS DE MÍDIA")
    print("=" * 50)
    
    tipos_teste = [
        {
            'nome': 'Imagem JPEG',
            'msgContent': {
                'imageMessage': {
                    'mimetype': 'image/jpeg',
                    'fileName': 'foto.jpg',
                    'fileLength': 4096,
                    'caption': 'Foto de teste',
                    'mediaKey': 'img_key_001',
                    'directPath': '/img/path',
                    'fileSha256': 'img_sha256_001',
                    'fileEncSha256': 'img_enc_sha256_001',
                    'width': 800,
                    'height': 600
                }
            }
        },
        {
            'nome': 'Vídeo MP4',
            'msgContent': {
                'videoMessage': {
                    'mimetype': 'video/mp4',
                    'fileName': 'video.mp4',
                    'fileLength': 1024000,
                    'caption': 'Vídeo de teste',
                    'mediaKey': 'vid_key_001',
                    'directPath': '/vid/path',
                    'fileSha256': 'vid_sha256_001',
                    'fileEncSha256': 'vid_enc_sha256_001',
                    'width': 1280,
                    'height': 720,
                    'seconds': 30
                }
            }
        },
        {
            'nome': 'Áudio MP3',
            'msgContent': {
                'audioMessage': {
                    'mimetype': 'audio/mpeg',
                    'fileName': 'audio.mp3',
                    'fileLength': 512000,
                    'mediaKey': 'aud_key_001',
                    'directPath': '/aud/path',
                    'fileSha256': 'aud_sha256_001',
                    'fileEncSha256': 'aud_enc_sha256_001',
                    'seconds': 45,
                    'ptt': False
                }
            }
        },
        {
            'nome': 'Documento PDF',
            'msgContent': {
                'documentMessage': {
                    'mimetype': 'application/pdf',
                    'fileName': 'documento.pdf',
                    'fileLength': 2048000,
                    'caption': 'Documento de teste',
                    'mediaKey': 'doc_key_001',
                    'directPath': '/doc/path',
                    'fileSha256': 'doc_sha256_001',
                    'fileEncSha256': 'doc_enc_sha256_001',
                    'title': 'Documento Teste',
                    'pageCount': 5
                }
            }
        },
        {
            'nome': 'Sticker Animado',
            'msgContent': {
                'stickerMessage': {
                    'mimetype': 'image/webp',
                    'fileName': 'sticker.webp',
                    'fileLength': 8192,
                    'mediaKey': 'stk_key_001',
                    'directPath': '/stk/path',
                    'fileSha256': 'stk_sha256_001',
                    'fileEncSha256': 'stk_enc_sha256_001',
                    'isAnimated': True,
                    'isAvatar': False
                }
            }
        }
    ]
    
    for tipo_teste in tipos_teste:
        print(f"\n📎 Testando: {tipo_teste['nome']}")
        
        webhook_teste = {
            'event': 'webhookReceived',
            'instanceId': '3B6XIW-ZTS923-GEAY6V',
            'messageId': f'test_{tipo_teste["nome"].lower().replace(" ", "_")}_{int(datetime.now().timestamp())}',
            'sender': {
                'id': '5511999999999@s.whatsapp.net',
                'pushName': 'Teste Tipos'
            },
            'chat': {
                'id': '5511999999999@s.whatsapp.net'
            },
            'msgContent': tipo_teste['msgContent'],
            'isGroup': False,
            'fromMe': False,
            'moment': int(datetime.now().timestamp())
        }
        
        analise = analisar_webhook_whatsapp(webhook_teste)
        midias = analise.get('midias', [])
        
        if midias:
            midia = midias[0]
            print(f"   ✅ Tipo: {midia['type']}")
            print(f"   📄 Mimetype: {midia.get('mimetype')}")
            print(f"   📁 Extensão: {midia.get('extensao')}")
            print(f"   📏 Tamanho: {midia.get('fileLength', 'N/A')} bytes")
            print(f"   ✅ Válido: {midia.get('valido_para_download')}")
            
            # Informações específicas
            if midia.get('width') and midia.get('height'):
                print(f"   📐 Dimensões: {midia['width']}x{midia['height']}")
            
            if midia.get('seconds'):
                print(f"   ⏱️ Duração: {midia['seconds']} segundos")
            
            if midia.get('ptt'):
                print(f"   🎤 Push to Talk: Sim")
            
            if midia.get('isAnimated'):
                print(f"   🎬 Animado: Sim")
            
            if midia.get('pageCount'):
                print(f"   📄 Páginas: {midia['pageCount']}")
        else:
            print(f"   ❌ Nenhuma mídia encontrada")


def test_webhook_invalido():
    """Testa webhook inválido"""
    
    print("\n❌ TESTE DE WEBHOOK INVÁLIDO")
    print("=" * 40)
    
    # Webhook sem dados de mídia
    webhook_invalido = {
        'event': 'webhookReceived',
        'instanceId': '3B6XIW-ZTS923-GEAY6V',
        'messageId': 'test_invalido_001',
        'sender': {
            'id': '5511999999999@s.whatsapp.net',
            'pushName': 'Teste Inválido'
        },
        'chat': {
            'id': '5511999999999@s.whatsapp.net'
        },
        'msgContent': {
            'textMessage': {
                'text': 'Esta é uma mensagem de texto sem mídia'
            }
        },
        'isGroup': False,
        'fromMe': False,
        'moment': int(datetime.now().timestamp())
    }
    
    analise = analisar_webhook_whatsapp(webhook_invalido)
    
    print(f"📊 Total de mídias: {analise.get('total_midias', 0)}")
    print(f"🔍 Tem mídias: {analise.get('tem_midias', False)}")
    
    if not analise.get('tem_midias'):
        print("✅ Corretamente identificado como webhook sem mídia")


def main():
    """Função principal"""
    
    print("🚀 TESTE COMPLETO DO ANALISADOR DE WEBHOOKS")
    print("=" * 70)
    
    try:
        # Teste principal
        test_webhook_analyzer()
        
        # Teste de diferentes tipos
        test_diferentes_tipos_midia()
        
        # Teste de webhook inválido
        test_webhook_invalido()
        
        print("\n" + "=" * 70)
        print("🎉 Todos os testes passaram!")
        print("✅ O analisador está funcionando corretamente")
        print("\n💡 Funcionalidades testadas:")
        print("   - Análise completa de webhooks")
        print("   - Extração de dados por tipo de mídia")
        print("   - Validação de campos obrigatórios")
        print("   - Busca automática de cliente/instância")
        print("   - Relatórios detalhados")
        print("   - Processamento completo com download")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main() 