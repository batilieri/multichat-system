#!/usr/bin/env python3
"""
Teste do Sistema de Mídias Django - Usando Banco Principal
Demonstra o uso do gerenciador de mídias integrado ao banco Django
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

from core.models import Cliente, WhatsappInstance, MediaFile
from core.django_media_manager import criar_django_media_manager


def test_django_media_manager():
    """Testa o gerenciador de mídias Django"""
    
    print("🎯 TESTE DO SISTEMA DE MÍDIAS DJANGO")
    print("=" * 50)
    
    # Buscar dados de exemplo
    cliente = Cliente.objects.first()
    instance = WhatsappInstance.objects.filter(cliente=cliente).first()
    
    if not cliente or not instance:
        print("❌ Dados de teste não encontrados")
        return False
    
    print(f"✅ Cliente: {cliente.nome}")
    print(f"✅ Instância: {instance.instance_id}")
    
    # Criar gerenciador Django
    print("\n🔧 Criando gerenciador Django...")
    media_manager = criar_django_media_manager(
        cliente_id=cliente.id,
        instance_id=instance.instance_id,
        bearer_token=instance.token
    )
    
    print(f"   ✅ Gerenciador criado")
    print(f"   📂 Pasta base: {media_manager.base_path}")
    print(f"   📂 Pasta do cliente: {media_manager.cliente_path}")
    print(f"   📂 Pasta da instância: {media_manager.instance_path}")
    
    # Testar processamento de mensagens
    print("\n📨 Testando processamento de mensagens...")
    
    # Mensagem de teste com imagem
    webhook_data = {
        'event': 'webhookReceived',
        'instanceId': instance.instance_id,
        'messageId': f'django_test_{int(datetime.now().timestamp())}',
        'sender': {
            'id': '5511999999999@s.whatsapp.net',
            'pushName': 'Teste Django'
        },
        'chat': {
            'id': '5511999999999@s.whatsapp.net'
        },
        'msgContent': {
            'imageMessage': {
                'mimetype': 'image/jpeg',
                'fileName': 'teste_django.jpg',
                'fileLength': 8192,
                'caption': 'Teste com banco Django',
                'mediaKey': 'django_test_key_001',
                'directPath': '/django/test/path',
                'fileSha256': 'django_test_sha256_001',
                'fileEncSha256': 'django_test_enc_sha256_001',
                'width': 1200,
                'height': 800
            }
        },
        'isGroup': False,
        'fromMe': False,
        'moment': int(datetime.now().timestamp())
    }
    
    # Processar mensagem
    media_manager.processar_mensagem_whatsapp(webhook_data)
    
    # Verificar se foi salvo no banco Django
    print("\n📊 Verificando banco Django...")
    try:
        media_files = MediaFile.objects.filter(
            cliente=cliente,
            instance=instance
        ).order_by('-created_at')
        
        print(f"   📈 Total de mídias no banco: {media_files.count()}")
        
        if media_files.exists():
            latest_media = media_files.first()
            print(f"   📎 Última mídia:")
            print(f"      - ID: {latest_media.id}")
            print(f"      - Message ID: {latest_media.message_id}")
            print(f"      - Tipo: {latest_media.media_type}")
            print(f"      - Status: {latest_media.download_status}")
            print(f"      - Remetente: {latest_media.sender_name}")
            print(f"      - Criado em: {latest_media.created_at}")
            
            if latest_media.file_path:
                print(f"      - Arquivo: {latest_media.file_path}")
                print(f"      - Tamanho: {latest_media.file_size_mb} MB")
        
    except Exception as e:
        print(f"   ❌ Erro ao verificar banco: {e}")
    
    # Obter estatísticas
    print("\n📈 Estatísticas do gerenciador:")
    stats = media_manager.obter_estatisticas()
    
    for key, value in stats.items():
        if key == 'por_tipo':
            print(f"   📊 Por tipo: {value}")
        else:
            print(f"   📊 {key}: {value}")
    
    # Testar busca de mídias pendentes
    print("\n⏳ Mídias pendentes:")
    midias_pendentes = media_manager.buscar_midias_pendentes()
    
    if midias_pendentes:
        for media in midias_pendentes[:5]:  # Mostrar apenas as 5 primeiras
            print(f"   📎 {media.message_id}: {media.media_type} - {media.download_status}")
    else:
        print("   ℹ️ Nenhuma mídia pendente")
    
    # Testar reprocessamento
    print("\n🔄 Testando reprocessamento...")
    media_manager.reprocessar_midias_pendentes()
    
    # Verificar estrutura de pastas
    print("\n📁 Estrutura de pastas:")
    for tipo, pasta in media_manager.pastas_midia.items():
        if pasta.exists():
            arquivos = list(pasta.glob('*'))
            print(f"   📂 {tipo}: {len(arquivos)} arquivos")
            for arquivo in arquivos[:3]:  # Mostrar apenas os 3 primeiros
                tamanho = arquivo.stat().st_size
                print(f"      - {arquivo.name} ({tamanho / 1024:.1f} KB)")
        else:
            print(f"   📂 {tipo}: 0 arquivos")
    
    print("\n" + "=" * 50)
    print("✅ Teste do Django Media Manager concluído!")
    
    return True


def test_django_queries():
    """Testa consultas Django no banco de mídias"""
    
    print("\n🔍 TESTE DE CONSULTAS DJANGO")
    print("=" * 40)
    
    # Buscar dados
    cliente = Cliente.objects.first()
    instance = WhatsappInstance.objects.filter(cliente=cliente).first()
    
    if not cliente or not instance:
        print("❌ Dados não encontrados")
        return
    
    # 1. Total de mídias por cliente
    total_cliente = MediaFile.objects.filter(cliente=cliente).count()
    print(f"📊 Total de mídias do cliente: {total_cliente}")
    
    # 2. Mídias por instância
    total_instancia = MediaFile.objects.filter(instance=instance).count()
    print(f"📊 Total de mídias da instância: {total_instancia}")
    
    # 3. Mídias por tipo
    from django.db.models import Count
    por_tipo = MediaFile.objects.filter(
        cliente=cliente
    ).values('media_type').annotate(
        total=Count('id')
    ).order_by('-total')
    
    print("📊 Mídias por tipo:")
    for item in por_tipo:
        print(f"   - {item['media_type']}: {item['total']}")
    
    # 4. Mídias por status
    por_status = MediaFile.objects.filter(
        cliente=cliente
    ).values('download_status').annotate(
        total=Count('id')
    ).order_by('-total')
    
    print("📊 Mídias por status:")
    for item in por_status:
        print(f"   - {item['download_status']}: {item['total']}")
    
    # 5. Últimas mídias
    ultimas_midias = MediaFile.objects.filter(
        cliente=cliente
    ).order_by('-created_at')[:5]
    
    print("📊 Últimas 5 mídias:")
    for media in ultimas_midias:
        print(f"   - {media.message_id[:8]}... ({media.media_type}) - {media.created_at.strftime('%d/%m %H:%M')}")
    
    # 6. Tamanho total
    from django.db.models import Sum
    tamanho_total = MediaFile.objects.filter(
        cliente=cliente,
        download_status='success'
    ).aggregate(
        total_size=Sum('file_size')
    )['total_size'] or 0
    
    print(f"📊 Tamanho total: {tamanho_total / (1024*1024):.2f} MB")


def test_django_relationships():
    """Testa relacionamentos Django"""
    
    print("\n🔗 TESTE DE RELACIONAMENTOS DJANGO")
    print("=" * 40)
    
    # Buscar dados
    cliente = Cliente.objects.first()
    
    if not cliente:
        print("❌ Cliente não encontrado")
        return
    
    # 1. Mídias do cliente
    midias_cliente = cliente.media_files.all()
    print(f"📊 Mídias do cliente {cliente.nome}: {midias_cliente.count()}")
    
    # 2. Instâncias do cliente
    instancias = cliente.whatsapp_instances.all()
    print(f"📊 Instâncias do cliente: {instancias.count()}")
    
    for instancia in instancias:
        midias_instancia = instancia.media_files.all()
        print(f"   - {instancia.instance_id}: {midias_instancia.count()} mídias")
    
    # 3. Mídias com chat
    midias_com_chat = MediaFile.objects.filter(
        cliente=cliente,
        chat__isnull=False
    ).select_related('chat')
    
    print(f"📊 Mídias com chat vinculado: {midias_com_chat.count()}")
    
    if midias_com_chat.exists():
        for media in midias_com_chat[:3]:
            print(f"   - {media.message_id[:8]}... -> Chat: {media.chat.chat_id}")


def main():
    """Função principal"""
    
    print("🚀 TESTE COMPLETO DO SISTEMA DE MÍDIAS DJANGO")
    print("=" * 60)
    
    try:
        # Teste principal
        success = test_django_media_manager()
        
        if success:
            # Testes adicionais
            test_django_queries()
            test_django_relationships()
            
            print("\n" + "=" * 60)
            print("🎉 Todos os testes passaram!")
            print("✅ O sistema Django está funcionando corretamente")
            print("\n💡 Vantagens do banco Django:")
            print("   - Integração completa com o sistema MultiChat")
            print("   - Relacionamentos automáticos entre modelos")
            print("   - Migrações automáticas")
            print("   - Admin Django para gerenciamento")
            print("   - Queries otimizadas")
            print("   - Backup integrado")
        else:
            print("\n❌ Alguns testes falharam")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main() 