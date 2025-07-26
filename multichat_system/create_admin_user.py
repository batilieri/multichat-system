#!/usr/bin/env python
"""
Script para criar um usuário administrador inicial no sistema MultiChat.

Este script cria um usuário com tipo 'admin' que terá acesso total ao sistema.
Execute este script após a primeira migração do banco de dados.

Uso:
    python manage.py shell < create_admin_user.py
    ou
    python create_admin_user.py
"""

import os
import sys
import django

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from authentication.models import Usuario

def create_admin_user():
    """
    Cria um usuário administrador inicial.
    """
    try:
        # Verificar se já existe um admin
        if Usuario.objects.filter(tipo_usuario='admin').exists():
            print("✅ Usuário administrador já existe!")
            admin = Usuario.objects.filter(tipo_usuario='admin').first()
            print(f"   Email: {admin.email}")
            print(f"   Nome: {admin.nome}")
            return
        
        # Criar usuário administrador
        admin_user = Usuario.objects.create_user(
            username='admin',
            email='admin@multichat.com',
            password='admin123',
            nome='Administrador do Sistema',
            tipo_usuario='admin',
            is_staff=True,
            is_superuser=True
        )
        
        print("✅ Usuário administrador criado com sucesso!")
        print(f"   Email: {admin_user.email}")
        print(f"   Senha: admin123")
        print(f"   Nome: {admin_user.nome}")
        print(f"   Tipo: {admin_user.tipo_usuario}")
        print("\n⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário administrador: {e}")

def create_sample_cliente():
    """
    Cria um cliente de exemplo.
    """
    try:
        from core.models import Cliente
        
        # Verificar se já existe um cliente
        if Cliente.objects.filter(email='cliente@exemplo.com').exists():
            print("✅ Cliente de exemplo já existe!")
            return
        
        # Criar cliente de exemplo
        cliente = Cliente.objects.create(
            nome='Cliente Exemplo',
            email='cliente@exemplo.com',
            telefone='(11) 99999-9999',
            empresa='Empresa Exemplo LTDA',
            ativo=True
        )
        
        print("✅ Cliente de exemplo criado com sucesso!")
        print(f"   Nome: {cliente.nome}")
        print(f"   Email: {cliente.email}")
        print(f"   Empresa: {cliente.empresa}")
        
    except Exception as e:
        print(f"❌ Erro ao criar cliente de exemplo: {e}")

def create_sample_colaborador():
    """
    Cria um colaborador de exemplo.
    """
    try:
        from core.models import Cliente
        
        # Buscar cliente de exemplo
        cliente = Cliente.objects.filter(email='cliente@exemplo.com').first()
        if not cliente:
            print("❌ Cliente de exemplo não encontrado. Execute create_sample_cliente() primeiro.")
            return
        
        # Verificar se já existe um colaborador
        if Usuario.objects.filter(email='colaborador@exemplo.com').exists():
            print("✅ Colaborador de exemplo já existe!")
            return
        
        # Criar colaborador de exemplo
        colaborador = Usuario.objects.create_user(
            username='colaborador',
            email='colaborador@exemplo.com',
            password='colab123',
            nome='Colaborador Exemplo',
            tipo_usuario='colaborador',
            cliente=cliente,
            telefone='(11) 88888-8888'
        )
        
        print("✅ Colaborador de exemplo criado com sucesso!")
        print(f"   Email: {colaborador.email}")
        print(f"   Senha: colab123")
        print(f"   Nome: {colaborador.nome}")
        print(f"   Cliente: {colaborador.cliente.nome}")
        
    except Exception as e:
        print(f"❌ Erro ao criar colaborador de exemplo: {e}")

if __name__ == '__main__':
    print("🚀 Criando dados iniciais do sistema MultiChat...\n")
    
    create_admin_user()
    print()
    
    create_sample_cliente()
    print()
    
    create_sample_colaborador()
    print()
    
    print("🎉 Configuração inicial concluída!")
    print("\n📋 Resumo dos usuários criados:")
    print("   Admin: admin@multichat.com / admin123")
    print("   Cliente: cliente@exemplo.com")
    print("   Colaborador: colaborador@exemplo.com / colab123")
    print("\n⚠️  Lembre-se de alterar as senhas após o primeiro login!") 