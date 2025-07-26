#!/usr/bin/env python
"""
Script de configuração completa do sistema MultiChat.

Este script automatiza todo o processo de configuração inicial:
1. Executa migrações
2. Cria usuários iniciais
3. Configura dados de exemplo
4. Verifica se tudo está funcionando

Uso:
    python setup_system.py
"""

import os
import sys
import django
import subprocess
from pathlib import Path

def run_command(command, description):
    """Executa um comando e mostra o resultado."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode == 0:
            print(f"✅ {description} concluído com sucesso!")
            if result.stdout:
                print(f"   Saída: {result.stdout.strip()}")
        else:
            print(f"❌ Erro em {description}:")
            print(f"   {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao executar {description}: {e}")
        return False
    return True

def setup_django():
    """Configura o ambiente Django."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
    django.setup()

def create_migrations():
    """Cria e executa as migrações."""
    commands = [
        ("python manage.py makemigrations", "Criando migrações"),
        ("python manage.py migrate", "Executando migrações"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True

def create_initial_data():
    """Cria dados iniciais do sistema."""
    print("\n🔄 Criando dados iniciais...")
    
    try:
        # Importar após setup do Django
        from authentication.models import Usuario
        from core.models import Cliente
        
        # Criar usuário administrador
        if not Usuario.objects.filter(tipo_usuario='admin').exists():
            admin_user = Usuario.objects.create_user(
                username='admin',
                email='admin@multichat.com',
                password='admin123',
                nome='Administrador do Sistema',
                tipo_usuario='admin',
                is_staff=True,
                is_superuser=True
            )
            print("✅ Usuário administrador criado")
        else:
            print("✅ Usuário administrador já existe")
        
        # Criar cliente de exemplo
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
            print("✅ Cliente de exemplo já existe")
        
        # Criar colaborador de exemplo
        cliente = Cliente.objects.filter(email='cliente@exemplo.com').first()
        if cliente and not Usuario.objects.filter(email='colaborador@exemplo.com').exists():
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
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar dados iniciais: {e}")
        return False

def verify_system():
    """Verifica se o sistema está funcionando corretamente."""
    print("\n🔄 Verificando sistema...")
    
    try:
        from authentication.models import Usuario
        from core.models import Cliente
        
        # Verificar usuários
        admin_count = Usuario.objects.filter(tipo_usuario='admin').count()
        cliente_count = Usuario.objects.filter(tipo_usuario='cliente').count()
        colaborador_count = Usuario.objects.filter(tipo_usuario='colaborador').count()
        total_clientes = Cliente.objects.count()
        
        print(f"✅ Usuários no sistema:")
        print(f"   - Administradores: {admin_count}")
        print(f"   - Clientes: {cliente_count}")
        print(f"   - Colaboradores: {colaborador_count}")
        print(f"   - Total de clientes: {total_clientes}")
        
        if admin_count > 0:
            print("✅ Sistema configurado corretamente!")
            return True
        else:
            print("❌ Nenhum administrador encontrado!")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar sistema: {e}")
        return False

def show_credentials():
    """Mostra as credenciais de acesso."""
    print("\n🎉 Configuração concluída!")
    print("\n📋 Credenciais de acesso:")
    print("   ┌─────────────────────────────────────────┐")
    print("   │ Administrador                           │")
    print("   │ Email: admin@multichat.com              │")
    print("   │ Senha: admin123                         │")
    print("   │ Acesso: Total ao sistema                │")
    print("   └─────────────────────────────────────────┘")
    print("")
    print("   ┌─────────────────────────────────────────┐")
    print("   │ Cliente                                 │")
    print("   │ Email: cliente@exemplo.com              │")
    print("   │ Senha: (criar via admin)                │")
    print("   │ Acesso: Gerenciar colaboradores         │")
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
    print("   - Use HTTPS em produção")
    print("   - Configure CORS adequadamente")
    print("")
    print("🚀 Para iniciar o sistema:")
    print("   Backend: python manage.py runserver")
    print("   Frontend: npm run dev (na pasta multichat-frontend)")

def main():
    """Função principal do script."""
    print("🚀 Configurando sistema MultiChat...")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not Path("manage.py").exists():
        print("❌ Execute este script na pasta multichat_system/")
        return False
    
    # Setup do Django
    setup_django()
    
    # Executar migrações
    if not create_migrations():
        print("❌ Falha nas migrações!")
        return False
    
    # Criar dados iniciais
    if not create_initial_data():
        print("❌ Falha ao criar dados iniciais!")
        return False
    
    # Verificar sistema
    if not verify_system():
        print("❌ Falha na verificação do sistema!")
        return False
    
    # Mostrar credenciais
    show_credentials()
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 