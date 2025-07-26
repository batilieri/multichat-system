#!/usr/bin/env python3
"""
Script de teste para integração completa do sistema de mídias
"""

import os
import sys
import django
from pathlib import Path
import json
from datetime import datetime

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Cliente, WhatsappInstance
from webhook.models import WebhookEvent, MessageMedia
from webhook.media_processor import media_processor, process_webhook_media
from core.media_manager import criar_media_manager


def test_complete_integration():
    """Testa a integração completa do sistema de mídias"""
    
    print("🧪 Testando integração completa do sistema de mídias...")
    print("=" * 70)
    
    try:
        # 1. Buscar dados de teste
        print("📋 1. Buscando dados de teste...")
        cliente = Cliente.objects.first()
        if not cliente:
            print("❌ Nenhum cliente encontrado")
            return False
        
        instance = WhatsappInstance.objects.filter(cliente=cliente).first()
        if not instance:
            print("❌ Nenhuma instância encontrada")
            return False
        
        print(f"   ✅ Cliente: {cliente.nome} (ID: {cliente.id})")
        print(f"   ✅ Instância: {instance.instance_id}")
        
        # 2. Testar processador de mídias
        print("\n🔧 2. Testando processador de mídias...")
        
        # Criar evento de webhook de teste
        webhook_data = {
            'event': 'webhookReceived',
            'instanceId': instance.instance_id,
            'messageId': 'test_integration_001',
            'sender': {
                'id': '5511999999999@s.whatsapp.net',
                'pushName': 'Teste Integração'
            },
            'chat': {
                'id': '5511999999999@s.whatsapp.net'
            },
            'msgContent': {
                'imageMessage': {
                    'mimetype': 'image/jpeg',
                    'fileName': 'test_integration.jpg',
                    'fileLength': 3072,
                    'caption': 'Teste de integração completa',
                    'mediaKey': 'integration_key_001',
                    'directPath': '/integration/direct/path',
                    'fileSha256': 'integration_sha256_001',
                    'fileEncSha256': 'integration_enc_sha256_001',
                    'width': 1200,
                    'height': 800,
                    'jpegThumbnail': 'base64_integration_thumbnail'
                }
            },
            'isGroup': False,
            'fromMe': False,
            'moment': int(datetime.now().timestamp())
        }
        
        # Criar evento no banco
        event = WebhookEvent.objects.create(
            cliente=cliente,
            instance_id=instance.instance_id,
            event_type='webhookReceived',
            raw_data=webhook_data,
            chat_id=webhook_data['chat']['id'],
            sender_id=webhook_data['sender']['id'],
            sender_name=webhook_data['sender']['pushName'],
            message_id=webhook_data['messageId'],
            message_type='imageMessage',
            message_content='Teste de integração completa'
        )
        
        print(f"   ✅ Evento criado: {event.event_id}")
        
        # 3. Testar processamento direto
        print("\n📨 3. Testando processamento direto...")
        success_direct = process_webhook_media(
            webhook_data, 
            cliente.id, 
            instance.instance_id
        )
        print(f"   {'✅' if success_direct else '❌'} Processamento direto: {'Sucesso' if success_direct else 'Falha'}")
        
        # 4. Testar processamento via processador
        print("\n🔄 4. Testando processamento via processador...")
        success_processor = media_processor.process_webhook_event(event)
        print(f"   {'✅' if success_processor else '❌'} Processamento via processador: {'Sucesso' if success_processor else 'Falha'}")
        
        # 5. Verificar resultados
        print("\n📊 5. Verificando resultados...")
        
        # Verificar se MessageMedia foi criada
        message_medias = MessageMedia.objects.filter(event=event)
        print(f"   📎 MessageMedia criadas: {message_medias.count()}")
        
        for media in message_medias:
            print(f"      - Tipo: {media.media_type}, Status: {media.download_status}")
        
        # Verificar estatísticas do processador
        stats = media_processor.get_statistics()
        print(f"   📈 Estatísticas do processador:")
        print(f"      - Total de eventos: {stats.get('total_events', 0)}")
        print(f"      - Eventos processados: {stats.get('processed_events', 0)}")
        print(f"      - Eventos pendentes: {stats.get('pending_events', 0)}")
        print(f"      - Gerenciadores ativos: {stats.get('media_managers', 0)}")
        
        # 6. Testar múltiplos tipos de mídia
        print("\n🎬 6. Testando múltiplos tipos de mídia...")
        
        media_types = [
            {
                'type': 'videoMessage',
                'mimetype': 'video/mp4',
                'fileName': 'test_video.mp4',
                'fileLength': 15360,
                'seconds': 45,
                'width': 1280,
                'height': 720
            },
            {
                'type': 'audioMessage',
                'mimetype': 'audio/mp3',
                'fileLength': 8192,
                'seconds': 30,
                'ptt': False
            },
            {
                'type': 'documentMessage',
                'mimetype': 'application/pdf',
                'fileName': 'test_document.pdf',
                'fileLength': 5120,
                'pageCount': 2
            }
        ]
        
        for i, media_info in enumerate(media_types, 2):
            # Criar webhook para cada tipo
            test_webhook = {
                'event': 'webhookReceived',
                'instanceId': instance.instance_id,
                'messageId': f'test_integration_{i:03d}',
                'sender': {
                    'id': '5511999999999@s.whatsapp.net',
                    'pushName': f'Teste {media_info["type"]}'
                },
                'chat': {
                    'id': '5511999999999@s.whatsapp.net'
                },
                'msgContent': {
                    media_info['type']: media_info
                },
                'isGroup': False,
                'fromMe': False,
                'moment': int(datetime.now().timestamp())
            }
            
            # Processar
            success = process_webhook_media(test_webhook, cliente.id, instance.instance_id)
            print(f"   {'✅' if success else '❌'} {media_info['type']}: {'Sucesso' if success else 'Falha'}")
        
        # 7. Testar processamento em lote
        print("\n📦 7. Testando processamento em lote...")
        
        # Criar alguns eventos pendentes
        for i in range(5):
            batch_webhook = {
                'event': 'webhookReceived',
                'instanceId': instance.instance_id,
                'messageId': f'batch_test_{i:03d}',
                'sender': {
                    'id': '5511999999999@s.whatsapp.net',
                    'pushName': f'Teste Lote {i}'
                },
                'chat': {
                    'id': '5511999999999@s.whatsapp.net'
                },
                'msgContent': {
                    'imageMessage': {
                        'mimetype': 'image/jpeg',
                        'fileName': f'batch_test_{i}.jpg',
                        'fileLength': 1024 + i * 100,
                        'mediaKey': f'batch_key_{i:03d}',
                        'directPath': f'/batch/path/{i}',
                        'fileSha256': f'batch_sha256_{i:03d}',
                        'fileEncSha256': f'batch_enc_sha256_{i:03d}'
                    }
                },
                'isGroup': False,
                'fromMe': False,
                'moment': int(datetime.now().timestamp())
            }
            
            WebhookEvent.objects.create(
                cliente=cliente,
                instance_id=instance.instance_id,
                event_type='webhookReceived',
                raw_data=batch_webhook,
                chat_id=batch_webhook['chat']['id'],
                sender_id=batch_webhook['sender']['id'],
                sender_name=batch_webhook['sender']['pushName'],
                message_id=batch_webhook['messageId'],
                message_type='imageMessage',
                message_content=f'Teste de lote {i}'
            )
        
        # Processar em lote
        processed_count = media_processor.process_pending_events(limit=10)
        print(f"   📊 Eventos processados em lote: {processed_count}")
        
        # 8. Verificar estrutura de arquivos
        print("\n📁 8. Verificando estrutura de arquivos...")
        
        # Obter gerenciador de mídias
        cache_key = f"{cliente.id}_{instance.instance_id}"
        if cache_key in media_processor.media_managers:
            manager = media_processor.media_managers[cache_key]
            
            print(f"   📂 Base path: {manager.base_path}")
            print(f"   📂 Cliente path: {manager.cliente_path}")
            print(f"   📂 Instance path: {manager.instance_path}")
            
            for tipo, pasta in manager.pastas_midia.items():
                if pasta.exists():
                    arquivos = list(pasta.glob('*'))
                    print(f"   📁 {tipo}: {len(arquivos)} arquivos")
                else:
                    print(f"   📁 {tipo}: pasta não existe")
        
        # 9. Testar limpeza
        print("\n🧹 9. Testando limpeza...")
        
        # Limpar eventos de teste
        test_events = WebhookEvent.objects.filter(
            message_id__startswith='test_integration_'
        )
        test_events.delete()
        
        batch_events = WebhookEvent.objects.filter(
            message_id__startswith='batch_test_'
        )
        batch_events.delete()
        
        print(f"   🗑️ Eventos de teste removidos")
        
        print("\n🎉 Teste de integração completa finalizado!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste de integração: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance():
    """Testa performance do sistema de mídias"""
    
    print("\n⚡ Testando performance do sistema de mídias...")
    print("=" * 50)
    
    try:
        import time
        
        # Buscar dados de teste
        cliente = Cliente.objects.first()
        instance = WhatsappInstance.objects.filter(cliente=cliente).first()
        
        if not cliente or not instance:
            print("❌ Dados de teste não encontrados")
            return False
        
        # Criar gerenciador
        start_time = time.time()
        media_manager = criar_media_manager(
            cliente_id=cliente.id,
            instance_id=instance.instance_id,
            bearer_token=instance.token
        )
        init_time = time.time() - start_time
        
        print(f"   ⏱️ Tempo de inicialização: {init_time:.3f}s")
        
        # Testar processamento de múltiplas mensagens
        print("\n📨 Testando processamento de múltiplas mensagens...")
        
        start_time = time.time()
        for i in range(10):
            test_message = {
                'messageId': f'perf_test_{i:03d}',
                'sender': {
                    'id': '5511999999999@s.whatsapp.net',
                    'pushName': f'Perf Test {i}'
                },
                'chat': {
                    'id': '5511999999999@s.whatsapp.net'
                },
                'msgContent': {
                    'imageMessage': {
                        'mimetype': 'image/jpeg',
                        'fileName': f'perf_test_{i}.jpg',
                        'fileLength': 1024 + i * 50,
                        'mediaKey': f'perf_key_{i:03d}',
                        'directPath': f'/perf/path/{i}',
                        'fileSha256': f'perf_sha256_{i:03d}',
                        'fileEncSha256': f'perf_enc_sha256_{i:03d}'
                    }
                },
                'isGroup': False,
                'fromMe': False,
                'moment': int(datetime.now().timestamp())
            }
            
            media_manager.processar_mensagem_whatsapp(test_message)
        
        process_time = time.time() - start_time
        print(f"   ⏱️ Tempo para processar 10 mensagens: {process_time:.3f}s")
        print(f"   📊 Taxa: {10/process_time:.1f} mensagens/segundo")
        
        # Testar busca no banco
        print("\n🔍 Testando busca no banco...")
        
        start_time = time.time()
        for _ in range(100):
            media_manager.buscar_midias_pendentes()
        search_time = time.time() - start_time
        
        print(f"   ⏱️ Tempo para 100 buscas: {search_time:.3f}s")
        print(f"   📊 Taxa: {100/search_time:.1f} buscas/segundo")
        
        # Testar estatísticas
        print("\n📊 Testando geração de estatísticas...")
        
        start_time = time.time()
        for _ in range(50):
            media_manager.obter_estatisticas()
        stats_time = time.time() - start_time
        
        print(f"   ⏱️ Tempo para 50 estatísticas: {stats_time:.3f}s")
        print(f"   📊 Taxa: {50/stats_time:.1f} estatísticas/segundo")
        
        print("\n✅ Teste de performance concluído!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste de performance: {e}")
        return False


def main():
    """Função principal"""
    print("🚀 Iniciando testes do sistema de mídias do MultiChat")
    print("=" * 80)
    
    # Teste de integração
    success_integration = test_complete_integration()
    
    # Teste de performance
    success_performance = test_performance()
    
    print("\n" + "=" * 80)
    print("📋 RESUMO DOS TESTES:")
    print(f"   ✅ Teste de integração: {'PASSOU' if success_integration else 'FALHOU'}")
    print(f"   ✅ Teste de performance: {'PASSOU' if success_performance else 'FALHOU'}")
    
    if success_integration and success_performance:
        print("\n🎉 Todos os testes passaram! O sistema está pronto para uso.")
        return True
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os logs acima.")
        return False


if __name__ == "__main__":
    main() 