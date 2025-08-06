#!/usr/bin/env python3
"""
Script de teste para verificar o download de mídias
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

from core.models import Cliente, WhatsappInstance, MediaFile
from core.django_media_manager import DjangoMediaManager
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_media_download():
    """Testa o download de mídias"""
    try:
        print("🔍 Verificando configuração do sistema...")
        
        # Verificar clientes
        clientes = Cliente.objects.all()
        print(f"📊 Total de clientes: {clientes.count()}")
        
        for cliente in clientes:
            print(f"  - Cliente {cliente.id}: {cliente.nome}")
            
            # Verificar instâncias
            instancias = WhatsappInstance.objects.filter(cliente=cliente)
            print(f"    Instâncias: {instancias.count()}")
            
            for instancia in instancias:
                print(f"      - Instância {instancia.instance_id}: {instancia.status}")
                
                # Verificar mídias
                medias = MediaFile.objects.filter(
                    cliente=cliente,
                    instance=instancia
                )
                print(f"        Mídias: {medias.count()}")
                
                for media in medias:
                    print(f"          - {media.media_type}: {media.download_status}")
                    if media.file_path:
                        file_exists = Path(media.file_path).exists()
                        print(f"            Arquivo existe: {file_exists}")
        
        # Verificar arquivos na pasta wapi
        wapi_path = Path(__file__).parent / "wapi" / "midias"
        print(f"\n📁 Verificando arquivos em {wapi_path}:")
        
        if wapi_path.exists():
            for tipo in ['audios', 'imagens', 'videos', 'documentos', 'stickers']:
                tipo_path = wapi_path / tipo
                if tipo_path.exists():
                    files = list(tipo_path.glob('*'))
                    print(f"  {tipo}: {len(files)} arquivos")
                    for file in files[:3]:  # Mostrar apenas os 3 primeiros
                        print(f"    - {file.name} ({file.stat().st_size} bytes)")
                else:
                    print(f"  {tipo}: pasta não existe")
        else:
            print("  Pasta wapi/midias não existe")
        
        # Testar gerenciador de mídias
        print(f"\n🧪 Testando gerenciador de mídias...")
        
        # Buscar cliente que tem instância
        cliente_com_instancia = None
        for cliente in Cliente.objects.all():
            if WhatsappInstance.objects.filter(cliente=cliente).exists():
                cliente_com_instancia = cliente
                break
                
        if not cliente_com_instancia:
            print("❌ Nenhum cliente com instância encontrado")
            return
            
        instancia = WhatsappInstance.objects.filter(cliente=cliente_com_instancia).first()
        if not instancia:
            print("❌ Nenhuma instância encontrada")
            return
            
        print(f"✅ Usando Cliente {cliente_com_instancia.id} ({cliente_com_instancia.nome})")
        print(f"✅ Usando Instância {instancia.instance_id}")
        
        # Criar gerenciador
        try:
            media_manager = DjangoMediaManager(
                cliente_id=cliente_com_instancia.id,
                instance_id=instancia.instance_id,
                bearer_token=instancia.token
            )
            print("✅ Gerenciador de mídias criado com sucesso")
            
            # Verificar pastas
            for tipo, pasta in media_manager.pastas_midia.items():
                if pasta.exists():
                    files = list(pasta.glob('*'))
                    print(f"  {tipo}: {len(files)} arquivos em {pasta}")
                else:
                    print(f"  {tipo}: pasta não existe - {pasta}")
                    
        except Exception as e:
            print(f"❌ Erro ao criar gerenciador: {e}")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_media_download() 