#!/usr/bin/env python3
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem

def verificar_mensagens():
    total = Mensagem.objects.count()
    midias = Mensagem.objects.filter(tipo__in=['audio', 'imagem', 'video', 'sticker', 'documento']).count()
    
    print(f"Total de mensagens: {total}")
    print(f"Mensagens com mídia: {midias}")
    
    # Verificar tipos específicos
    for tipo in ['audio', 'imagem', 'video', 'sticker', 'documento']:
        count = Mensagem.objects.filter(tipo=tipo).count()
        print(f"- {tipo}: {count}")

if __name__ == '__main__':
    verificar_mensagens() 