#!/usr/bin/env python
"""
Script para testar a edição de mensagens e verificar se a API está funcionando.
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

def test_api_edit_endpoint():
    """Testa o endpoint de edição da API."""
    
    print("🧪 TESTANDO ENDPOINT DE EDIÇÃO")
    print("=" * 50)
    
    # 1. Buscar uma mensagem que pode ser editada
    mensagem = Mensagem.objects.filter(
        from_me=True,
        message_id__isnull=False,
        tipo__in=['texto', 'text']
    ).first()
    
    if not mensagem:
        print("❌ Nenhuma mensagem encontrada para edição")
        print("   Buscando mensagens disponíveis...")
        mensagens = Mensagem.objects.all()[:5]
        for msg in mensagens:
            print(f"   - ID: {msg.id}, from_me: {msg.from_me}, message_id: {msg.message_id}, tipo: {msg.tipo}")
        return
    
    print(f"✅ Mensagem encontrada:")
    print(f"   - ID: {mensagem.id}")
    print(f"   - Conteúdo: {mensagem.conteudo[:50]}...")
    print(f"   - Message ID: {mensagem.message_id}")
    print(f"   - from_me: {mensagem.from_me}")
    print(f"   - tipo: {mensagem.tipo}")
    
    # 2. Testar endpoint
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/mensagens/{mensagem.id}/editar/"
    
    # Dados para teste
    novo_texto = f"Texto editado via teste - {mensagem.id}"
    
    payload = {
        "novo_texto": novo_texto
    }
    
    print(f"\n🌐 Testando endpoint: {endpoint}")
    print(f"📤 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Fazer requisição sem token (para testar erro de autenticação)
        response = requests.post(
            endpoint,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📡 Status: {response.status_code}")
        print(f"📡 Headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            print(f"📡 Resposta JSON: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError:
            print(f"📡 Resposta não-JSON: {response.text}")
            data = {}
        
        if response.status_code == 401:
            print("✅ Erro de autenticação esperado (sem token)")
        elif response.status_code == 200:
            print("✅ Edição realizada com sucesso!")
        else:
            print(f"❌ Status inesperado: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - Servidor não está rodando")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def test_message_properties():
    """Testa as propriedades das mensagens para debug."""
    
    print("\n🔍 TESTANDO PROPRIEDADES DAS MENSAGENS")
    print("=" * 50)
    
    mensagens = Mensagem.objects.all()[:10]
    
    for i, msg in enumerate(mensagens, 1):
        print(f"\n📝 Mensagem {i}:")
        print(f"   - ID: {msg.id}")
        print(f"   - from_me: {msg.from_me}")
        print(f"   - message_id: {msg.message_id}")
        print(f"   - tipo: {msg.tipo}")
        print(f"   - conteúdo: {msg.conteudo[:30]}...")
        print(f"   - chat_id: {msg.chat.chat_id if msg.chat else 'N/A'}")
        
        # Verificar se pode ser editada
        pode_editar = (
            msg.from_me and 
            msg.message_id and 
            msg.tipo in ['texto', 'text']
        )
        
        print(f"   - Pode editar: {'✅' if pode_editar else '❌'}")
        
        if not pode_editar:
            if not msg.from_me:
                print("     ❌ Não é mensagem enviada pelo usuário")
            if not msg.message_id:
                print("     ❌ Sem message_id")
            if msg.tipo not in ['texto', 'text']:
                print("     ❌ Não é mensagem de texto")

def test_wapi_edit_direct():
    """Testa edição direta via W-API."""
    
    print("\n🔧 TESTANDO EDIÇÃO DIRETA VIA W-API")
    print("=" * 50)
    
    # Buscar mensagem válida
    mensagem = Mensagem.objects.filter(
        from_me=True,
        message_id__isnull=False,
        tipo__in=['texto', 'text']
    ).first()
    
    if not mensagem:
        print("❌ Nenhuma mensagem válida encontrada")
        return
    
    print(f"✅ Mensagem para teste:")
    print(f"   - ID: {mensagem.id}")
    print(f"   - Message ID: {mensagem.message_id}")
    print(f"   - Chat ID: {mensagem.chat.chat_id}")
    print(f"   - Conteúdo: {mensagem.conteudo[:50]}...")
    
    # Buscar instância
    try:
        instancia = mensagem.chat.cliente.whatsappinstance_set.first()
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
            novo_texto = f"Teste W-API direto - {mensagem.id}"
            
            print(f"🔄 Editando via W-API...")
            print(f"   - Phone: {mensagem.chat.chat_id}")
            print(f"   - Message ID: {mensagem.message_id}")
            print(f"   - Novo texto: {novo_texto}")
            
            resultado = editor.editar_mensagem(
                phone=mensagem.chat.chat_id,
                message_id=mensagem.message_id,
                new_text=novo_texto
            )
            
            print(f"📡 Resultado: {resultado}")
            
            if "erro" not in resultado:
                print("✅ Edição via W-API bem-sucedida!")
                
                # Atualizar no banco
                mensagem.conteudo = novo_texto
                mensagem.save()
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

def check_frontend_requirements():
    """Verifica os requisitos para o frontend funcionar."""
    
    print("\n🔍 VERIFICANDO REQUISITOS DO FRONTEND")
    print("=" * 50)
    
    # 1. Verificar se há mensagens próprias
    mensagens_proprias = Mensagem.objects.filter(from_me=True)
    print(f"📊 Mensagens próprias: {mensagens_proprias.count()}")
    
    # 2. Verificar se há mensagens com message_id
    mensagens_com_id = Mensagem.objects.filter(message_id__isnull=False)
    print(f"📊 Mensagens com message_id: {mensagens_com_id.count()}")
    
    # 3. Verificar se há mensagens de texto
    mensagens_texto = Mensagem.objects.filter(tipo__in=['texto', 'text'])
    print(f"📊 Mensagens de texto: {mensagens_texto.count()}")
    
    # 4. Verificar mensagens editáveis
    mensagens_editaveis = Mensagem.objects.filter(
        from_me=True,
        message_id__isnull=False,
        tipo__in=['texto', 'text']
    )
    print(f"📊 Mensagens editáveis: {mensagens_editaveis.count()}")
    
    if mensagens_editaveis.count() == 0:
        print("❌ Nenhuma mensagem pode ser editada!")
        print("   Verifique se há:")
        print("   - Mensagens com from_me=True")
        print("   - Mensagens com message_id preenchido")
        print("   - Mensagens do tipo 'texto' ou 'text'")
    else:
        print("✅ Há mensagens que podem ser editadas")
        
        # Mostrar exemplo
        exemplo = mensagens_editaveis.first()
        print(f"   Exemplo: ID {exemplo.id}, conteúdo: {exemplo.conteudo[:30]}...")

if __name__ == "__main__":
    print("🚀 TESTE COMPLETO - SISTEMA DE EDIÇÃO")
    print("=" * 60)
    
    # Executar testes
    test_api_edit_endpoint()
    test_message_properties()
    test_wapi_edit_direct()
    check_frontend_requirements()
    
    print("\n✅ Todos os testes executados!")
    print("\n💡 Dicas para o frontend:")
    print("   - Verifique se o servidor está rodando na porta 8000")
    print("   - Confirme se há mensagens editáveis no banco")
    print("   - Verifique se o token de autenticação está válido")
    print("   - Teste com uma mensagem própria de texto") 