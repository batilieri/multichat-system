
#!/usr/bin/env python3
"""
Script para monitorar downloads de mídia em tempo real
"""

import os
import sys
import django
import time
from datetime import datetime, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import MediaFile

def monitorar_downloads():
    """Monitora downloads de mídia em tempo real"""
    print("📊 Monitorando downloads de mídia...")
    print("Pressione Ctrl+C para parar")
    
    ultima_verificacao = datetime.now()
    
    try:
        while True:
            # Verificar novas mídias
            novas_midias = MediaFile.objects.filter(
                created_at__gte=ultima_verificacao
            ).order_by('-created_at')
            
            if novas_midias.exists():
                print(f"\n🆕 {novas_midias.count()} nova(s) mídia(s) encontrada(s):")
                
                for midia in novas_midias:
                    print(f"   📎 {midia.media_type} - {midia.sender_name}")
                    print(f"      Status: {midia.download_status}")
                    print(f"      Arquivo: {midia.file_name}")
                    if midia.file_path:
                        existe = os.path.exists(midia.file_path)
                        print(f"      Existe: {'✅' if existe else '❌'}")
            
            ultima_verificacao = datetime.now()
            time.sleep(5)  # Verificar a cada 5 segundos
            
    except KeyboardInterrupt:
        print("\n⏹️  Monitoramento interrompido")

if __name__ == "__main__":
    monitorar_downloads()
