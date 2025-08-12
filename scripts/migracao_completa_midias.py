#!/usr/bin/env python3
"""
Script de migração completa de mídias
"""

import os
import sys
import django
import shutil
from pathlib import Path
from datetime import datetime

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent / "multichat_system"
sys.path.append(str(project_root))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Cliente, WhatsappInstance, MediaFile, Chat, Mensagem
from django.utils import timezone
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migracao_completa_midias():
    """Faz migração completa de todas as mídias encontradas"""
    print("🚀 INICIANDO MIGRAÇÃO COMPLETA DE MÍDIAS")
    print("=" * 60)
    
    # 1. Verificar clientes e instâncias
    print("1️⃣ VERIFICANDO CLIENTES E INSTÂNCIAS")
    clientes = Cliente.objects.all()
    print(f"   Total de clientes: {clientes.count()}")
    
    for cliente in clientes:
        print(f"   👤 Cliente: {cliente.nome} (ID: {cliente.id})")
        instances = WhatsappInstance.objects.filter(cliente=cliente)
        print(f"      📱 Instâncias: {instances.count()}")
        
        for instance in instances:
            print(f"         🔗 {instance.instance_id} - {instance.status}")
            
            # 2. Verificar pasta de mídias da instância
            instance_media_path = Path(__file__).parent / "multichat_system" / "media_storage" / f"cliente_{cliente.id}" / f"instance_{instance.instance_id}"
            
            if instance_media_path.exists():
                print(f"         📁 Pasta de mídias: {instance_media_path}")
                
                # 3. Processar cada tipo de mídia
                media_types = ['audio', 'image', 'video', 'document', 'sticker']
                
                for media_type in media_types:
                    media_path = instance_media_path / media_type
                    if media_path.exists():
                        files = list(media_path.glob("*"))
                        print(f"            📂 {media_type}: {len(files)} arquivos")
                        
                        for file in files:
                            if file.is_file():
                                # Verificar se já existe no banco
                                existing_media = MediaFile.objects.filter(
                                    file_name=file.name,
                                    media_type=media_type,
                                    cliente=cliente,
                                    instance=instance
                                ).first()
                                
                                if existing_media:
                                    print(f"               ✅ Já existe: {file.name}")
                                else:
                                    # Criar registro no banco
                                    try:
                                        media_file = MediaFile.objects.create(
                                            cliente=cliente,
                                            instance=instance,
                                            message_id=f"migrado_{file.stem}",
                                            sender_name="Migração",
                                            sender_id="migracao",
                                            media_type=media_type,
                                            mimetype="application/octet-stream",
                                            file_name=file.name,
                                            file_path=str(file),
                                            file_size=file.stat().st_size,
                                            download_status='success',
                                            download_timestamp=timezone.now(),
                                            message_timestamp=timezone.now(),
                                            is_group=False,
                                            from_me=False
                                        )
                                        print(f"               ✅ Criado: {file.name} (ID: {media_file.id})")
                                    except Exception as e:
                                        print(f"               ❌ Erro ao criar: {file.name} - {e}")
            else:
                print(f"         ❌ Pasta não existe: {instance_media_path}")
    
    # 4. Verificar pasta wapi/midias (mídias antigas)
    print("\n2️⃣ VERIFICANDO PASTA WAPI/MIDIAS")
    wapi_path = Path(__file__).parent / "wapi" / "midias"
    
    if wapi_path.exists():
        print(f"   📁 Pasta wapi/midias encontrada: {wapi_path}")
        
        # Encontrar cliente padrão (primeiro cliente)
        cliente_padrao = Cliente.objects.first()
        if not cliente_padrao:
            print("   ❌ Nenhum cliente encontrado no banco")
            return
        
        # Encontrar instância padrão
        instance_padrao = WhatsappInstance.objects.filter(cliente=cliente_padrao).first()
        if not instance_padrao:
            # Tentar encontrar qualquer instância
            instance_padrao = WhatsappInstance.objects.first()
            if instance_padrao:
                cliente_padrao = instance_padrao.cliente
                print(f"   👤 Usando cliente com instância: {cliente_padrao.nome}")
                print(f"   📱 Usando instância: {instance_padrao.instance_id}")
            else:
                print("   ❌ Nenhuma instância encontrada")
                return
        else:
            print(f"   👤 Usando cliente padrão: {cliente_padrao.nome}")
            print(f"   📱 Usando instância padrão: {instance_padrao.instance_id}")
        
        # Processar cada subpasta
        for subdir in wapi_path.iterdir():
            if subdir.is_dir():
                print(f"   📂 Processando: {subdir.name}")
                files = list(subdir.glob("*"))
                print(f"      📄 Arquivos encontrados: {len(files)}")
                
                for file in files:
                    if file.is_file():
                        # Determinar tipo de mídia baseado na extensão
                        media_type = determinar_tipo_midia(file.name)
                        
                        # Verificar se já existe
                        existing_media = MediaFile.objects.filter(
                            file_name=file.name,
                            media_type=media_type,
                            cliente=cliente_padrao,
                            instance=instance_padrao
                        ).first()
                        
                        if existing_media:
                            print(f"         ✅ Já existe: {file.name}")
                        else:
                            # Copiar arquivo para media_storage
                            dest_path = Path(__file__).parent / "multichat_system" / "media_storage" / f"cliente_{cliente_padrao.id}" / f"instance_{instance_padrao.instance_id}" / media_type
                            dest_path.mkdir(parents=True, exist_ok=True)
                            
                            dest_file = dest_path / file.name
                            try:
                                shutil.copy2(file, dest_file)
                                
                                # Criar registro no banco
                                media_file = MediaFile.objects.create(
                                    cliente=cliente_padrao,
                                    instance=instance_padrao,
                                    message_id=f"wapi_{file.stem}",
                                    sender_name="WAPI",
                                    sender_id="wapi",
                                    media_type=media_type,
                                    mimetype="application/octet-stream",
                                    file_name=file.name,
                                    file_path=str(dest_file),
                                    file_size=file.stat().st_size,
                                    download_status='success',
                                    download_timestamp=timezone.now(),
                                    message_timestamp=timezone.now(),
                                    is_group=False,
                                    from_me=False
                                )
                                print(f"         ✅ Migrado: {file.name} (ID: {media_file.id})")
                            except Exception as e:
                                print(f"         ❌ Erro ao migrar: {file.name} - {e}")
    else:
        print(f"   ❌ Pasta wapi/midias não encontrada: {wapi_path}")
    
    # 5. Resumo final
    print("\n3️⃣ RESUMO FINAL")
    total_midias = MediaFile.objects.count()
    midias_sucesso = MediaFile.objects.filter(download_status='success').count()
    
    print(f"   📊 Total de mídias no banco: {total_midias}")
    print(f"   ✅ Mídias com sucesso: {midias_sucesso}")
    print(f"   ❌ Mídias que falharam: {total_midias - midias_sucesso}")
    
    if total_midias > 0:
        print(f"\n   📋 ÚLTIMAS MÍDIAS ADICIONADAS:")
        for m in MediaFile.objects.order_by('-id')[:5]:
            print(f"      ID: {m.id} | Tipo: {m.media_type} | Arquivo: {m.file_name} | Status: {m.download_status}")

def determinar_tipo_midia(filename):
    """Determina o tipo de mídia baseado na extensão do arquivo"""
    ext = Path(filename).suffix.lower()
    
    if ext in ['.mp3', '.wav', '.ogg', '.m4a', '.aac']:
        return 'audio'
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
        return 'image'
    elif ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']:
        return 'video'
    elif ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
        return 'document'
    elif ext in ['.webp', '.gif']:
        return 'sticker'
    else:
        return 'document'  # Padrão

if __name__ == "__main__":
    migracao_completa_midias() 