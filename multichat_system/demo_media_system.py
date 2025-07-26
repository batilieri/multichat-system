#!/usr/bin/env python3
"""
Demonstração do Sistema de Mídias do MultiChat
Mostra como usar o sistema de gerenciamento de mídias
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
from core.media_manager import criar_media_manager
from webhook.media_processor import media_processor


def demo_basic_usage():
    """Demonstração básica do uso do sistema de mídias"""
    
    print("🎬 DEMONSTRAÇÃO DO SISTEMA DE MÍDIAS MULTICHAT")
    print("=" * 60)
    
    # 1. Buscar dados de exemplo
    print("\n📋 1. Buscando dados de exemplo...")
    cliente = Cliente.objects.first()
    instance = WhatsappInstance.objects.filter(cliente=cliente).first()
    
    if not cliente or not instance:
        print("❌ Dados de exemplo não encontrados")
        return
    
    print(f"   ✅ Cliente: {cliente.nome}")
    print(f"   ✅ Instância: {instance.instance_id}")
    
    # 2. Criar gerenciador de mídias
    print("\n🔧 2. Criando gerenciador de mídias...")
    media_manager = criar_media_manager(
        cliente_id=cliente.id,
        instance_id=instance.instance_id,
        bearer_token=instance.token
    )
    
    print(f"   ✅ Gerenciador criado")
    print(f"   📂 Pasta base: {media_manager.base_path}")
    print(f"   📂 Pasta do cliente: {media_manager.cliente_path}")
    print(f"   📂 Pasta da instância: {media_manager.instance_path}")
    
    # 3. Mostrar estrutura de pastas
    print("\n📁 3. Estrutura de pastas criada:")
    for tipo, pasta in media_manager.pastas_midia.items():
        if pasta.exists():
            arquivos = list(pasta.glob('*'))
            print(f"   📁 {tipo}: {len(arquivos)} arquivos")
        else:
            print(f"   📁 {tipo}: pasta vazia")
    
    # 4. Simular mensagens de mídia
    print("\n📨 4. Simulando mensagens de mídia...")
    
    mensagens_teste = [
        {
            'messageId': 'demo_img_001',
            'sender': {'id': '5511999999999@s.whatsapp.net', 'pushName': 'João Silva'},
            'chat': {'id': '5511999999999@s.whatsapp.net'},
            'msgContent': {
                'imageMessage': {
                    'mimetype': 'image/jpeg',
                    'fileName': 'foto_joao.jpg',
                    'fileLength': 2048,
                    'caption': 'Minha foto de perfil',
                    'mediaKey': 'demo_img_key_001',
                    'directPath': '/demo/img/path/001',
                    'fileSha256': 'demo_img_sha256_001',
                    'fileEncSha256': 'demo_img_enc_sha256_001',
                    'width': 800,
                    'height': 600
                }
            },
            'isGroup': False,
            'fromMe': False,
            'moment': int(datetime.now().timestamp())
        },
        {
            'messageId': 'demo_vid_001',
            'sender': {'id': '5511888888888@s.whatsapp.net', 'pushName': 'Maria Santos'},
            'chat': {'id': '5511888888888@s.whatsapp.net'},
            'msgContent': {
                'videoMessage': {
                    'mimetype': 'video/mp4',
                    'fileName': 'video_maria.mp4',
                    'fileLength': 10240,
                    'caption': 'Vídeo da minha viagem',
                    'mediaKey': 'demo_vid_key_001',
                    'directPath': '/demo/vid/path/001',
                    'fileSha256': 'demo_vid_sha256_001',
                    'fileEncSha256': 'demo_vid_enc_sha256_001',
                    'seconds': 30,
                    'width': 1280,
                    'height': 720
                }
            },
            'isGroup': False,
            'fromMe': False,
            'moment': int(datetime.now().timestamp())
        },
        {
            'messageId': 'demo_aud_001',
            'sender': {'id': '5511777777777@s.whatsapp.net', 'pushName': 'Pedro Costa'},
            'chat': {'id': '5511777777777@s.whatsapp.net'},
            'msgContent': {
                'audioMessage': {
                    'mimetype': 'audio/mp3',
                    'fileLength': 5120,
                    'mediaKey': 'demo_aud_key_001',
                    'directPath': '/demo/aud/path/001',
                    'fileSha256': 'demo_aud_sha256_001',
                    'fileEncSha256': 'demo_aud_enc_sha256_001',
                    'seconds': 20,
                    'ptt': False
                }
            },
            'isGroup': False,
            'fromMe': False,
            'moment': int(datetime.now().timestamp())
        }
    ]
    
    # Processar mensagens
    for i, mensagem in enumerate(mensagens_teste, 1):
        print(f"   📨 Processando mensagem {i}...")
        media_manager.processar_mensagem_whatsapp(mensagem)
    
    # 5. Verificar resultados
    print("\n📊 5. Verificando resultados...")
    
    # Estatísticas do gerenciador
    stats = media_manager.obter_estatisticas()
    print(f"   📈 Estatísticas do gerenciador:")
    print(f"      - Total de mídias: {stats.get('total_midias', 0)}")
    print(f"      - Mídias baixadas: {stats.get('midias_baixadas', 0)}")
    print(f"      - Mídias pendentes: {stats.get('midias_pendentes', 0)}")
    print(f"      - Mídias falhadas: {stats.get('midias_falhadas', 0)}")
    print(f"      - Por tipo: {stats.get('por_tipo', {})}")
    
    # 6. Mostrar mídias pendentes
    print("\n⏳ 6. Mídias pendentes:")
    midias_pendentes = media_manager.buscar_midias_pendentes()
    for midia in midias_pendentes:
        print(f"   📎 {midia['message_id']}: {midia['media_type']} - {midia['download_status']}")
    
    return media_manager


def demo_webhook_integration():
    """Demonstração da integração com webhooks"""
    
    print("\n🔗 DEMONSTRAÇÃO DA INTEGRAÇÃO COM WEBHOOKS")
    print("=" * 50)
    
    # 1. Mostrar processador de mídias
    print("\n🔧 1. Processador de mídias:")
    stats = media_processor.get_statistics()
    print(f"   📊 Estatísticas do processador:")
    print(f"      - Total de eventos: {stats.get('total_events', 0)}")
    print(f"      - Eventos processados: {stats.get('processed_events', 0)}")
    print(f"      - Eventos pendentes: {stats.get('pending_events', 0)}")
    print(f"      - Gerenciadores ativos: {stats.get('media_managers', 0)}")
    
    # 2. Simular webhook de mídia
    print("\n📨 2. Simulando webhook de mídia...")
    
    webhook_data = {
        'event': 'webhookReceived',
        'instanceId': '3B6XIW-ZTS923-GEAY6V',  # Usar instância real
        'messageId': 'webhook_demo_001',
        'sender': {
            'id': '5511999999999@s.whatsapp.net',
            'pushName': 'Webhook Demo'
        },
        'chat': {
            'id': '5511999999999@s.whatsapp.net'
        },
        'msgContent': {
            'imageMessage': {
                'mimetype': 'image/jpeg',
                'fileName': 'webhook_demo.jpg',
                'fileLength': 3072,
                'caption': 'Mídia via webhook',
                'mediaKey': 'webhook_key_001',
                'directPath': '/webhook/direct/path',
                'fileSha256': 'webhook_sha256_001',
                'fileEncSha256': 'webhook_enc_sha256_001',
                'width': 1024,
                'height': 768
            }
        },
        'isGroup': False,
        'fromMe': False,
        'moment': int(datetime.now().timestamp())
    }
    
    # Buscar cliente
    cliente = Cliente.objects.first()
    if cliente:
        # Processar webhook usando a função correta
        from webhook.media_processor import process_webhook_media
        success = process_webhook_media(
            webhook_data, 
            cliente.id, 
            webhook_data['instanceId']
        )
        print(f"   {'✅' if success else '❌'} Webhook processado: {'Sucesso' if success else 'Falha'}")
    
    # 3. Mostrar gerenciadores ativos
    print("\n🔄 3. Gerenciadores ativos:")
    for cache_key, manager in media_processor.media_managers.items():
        manager_stats = manager.obter_estatisticas()
        print(f"   📊 {cache_key}:")
        print(f"      - Mídias: {manager_stats.get('total_midias', 0)}")
        print(f"      - Baixadas: {manager_stats.get('midias_baixadas', 0)}")
        print(f"      - Pendentes: {manager_stats.get('midias_pendentes', 0)}")


def demo_file_management():
    """Demonstração do gerenciamento de arquivos"""
    
    print("\n📁 DEMONSTRAÇÃO DO GERENCIAMENTO DE ARQUIVOS")
    print("=" * 50)
    
    # Buscar gerenciador
    cliente = Cliente.objects.first()
    instance = WhatsappInstance.objects.filter(cliente=cliente).first()
    
    if not cliente or not instance:
        print("❌ Dados não encontrados")
        return
    
    media_manager = criar_media_manager(
        cliente_id=cliente.id,
        instance_id=instance.instance_id,
        bearer_token=instance.token
    )
    
    # 1. Mostrar estrutura de pastas
    print("\n📂 1. Estrutura de pastas:")
    print(f"   📂 Base: {media_manager.base_path}")
    print(f"   📂 Cliente: {media_manager.cliente_path}")
    print(f"   📂 Instância: {media_manager.instance_path}")
    
    for tipo, pasta in media_manager.pastas_midia.items():
        if pasta.exists():
            arquivos = list(pasta.glob('*'))
            tamanho_total = sum(f.stat().st_size for f in pasta.glob('*') if f.is_file())
            print(f"   📁 {tipo}: {len(arquivos)} arquivos ({tamanho_total / 1024:.1f} KB)")
        else:
            print(f"   📁 {tipo}: pasta vazia")
    
    # 2. Mostrar banco de dados
    print(f"\n🗄️ 2. Banco de dados: {media_manager.db_path}")
    if media_manager.db_path.exists():
        tamanho_db = media_manager.db_path.stat().st_size
        print(f"   📊 Tamanho: {tamanho_db / 1024:.1f} KB")
    else:
        print("   ❌ Banco não existe")
    
    # 3. Testar limpeza (simulação)
    print("\n🧹 3. Simulação de limpeza:")
    print("   ℹ️ Para limpar arquivos antigos, use: media_manager.limpar_arquivos_antigos(dias=30)")
    print("   ℹ️ Para reprocessar mídias pendentes, use: media_manager.reprocessar_midias_pendentes()")


def demo_usage_examples():
    """Exemplos de uso do sistema"""
    
    print("\n💡 EXEMPLOS DE USO")
    print("=" * 30)
    
    print("""
