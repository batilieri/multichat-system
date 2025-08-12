#!/usr/bin/env python3
"""
Diagnóstico completo do problema de envio de imagem
Analisa todos os componentes: instância, chat_id, token e formato da imagem
"""

import sys
import os
import json
import base64
import requests
from urllib.parse import urlparse

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verificar_instancia_whatsapp():
    """Verifica se a instância do WhatsApp está configurada e ativa"""
    print("🔍 Verificando instância do WhatsApp...")
    
    try:
        # Importar Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
        import django
        django.setup()
        
        from core.models import WhatsappInstance
        
        # Buscar instâncias
        instances = WhatsappInstance.objects.all()
        
        if not instances.exists():
            print("❌ Nenhuma instância do WhatsApp encontrada")
            return False
        
        print(f"📱 Encontradas {instances.count()} instância(s):")
        
        for instance in instances:
            print(f"  - ID: {instance.instance_id}")
            print(f"  - Cliente: {instance.cliente.nome if instance.cliente else 'N/A'}")
            print(f"  - Token: {'✅ Configurado' if instance.token else '❌ Não configurado'}")
            print(f"  - Status: {instance.status if hasattr(instance, 'status') else 'N/A'}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar instâncias: {e}")
        return False

def verificar_chats():
    """Verifica se existem chats configurados"""
    print("💬 Verificando chats...")
    
    try:
        from core.models import Chat
        
        chats = Chat.objects.all()
        
        if not chats.exists():
            print("❌ Nenhum chat encontrado")
            return False
        
        print(f"📋 Encontrados {chats.count()} chat(s):")
        
        for chat in chats[:5]:  # Mostrar apenas os 5 primeiros
            print(f"  - ID: {chat.id}")
            print(f"  - Chat ID: {chat.chat_id}")
            print(f"  - Cliente: {chat.cliente.nome if chat.cliente else 'N/A'}")
            print(f"  - Nome: {chat.nome}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar chats: {e}")
        return False

def testar_token_wapi():
    """Testa se o token da W-API está funcionando"""
    print("🔑 Testando token da W-API...")
    
    try:
        from core.models import WhatsappInstance
        
        instance = WhatsappInstance.objects.first()
        
        if not instance or not instance.token:
            print("❌ Instância ou token não encontrado")
            return False
        
        # Testar status da instância
        url = "https://api.w-api.app/v1/auth/status"
        headers = {
            "Authorization": f"Bearer {instance.token}",
            "Content-Type": "application/json"
        }
        params = {"instanceId": instance.instance_id}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Token válido - Status: {data.get('status', 'N/A')}")
            return True
        else:
            print(f"❌ Token inválido ou instância inativa")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar token: {e}")
        return False

def testar_formato_base64():
    """Testa diferentes formatos de base64"""
    print("🖼️ Testando formatos de base64...")
    
    # Teste 1: Base64 simples (sem data URL)
    base64_simples = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    # Teste 2: Base64 com data URL
    base64_data_url = f"data:image/png;base64,{base64_simples}"
    
    # Teste 3: Base64 com data URL JPEG
    base64_jpeg = f"data:image/jpeg;base64,{base64_simples}"
    
    formatos_teste = [
        ("Base64 simples", base64_simples),
        ("Data URL PNG", base64_data_url),
        ("Data URL JPEG", base64_jpeg)
    ]
    
    for nome, formato in formatos_teste:
        print(f"\n📝 Testando: {nome}")
        print(f"   Tamanho: {len(formato)} caracteres")
        print(f"   Inicia com: {formato[:20]}...")
        
        # Verificar se é base64 válido
        try:
            if formato.startswith('data:'):
                # Extrair apenas a parte base64
                base64_part = formato.split(',')[1]
                decoded = base64.b64decode(base64_part)
                print(f"   ✅ Base64 válido (decodificado: {len(decoded)} bytes)")
            else:
                decoded = base64.b64decode(formato)
                print(f"   ✅ Base64 válido (decodificado: {len(decoded)} bytes)")
        except Exception as e:
            print(f"   ❌ Base64 inválido: {e}")
    
    return True

