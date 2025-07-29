#!/usr/bin/env python
"""
Exemplo prático de como usar o sistema de edição de mensagens.
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

def exemplo_edicao_via_api():
    """Exemplo de como editar mensagens via API REST."""
    
    print("🌐 EXEMPLO: Edição via API REST")
    print("=" * 50)
    
    # 1. Buscar uma mensagem que pode ser editada
    mensagem = Mensagem.objects.filter(
        from_me=True,
        message_id__isnull=False,
        tipo__in=['texto', 'text']
    ).first()
    
    if not mensagem:
        print("❌ Nenhuma mensagem encontrada para edição")
        return
    
    print(f"📝 Mensagem encontrada:")
    print(f"   - ID: {mensagem.id}")
    print(f"   - Conteúdo atual: {mensagem.conteudo[:50]}...")
    print(f"   - Message ID: {mensagem.message_id}")
    
    # 2. Configurar requisição
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/mensagens/{mensagem.id}/editar/"
    
    # Substitua pelo seu token de acesso
    token = "SEU_TOKEN_AQUI"
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 3. Dados para edição
    novo_texto = f"Texto editado via API - {mensagem.id}"
    
    payload = {
        "novo_texto": novo_texto
    }
    
    print(f"\n🔄 Enviando requisição...")
    print(f"   - URL: {endpoint}")
    print(f"   - Método: POST")
    print(f"   - Novo texto: {novo_texto}")
    
    try:
        # 4. Fazer requisição
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        print(f"\n📡 Resposta:")
        print(f"   - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Edição realizada com sucesso!")
            print(f"   - Novo texto: {data.get('novo_texto')}")
            print(f"   - Message ID: {data.get('message_id')}")
            print(f"   - Chat ID: {data.get('chat_id')}")
            
            # Verificar se foi atualizado no banco
            mensagem.refresh_from_db()
            print(f"   - Conteúdo no banco: {mensagem.conteudo}")
            
        else:
            data = response.json()
            print("❌ Erro na edição:")
            print(f"   - Erro: {data.get('error')}")
            print(f"   - Detalhes: {data.get('details')}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

def exemplo_edicao_direta_wapi():
    """Exemplo de como editar mensagens diretamente via W-API."""
    
    print("\n🔧 EXEMPLO: Edição direta via W-API")
    print("=" * 50)
    
    # 1. Buscar mensagem e instância
    mensagem = Mensagem.objects.filter(
        from_me=True,
        message_id__isnull=False,
        tipo__in=['texto', 'text']
    ).first()
    
    if not mensagem:
        print("❌ Nenhuma mensagem encontrada para edição")
        return
    
    # Buscar instância WhatsApp
    try:
        instancia = mensagem.chat.cliente.whatsappinstance_set.first()
        if not instancia:
            print("❌ Cliente não possui instância WhatsApp configurada")
            return
            
        print(f"✅ Instância encontrada: {instancia.instance_id}")
        
        # 2. Importar classe de edição
        import sys
        import os
        wapi_path = os.path.join(os.path.dirname(__file__), '..', 'wapi')
        if wapi_path not in sys.path:
            sys.path.append(wapi_path)
        
        try:
            from mensagem.editar.editarMensagens import EditarMensagem
            
            # 3. Criar editor
            editor = EditarMensagem(instancia.instance_id, instancia.token)
            
            # 4. Dados para edição
            novo_texto = f"Texto editado diretamente via W-API - {mensagem.id}"
            
            print(f"📝 Editando mensagem:")
            print(f"   - Phone: {mensagem.chat.chat_id}")
            print(f"   - Message ID: {mensagem.message_id}")
            print(f"   - Novo texto: {novo_texto}")
            
            # 5. Editar via W-API
            resultado = editor.editar_mensagem(
                phone=mensagem.chat.chat_id,
                message_id=mensagem.message_id,
                new_text=novo_texto
            )
            
            print(f"\n📡 Resultado da W-API:")
            print(f"   - Resposta: {resultado}")
            
            if "erro" not in resultado:
                print("✅ Edição via W-API bem-sucedida!")
                
                # 6. Atualizar no banco local
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

def exemplo_exclusao_mensagens():
    """Exemplo de como excluir mensagens."""
    
    print("\n🗑️ EXEMPLO: Exclusão de mensagens")
    print("=" * 50)
    
    # 1. Buscar mensagem para excluir
    mensagem = Mensagem.objects.filter(
        from_me=True,
        message_id__isnull=False
    ).first()
    
    if not mensagem:
        print("❌ Nenhuma mensagem encontrada para exclusão")
        return
    
    print(f"📝 Mensagem para excluir:")
    print(f"   - ID: {mensagem.id}")
    print(f"   - Conteúdo: {mensagem.conteudo[:50]}...")
    print(f"   - Message ID: {mensagem.message_id}")
    
    # 2. Importar classe de exclusão
    import sys
    import os
    wapi_path = os.path.join(os.path.dirname(__file__), '..', 'wapi')
    if wapi_path not in sys.path:
        sys.path.append(wapi_path)
    
    try:
        from mensagem.deletar.deletarMensagens import DeletaMensagem
        
        # 3. Buscar instância
        instancia = mensagem.chat.cliente.whatsappinstance_set.first()
        if not instancia:
            print("❌ Cliente não possui instância WhatsApp configurada")
            return
            
        # 4. Criar deletador
        deletador = DeletaMensagem(instancia.instance_id, instancia.token)
        
        print(f"🔄 Excluindo mensagem...")
        print(f"   - Phone: {mensagem.chat.chat_id}")
        print(f"   - Message ID: {mensagem.message_id}")
        
        # 5. Excluir via W-API
        resultado = deletador.deletar(
            phone_number=mensagem.chat.chat_id,
            message_ids=mensagem.message_id
        )
        
        print(f"\n📡 Resultado da exclusão:")
        print(f"   - Resposta: {resultado}")
        
        if resultado.get("success"):
            print("✅ Mensagem excluída com sucesso!")
            
            # 6. Excluir do banco local
            mensagem.delete()
            print("✅ Mensagem removida do banco de dados")
            
        else:
            print("❌ Erro na exclusão:")
            print(f"   - Erro: {resultado.get('error', 'N/A')}")
            
    except ImportError as e:
        print(f"❌ Erro ao importar DeletaMensagem: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def exemplo_validacoes():
    """Exemplo de validações do sistema."""
    
    print("\n🔍 EXEMPLO: Validações do sistema")
    print("=" * 50)
    
    # Buscar diferentes tipos de mensagens
    mensagens = Mensagem.objects.all()[:10]
    
    for i, msg in enumerate(mensagens, 1):
        print(f"\n📝 Mensagem {i}:")
        print(f"   - ID: {msg.id}")
        print(f"   - from_me: {msg.from_me}")
        print(f"   - message_id: {msg.message_id}")
        print(f"   - tipo: {msg.tipo}")
        print(f"   - conteúdo: {msg.conteudo[:30]}...")
        
        # Simular validações
        erros = []
        
        if not msg.message_id:
            erros.append("❌ Sem message_id")
        if not msg.from_me:
            erros.append("❌ Não é mensagem enviada pelo usuário")
        if msg.tipo not in ['texto', 'text']:
            erros.append("❌ Não é mensagem de texto")
            
        if erros:
            print(f"   - Validações: {' | '.join(erros)}")
        else:
            print(f"   - ✅ Pode ser editada")

def exemplo_uso_completo():
    """Exemplo completo de uso do sistema."""
    
    print("\n🚀 EXEMPLO COMPLETO: Uso do sistema")
    print("=" * 50)
    
    # 1. Buscar mensagem válida
    mensagem = Mensagem.objects.filter(
        from_me=True,
        message_id__isnull=False,
        tipo__in=['texto', 'text']
    ).first()
    
    if not mensagem:
        print("❌ Nenhuma mensagem válida encontrada")
        return
    
    print(f"✅ Mensagem encontrada para teste:")
    print(f"   - ID: {mensagem.id}")
    print(f"   - Conteúdo: {mensagem.conteudo}")
    print(f"   - Message ID: {mensagem.message_id}")
    
    # 2. Buscar instância
    instancia = mensagem.chat.cliente.whatsappinstance_set.first()
    if not instancia:
        print("❌ Instância não encontrada")
        return
    
    print(f"✅ Instância encontrada: {instancia.instance_id}")
    
    # 3. Importar classes
    import sys
    import os
    wapi_path = os.path.join(os.path.dirname(__file__), '..', 'wapi')
    if wapi_path not in sys.path:
        sys.path.append(wapi_path)
    
    try:
        from mensagem.editar.editarMensagens import EditarMensagem
        from mensagem.deletar.deletarMensagens import DeletaMensagem
        
        # 4. Criar instâncias
        editor = EditarMensagem(instancia.instance_id, instancia.token)
        deletador = DeletaMensagem(instancia.instance_id, instancia.token)
        
        # 5. Testar edição
        print(f"\n✏️ Testando edição...")
        novo_texto = f"Teste completo - {mensagem.id}"
        
        resultado_edicao = editor.editar_mensagem(
            phone=mensagem.chat.chat_id,
            message_id=mensagem.message_id,
            new_text=novo_texto
        )
        
        if "erro" not in resultado_edicao:
            print("✅ Edição bem-sucedida!")
            mensagem.conteudo = novo_texto
            mensagem.save()
        else:
            print(f"❌ Erro na edição: {resultado_edicao}")
        
        # 6. Testar exclusão (opcional)
        print(f"\n🗑️ Testando exclusão...")
        resultado_exclusao = deletador.deletar(
            phone_number=mensagem.chat.chat_id,
            message_ids=mensagem.message_id
        )
        
        if resultado_exclusao.get("success"):
            print("✅ Exclusão bem-sucedida!")
            mensagem.delete()
        else:
            print(f"❌ Erro na exclusão: {resultado_exclusao}")
            
    except ImportError as e:
        print(f"❌ Erro ao importar classes: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    print("🎯 EXEMPLOS PRÁTICOS - SISTEMA DE EDIÇÃO DE MENSAGENS")
    print("=" * 70)
    
    # Executar exemplos
    exemplo_edicao_via_api()
    exemplo_edicao_direta_wapi()
    exemplo_exclusao_mensagens()
    exemplo_validacoes()
    exemplo_uso_completo()
    
    print("\n✅ Todos os exemplos executados!")
    print("\n💡 Dicas:")
    print("   - Substitua 'SEU_TOKEN_AQUI' pelo token real")
    print("   - Certifique-se de que o servidor está rodando")
    print("   - Verifique se há mensagens válidas no banco")
    print("   - Confirme se as instâncias WhatsApp estão configuradas") 