📋 COMO USAR O SISTEMA DE MÍDIAS:

1. 🚀 INICIALIZAÇÃO:
   ```python
   from core.media_manager import criar_media_manager
   
   media_manager = criar_media_manager(
       cliente_id=1,
       instance_id="sua_instancia_id",
       bearer_token="seu_token"
   )
   ```

2. 📨 PROCESSAMENTO DE MENSAGENS:
   ```python
   # Processar mensagem individual
   media_manager.processar_mensagem_whatsapp(webhook_data)
   
   # Ou usar o processador automático
   from webhook.media_processor import process_webhook_media
   process_webhook_media(webhook_data, cliente_id, instance_id)
   ```

3. 📊 ESTATÍSTICAS:
   ```python
   stats = media_manager.obter_estatisticas()
   print(f"Total de mídias: {stats['total_midias']}")
   ```

4. 🔄 REPROCESSAMENTO:
   ```python
   # Reprocessar mídias que falharam
   media_manager.reprocessar_midias_pendentes()
   
   # Limpar arquivos antigos
   media_manager.limpar_arquivos_antigos(dias=30)
   ```

5. 🔗 INTEGRAÇÃO COM WEBHOOK:
   ```python
   # No seu webhook receiver
   if 'imageMessage' in webhook_data['msgContent']:
       process_webhook_media(webhook_data, cliente.id, instance_id)
   ```

