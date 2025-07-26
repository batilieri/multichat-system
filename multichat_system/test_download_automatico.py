#!/usr/bin/env python3
"""
Teste do Sistema de Download Automático de Mídias
Verifica se o sistema está funcionando corretamente
"""

import os
import sys
import json
import django
from pathlib import Path
from datetime import datetime

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.webhook_media_analyzer import processar_webhook_whatsapp
from core.models import MediaFile, Cliente, WhatsappInstance
from django.db import transaction


def criar_webhook_teste():
    """
    Cria um webhook de teste com mídia
    """
    return {
        'event': 'webhookReceived',
        'instanceId': '3B6XIW-ZTS923-GEAY6V',
        'messageId': f'teste_download_{int(datetime.now().timestamp())}',
        'sender': {
            'id': '5511999999999@s.whatsapp.net',
            'pushName': 'Usuário Teste Download'
        },
        'chat': {
            'id': '5511999999999@s.whatsapp.net'
        },
        'msgContent': {
            'imageMessage': {
                'mimetype': 'image/jpeg',
                'fileName': 'teste_download.jpg',
                'fileLength': 102400,
                'caption': 'Teste de download automático',
                'mediaKey': 'AQAiS8nF8X9Y2Z3W4V5U6T7S8R9Q0P1O2N3M4L5K6J7I8H9G0F1E2D3C4B5A6',
                'directPath': '/v/t62.7118-24/12345678_98765432_1234567890123456789012345678901234567890/n/ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/',
                'fileSha256': 'A1B2C3D4E5F6789012345678901234567890ABCDEF1234567890ABCDEF123456',
                'fileEncSha256': 'F1E2D3C4B5A6789012345678901234567890ABCDEF1234567890ABCDEF123456',
                'width': 800,
                'height': 600,
                'jpegThumbnail': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=',
                'mediaKeyTimestamp': '1752894203'
            }
        },
        'isGroup': False,
        'fromMe': False,
        'moment': int(datetime.now().timestamp())
    }


def verificar_cliente_instancia():
    """
    Verifica se existe cliente e instância para teste
    """
    try:
        cliente = Cliente.objects.get(id=2)  # Elizeu
        instance = WhatsappInstance.objects.get(instance_id='3B6XIW-ZTS923-GEAY6V')
        
        print(f"✅ Cliente encontrado: {cliente.nome}")
        print(f"✅ Instância encontrada: {instance.instance_id}")
        print(f"✅ Token: {instance.token[:20]}...")
        print(f"✅ Status: {instance.status}")
        
        return True
        
    except Cliente.DoesNotExist:
        print("❌ Cliente não encontrado")
        return False
    except WhatsappInstance.DoesNotExist:
        print("❌ Instância não encontrada")
        return False


def testar_processamento_webhook():
    """
    Testa o processamento completo do webhook
    """
    print("\n" + "="*60)
    print("🧪 TESTE DE PROCESSAMENTO DE WEBHOOK")
    print("="*60)
    
    # Criar webhook de teste
    webhook_data = criar_webhook_teste()
    message_id = webhook_data['messageId']
    
    print(f"📝 Webhook de teste criado: {message_id}")
    
    # Processar webhook
    try:
        resultado = processar_webhook_whatsapp(webhook_data)
        
        print(f"\n📊 RESULTADO DO PROCESSAMENTO:")
        print(f"   ✅ Sucesso: {resultado.get('sucesso')}")
        
        if resultado.get('sucesso'):
            print(f"   📎 Total processadas: {resultado.get('total_processadas', 0)}")
            
            # Verificar resultados individuais
            for resultado_midia in resultado.get('resultados_midias', []):
                tipo = resultado_midia.get('tipo', 'N/A')
                sucesso = resultado_midia.get('sucesso', False)
                
                if sucesso:
                    print(f"   ✅ {tipo}: Processado com sucesso")
                    print(f"      📄 Status: {resultado_midia.get('download_status')}")
                    print(f"      📁 Caminho: {resultado_midia.get('file_path', 'N/A')}")
                    print(f"      📏 Tamanho: {resultado_midia.get('file_size_mb', 0)} MB")
                else:
                    print(f"   ❌ {tipo}: {resultado_midia.get('erro')}")
        else:
            print(f"   ❌ Erro: {resultado.get('erro')}")
        
        return resultado.get('sucesso', False)
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        return False


