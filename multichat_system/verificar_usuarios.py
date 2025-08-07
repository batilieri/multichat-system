#!/usr/bin/env python3
"""
Script para verificar usuários existentes no sistema
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from authentication.models import Usuario

def verificar_usuarios():
    """Verifica usuários existentes no sistema"""
    print("👥 Verificando usuários existentes...")
    
    usuarios = Usuario.objects.all()
    
    if not usuarios.exists():
        print("❌ Nenhum usuário encontrado!")
        return
    
    print(f"📊 Total de usuários: {usuarios.count()}")
    
    for usuario in usuarios:
        print(f"\n👤 Usuário ID: {usuario.id}")
        print(f"   Email: {usuario.email}")
        print(f"   Username: {usuario.username}")
        print(f"   Nome: {usuario.nome}")
        print(f"   Tipo: {usuario.tipo_usuario}")
        print(f"   Ativo: {usuario.is_active}")
        print(f"   Admin: {usuario.is_superuser}")
        print(f"   Staff: {usuario.is_staff}")

def criar_usuario_admin():
    """Cria um usuário admin se não existir"""
    print("\n🔧 Criando usuário admin...")
    
    # Verificar se já existe um admin
    admin = Usuario.objects.filter(is_superuser=True).first()
    
    if admin:
        print(f"✅ Admin já existe: {admin.email}")
        return admin
    
    try:
        # Criar usuário admin
        admin = Usuario.objects.create_superuser(
            username='admin',
            email='admin@multichat.com',
            password='admin123',
            nome='Administrador',
            tipo_usuario='admin'
        )
        print(f"✅ Admin criado: {admin.email}")
        return admin
    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")
        return None

def testar_login_usuario(usuario):
    """Testa login com um usuário específico"""
    print(f"\n🔑 Testando login com {usuario.email}...")
    
    import requests
    
    login_data = {
        "email": usuario.email,
        "password": "admin123"  # Senha padrão
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login bem-sucedido!")
            print(f"🔑 Access Token: {data.get('access', '')[:50]}...")
            print(f"👤 Usuário: {data.get('user', {}).get('username', 'N/A')}")
            
            # Testar acesso com o token
            token = data.get('access')
            if token:
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.get("http://localhost:8000/api/mensagens/906/", headers=headers)
                
                if response.status_code == 200:
                    print("✅ Acesso com token funcionando!")
                    return token
                else:
                    print(f"❌ Erro ao acessar com token: {response.status_code}")
                    
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar login: {e}")
    
    return None

def main():
    """Função principal"""
    print("🚀 Verificando usuários do sistema...")
    print("=" * 60)
    
    # Verificar usuários existentes
    verificar_usuarios()
    
    # Criar admin se necessário
    admin = criar_usuario_admin()
    
    if admin:
        # Testar login
        token = testar_login_usuario(admin)
        
        if token:
            print(f"\n✅ Token válido obtido: {token[:50]}...")
            print("💡 Use este token no frontend para testar")
    
    print("\n" + "=" * 60)
    print("✅ Verificação de usuários concluída!")

if __name__ == "__main__":
    main() 