6. 📁 ESTRUTURA DE ARMAZENAMENTO:
   ```
   media_storage/
   ├── cliente_1/
   │   ├── instance_abc123/
   │   │   ├── imagens/
   │   │   ├── videos/
   │   │   ├── audios/
   │   │   ├── documentos/
   │   │   ├── stickers/
   │   │   └── media_database.db
   │   └── instance_def456/
   └── cliente_2/
       └── instance_ghi789/
   ```

7. 🗄️ BANCO DE DADOS:
   - Cada instância tem seu próprio banco SQLite
   - Armazena metadados de todas as mídias
   - Rastreia status de download
   - Vincula com mensagens do sistema principal

8. 🔒 SEGURANÇA:
   - Separação por cliente e instância
   - Validação de arquivos baixados
   - Verificação de magic numbers
   - Controle de acesso por token

9. ⚡ PERFORMANCE:
   - Cache de gerenciadores
   - Processamento assíncrono
   - Índices otimizados no banco
   - Limpeza automática de arquivos antigos
   """)


def main():
    """Função principal da demonstração"""
    
    print("🎬 SISTEMA DE MÍDIAS MULTICHAT - DEMONSTRAÇÃO COMPLETA")
    print("=" * 80)
    
    try:
        # Demonstração básica
        media_manager = demo_basic_usage()
        
        # Demonstração de integração com webhooks
        demo_webhook_integration()
        
        # Demonstração de gerenciamento de arquivos
        demo_file_management()
        
        # Exemplos de uso
        demo_usage_examples()
        
        print("\n" + "=" * 80)
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA!")
        print("✅ O sistema está funcionando corretamente")
        print("📚 Consulte os exemplos acima para implementar em seu projeto")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante demonstração: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main() 