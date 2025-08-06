
#!/usr/bin/env python3
"""
Script para reprocessar mídias que falharam no download
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

from core.models import MediaFile, WhatsappInstance
from webhook.views import save_media_file

def reprocessar_midias_falhadas():
    """Reprocessa mídias que falharam no download"""
    print("🔄 Rep processando mídias falhadas...")
    
    # Buscar mídias que falharam
    midias_falhadas = MediaFile.objects.filter(download_status='failed')
    
    if not midias_falhadas.exists():
        print("✅ Nenhuma mídia falhada encontrada!")
        return
    
    print(f"📊 Encontradas {midias_falhadas.count()} mídias falhadas")
    
    for midia in midias_falhadas:
        print(f"\n📎 Processando mídia {midia.id}: {midia.media_type}")
        
        try:
            # Tentar baixar novamente (simular com dados de teste)
            file_link = f"https://api.w-api.app/media/test/{midia.message_id}"
            
            resultado = save_media_file(
                file_link,
                midia.media_type,
                midia.message_id,
                midia.sender_name,
                midia.cliente,
                midia.instance
            )
            
            if resultado:
                print(f"✅ Mídia {midia.id} reprocessada com sucesso!")
                midia.download_status = 'success'
                midia.file_path = resultado
                midia.save()
            else:
                print(f"❌ Falha ao reprocessar mídia {midia.id}")
                
        except Exception as e:
            print(f"❌ Erro ao reprocessar mídia {midia.id}: {e}")

if __name__ == "__main__":
    reprocessar_midias_falhadas()
