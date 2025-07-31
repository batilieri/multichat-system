#!/usr/bin/env python3
"""
Teste para verificar se as URLs do Django estão sendo registradas corretamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')

# Adicionar o diretório atual ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Inicializar Django
django.setup()

from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver

def listar_urls():
    """Lista todas as URLs registradas"""
    
    print("🔍 Listando URLs registradas...")
    
    # Obter o resolver principal
    resolver = get_resolver()
    
    def print_urls(url_patterns, prefix=''):
        for pattern in url_patterns:
            if hasattr(pattern, 'url_patterns'):
                # É um URLResolver (grupo de URLs)
                print(f"{prefix}📁 {pattern.pattern}")
                print_urls(pattern.url_patterns, prefix + '  ')
            else:
                # É um URLPattern (URL individual)
                if hasattr(pattern, 'name') and pattern.name:
                    print(f"{prefix}🔗 {pattern.pattern} -> {pattern.name}")
                else:
                    print(f"{prefix}🔗 {pattern.pattern}")
    
    print_urls(resolver.url_patterns)

def verificar_endpoint_imagem():
    """Verifica especificamente o endpoint de imagem"""
    
    print("\n🔍 Verificando endpoint de imagem...")
    
    # Verificar se o ChatViewSet está registrado
    from api.views import ChatViewSet
    
    # Listar actions do ChatViewSet
    actions = []
    for attr_name in dir(ChatViewSet):
        attr = getattr(ChatViewSet, attr_name)
        if hasattr(attr, 'detail') and hasattr(attr, 'url_path'):
            actions.append({
                'name': attr_name,
                'url_path': attr.url_path,
                'methods': attr.mapping if hasattr(attr, 'mapping') else ['get']
            })
    
    print(f"📱 Actions do ChatViewSet:")
    for action in actions:
        print(f"  - {action['name']}: {action['url_path']} ({', '.join(action['methods'])})")
    
    # Verificar se enviar_imagem está na lista
    enviar_imagem_action = next((a for a in actions if a['name'] == 'enviar_imagem'), None)
    
    if enviar_imagem_action:
        print(f"✅ Action 'enviar_imagem' encontrada!")
        print(f"   URL Path: {enviar_imagem_action['url_path']}")
        print(f"   Methods: {enviar_imagem_action['methods']}")
    else:
        print("❌ Action 'enviar_imagem' NÃO encontrada!")
        
        # Verificar se o método existe
        if hasattr(ChatViewSet, 'enviar_imagem'):
            print("⚠️ Método existe mas não foi registrado como action")
        else:
            print("❌ Método não existe")

def testar_importacao_enviar_imagem():
    """Testa se a importação do EnviarImagem funciona"""
    
    print("\n🔍 Testando importação do EnviarImagem...")
    
    try:
        # Adicionar o caminho para o módulo wapi
        wapi_path = os.path.join(current_dir, '..', 'wapi')
        sys.path.insert(0, wapi_path)
        
        from mensagem.enviosMensagensDocs.enviarImagem import EnviarImagem
        print("✅ Importação do EnviarImagem funcionou!")
        
        # Testar criação da classe
        try:
            instance = EnviarImagem("test_instance", "test_token")
            print("✅ Criação da classe EnviarImagem funcionou!")
        except Exception as e:
            print(f"❌ Erro ao criar instância: {e}")
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def verificar_urls_api():
    """Verifica URLs específicas da API"""
    
    print("\n🔍 Verificando URLs da API...")
    
    # URLs esperadas
    expected_urls = [
        '/api/chats/',
        '/api/chats/{id}/',
        '/api/chats/{id}/enviar-imagem/',
        '/api/mensagens/',
        '/api/mensagens/{id}/reagir/',
        '/api/mensagens/{id}/remover-reacao/',
    ]
    
    resolver = get_resolver()
    
    def find_url_pattern(url_patterns, target_path):
        for pattern in url_patterns:
            if hasattr(pattern, 'url_patterns'):
                result = find_url_pattern(pattern.url_patterns, target_path)
                if result:
                    return result
            else:
                if target_path in str(pattern.pattern):
                    return pattern
        return None
    
    for expected_url in expected_urls:
        pattern = find_url_pattern(resolver.url_patterns, expected_url)
        if pattern:
            print(f"✅ {expected_url}")
        else:
            print(f"❌ {expected_url}")

if __name__ == "__main__":
    print("🚀 Iniciando verificação de URLs...")
    
    # Listar todas as URLs
    listar_urls()
    
    # Verificar endpoint de imagem
    verificar_endpoint_imagem()
    
    # Testar importação
    testar_importacao_enviar_imagem()
    
    # Verificar URLs da API
    verificar_urls_api()
    
    print("\n✅ Verificação concluída!") 