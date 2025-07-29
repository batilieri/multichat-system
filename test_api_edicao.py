#!/usr/bin/env python
"""
Script para testar a API de edição de mensagens
"""
import requests
import json

def test_api_edicao():
    """Testa a API de edição de mensagens"""
    print("🧪 Testando API de edição de mensagens...")
    
    # URL base da API
    base_url = "http://localhost:8000"
    
    # Primeiro, vamos listar mensagens para encontrar uma editável
    print("\n📋 Buscando mensagens...")
    
    try:
        # Listar mensagens
        response = requests.get(f"{base_url}/api/mensagens/")
        
        if response.status_code == 200:
            mensagens = response.json()
            print(f"✅ Encontradas {len(mensagens)} mensagens")
            
            # Procurar mensagens editáveis
            mensagens_editaveis = []
            for msg in mensagens:
                if (msg.get('from_me') and 
                    msg.get('tipo') in ['texto', 'text'] and 
                    msg.get('message_id')):
                    mensagens_editaveis.append(msg)
            
            print(f"📝 Mensagens editáveis encontradas: {len(mensagens_editaveis)}")
            
            if mensagens_editaveis:
                # Testar edição com a primeira mensagem editável
                msg = mensagens_editaveis[0]
                print(f"\n🎯 Testando edição da mensagem ID: {msg['id']}")
                print(f"   Conteúdo atual: {msg.get('conteudo', 'N/A')}")
                print(f"   Message ID: {msg.get('message_id')}")
                print(f"   From Me: {msg.get('from_me')}")
                print(f"   Tipo: {msg.get('tipo')}")
                
                # Tentar editar
                novo_texto = f"{msg.get('conteudo', '')} [EDITADO]"
                
                edit_data = {
                    'novo_texto': novo_texto
                }
                
                print(f"\n✏️ Enviando edição...")
                print(f"   URL: {base_url}/api/mensagens/{msg['id']}/editar/")
                print(f"   Novo texto: {novo_texto}")
                
                edit_response = requests.post(
                    f"{base_url}/api/mensagens/{msg['id']}/editar/",
                    json=edit_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                print(f"\n📡 Resposta da API:")
                print(f"   Status: {edit_response.status_code}")
                print(f"   Headers: {dict(edit_response.headers)}")
                
                try:
                    response_data = edit_response.json()
                    print(f"   Data: {json.dumps(response_data, indent=2)}")
                except:
                    print(f"   Text: {edit_response.text}")
                
                if edit_response.status_code == 200:
                    print("✅ Edição realizada com sucesso!")
                else:
                    print("❌ Erro na edição!")
                    
            else:
                print("❌ Nenhuma mensagem editável encontrada!")
                print("💡 Para testar, você precisa de mensagens que:")
                print("   - Tenham from_me=True")
                print("   - Sejam do tipo 'texto' ou 'text'")
                print("   - Tenham message_id preenchido")
                
        else:
            print(f"❌ Erro ao buscar mensagens: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão! Verifique se o backend está rodando em http://localhost:8000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_api_edicao() 