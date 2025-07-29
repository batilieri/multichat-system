#!/usr/bin/env python
"""
Script para testar a edição de mensagens via API.
"""

import os
import sys
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente
from authentication.models import Usuario

def test_edit_message():
    """Testa a edição de mensagens via API."""
    
    print("🧪 TESTANDO EDIÇÃO DE MENSAGENS")
    print("=" * 50)
    
    # 1. Verificar se há mensagens no banco
    mensagens = Mensagem.objects.all()
    print(f"📊 Total de mensagens no banco: {mensagens.count()}")
    
    if mensagens.count() == 0:
        print("❌ Nenhuma mensagem encontrada para testar")
        return
    
    # 2. Buscar uma mensagem que pode ser editada
    mensagem_test = mensagens.filter(
        from_me=True,
        message_id__isnull=False,
        tipo__in=['texto', 'text']
    ).first()
    
    if not mensagem_test:
        print("❌ Nenhuma mensagem encontrada com from_me=True, message_id e tipo texto")
        print("   Mensagens disponíveis:")
        for msg in mensagens[:10]:
            print(f"   - ID: {msg.id}, from_me: {msg.from_me}, message_id: {msg.message_id}, tipo: {msg.tipo}")
        return
    
    print(f"✅ Mensagem encontrada para teste:")
    print(f"   - ID: {mensagem_test.id}")
    print(f"   - message_id: {mensagem_test.message_id}")
    print(f"   - from_me: {mensagem_test.from_me}")
    print(f"   - tipo: {mensagem_test.tipo}")
    print(f"   - chat_id: {mensagem_test.chat.chat_id}")
    print(f"   - conteúdo atual: {mensagem_test.conteudo[:100]}...")
    
    # 3. Testar endpoint da API
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/mensagens/{mensagem_test.id}/editar/"
    
    print(f"\n🌐 Testando endpoint: {endpoint}")
    
    # Dados para teste
    novo_texto = f"Texto editado via API - {mensagem_test.id}"
    
    payload = {
        "novo_texto": novo_texto
    }
    
    print(f"📤 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Fazer requisição POST
        response = requests.post(
            endpoint,
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer SEU_TOKEN_AQUI'  # Substitua pelo token real
            },
            timeout=30
        )
        
        print(f"📡 Status da resposta: {response.status_code}")
        print(f"📡 Headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            print(f"📡 Resposta JSON: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError:
            print(f"📡 Resposta não-JSON: {response.text}")
            data = {}
        
        if response.status_code == 200:
            print("✅ Edição realizada com sucesso!")
            print(f"   - Novo texto: {data.get('novo_texto', 'N/A')}")
            print(f"   - Message ID: {data.get('message_id', 'N/A')}")
            print(f"   - Chat ID: {data.get('chat_id', 'N/A')}")
            
            # Verificar se a mensagem foi atualizada no banco
            mensagem_test.refresh_from_db()
            print(f"   - Conteúdo no banco: {mensagem_test.conteudo}")
            
        elif response.status_code == 400:
            print("❌ Erro de validação:")
            print(f"   - Erro: {data.get('error', 'N/A')}")
            print(f"   - Detalhes: {data.get('details', 'N/A')}")
            
        elif response.status_code == 401:
            print("❌ Erro de autenticação - Token inválido ou ausente")
            
        elif response.status_code == 403:
            print("❌ Erro de permissão - Usuário não tem permissão para editar")
            
        elif response.status_code == 404:
            print("❌ Mensagem não encontrada")
            
        else:
            print(f"❌ Erro inesperado: {response.status_code}")
            print(f"   - Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - Servidor não está rodando")
    except requests.exceptions.Timeout:
        print("❌ Timeout - Servidor demorou para responder")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def test_edit_validation():
    """Testa validações de edição."""
    
    print("\n🧪 TESTANDO VALIDAÇÕES DE EDIÇÃO")
    print("=" * 50)
    
    # Buscar diferentes tipos de mensagens para testar
    mensagens = Mensagem.objects.all()[:5]
    
    for msg in mensagens:
        print(f"\n📝 Testando mensagem ID: {msg.id}")
        print(f"   - from_me: {msg.from_me}")
        print(f"   - message_id: {msg.message_id}")
        print(f"   - tipo: {msg.tipo}")
        
        # Simular validações
        if not msg.message_id:
            print("   ❌ Não pode editar: sem message_id")
        elif not msg.from_me:
            print("   ❌ Não pode editar: não é mensagem enviada pelo usuário")
        elif msg.tipo not in ['texto', 'text']:
            print("   ❌ Não pode editar: não é mensagem de texto")
        else:
            print("   ✅ Pode editar: atende todos os requisitos")

def test_wapi_edit_direct():
    """Testa edição direta via W-API."""
    
    print("\n🧪 TESTANDO EDIÇÃO DIRETA VIA W-API")
    print("=" * 50)
    
    # Buscar uma mensagem válida
    mensagem_test = Mensagem.objects.filter(
        from_me=True,
        message_id__isnull=False,
        tipo__in=['texto', 'text']
    ).first()
    
    if not mensagem_test:
        print("❌ Nenhuma mensagem válida encontrada para teste")
        return
    
    print(f"✅ Mensagem para teste:")
    print(f"   - ID: {mensagem_test.id}")
    print(f"   - message_id: {mensagem_test.message_id}")
    print(f"   - chat_id: {mensagem_test.chat.chat_id}")
    print(f"   - conteúdo: {mensagem_test.conteudo[:50]}...")
    
    # Buscar instância WhatsApp
    try:
        instancia = mensagem_test.chat.cliente.whatsappinstance_set.first()
        if not instancia:
            print("❌ Cliente não possui instância WhatsApp configurada")
            return
            
        print(f"✅ Instância encontrada: {instancia.instance_id}")
        
        # Importar classe de edição
        import sys
        import os
        wapi_path = os.path.join(os.path.dirname(__file__), '..', 'wapi')
        if wapi_path not in sys.path:
            sys.path.append(wapi_path)
        
        try:
            from mensagem.editar.editarMensagens import EditarMensagem
            
            # Criar editor
            editor = EditarMensagem(instancia.instance_id, instancia.token)
            
            # Testar edição
            novo_texto = f"Teste direto W-API - {mensagem_test.id}"
            
            print(f"🔄 Editando via W-API...")
            print(f"   - Phone: {mensagem_test.chat.chat_id}")
            print(f"   - Message ID: {mensagem_test.message_id}")
            print(f"   - Novo texto: {novo_texto}")
            
            resultado = editor.editar_mensagem(
                phone=mensagem_test.chat.chat_id,
                message_id=mensagem_test.message_id,
                new_text=novo_texto
            )
            
            print(f"📡 Resultado: {resultado}")
            
            if "erro" not in resultado:
                print("✅ Edição via W-API bem-sucedida!")
                
                # Atualizar no banco
                mensagem_test.conteudo = novo_texto
                mensagem_test.save()
                print("✅ Mensagem atualizada no banco de dados")
                
            else:
                print("❌ Erro na edição via W-API:")
                print(f"   - Erro: {resultado.get('erro', 'N/A')}")
                
        except ImportError as e:
            print(f"❌ Erro ao importar EditarMensagem: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            
    except Exception as e:
        print(f"❌ Erro ao buscar instância: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DE EDIÇÃO DE MENSAGENS")
    print("=" * 60)
    
    # Executar testes
    test_edit_message()
    test_edit_validation()
    test_wapi_edit_direct()
    
    print("\n✅ Testes concluídos!") 