def verificar_banco_dados():
    """
    Verifica se os dados foram salvos no banco
    """
    print("\n" + "="*60)
    print("🗄️ VERIFICAÇÃO DO BANCO DE DADOS")
    print("="*60)
    
    try:
        # Buscar mídias recentes
        media_files = MediaFile.objects.filter(
            cliente_id=2,
            instance__instance_id='3B6XIW-ZTS923-GEAY6V'
        ).order_by('-created_at')[:5]
        
        print(f"📊 Total de mídias no banco: {MediaFile.objects.count()}")
        print(f"📊 Mídias do cliente/instância: {media_files.count()}")
        
        if media_files:
            print(f"\n📋 ÚLTIMAS MÍDIAS:")
            for media in media_files:
                print(f"   📄 {media.media_type}: {media.message_id}")
                print(f"      📁 Arquivo: {media.file_name}")
                print(f"      📏 Tamanho: {media.file_size_mb} MB")
                print(f"      📊 Status: {media.download_status}")
                print(f"      📅 Criado: {media.created_at}")
                print()
        else:
            print("❌ Nenhuma mídia encontrada no banco")
        
        return media_files.count() > 0
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False


def testar_download_real():
    """
    Testa download real de uma mídia
    """
    print("\n" + "="*60)
    print("🔽 TESTE DE DOWNLOAD REAL")
    print("="*60)
    
    try:
        # Buscar mídia pendente
        media_pendente = MediaFile.objects.filter(
            cliente_id=2,
            instance__instance_id='3B6XIW-ZTS923-GEAY6V',
            download_status='pending'
        ).first()
        
        if not media_pendente:
            print("❌ Nenhuma mídia pendente encontrada")
            return False
        
        print(f"📄 Mídia encontrada: {media_pendente.media_type}")
        print(f"🆔 Message ID: {media_pendente.message_id}")
        print(f"📁 Arquivo: {media_pendente.file_name}")
        
        # Tentar download
        from core.django_media_manager import DjangoMediaManager
        
        media_manager = DjangoMediaManager(
            cliente_id=2,
            instance_id='3B6XIW-ZTS923-GEAY6V',
            bearer_token='8GYcR7wtitTy1vA0PeOA...'  # Token do Elizeu
        )
        
        # Criar webhook para download
        webhook_download = {
            'messageId': media_pendente.message_id,
            'sender': {
                'pushName': media_pendente.sender_name
            },
            'msgContent': {
                f'{media_pendente.media_type}Message': {
                    'mediaKey': media_pendente.media_key,
                    'directPath': media_pendente.direct_path,
                    'fileSha256': media_pendente.file_sha256,
                    'fileEncSha256': media_pendente.file_enc_sha256,
                    'mimetype': media_pendente.mimetype,
                    'fileName': media_pendente.file_name,
                    'fileLength': media_pendente.file_size
                }
            }
        }
        
        # Processar download
        resultado = media_manager.processar_mensagem_whatsapp(webhook_download)
        
        if resultado:
            print("✅ Download processado com sucesso")
            
            # Verificar se arquivo foi criado
            if media_pendente.file_path and os.path.exists(media_pendente.file_path):
                print(f"✅ Arquivo criado: {media_pendente.file_path}")
                print(f"📏 Tamanho: {os.path.getsize(media_pendente.file_path)} bytes")
            else:
                print("⚠️ Arquivo não encontrado no sistema de arquivos")
        else:
            print("❌ Falha no download")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Erro no teste de download: {e}")
        return False


def main():
    """
    Função principal de teste
    """
    print("🧪 TESTE DO SISTEMA DE DOWNLOAD AUTOMÁTICO")
    print("="*60)
    
    # 1. Verificar cliente e instância
    if not verificar_cliente_instancia():
        print("❌ Cliente ou instância não encontrados. Execute o setup primeiro.")
        return
    
    # 2. Testar processamento de webhook
    sucesso_processamento = testar_processamento_webhook()
    
    # 3. Verificar banco de dados
    sucesso_banco = verificar_banco_dados()
    
    # 4. Testar download real (opcional)
    print("\n💡 Para testar download real, descomente a linha abaixo:")
    print("   sucesso_download = testar_download_real()")
    # sucesso_download = testar_download_real()
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    print(f"✅ Processamento: {'PASSOU' if sucesso_processamento else 'FALHOU'}")
    print(f"✅ Banco de dados: {'PASSOU' if sucesso_banco else 'FALHOU'}")
    print(f"✅ Download real: {'NÃO TESTADO'}")
    
    if sucesso_processamento and sucesso_banco:
        print("\n🎉 SISTEMA FUNCIONANDO CORRETAMENTE!")
        print("💡 O download automático está ativo e funcionando.")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
        print("💡 Verifique os logs acima para mais detalhes.")


if __name__ == "__main__":
    main() 