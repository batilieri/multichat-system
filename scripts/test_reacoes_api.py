#!/usr/bin/env python
"""
Script para testar a API de reações
"""
import requests
import json

def test_reacoes_api():
    """Testa a API de reações"""
    print("🧪 Testando API de reações...")
    
    # URL base
    base_url = "http://localhost:8000"
    
    # Teste 1: Verificar se a API está rodando
    try:
        response = requests.get(f"{base_url}/api/")
        print(f"✅ API está rodando: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao conectar com API: {e}")
        return
    
    # Teste 2: Listar mensagens
    try:
        response = requests.get(f"{base_url}/api/mensagens/")
        if response.status_code == 200:
            mensagens = response.json()
            print(f"✅ Mensagens encontradas: {len(mensagens)}")
            
            if mensagens:
                # Pegar primeira mensagem para teste
                mensagem = mensagens[0]
                mensagem_id = mensagem['id']
                print(f"🎯 Testando reações na mensagem ID: {mensagem_id}")
                
                # Teste 3: Adicionar reação
                emoji = "👍"
                data = {"emoji": emoji}
                
                response = requests.post(
                    f"{base_url}/api/mensagens/{mensagem_id}/reagir/",
                    json=data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    resultado = response.json()
                    print(f"✅ Reação adicionada: {resultado}")
                    
                    # Teste 4: Verificar se a reação foi salva
                    response = requests.get(f"{base_url}/api/mensagens/{mensagem_id}/")
                    if response.status_code == 200:
                        mensagem_atualizada = response.json()
                        reacoes = mensagem_atualizada.get('reacoes', [])
                        print(f"✅ Reações na mensagem: {reacoes}")
                        
                        # Teste 5: Remover reação
                        response = requests.post(
                            f"{base_url}/api/mensagens/{mensagem_id}/reagir/",
                            json=data,
                            headers={'Content-Type': 'application/json'}
                        )
                        
                        if response.status_code == 200:
                            resultado = response.json()
                            print(f"✅ Reação removida: {resultado}")
                        else:
                            print(f"❌ Erro ao remover reação: {response.status_code}")
                    else:
                        print(f"❌ Erro ao buscar mensagem: {response.status_code}")
                else:
                    print(f"❌ Erro ao adicionar reação: {response.status_code}")
                    print(f"Resposta: {response.text}")
            else:
                print("❌ Nenhuma mensagem encontrada para teste")
        else:
            print(f"❌ Erro ao listar mensagens: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

if __name__ == "__main__":
    print("🧪 Teste da API de Reações")
    print("=" * 40)
    test_reacoes_api()
    print("\n✅ Teste concluído!") 