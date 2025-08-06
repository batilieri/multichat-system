#!/usr/bin/env python3
"""
Script para migrar mídias existentes da pasta wapi para o sistema Django
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

def migrar_midias_existentes():
    """Migra mídias existentes da pasta wapi para o sistema Django"""
    try:
        print("🔄 Iniciando migração de mídias existentes...")
        
        # Buscar cliente e instância
        cliente = Cliente.objects.get(id=2)  # Elizeu Batiliere Dos Santos
        instancia = WhatsappInstance.objects.get(
            cliente=cliente,
            instance_id="3B6XIW-ZTS923-GEAY6V"
        )
        
        print(f"✅ Cliente: {cliente.nome}")
        print(f"✅ Instância: {instancia.instance_id}")
        
        # Caminhos
        wapi_path = Path(__file__).parent / "wapi" / "midias"
        media_storage_path = project_root / "media_storage" / f"cliente_{cliente.id}" / f"instance_{instancia.instance_id}"
        
        print(f"📁 Origem: {wapi_path}")
        print(f"📁 Destino: {media_storage_path}")
        
        # Mapeamento de tipos
        tipo_mapping = {
            'audios': 'audio',
            'imagens': 'image', 
            'videos': 'video',
            'documentos': 'document',
            'stickers': 'sticker'
        }
        
        # Contadores
        total_migradas = 0
        total_erros = 0
        
        # Processar cada tipo de mídia
        for pasta_origem, tipo_midia in tipo_mapping.items():
            origem_path = wapi_path / pasta_origem
            destino_path = media_storage_path / tipo_midia
            
            if not origem_path.exists():
                print(f"⚠️ Pasta não existe: {origem_path}")
                continue
                
            # Criar pasta de destino
            destino_path.mkdir(parents=True, exist_ok=True)
            
            # Listar arquivos
            arquivos = list(origem_path.glob('*'))
            print(f"\n📁 Processando {pasta_origem}: {len(arquivos)} arquivos")
            
            for arquivo in arquivos:
                if arquivo.is_file():
                    try:
                        # Gerar nome único
                        nome_arquivo = f"migrado_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{arquivo.name}"
                        caminho_destino = destino_path / nome_arquivo
                        
                        # Copiar arquivo
                        shutil.copy2(arquivo, caminho_destino)
                        
                        # Determinar mimetype
                        mimetype = 'application/octet-stream'
                        if arquivo.suffix.lower() in ['.jpg', '.jpeg']:
                            mimetype = 'image/jpeg'
                        elif arquivo.suffix.lower() == '.png':
                            mimetype = 'image/png'
                        elif arquivo.suffix.lower() == '.mp3':
                            mimetype = 'audio/mpeg'
                        elif arquivo.suffix.lower() == '.m4a':
                            mimetype = 'audio/mp4'
                        elif arquivo.suffix.lower() == '.mp4':
                            mimetype = 'video/mp4'
                        
                        # Criar registro no banco
                        media_file = MediaFile.objects.create(
                            cliente=cliente,
                            instance=instancia,
                            message_id=f"migrado_{arquivo.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            sender_name="Migração Automática",
                            sender_id="migracao",
                            media_type=tipo_midia,
                            mimetype=mimetype,
                            file_name=nome_arquivo,
                            file_path=str(caminho_destino),
                            file_size=arquivo.stat().st_size,
                            download_status='success',
                            download_timestamp=timezone.now(),
                            message_timestamp=timezone.now(),
                            is_group=False,
                            from_me=False
                        )
                        
                        print(f"  ✅ {arquivo.name} → {nome_arquivo}")
                        total_migradas += 1
                        
                    except Exception as e:
                        print(f"  ❌ Erro ao migrar {arquivo.name}: {e}")
                        total_erros += 1
        
        print(f"\n📊 Resumo da migração:")
        print(f"  ✅ Migradas com sucesso: {total_migradas}")
        print(f"  ❌ Erros: {total_erros}")
        
        # Verificar resultado
        total_banco = MediaFile.objects.filter(cliente=cliente, instance=instancia).count()
        print(f"  📊 Total no banco: {total_banco}")
        
        return total_migradas > 0
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    migrar_midias_existentes() 