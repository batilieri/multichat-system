#!/usr/bin/env python3
"""
Teste para verificar se o método enviar_imagem está sendo registrado
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Inicializar Django
django.setup()

from api.views import ChatViewSet

def check_method_registration():
    """Verifica se o método enviar_imagem está registrado"""
    
    print("🔍 Verificando registro do método enviar_imagem...")
    
    # Verificar se o método existe
    if hasattr(ChatViewSet, 'enviar_imagem'):
        print("✅ Método enviar_imagem existe")
        
        # Verificar se é uma action
        method = getattr(ChatViewSet, 'enviar_imagem')
        if hasattr(method, 'detail') and hasattr(method, 'url_path'):
            print(f"✅ É uma action válida")
            print(f"   detail: {method.detail}")
            print(f"   url_path: {method.url_path}")
            print(f"   methods: {getattr(method, 'mapping', 'N/A')}")
        else:
            print("❌ Não é uma action válida")
    else:
        print("❌ Método enviar_imagem não existe")
    
    # Listar todas as actions do ChatViewSet
    print("\n📋 Todas as actions do ChatViewSet:")
    actions = []
    for attr_name in dir(ChatViewSet):
        attr = getattr(ChatViewSet, attr_name)
        if hasattr(attr, 'detail') and hasattr(attr, 'url_path'):
            actions.append({
                'name': attr_name,
                'url_path': attr.url_path,
                'detail': attr.detail,
                'methods': getattr(attr, 'mapping', ['get'])
            })
    
    for action in actions:
        print(f"  - {action['name']}: {action['url_path']} (detail={action['detail']}, methods={action['methods']})")

def test_import_requests():
    """Testa se o módulo requests está disponível"""
    
    print("\n🔍 Testando importação do requests...")
    
    try:
        import requests
        print("✅ Módulo requests disponível")
    except ImportError as e:
        print(f"❌ Erro ao importar requests: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando verificação do método...")
    
    check_method_registration()
    test_import_requests()
    
    print("\n✅ Verificação concluída!") 