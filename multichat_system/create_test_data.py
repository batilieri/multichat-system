#!/usr/bin/env python
"""
Script para criar dados de teste para o MultiChat System
"""

import os
import sys
import django
from django.contrib.auth.hashers import make_password
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Cliente, Departamento
from authentication.models import Usuario

def create_test_data():
    print("Criando dados de teste...")
    
    # Criar cliente de teste
    cliente, created = Cliente.objects.get_or_create(
        email='teste@empresa.com',
        defaults={
            'nome': 'Empresa Teste Ltda',
            'empresa': 'Empresa Teste Ltda',
            'telefone': '5511999999999',
            'ativo': True
        }
    )
    
    if created:
        print(f"Cliente criado: {cliente.nome}")
    else:
        print(f"Cliente já existe: {cliente.nome}")
    
    # Criar departamento
    departamento, created = Departamento.objects.get_or_create(
        cliente=cliente,
        nome='Suporte',
        defaults={
            'ativo': True
        }
    )
    
    if created:
        print(f"Departamento criado: {departamento.nome}")
    else:
        print(f"Departamento já existe: {departamento.nome}")
    
    # Criar usuário de teste
    usuario, created = Usuario.objects.get_or_create(
        username='admin@multichat.com',
        defaults={
            'email': 'admin@multichat.com',
            'first_name': 'Administrador',
            'telefone': '5511999999999',
            'password': make_password('admin123'),
            'tipo_usuario': 'admin',
            'cliente': cliente,
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    if created:
        print(f"Usuário criado: {usuario.first_name} ({usuario.email})")
    else:
        print(f"Usuário já existe: {usuario.first_name} ({usuario.email})")
    
    # Criar usuário colaborador
    colaborador, created = Usuario.objects.get_or_create(
        username='colaborador@multichat.com',
        defaults={
            'email': 'colaborador@multichat.com',
            'first_name': 'João',
            'last_name': 'Silva',
            'telefone': '5511888888888',
            'password': make_password('123456'),
            'tipo_usuario': 'colaborador',
            'cliente': cliente
        }
    )
    
    if created:
        print(f"Colaborador criado: {colaborador.first_name} {colaborador.last_name} ({colaborador.email})")
    else:
        print(f"Colaborador já existe: {colaborador.first_name} {colaborador.last_name} ({colaborador.email})")
    
    print("\nDados de teste criados com sucesso!")
    print("\nCredenciais de login:")
    print("Email: admin@multichat.com")
    print("Senha: admin123")
    print("\nOu:")
    print("Email: colaborador@multichat.com")
    print("Senha: 123456")

if __name__ == '__main__':
    create_test_data()

