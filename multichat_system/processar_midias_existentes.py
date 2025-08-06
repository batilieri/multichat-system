#!/usr/bin/env python3
"""
Script para processar mídias existentes que falharam no download
"""

import os
import sys
import django
import json
import requests
from pathlib import Path
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import MediaFile, WhatsappInstance, Mensagem
from webhook.views import save_media_file

def processar_midias_falhadas():
    """Processa mídias que falharam no download"""
    print("🔄 Processando mídias falhadas...")
    
    # Buscar mídias que falharam
    midias_falhadas = MediaFile.objects.filter(download_status='failed')
    
    if not midias_falhadas.exists():
        print("✅ Nenhuma mídia falhada encontrada!")
        return
    
    print(f"📊 Encontradas {midias_falhadas.count()} mídias falhadas")
    
    for midia in midias_falhadas:
        print(f"\n📎 Processando mídia {midia.id}: {midia.media_type}")
        print(f"   Message ID: {midia.message_id}")
        print(f"   Sender: {midia.sender_name}")
        
        try:
            # Tentar baixar novamente
            resultado = tentar_download_novamente(midia)
            
            if resultado:
                print(f"✅ Mídia {midia.id} reprocessada com sucesso!")
                midia.download_status = 'success'
                midia.file_path = resultado
                midia.download_timestamp = datetime.now()
                midia.save()
            else:
                print(f"❌ Falha ao reprocessar mídia {midia.id}")
                
        except Exception as e:
            print(f"❌ Erro ao reprocessar mídia {midia.id}: {e}")

def tentar_download_novamente(midia):
    """Tenta baixar mídia novamente"""
    try:
        # Simular download (substitua por lógica real)
        file_link = f"https://api.w-api.app/media/test/{midia.message_id}"
        
        resultado = save_media_file(
            file_link,
            midia.media_type,
            midia.message_id,
            midia.sender_name,
            midia.cliente,
            midia.instance
        )
        
        return resultado
        
    except Exception as e:
        print(f"❌ Erro no download: {e}")
        return None

def verificar_midias_sem_arquivo():
    """Verifica mídias que não têm arquivo físico"""
    print("\n🔍 Verificando mídias sem arquivo físico...")
    
    midias = MediaFile.objects.filter(download_status='success')
    
    for midia in midias:
        if midia.file_path and not os.path.exists(midia.file_path):
            print(f"❌ Arquivo não existe: {midia.file_path}")
            print(f"   Mídia ID: {midia.id}")
            print(f"   Tipo: {midia.media_type}")
            
            # Marcar para reprocessamento
            midia.download_status = 'failed'
            midia.save()
            print(f"✅ Marcada para reprocessamento")

def criar_estrutura_pastas_midias():
    """Cria estrutura de pastas para mídias"""
    print("\n📂 Criando estrutura de pastas...")
    
    instancias = WhatsappInstance.objects.all()
    
    for instancia in instancias:
        cliente = instancia.cliente
        base_path = Path(__file__).parent / "media_storage" / f"cliente_{cliente.id}" / f"instance_{instancia.instance_id}"
        
        # Criar pastas para cada tipo de mídia
        tipos_midia = ['image', 'video', 'audio', 'document', 'sticker']
        
        for tipo in tipos_midia:
            tipo_path = base_path / tipo
            tipo_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Pasta {tipo}: {tipo_path}")

def main():
    """Função principal"""
    print("🚀 Processando mídias existentes...")
    print("=" * 50)
    
    # Criar estrutura de pastas
    criar_estrutura_pastas_midias()
    
    # Verificar mídias sem arquivo
    verificar_midias_sem_arquivo()
    
    # Processar mídias falhadas
    processar_midias_falhadas()
    
    print("\n" + "=" * 50)
    print("✅ Processamento concluído!")

if __name__ == "__main__":
    main() 