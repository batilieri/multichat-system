#!/usr/bin/env python
"""
Script para criar um usuário do tipo cliente associado ao cliente 'Elizeu Batiliere Dos Santos'.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from authentication.models import Usuario
from core.models import Cliente

nome = 'ELIZEU BATILIERE DOS SANTOS'
email = 'elizeu.batiliere@example.com'
telefone = '(11) 99999-9999'
empresa = 'Empresa Exemplo'

cliente, created = Cliente.objects.get_or_create(
    nome=nome,
    defaults={
        'email': email,
        'telefone': telefone,
        'empresa': empresa
    }
)

if created:
    print(f'Cliente criado: {cliente}')
else:
    print(f'Cliente já existe: {cliente}')

def criar_usuario_cliente():
    try:
        cliente = Cliente.objects.get(nome__icontains='elizeu')
        email = 'cliente.elizeu@empresa.com'
        if Usuario.objects.filter(email=email).exists():
            print(f"Usuário {email} já existe.")
            return
        usuario = Usuario.objects.create_user(
            username=email,
            email=email,
            password='senha123',
            nome='Cliente Elizeu',
            tipo_usuario='cliente',
            cliente=cliente
        )
        print(f"Usuário cliente criado: {usuario.email} (senha: senha123), associado ao cliente '{cliente.nome}'")
    except Cliente.DoesNotExist:
        print("Cliente com nome contendo 'elizeu' não encontrado.")

if __name__ == '__main__':
    criar_usuario_cliente() 