#!/usr/bin/env python
"""
Script para corrigir usuários existentes no sistema.

Este script corrige os usuários que já existem no banco de dados.
"""

import os
import sys
import django

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from authentication.models import Usuario
from core.models import Cliente

def correct_existing_users():
    """Corrige os usuários existentes."""
    try:
        print("🔧 Corrigindo usuários existentes...")
        
        # Corrigir admin@test.com
        try:
            user = Usuario.objects.get(email='admin@test.com')
            user.tipo_usuario = 'admin'
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print("✅ admin@test.com corrigido para admin")
        except Usuario.DoesNotExist:
            print("❌ admin@test.com não encontrado")
        
        # Corrigir admin@multichat.com
        try:
            user = Usuario.objects.get(email='admin@multichat.com')
            user.tipo_usuario = 'admin'
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print("✅ admin@multichat.com corrigido para admin")
        except Usuario.DoesNotExist:
            print("❌ admin@multichat.com não encontrado")
        
        # Corrigir colaborador@multichat.com
        try:
            user = Usuario.objects.get(email='colaborador@multichat.com')
            # Buscar cliente para associar
            cliente = Cliente.objects.first()
            if cliente:
                user.cliente = cliente
                user.tipo_usuario = 'colaborador'
                user.save()
                print(f"✅ colaborador@multichat.com associado ao cliente {cliente.nome}")
            else:
                print("❌ Nenhum cliente encontrado para associar")
        except Usuario.DoesNotExist:
            print("❌ colaborador@multichat.com não encontrado")
        
        # Criar usuário para cliente teste@empresa.com
        try:
            cliente = Cliente.objects.get(email='teste@empresa.com')
            if not Usuario.objects.filter(email='teste@empresa.com').exists():
                user = Usuario.objects.create_user(
                    username='cliente_teste',
                    email='teste@empresa.com',
                    password='cliente123',
                    nome='Cliente Teste',
                    tipo_usuario='cliente',
                    telefone='(11) 77777-7777'
                )
                print("✅ Usuário criado para cliente teste@empresa.com")
            else:
                print("✅ Usuário já existe para teste@empresa.com")
        except Cliente.DoesNotExist:
            print("❌ Cliente teste@empresa.com não encontrado")
            
    except Exception as e:
        print(f"❌ Erro ao corrigir usuários: {e}")

def show_final_status():
    """Mostra o status final do sistema."""
    try:
        admin_count = Usuario.objects.filter(tipo_usuario='admin').count()
        cliente_count = Usuario.objects.filter(tipo_usuario='cliente').count()
        colaborador_count = Usuario.objects.filter(tipo_usuario='colaborador').count()
        total_clientes = Cliente.objects.count()
        
        print("\n📊 Status Final do Sistema:")
        print(f"   - Administradores: {admin_count}")
        print(f"   - Clientes: {cliente_count}")
        print(f"   - Colaboradores: {colaborador_count}")
        print(f"   - Total de clientes: {total_clientes}")
        
        if admin_count > 0:
            print("✅ Sistema configurado corretamente!")
            
            # Mostrar admins
            admins = Usuario.objects.filter(tipo_usuario='admin')
            print("\n👑 Administradores:")
            for admin in admins:
                print(f"   - {admin.email} ({admin.nome})")
        else:
            print("❌ Nenhum administrador encontrado!")
            
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")

def main():
    """Função principal."""
    print("🔧 Corrigindo usuários existentes...")
    print("=" * 50)
    
    correct_existing_users()
    print()
    show_final_status()
    print()
    
    print("🎉 Correção concluída!")
    print("\n📋 Credenciais de acesso:")
    print("   ┌─────────────────────────────────────────┐")
    print("   │ Administrador                           │")
    print("   │ Email: admin@multichat.com              │")
    print("   │ Senha: (senha atual)                    │")
    print("   │ Acesso: Total ao sistema                │")
    print("   └─────────────────────────────────────────┘")
    print("")
    print("   ┌─────────────────────────────────────────┐")
    print("   │ Cliente                                 │")
    print("   │ Email: teste@empresa.com                │")
    print("   │ Senha: cliente123                       │")
    print("   │ Acesso: Gerenciar colaboradores         │")
    print("   └─────────────────────────────────────────┘")
    print("")
    print("⚠️  IMPORTANTE:")
    print("   - O admin tem acesso total a todas as funcionalidades")
    print("   - Clientes podem gerenciar colaboradores")
    print("   - Colaboradores veem apenas chat e dashboard")

if __name__ == '__main__':
    main() 