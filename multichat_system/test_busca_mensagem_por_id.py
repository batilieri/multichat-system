#!/usr/bin/env python
"""
Script para testar a busca de mensagem por ID interno vs message_id.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem

def test_busca_mensagem_por_id():
    """Testa a busca de mensagem por ID interno vs message_id"""
    
    print("🧪 Testando busca de mensagem por ID interno vs message_id...")
    
    # Buscar uma mensagem com message_id
    mensagem = Mensagem.objects.filter(
        message_id__isnull=False
    ).exclude(message_id='').first()
    
    if not mensagem:
        print("❌ Nenhuma mensagem com message_id encontrada")
        return
    
    print(f"📋 Mensagem encontrada:")
    print(f"   - ID interno: {mensagem.id}")
    print(f"   - message_id: {mensagem.message_id}")
    
    # Testar busca por ID interno
    try:
        mensagem_por_id = Mensagem.objects.get(id=mensagem.id)
        print(f"✅ Busca por ID interno ({mensagem.id}) funcionou!")
    except Mensagem.DoesNotExist:
        print(f"❌ Busca por ID interno ({mensagem.id}) falhou!")
    
    # Testar busca por message_id
    try:
        mensagem_por_message_id = Mensagem.objects.get(message_id=mensagem.message_id)
        print(f"✅ Busca por message_id ({mensagem.message_id}) funcionou!")
    except Mensagem.DoesNotExist:
        print(f"❌ Busca por message_id ({mensagem.message_id}) falhou!")
    
    # Testar busca por message_id como se fosse ID interno
    try:
        mensagem_por_message_id_como_id = Mensagem.objects.get(id=mensagem.message_id)
        print(f"✅ Busca por message_id como ID interno funcionou!")
    except Mensagem.DoesNotExist:
        print(f"❌ Busca por message_id como ID interno falhou!")
    except ValueError:
        print(f"❌ message_id não é um ID válido (não é número)")

if __name__ == "__main__":
    test_busca_mensagem_por_id() 