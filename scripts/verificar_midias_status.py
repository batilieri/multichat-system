#!/usr/bin/env python3
"""
Script para verificar o status atual das mídias
"""

import os
import sys
import django
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent / "multichat_system"
sys.path.append(str(project_root))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import MediaFile, Cliente, WhatsappInstance
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verificar_status_midias():
    """Verifica o status atual das mídias"""
    print("🔍 VERIFICANDO STATUS DAS MÍDIAS")
    print("=" * 50)
    
    # Verificar mídias no banco
    total_midias = MediaFile.objects.count()
    midias_sucesso = MediaFile.objects.filter(download_status='success').count()
    midias_pendentes = MediaFile.objects.filter(download_status='pending').count()
    midias_falharam = MediaFile.objects.filter(download_status='failed').count()
    
    print(f"📊 ESTATÍSTICAS DO BANCO:")
    print(f"   Total de mídias: {total_midias}")
    print(f"   Mídias com sucesso: {midias_sucesso}")
    print(f"   Mídias pendentes: {midias_pendentes}")
    print(f"   Mídias que falharam: {midias_falharam}")
    
    if total_midias > 0:
        print(f"\n📋 DETALHES DAS MÍDIAS:")
        for m in MediaFile.objects.all():
            print(f"   ID: {m.id}")
            print(f"   Tipo: {m.media_type}")
            print(f"   Status: {m.download_status}")
            print(f"   Arquivo: {m.file_name}")
            print(f"   Caminho: {m.file_path}")
            print(f"   Tamanho: {m.file_size} bytes")
            print(f"   Cliente: {m.cliente.nome if m.cliente else 'N/A'}")
            print(f"   Instância: {m.instance.instance_id if m.instance else 'N/A'}")
            print("   " + "-" * 30)
    else:
        print("❌ Nenhuma mídia encontrada no banco de dados")
    
    # Verificar pastas de mídias
    print(f"\n📁 VERIFICANDO PASTAS DE MÍDIAS:")
    
    # Verificar pasta wapi/midias
    wapi_path = Path(__file__).parent.parent / "wapi" / "midias"
    if wapi_path.exists():
        print(f"✅ Pasta wapi/midias existe: {wapi_path}")
        for subdir in wapi_path.iterdir():
            if subdir.is_dir():
                files = list(subdir.glob("*"))
                print(f"   📂 {subdir.name}: {len(files)} arquivos")
                for file in files[:5]:  # Mostrar apenas os primeiros 5
                    print(f"      📄 {file.name} ({file.stat().st_size} bytes)")
                if len(files) > 5:
                    print(f"      ... e mais {len(files) - 5} arquivos")
    else:
        print(f"❌ Pasta wapi/midias não existe: {wapi_path}")
    
    # Verificar pasta media_storage
    media_storage_path = Path(__file__).parent / "media_storage"
    if media_storage_path.exists():
        print(f"✅ Pasta media_storage existe: {media_storage_path}")
        for cliente_dir in media_storage_path.iterdir():
            if cliente_dir.is_dir():
                print(f"   👤 Cliente: {cliente_dir.name}")
                for instance_dir in cliente_dir.iterdir():
                    if instance_dir.is_dir():
                        print(f"      📱 Instância: {instance_dir.name}")
                        for media_type_dir in instance_dir.iterdir():
                            if media_type_dir.is_dir():
                                files = list(media_type_dir.glob("*"))
                                print(f"         📂 {media_type_dir.name}: {len(files)} arquivos")
                                for file in files[:3]:  # Mostrar apenas os primeiros 3
                                    print(f"            📄 {file.name} ({file.stat().st_size} bytes)")
                                if len(files) > 3:
                                    print(f"            ... e mais {len(files) - 3} arquivos")
    else:
        print(f"❌ Pasta media_storage não existe: {media_storage_path}")
    
    # Verificar clientes e instâncias
    print(f"\n👥 VERIFICANDO CLIENTES E INSTÂNCIAS:")
    clientes = Cliente.objects.all()
    print(f"   Total de clientes: {clientes.count()}")
    for cliente in clientes:
        print(f"   👤 Cliente: {cliente.nome} (ID: {cliente.id})")
        instances = WhatsappInstance.objects.filter(cliente=cliente)
        print(f"      📱 Instâncias: {instances.count()}")
        for instance in instances:
            print(f"         🔗 {instance.instance_id} - {instance.status}")

if __name__ == "__main__":
    verificar_status_midias() 