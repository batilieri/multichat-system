#!/usr/bin/env python3
"""
Script para verificar se o sistema de download automático está funcionando
"""

import os
import sys
import django
import json
from pathlib import Path

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import MediaFile, WhatsappInstance

def verificar_sistema_download():
    """Verifica se o sistema de download está funcionando"""
    print("🔍 Verificando sistema de download automático...")
    print("=" * 60)
    
    # 1. Verificar instâncias
    print("📱 Verificando instâncias...")
    instancias = WhatsappInstance.objects.all()
    
    for instancia in instancias:
        print(f"   ✅ Instância: {instancia.instance_id}")
        print(f"      Cliente: {instancia.cliente.nome}")
        print(f"      Status: {instancia.status}")
        print(f"      Token: {'✅' if instancia.token else '❌'}")
        
        # Verificar pasta de mídia
        media_path = Path(__file__).parent / "media_storage" / f"cliente_{instancia.cliente.id}" / f"instance_{instancia.instance_id}"
        print(f"      Pasta mídia: {'✅' if media_path.exists() else '❌'}")
        
        # Verificar subpastas
        tipos_midia = ['image', 'video', 'audio', 'document', 'sticker']
        for tipo in tipos_midia:
            tipo_path = media_path / tipo
            if tipo_path.exists():
                arquivos = list(tipo_path.glob('*'))
                print(f"         {tipo}: {len(arquivos)} arquivos")
    
    # 2. Verificar mídias no banco
    print("\n📊 Verificando mídias no banco...")
    midias = MediaFile.objects.all()
    
    if not midias.exists():
        print("   ❌ Nenhuma mídia encontrada no banco!")
    else:
        print(f"   📊 Total de mídias: {midias.count()}")
        
        # Estatísticas por tipo
        tipos = {}
        status = {}
        
        for midia in midias:
            tipos[midia.media_type] = tipos.get(midia.media_type, 0) + 1
            status[midia.download_status] = status.get(midia.download_status, 0) + 1
        
        print("   📈 Por tipo:")
        for tipo, count in tipos.items():
            print(f"      {tipo}: {count}")
        
        print("   📈 Por status:")
        for stat, count in status.items():
            print(f"      {stat}: {count}")
    
    # 3. Verificar arquivos físicos
    print("\n📁 Verificando arquivos físicos...")
    midias_sucesso = MediaFile.objects.filter(download_status='success')
    
    arquivos_existem = 0
    arquivos_faltando = 0
    
    for midia in midias_sucesso:
        if midia.file_path and os.path.exists(midia.file_path):
            arquivos_existem += 1
        else:
            arquivos_faltando += 1
            print(f"   ❌ Arquivo não existe: {midia.file_path}")
    
    print(f"   ✅ Arquivos existem: {arquivos_existem}")
    print(f"   ❌ Arquivos faltando: {arquivos_faltando}")
    
    # 4. Verificar mídias recentes
    print("\n🆕 Verificando mídias recentes...")
    from django.utils import timezone
    from datetime import timedelta
    
    agora = timezone.now()
    uma_hora_atras = agora - timedelta(hours=1)
    
    midias_recentes = MediaFile.objects.filter(
        created_at__gte=uma_hora_atras
    ).order_by('-created_at')
    
    if midias_recentes.exists():
        print(f"   📊 Mídias na última hora: {midias_recentes.count()}")
        
        for midia in midias_recentes[:5]:  # Mostrar apenas as 5 mais recentes
            print(f"      📎 {midia.media_type} - {midia.sender_name}")
            print(f"         Message ID: {midia.message_id}")
            print(f"         Status: {midia.download_status}")
            if midia.file_path:
                existe = os.path.exists(midia.file_path)
                print(f"         Arquivo: {'✅' if existe else '❌'}")
    else:
        print("   ⚠️  Nenhuma mídia na última hora")
    
    # 5. Resumo do sistema
    print("\n📋 Resumo do Sistema:")
    print("=" * 40)
    
    total_midias = midias.count()
    midias_sucesso_count = midias_sucesso.count()
    midias_falhadas = midias.filter(download_status='failed').count()
    
    print(f"   📊 Total de mídias: {total_midias}")
    print(f"   ✅ Baixadas com sucesso: {midias_sucesso_count}")
    print(f"   ❌ Falharam: {midias_falhadas}")
    
    if total_midias > 0:
        taxa_sucesso = (midias_sucesso_count / total_midias) * 100
        print(f"   📈 Taxa de sucesso: {taxa_sucesso:.1f}%")
    
    # Verificar se há arquivos físicos
    if arquivos_existem > 0:
        print(f"   📁 Arquivos físicos: {arquivos_existem} existem")
    
    if arquivos_faltando > 0:
        print(f"   ⚠️  Arquivos faltando: {arquivos_faltando}")
    
    print("\n" + "=" * 60)
    
    if midias_sucesso_count > 0 and arquivos_existem > 0:
        print("✅ Sistema funcionando corretamente!")
    else:
        print("❌ Sistema precisa de ajustes!")

def testar_webhook_simulado():
    """Testa webhook simulado para verificar funcionamento"""
    print("\n🧪 Testando webhook simulado...")
    
    # Dados de teste
    webhook_data = {
        "instanceId": "3B6XIW-ZTS923-GEAY6V",
        "messageId": "TEST_MESSAGE_123",
        "sender": {
            "id": "556992962392@c.us",
            "pushName": "Teste"
        },
        "msgContent": {
            "imageMessage": {
                "mediaKey": "test_key_123",
                "directPath": "/test/path/image.jpg",
                "mimetype": "image/jpeg",
                "fileLength": "1024"
            }
        }
    }
    
    try:
        from webhook.views import process_media_automatically
        
        instancia = WhatsappInstance.objects.get(instance_id="3B6XIW-ZTS923-GEAY6V")
        cliente = instancia.cliente
        
        print(f"   📱 Testando com instância: {instancia.instance_id}")
        print(f"   👤 Cliente: {cliente.nome}")
        
        resultado = process_media_automatically(webhook_data, cliente, instancia)
        
        if resultado:
            print("   ✅ Processamento funcionou!")
        else:
            print("   ❌ Processamento falhou!")
            
    except Exception as e:
        print(f"   ❌ Erro no teste: {e}")

def main():
    """Função principal"""
    print("🚀 Verificando sistema de download automático...")
    
    verificar_sistema_download()
    testar_webhook_simulado()
    
    print("\n✅ Verificação concluída!")

if __name__ == "__main__":
    main() 