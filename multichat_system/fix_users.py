#!/usr/bin/env python
"""
Script para corrigir usuários existentes e criar um administrador.

Este script:
1. Cria um usuário administrador se não existir
2. Corrige usuários existentes que podem ter problemas
3. Verifica se todos os tipos de usuário estão corretos

Uso:
    python manage.py shell < fix_users.py
    ou
    python fix_users.py
"""

import os
import sys
import django

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from authentication.models import Usuario
from core.models import Cliente

def create_admin_user():
    """Cria um usuário administrador se não existir."""
    try:
        # Verificar se já existe um admin
        if Usuario.objects.filter(tipo_usuario='admin').exists():
            print("✅ Usuário administrador já existe!")
            admin = Usuario.objects.filter(tipo_usuario='admin').first()
            print(f"   Email: {admin.email}")
            print(f"   Nome: {admin.nome}")
            return admin
        else:
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
            return admin_user
            
    except Exception as e:
        print(f"❌ Erro ao criar usuário administrador: {e}")
        return None

def fix_existing_users():
    """Corrige usuários existentes que podem ter problemas."""
    try:
        # Verificar usuários sem tipo_usuario definido
        users_without_type = Usuario.objects.filter(tipo_usuario__isnull=True)
        if users_without_type.exists():
            print(f"🔄 Encontrados {users_without_type.count()} usuários sem tipo definido")
            for user in users_without_type:
                # Definir como colaborador por padrão
                user.tipo_usuario = 'colaborador'
                user.save()
                print(f"   ✅ Usuário {user.email} definido como colaborador")
        
        # Verificar usuários com cliente None mas tipo colaborador
        colaboradores_sem_cliente = Usuario.objects.filter(
            tipo_usuario='colaborador',
            cliente__isnull=True
        )
        if colaboradores_sem_cliente.exists():
            print(f"🔄 Encontrados {colaboradores_sem_cliente.count()} colaboradores sem cliente")
            for user in colaboradores_sem_cliente:
                print(f"   ⚠️  Usuário {user.email} é colaborador mas não tem cliente associado")
        
        # Verificar se há clientes sem usuário correspondente
        clientes = Cliente.objects.all()
        for cliente in clientes:
            if not Usuario.objects.filter(email=cliente.email).exists():
                print(f"   ⚠️  Cliente {cliente.email} não tem usuário correspondente")
                
    except Exception as e:
        print(f"❌ Erro ao corrigir usuários: {e}")

def create_sample_data():
    """Cria dados de exemplo se não existirem."""
    try:
        # Criar cliente de exemplo se não existir
        if not Cliente.objects.filter(email='cliente@exemplo.com').exists():
            cliente = Cliente.objects.create(
                nome='Cliente Exemplo',
                email='cliente@exemplo.com',
                telefone='(11) 99999-9999',
                empresa='Empresa Exemplo LTDA',
                ativo=True
            )
            print("✅ Cliente de exemplo criado")
        else:
            cliente = Cliente.objects.get(email='cliente@exemplo.com')
            print("✅ Cliente de exemplo já existe")
        
        # Criar colaborador de exemplo se não existir
        if not Usuario.objects.filter(email='colaborador@exemplo.com').exists():
            colaborador = Usuario.objects.create_user(
                username='colaborador',
                email='colaborador@exemplo.com',
                password='colab123',
                nome='Colaborador Exemplo',
                tipo_usuario='colaborador',
                cliente=cliente,
                telefone='(11) 88888-8888'
            )
            print("✅ Colaborador de exemplo criado")
        else:
            print("✅ Colaborador de exemplo já existe")
            
    except Exception as e:
        print(f"❌ Erro ao criar dados de exemplo: {e}")

def show_system_status():
    """Mostra o status atual do sistema."""
    try:
        admin_count = Usuario.objects.filter(tipo_usuario='admin').count()
        cliente_count = Usuario.objects.filter(tipo_usuario='cliente').count()
        colaborador_count = Usuario.objects.filter(tipo_usuario='colaborador').count()
        total_clientes = Cliente.objects.count()
        
        print("\n📊 Status do Sistema:")
        print(f"   - Administradores: {admin_count}")
        print(f"   - Clientes: {cliente_count}")
        print(f"   - Colaboradores: {colaborador_count}")
        print(f"   - Total de clientes: {total_clientes}")
        
        if admin_count > 0:
            print("✅ Sistema configurado corretamente!")
        else:
            print("❌ Nenhum administrador encontrado!")
            
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")

def main():
    """Função principal do script."""
    print("🔧 Corrigindo sistema MultiChat...")
    print("=" * 50)
    
    # Criar admin se necessário
    admin = create_admin_user()
    print()
    
    # Corrigir usuários existentes
    fix_existing_users()
    print()
    
    # Criar dados de exemplo
    create_sample_data()
    print()
    
    # Mostrar status
    show_system_status()
    print()
    
    print("🎉 Correção concluída!")
    print("\n📋 Credenciais de acesso:")
    print("   ┌─────────────────────────────────────────┐")
    print("   │ Administrador                           │")
    print("   │ Email: admin@multichat.com              │")
    print("   │ Senha: admin123                         │")
    print("   │ Acesso: Total ao sistema                │")
    print("   └─────────────────────────────────────────┘")
    print("")
    print("   ┌─────────────────────────────────────────┐")
    print("   │ Colaborador                             │")
    print("   │ Email: colaborador@exemplo.com          │")
    print("   │ Senha: colab123                         │")
    print("   │ Acesso: Apenas chat                     │")
    print("   └─────────────────────────────────────────┘")
    print("")
    print("⚠️  IMPORTANTE:")
    print("   - Altere as senhas após o primeiro login")
    print("   - O admin tem acesso total a todas as funcionalidades")
    print("   - Colaboradores veem apenas chat e dashboard")

if __name__ == '__main__':
    main() 