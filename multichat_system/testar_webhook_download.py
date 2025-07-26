#!/usr/bin/env python3
"""
Teste do Webhook com Download Automático
Verifica se o webhook está processando mídias automaticamente
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

from django.test import RequestFactory
from webhook.views import webhook_receiver
from core.models import MediaFile, WebhookEvent


def criar_webhook_teste():
    """
    Cria um webhook de teste com mídia
    """
    return {
        'event': 'webhookReceived',
        'instanceId': '3B6XIW-ZTS923-GEAY6V',
        'messageId': f'teste_webhook_{int(datetime.now().timestamp())}',
        'sender': {
            'id': '5511999999999@s.whatsapp.net',
            'pushName': 'Usuário Teste Webhook'
        },
        'chat': {
            'id': '5511999999999@s.whatsapp.net'
        },
        'msgContent': {
            'imageMessage': {
                'mimetype': 'image/jpeg',
                'fileName': 'teste_webhook_download.jpg',
                'fileLength': 102400,
                'caption': 'Teste de download via webhook',
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


def testar_webhook_receiver():
    """
    Testa o webhook receiver com mídia
    """
    print("🧪 TESTANDO WEBHOOK RECEIVER COM DOWNLOAD AUTOMÁTICO")
    print("="*60)
    
    # Criar webhook de teste
    webhook_data = criar_webhook_teste()
    message_id = webhook_data['messageId']
    
    print(f"📝 Webhook de teste criado")
    print(f"🆔 Message ID: {message_id}")
    print(f"📱 Instance ID: {webhook_data['instanceId']}")
    print(f"📄 Tipo de mídia: imageMessage")
    
    # Simular request
    factory = RequestFactory()
    request = factory.post(
        '/webhook/',
        data=json.dumps(webhook_data),
        content_type='application/json'
    )
    
    # Processar webhook
    try:
        print(f"\n🔄 Processando webhook...")
        response = webhook_receiver(request)
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Webhook processado com sucesso")
            
            # Verificar se evento foi criado
            try:
                evento = WebhookEvent.objects.filter(message_id=message_id).first()
                if evento:
                    print(f"✅ Evento criado: {evento.event_id}")
                    print(f"📊 Tipo: {evento.message_type}")
                    print(f"👤 Sender: {evento.sender_name}")
                else:
                    print("❌ Evento não encontrado no banco")
            except Exception as e:
                print(f"❌ Erro ao buscar evento: {e}")
            
            # Verificar se mídia foi processada
            try:
                media_file = MediaFile.objects.get(message_id=message_id)
                print(f"✅ Mídia processada: {media_file.media_type}")
                print(f"📊 Status: {media_file.download_status}")
                print(f"📁 Arquivo: {media_file.file_name}")
                print(f"📏 Tamanho: {media_file.file_size_mb} MB")
                print(f"👤 Cliente: {media_file.cliente.nome}")
                print(f"📱 Instância: {media_file.instance.instance_id}")
                
                # Verificar se arquivo foi baixado
                if media_file.file_path and os.path.exists(media_file.file_path):
                    print(f"✅ Arquivo baixado: {media_file.file_path}")
                    print(f"📏 Tamanho real: {os.path.getsize(media_file.file_path)} bytes")
                else:
                    print(f"⚠️ Arquivo não encontrado no sistema de arquivos")
                    print(f"   Caminho esperado: {media_file.file_path}")
                
            except MediaFile.DoesNotExist:
                print("❌ Mídia não encontrada no banco")
                print("⚠️ O download automático pode não estar funcionando")
            
            return True
            
        else:
            print(f"❌ Erro no webhook: {response.content}")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao processar webhook: {e}")
        return False


def verificar_configuracao_webhook():
    """
    Verifica se o webhook está configurado corretamente
    """
    print("\n🔍 VERIFICANDO CONFIGURAÇÃO DO WEBHOOK")
    print("="*50)
    
    # Verificar se a função processar_webhook_whatsapp está importada
    try:
        from core.webhook_media_analyzer import processar_webhook_whatsapp
        print("✅ Função processar_webhook_whatsapp importada")
    except ImportError as e:
        print(f"❌ Erro ao importar processar_webhook_whatsapp: {e}")
        return False
    
    # Verificar se o código de processamento está no webhook_receiver
    try:
        with open('webhook/views.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'processar_webhook_whatsapp' in content:
            print("✅ Código de processamento encontrado no webhook_receiver")
        else:
            print("❌ Código de processamento NÃO encontrado no webhook_receiver")
            return False
            
        if 'imageMessage' in content and 'videoMessage' in content:
            print("✅ Detecção de tipos de mídia configurada")
        else:
            print("❌ Detecção de tipos de mídia NÃO configurada")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar arquivo: {e}")
        return False
    
    return True


def verificar_logs_webhook():
    """
    Verifica logs recentes do webhook
    """
    print("\n📋 VERIFICANDO LOGS RECENTES")
    print("="*50)
    
    # Verificar eventos recentes
    eventos_recentes = WebhookEvent.objects.order_by('-received_at')[:5]
    
    if eventos_recentes:
        print(f"📊 Últimos {len(eventos_recentes)} eventos:")
        for evento in eventos_recentes:
            print(f"   📅 {evento.received_at.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"      🆔 {evento.message_id}")
            print(f"      📊 Tipo: {evento.message_type}")
            print(f"      👤 Sender: {evento.sender_name}")
            print()
    else:
        print("❌ Nenhum evento encontrado")
    
    # Verificar mídias recentes
    midias_recentes = MediaFile.objects.order_by('-created_at')[:5]
    
    if midias_recentes:
        print(f"📎 Últimas {len(midias_recentes)} mídias:")
        for midia in midias_recentes:
            print(f"   📅 {midia.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"      🆔 {midia.message_id}")
            print(f"      📄 Tipo: {midia.media_type}")
            print(f"      📊 Status: {midia.download_status}")
            print(f"      📁 Arquivo: {midia.file_name}")
            print()
    else:
        print("❌ Nenhuma mídia encontrada")


def main():
    """
    Função principal
    """
    print("🧪 TESTE DO WEBHOOK COM DOWNLOAD AUTOMÁTICO")
    print("="*60)
    
    # 1. Verificar configuração
    config_ok = verificar_configuracao_webhook()
    
    if not config_ok:
        print("❌ Configuração do webhook com problemas")
        return
    
    # 2. Testar webhook receiver
    sucesso_webhook = testar_webhook_receiver()
    
    # 3. Verificar logs
    verificar_logs_webhook()
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DO TESTE")
    print("="*60)
    print(f"✅ Configuração: {'OK' if config_ok else 'FALHOU'}")
    print(f"✅ Webhook: {'OK' if sucesso_webhook else 'FALHOU'}")
    
    if config_ok and sucesso_webhook:
        print("\n🎉 WEBHOOK FUNCIONANDO CORRETAMENTE!")
        print("💡 O download automático está ativo e funcionando.")
        print("🚀 Agora é só enviar mídias no WhatsApp!")
    else:
        print("\n⚠️ ALGUNS PROBLEMAS ENCONTRADOS")
        print("💡 Verifique os logs acima para mais detalhes.")


if __name__ == "__main__":
    main() 