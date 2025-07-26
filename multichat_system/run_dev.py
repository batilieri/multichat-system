#!/usr/bin/env python
"""
Script para executar o MultiChat System em desenvolvimento.

Este script automatiza o processo de inicialização do projeto,
incluindo verificações de dependências, migrações e criação de dados de teste.
"""

import os
import sys
import subprocess
import django
from pathlib import Path

def run_command(command, description):
    """Executa um comando e exibe o resultado."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} concluído com sucesso!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao {description.lower()}:")
        print(f"Comando: {command}")
        print(f"Erro: {e.stderr}")
        return False

def check_dependencies():
    """Verifica se as dependências estão instaladas."""
    print("🔍 Verificando dependências...")
    
    try:
        import django
        import rest_framework
        import corsheaders
        print("✅ Todas as dependências estão instaladas!")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("💡 Execute: pip install -r requirements.txt")
        return False

def setup_database():
    """Configura o banco de dados."""
    print("🗄️ Configurando banco de dados...")
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
    django.setup()
    
    from django.core.management import execute_from_command_line
    
    # Executar migrações
    if not run_command("python manage.py makemigrations", "Criando migrações"):
        return False
    
    if not run_command("python manage.py migrate", "Aplicando migrações"):
        return False
    
    return True

def create_superuser():
    """Cria um superusuário se não existir."""
    print("👤 Verificando superusuário...")
    
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(is_superuser=True).exists():
            print("📝 Criando superusuário...")
            print("Use as credenciais padrão:")
            print("Email: admin@multichat.com")
            print("Senha: admin123")
            
            user = User.objects.create_superuser(
                username='admin',
                email='admin@multichat.com',
                password='admin123',
                tipo_usuario='admin'
            )
            print(f"✅ Superusuário criado: {user.email}")
        else:
            print("✅ Superusuário já existe!")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao criar superusuário: {e}")
        return False

def create_test_data():
    """Cria dados de teste se necessário."""
    print("📊 Verificando dados de teste...")
    
    try:
        from core.models import Cliente, Departamento
        
        if not Cliente.objects.all().exists():
            print("📝 Criando dados de teste...")
            run_command("python create_test_data.py", "Criando dados de teste")
        else:
            print("✅ Dados de teste já existem!")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar dados de teste: {e}")
        return False

def main():
    """Função principal."""
    print("🚀 Iniciando MultiChat System...")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not Path("manage.py").exists():
        print("❌ Execute este script no diretório multichat_system/")
        sys.exit(1)
    
    # Verificar dependências
    if not check_dependencies():
        sys.exit(1)
    
    # Configurar banco de dados
    if not setup_database():
        sys.exit(1)
    
    # Criar superusuário
    if not create_superuser():
        sys.exit(1)
    
    # Criar dados de teste
    if not create_test_data():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 MultiChat System configurado com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Execute: python manage.py runserver 0.0.0.0:8000")
    print("2. Acesse: http://localhost:8000")
    print("3. Admin: http://localhost:8000/admin")
    print("4. Credenciais admin: admin@multichat.com / admin123")
    print("\n🌐 Para o frontend:")
    print("1. cd ../multichat-frontend")
    print("2. npm install")
    print("3. npm run dev")
    print("4. Acesse: http://localhost:5173")
    print("=" * 50)

if __name__ == "__main__":
    main() 