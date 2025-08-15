#!/usr/bin/env python3
"""
Script para testar o sistema de autenticação do MultiChat
Verifica se os tokens JWT estão sendo gerados e renovados corretamente
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
django.setup()

from django.contrib.auth import get_user_model
from authentication.models import Usuario

User = get_user_model()

def testar_sistema_autenticacao():
    """Testa o sistema de autenticação completo"""
    print("🔐 TESTANDO SISTEMA DE AUTENTICAÇÃO")
    print("=" * 60)
    
    API_BASE_URL = "http://localhost:8000"
    
    # 1. Verificar se o servidor está rodando
    try:
        response = requests.get(f"{API_BASE_URL}/api/", timeout=5)
        print(f"✅ Servidor rodando: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Servidor não está rodando: {e}")
        return
    
    # 2. Buscar usuário para teste
    try:
        user = Usuario.objects.filter(is_active=True).first()
        if not user:
            print("❌ Nenhum usuário ativo encontrado")
            return
        
        print(f"👤 Usuário de teste: {user.email}")
        print(f"   Tipo: {getattr(user, 'tipo_usuario', 'N/A')}")
        print(f"   Ativo: {user.is_active}")
        
    except Exception as e:
        print(f"❌ Erro ao buscar usuário: {e}")
        return
    
    # 3. Testar login
    print(f"\n🔑 Testando login...")
    try:
        login_data = {
            "email": user.email,
            "password": "admin123"  # Senha padrão, ajustar se necessário
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login/",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login bem-sucedido")
            print(f"   Access Token: {data.get('access', 'N/A')[:20]}...")
            print(f"   Refresh Token: {data.get('refresh', 'N/A')[:20]}...")
            print(f"   Usuário: {data.get('user', {}).get('email', 'N/A')}")
            
            access_token = data.get('access')
            refresh_token = data.get('refresh')
            
            # 4. Testar endpoint protegido
            print(f"\n🔒 Testando endpoint protegido...")
            headers = {"Authorization": f"Bearer {access_token}"}
            
            response = requests.get(
                f"{API_BASE_URL}/api/chats/",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Endpoint protegido acessível")
                chats_data = response.json()
                print(f"   Total de chats: {len(chats_data.get('results', chats_data))}")
            else:
                print(f"❌ Endpoint protegido retornou: {response.status_code}")
                print(f"   Resposta: {response.text}")
            
            # 5. Testar refresh token
            print(f"\n🔄 Testando refresh token...")
            refresh_data = {"refresh": refresh_token}
            
            response = requests.post(
                f"{API_BASE_URL}/api/auth/refresh/",
                json=refresh_data,
                timeout=10
            )
            
            if response.status_code == 200:
                refresh_response = response.json()
                print(f"✅ Refresh token funcionando")
                print(f"   Novo Access Token: {refresh_response.get('access', 'N/A')[:20]}...")
                
                # Verificar se o novo token funciona
                new_headers = {"Authorization": f"Bearer {refresh_response.get('access')}"}
                response = requests.get(
                    f"{API_BASE_URL}/api/chats/",
                    headers=new_headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"✅ Novo token funcionando corretamente")
                else:
                    print(f"❌ Novo token não está funcionando: {response.status_code}")
            else:
                print(f"❌ Refresh token falhou: {response.status_code}")
                print(f"   Resposta: {response.text}")
            
            # 6. Testar endpoint de check-updates
            print(f"\n📡 Testando endpoint check-updates...")
            last_check = (datetime.now() - timedelta(minutes=5)).isoformat()
            
            response = requests.get(
                f"{API_BASE_URL}/api/chats/check-updates/?last_check={last_check}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                updates_data = response.json()
                print(f"✅ Endpoint check-updates funcionando")
                print(f"   Tem atualizações: {updates_data.get('has_updates', False)}")
                print(f"   Timestamp: {updates_data.get('timestamp', 'N/A')}")
                
                if updates_data.get('updates'):
                    print(f"   Total de atualizações: {len(updates_data['updates'])}")
            else:
                print(f"❌ Endpoint check-updates falhou: {response.status_code}")
                print(f"   Resposta: {response.text}")
            
            # 7. Testar token expirado (simular)
            print(f"\n⏰ Testando comportamento com token inválido...")
            invalid_headers = {"Authorization": "Bearer invalid_token_here"}
            
            response = requests.get(
                f"{API_BASE_URL}/api/chats/",
                headers=invalid_headers,
                timeout=10
            )
            
            if response.status_code == 401:
                print(f"✅ Sistema rejeita tokens inválidos corretamente")
            else:
                print(f"⚠️ Sistema não rejeitou token inválido: {response.status_code}")
            
        else:
            print(f"❌ Login falhou: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n" + "=" * 60)
    print("🔍 VERIFICANDO CONFIGURAÇÕES JWT")
    print("=" * 60)
    
    # Verificar configurações JWT
    try:
        from django.conf import settings
        
        jwt_config = getattr(settings, 'SIMPLE_JWT', {})
        
        print(f"📋 Configurações JWT:")
        print(f"   ACCESS_TOKEN_LIFETIME: {jwt_config.get('ACCESS_TOKEN_LIFETIME', 'N/A')}")
        print(f"   REFRESH_TOKEN_LIFETIME: {jwt_config.get('REFRESH_TOKEN_LIFETIME', 'N/A')}")
        print(f"   ROTATE_REFRESH_TOKENS: {jwt_config.get('ROTATE_REFRESH_TOKENS', 'N/A')}")
        print(f"   BLACKLIST_AFTER_ROTATION: {jwt_config.get('BLACKLIST_AFTER_ROTATION', 'N/A')}")
        
        # Verificar se os tempos estão corretos
        access_lifetime = jwt_config.get('ACCESS_TOKEN_LIFETIME')
        if access_lifetime and hasattr(access_lifetime, 'total_seconds'):
            hours = access_lifetime.total_seconds() / 3600
            print(f"   ⏱️  Token de acesso expira em: {hours:.1f} horas")
            
            if hours >= 24:
                print(f"   ✅ Tempo de vida adequado para sistema de tempo real")
            else:
                print(f"   ⚠️  Tempo de vida pode ser muito curto para sistema de tempo real")
        
    except Exception as e:
        print(f"❌ Erro ao verificar configurações JWT: {e}")
    
    print(f"\n🎯 Teste de autenticação concluído!")

if __name__ == "__main__":
    testar_sistema_autenticacao() 