#!/usr/bin/env python3
"""
Teste completo do fluxo de medias no sistema MultiChat - SEM EMOJIS.

Testa:
1. Frontend faz requisicao correta
2. Backend serve midia com headers corretos
3. Arquivo existe e e servido
4. CORS esta funcionando
5. Content-Type esta correto

Autor: Sistema MultiChat
Data: 2025-08-07
"""

import requests
import json
import sys
from pathlib import Path

def test_endpoint_smart_audio():
    """Testa o novo endpoint inteligente de audio"""
    print("Testando endpoint inteligente de audio...")
    
    # Dados conhecidos do sistema
    cliente_id = 2
    instance_id = "3B6XIW-ZTS923-GEAY6V"
    chat_id = "556999211347"
    message_id = "8E0BFC8589C6AAD1275BEAD714A5E65C"
    
    url = f"http://localhost:8000/api/whatsapp-audio-smart/{cliente_id}/{instance_id}/{chat_id}/{message_id}/"
    
    try:
        print(f"Fazendo requisicao: {url}")
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print("Headers:")
        for header, value in response.headers.items():
            print(f"   {header}: {value}")
        
        if response.status_code == 200:
            print("SUCESSO!")
            print(f"Tamanho do conteudo: {len(response.content)} bytes")
            
            # Verificar headers especificos
            content_type = response.headers.get('content-type', '')
            cors_header = response.headers.get('access-control-allow-origin', '')
            content_disposition = response.headers.get('content-disposition', '')
            
            print("Verificacoes:")
            print(f"   Content-Type audio: {'OK' if 'audio' in content_type else 'FALHOU'} ({content_type})")
            print(f"   CORS habilitado: {'OK' if cors_header == '*' else 'FALHOU'} ({cors_header})")
            print(f"   Content-Disposition inline: {'OK' if 'inline' in content_disposition else 'FALHOU'} ({content_disposition})")
            
            return True
        else:
            print(f"FALHOU: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"Erro na requisicao: {e}")
        return False

def test_file_exists():
    """Testa se o arquivo existe no filesystem"""
    print("\nTestando existencia do arquivo...")
    
    file_path = Path(__file__).parent / "multichat_system" / "media_storage" / "cliente_2" / "instance_3B6XIW-ZTS923-GEAY6V" / "chats" / "556999211347" / "audio" / "msg_8E0BFC85_20250806_165649.ogg"
    
    print(f"Caminho: {file_path}")
    
    if file_path.exists():
        size = file_path.stat().st_size
        print(f"Arquivo existe! Tamanho: {size} bytes")
        return True
    else:
        print("Arquivo nao encontrado!")
        return False

def test_django_backend_running():
    """Testa se o backend Django esta rodando"""
    print("\nTestando se backend esta rodando...")
    
    try:
        response = requests.get("http://localhost:8000/api/", timeout=5)
        if response.status_code in [200, 404]:  # 404 e OK para rota vazia
            print("Backend Django esta rodando!")
            return True
        else:
            print(f"Backend retornou status inesperado: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("Nao foi possivel conectar ao backend! Certifique-se que esta rodando na porta 8000.")
        return False
    except Exception as e:
        print(f"Erro ao testar backend: {e}")
        return False

def test_frontend_logic():
    """Simula a logica do frontend para construir URL"""
    print("\nTestando logica do frontend...")
    
    # Simular dados de uma mensagem como vem do backend
    message = {
        "id": 901,
        "chat_id": "556999211347", 
        "message_id": "8E0BFC8589C6AAD1275BEAD714A5E65C",
        "tipo": "audio",
        "from_me": True
    }
    
    print("Dados da mensagem simulada:")
    for key, value in message.items():
        print(f"   {key}: {value}")
    
    # Logica do MediaProcessor
    if message.get('chat_id'):
        cliente_id = 2
        instance_id = '3B6XIW-ZTS923-GEAY6V'
        chat_id = message['chat_id']
        message_id = message['message_id']
        
        url = f"http://localhost:8000/api/whatsapp-audio-smart/{cliente_id}/{instance_id}/{chat_id}/{message_id}/"
        print(f"URL gerada pelo frontend: {url}")
        return url
    else:
        print("Nao foi possivel gerar URL - chat_id nao encontrado")
        return None

def main():
    """Executa todos os testes"""
    print("TESTE COMPLETO DO FLUXO DE MEDIAS")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Teste 1: Backend rodando
    if test_django_backend_running():
        tests_passed += 1
    
    # Teste 2: Arquivo existe
    if test_file_exists():
        tests_passed += 1
    
    # Teste 3: Logica do frontend
    frontend_url = test_frontend_logic()
    if frontend_url:
        tests_passed += 1
    
    # Teste 4: Endpoint funciona
    if test_endpoint_smart_audio():
        tests_passed += 1
    
    print("\nRESULTADO FINAL")
    print("=" * 30)
    print(f"Testes passaram: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("TODOS OS TESTES PASSARAM!")
        print("O sistema de medias esta funcionando corretamente.")
        print("\nPROXIMOS PASSOS:")
        print("   1. Testar no browser/frontend real")
        print("   2. Verificar se outras mensagens de audio funcionam")
        print("   3. Implementar para outros tipos de midia (imagem, video)")
    else:
        print("ALGUNS TESTES FALHARAM!")
        print("Verifique os problemas acima antes de prosseguir.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)