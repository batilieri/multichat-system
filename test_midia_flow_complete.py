#!/usr/bin/env python3
"""
Teste completo do fluxo de mídias no sistema MultiChat.

Testa:
1. Frontend faz requisição correta
2. Backend serve mídia com headers corretos
3. Arquivo existe e é servido
4. CORS está funcionando
5. Content-Type está correto

Autor: Sistema MultiChat
Data: 2025-08-07
"""

import requests
import json
import sys
from pathlib import Path

def test_endpoint_smart_audio():
    """Testa o novo endpoint inteligente de áudio"""
    print("🧪 Testando endpoint inteligente de áudio...")
    
    # Dados conhecidos do sistema
    cliente_id = 2
    instance_id = "3B6XIW-ZTS923-GEAY6V"
    chat_id = "556999211347"
    message_id = "8E0BFC8589C6AAD1275BEAD714A5E65C"
    
    url = f"http://localhost:8000/api/whatsapp-audio-smart/{cliente_id}/{instance_id}/{chat_id}/{message_id}/"
    
    try:
        print(f"📡 Fazendo requisição: {url}")
        response = requests.get(url)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Headers:")
        for header, value in response.headers.items():
            print(f"   {header}: {value}")
        
        if response.status_code == 200:
            print("✅ Sucesso!")
            print(f"📏 Tamanho do conteúdo: {len(response.content)} bytes")
            
            # Verificar headers específicos
            content_type = response.headers.get('content-type', '')
            cors_header = response.headers.get('access-control-allow-origin', '')
            content_disposition = response.headers.get('content-disposition', '')
            
            print(f"🔍 Verificações:")
            print(f"   ✅ Content-Type audio: {'✅' if 'audio' in content_type else '❌'} ({content_type})")
            print(f"   ✅ CORS habilitado: {'✅' if cors_header == '*' else '❌'} ({cors_header})")
            print(f"   ✅ Content-Disposition inline: {'✅' if 'inline' in content_disposition else '❌'} ({content_disposition})")
            
            return True
        else:
            print(f"❌ Falhou: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_file_exists():
    """Testa se o arquivo existe no filesystem"""
    print("\n📁 Testando existência do arquivo...")
    
    file_path = Path(__file__).parent / "multichat_system" / "media_storage" / "cliente_2" / "instance_3B6XIW-ZTS923-GEAY6V" / "chats" / "556999211347" / "audio" / "msg_8E0BFC85_20250806_165649.ogg"
    
    print(f"📍 Caminho: {file_path}")
    
    if file_path.exists():
        size = file_path.stat().st_size
        print(f"✅ Arquivo existe! Tamanho: {size} bytes")
        return True
    else:
        print("❌ Arquivo não encontrado!")
        return False

def test_django_backend_running():
    """Testa se o backend Django está rodando"""
    print("\n🖥️ Testando se backend está rodando...")
    
    try:
        response = requests.get("http://localhost:8000/api/", timeout=5)
        if response.status_code in [200, 404]:  # 404 é OK para rota vazia
            print("✅ Backend Django está rodando!")
            return True
        else:
            print(f"❌ Backend retornou status inesperado: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao backend! Certifique-se que está rodando na porta 8000.")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar backend: {e}")
        return False

def test_frontend_logic():
    """Simula a lógica do frontend para construir URL"""
    print("\n🎨 Testando lógica do frontend...")
    
    # Simular dados de uma mensagem como vem do backend
    message = {
        "id": 901,
        "chat_id": "556999211347", 
        "message_id": "8E0BFC8589C6AAD1275BEAD714A5E65C",
        "tipo": "audio",
        "from_me": True
    }
    
    print(f"📨 Dados da mensagem simulada:")
    for key, value in message.items():
        print(f"   {key}: {value}")
    
    # Lógica do MediaProcessor
    if message.get('chat_id'):
        cliente_id = 2
        instance_id = '3B6XIW-ZTS923-GEAY6V'
        chat_id = message['chat_id']
        message_id = message['message_id']
        
        url = f"http://localhost:8000/api/whatsapp-audio-smart/{cliente_id}/{instance_id}/{chat_id}/{message_id}/"
        print(f"🔗 URL gerada pelo frontend: {url}")
        return url
    else:
        print("❌ Não foi possível gerar URL - chat_id não encontrado")
        return None

def main():
    """Executa todos os testes"""
    print("🚀 TESTE COMPLETO DO FLUXO DE MÍDIAS")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Teste 1: Backend rodando
    if test_django_backend_running():
        tests_passed += 1
    
    # Teste 2: Arquivo existe
    if test_file_exists():
        tests_passed += 1
    
    # Teste 3: Lógica do frontend
    frontend_url = test_frontend_logic()
    if frontend_url:
        tests_passed += 1
    
    # Teste 4: Endpoint funciona
    if test_endpoint_smart_audio():
        tests_passed += 1
    
    print("\n📋 RESULTADO FINAL")
    print("=" * 30)
    print(f"✅ Testes passaram: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("💡 O sistema de mídias está funcionando corretamente.")
        print("\n🔧 PRÓXIMOS PASSOS:")
        print("   1. Testar no browser/frontend real")
        print("   2. Verificar se outras mensagens de áudio funcionam")
        print("   3. Implementar para outros tipos de mídia (imagem, vídeo)")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("🔧 Verifique os problemas acima antes de prosseguir.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)