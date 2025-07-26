#!/usr/bin/env python
"""
Script para verificar os usuários existentes no sistema.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from authentication.models import Usuario
from core.models import Cliente

def verificar_usuarios():
    """Verifica os usuários existentes no sistema."""
    
    print("=== USUÁRIOS EXISTENTES ===")
    usuarios = Usuario.objects.all()
    
    for usuario in usuarios:
        print(f"\nID: {usuario.id}")
        print(f"Nome: {usuario.nome}")
        print(f"Email: {usuario.email}")
        print(f"Tipo: {usuario.tipo_usuario}")
        print(f"Cliente: {usuario.cliente}")
        print(f"Ativo: {usuario.is_active}")
        print(f"Superuser: {usuario.is_superuser}")
        print(f"Staff: {usuario.is_staff}")
        print("-" * 50)
    
    print("\n=== CLIENTES EXISTENTES ===")
    clientes = Cliente.objects.all()
    
    for cliente in clientes:
        print(f"\nID: {cliente.id}")
        print(f"Nome: {cliente.nome}")
        print(f"Email: {cliente.email}")
        print(f"Empresa: {cliente.empresa}")
        print("-" * 50)

if __name__ == '__main__':
    verificar_usuarios() 