#!/usr/bin/env python
"""
Script para verificar os nomes dos clientes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Cliente

def verificar_clientes():
    """Verifica os nomes dos clientes cadastrados"""
    print("👤 CLIENTES CADASTRADOS")
    print("=" * 40)
    
    clientes = Cliente.objects.all()
    
    for cliente in clientes:
        print(f"ID: {cliente.id}")
        print(f"Nome: '{cliente.nome}'")
        print(f"Email: {cliente.email}")
        print(f"Telefone: {cliente.telefone}")
        print("-" * 40)

if __name__ == "__main__":
    verificar_clientes() 