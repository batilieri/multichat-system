#!/usr/bin/env python3
"""
Debug específico para problemas de remoção de reações
"""

import requests
import json
import sys
import os

def testar_endpoint_remocao():
    """Testa o endpoint de remoção diretamente"""
    print("🧪 Testando endpoint de remoção...")
    
    # URL do endpoint
    url = "http://localhost:8000/api/mensagens/1/remover-reacao/"
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📡 Enviando requisição para: {url}")
        
        response = requests.post(url, headers=headers)
        
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Resposta: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint funcionando!")
            print(f"  - Sucesso: {data.get('sucesso')}")
            print(f"  - Ação: {data.get('acao')}")
            print(f"  - Emoji Removido: {data.get('emoji_removido')}")
            print(f"  - Reações: {data.get('reacoes')}")
            print(f"  - WAPI Enviado: {data.get('wapi_enviado')}")
        else:
            print(f"❌ Erro no endpoint: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")

def verificar_mensagem_com_reacao():
    """Verifica se existe uma mensagem com reação para testar"""
    print("\n🔍 Verificando mensagens com reações...")
    
    try:
        # URL para listar mensagens
        url = "http://localhost:8000/api/mensagens/"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            mensagens = data.get('results', [])
            
            print(f"📊 Total de mensagens: {len(mensagens)}")
            
            # Procurar mensagens com reações
            mensagens_com_reacao = []
            for msg in mensagens[:10]:  # Primeiras 10
                reacoes = msg.get('reacoes', [])
                if reacoes:
                    mensagens_com_reacao.append({
                        'id': msg.get('id'),
                        'reacoes': reacoes,
                        'conteudo': msg.get('conteudo', '')[:50]
                    })
            
            print(f"📊 Mensagens com reações: {len(mensagens_com_reacao)}")
            
            for msg in mensagens_com_reacao:
                print(f"  - ID: {msg['id']}")
                print(f"    Reações: {msg['reacoes']}")
                print(f"    Conteúdo: {msg['conteudo']}")
            
            return mensagens_com_reacao
        else:
            print(f"❌ Erro ao buscar mensagens: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Erro ao verificar mensagens: {e}")
        return []

def testar_remocao_especifica(mensagem_id):
    """Testa remoção em uma mensagem específica"""
    print(f"\n🧪 Testando remoção na mensagem {mensagem_id}...")
    
    url = f"http://localhost:8000/api/mensagens/{mensagem_id}/remover-reacao/"
    
    try:
        response = requests.post(url, headers={"Content-Type": "application/json"})
        
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Resposta: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Remoção bem-sucedida!")
            print(f"  - Reações após remoção: {data.get('reacoes')}")
            print(f"  - WAPI Enviado: {data.get('wapi_enviado')}")
        else:
            print(f"❌ Erro na remoção: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar remoção: {e}")

def verificar_logs_backend():
    """Verifica se há logs de erro no backend"""
    print("\n🔍 Verificando possíveis problemas...")
    
    print("📋 POSSÍVEIS CAUSAS:")
    print("1. Mensagem não encontrada")
    print("2. Mensagem sem reações")
    print("3. Erro na integração W-API")
    print("4. Problema de permissões")
    print("5. Erro no banco de dados")
    
    print("\n🔧 SOLUÇÕES:")
    print("1. Verificar se a mensagem existe")
    print("2. Verificar se tem reações")
    print("3. Verificar logs do Django")
    print("4. Verificar conexão W-API")
    print("5. Verificar permissões do usuário")

def main():
    """Executa todos os testes de debug"""
    print("🚀 Iniciando debug da remoção de reações...")
    
    # Verificar mensagens com reações
    mensagens_com_reacao = verificar_mensagem_com_reacao()
    
    if mensagens_com_reacao:
        # Testar remoção na primeira mensagem com reação
        primeira_mensagem = mensagens_com_reacao[0]
        testar_remocao_especifica(primeira_mensagem['id'])
    else:
        print("\n⚠️ Nenhuma mensagem com reação encontrada!")
        print("💡 Adicione uma reação primeiro e depois teste a remoção.")
    
    # Testar endpoint geral
    testar_endpoint_remocao()
    
    # Verificar possíveis problemas
    verificar_logs_backend()
    
    print("\n✅ Debug concluído!")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Verifique se há mensagens com reações")
    print("2. Adicione uma reação se necessário")
    print("3. Teste a remoção novamente")
    print("4. Verifique logs do backend")

if __name__ == "__main__":
    main() 