def testar_envio_imagem_real():
    """Testa o envio real de imagem"""
    print("🚀 Testando envio real de imagem...")
    
    try:
        from core.models import WhatsappInstance, Chat
        
        # Buscar instância e chat
        instance = WhatsappInstance.objects.first()
        chat = Chat.objects.first()
        
        if not instance or not chat:
            print("❌ Instância ou chat não encontrado")
            return False
        
        if not instance.token:
            print("❌ Token não configurado")
            return False
        
        # Criar imagem de teste
        test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        # Testar com a classe EnviarImagem
        from multichat_system.api.views import EnviarImagem
        
        imagem_wapi = EnviarImagem(instance.instance_id, instance.token)
        
        # Extrair número do telefone
        phone = chat.chat_id.split('@')[0] if '@' in chat.chat_id else chat.chat_id
        
        print(f"📱 Enviando para: {phone}")
        print(f"🖼️ Tamanho da imagem: {len(test_image_base64)} caracteres")
        
        # Testar envio
        result = imagem_wapi.enviar_imagem_base64(
            phone=phone,
            image_base64=test_image_base64,
            caption="Teste de diagnóstico",
            delay=1
        )
        
        print(f"📡 Resultado: {json.dumps(result, indent=2)}")
        
        if result['sucesso']:
            print("✅ Envio bem-sucedido!")
            return True
        else:
            print(f"❌ Falha no envio: {result['erro']}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de envio: {e}")
        return False

def testar_endpoint_backend():
    """Testa o endpoint do backend"""
    print("🌐 Testando endpoint do backend...")
    
    try:
        API_BASE_URL = "http://localhost:8000"
        
        # Token de teste (substitua por um token válido)
        token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM1NzI4MDAwLCJpYXQiOjE3MzU3MjQ0MDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoxfQ.example"
        
        # Dados do teste
        chat_id = 21  # Substitua pelo ID do chat de teste
        image_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        # Testar endpoint de mensagens
        url = f"{API_BASE_URL}/api/mensagens/enviar-imagem/"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "chat_id": chat_id,
            "image_data": image_data,
            "image_type": "base64",
            "caption": "Teste de diagnóstico"
        }
        
        print(f"📤 Enviando para: {url}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint funcionando!")
            return True
        else:
            print(f"❌ Erro no endpoint: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")
        return False

def verificar_configuracao_wapi():
    """Verifica a configuração da W-API"""
    print("⚙️ Verificando configuração da W-API...")
    
    # Verificar URLs
    urls_wapi = [
        "https://api.w-api.app/v1/message/send-image",
        "https://api.w-api.app/v1/auth/status",
        "https://api.w-api.app/v1/auth/qrcode"
    ]
    
    for url in urls_wapi:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {url}: {response.status_code}")
        except Exception as e:
            print(f"❌ {url}: {e}")
    
    return True

def main():
    """Função principal"""
    print("🔬 DIAGNÓSTICO COMPLETO - ENVIO DE IMAGEM")
    print("=" * 60)
    
    # Testes
    testes = [
        ("Verificar instância WhatsApp", verificar_instancia_whatsapp),
        ("Verificar chats", verificar_chats),
        ("Testar token W-API", testar_token_wapi),
        ("Testar formatos base64", testar_formato_base64),
        ("Verificar configuração W-API", verificar_configuracao_wapi),
        ("Testar envio real", testar_envio_imagem_real),
        ("Testar endpoint backend", testar_endpoint_backend)
    ]
    
    resultados = []
    
    for nome, teste in testes:
        print(f"\n{'='*20} {nome} {'='*20}")
        
        try:
            resultado = teste()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"❌ Erro no teste {nome}: {e}")
            resultados.append((nome, False))
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DO DIAGNÓSTICO")
    print("=" * 60)
    
    for nome, resultado in resultados:
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{nome}: {status}")
    
    passed = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! O sistema está funcionando corretamente.")
    else:
        print("⚠️ Alguns testes falharam. Verifique os problemas identificados acima.")
        
        # Sugestões baseadas nos resultados
        print("\n💡 SUGESTÕES:")
        if not resultados[0][1]:  # Instância
            print("- Configure uma instância do WhatsApp")
        if not resultados[2][1]:  # Token
            print("- Verifique se o token da W-API está correto")
        if not resultados[5][1]:  # Envio real
            print("- Verifique a conexão com a W-API")
        if not resultados[6][1]:  # Endpoint
            print("- Verifique se o backend está rodando na porta 8000")

if __name__ == "__main__":
    main() 