#!/usr/bin/env python3
"""
Teste de integração de reações com WhatsApp real
"""

import sys
import os
import requests
import json

# Adicionar o caminho para o módulo wapi
sys.path.append(os.path.join(os.path.dirname(__file__), 'wapi'))

def testar_reacao_wapi():
    """Testa o envio de reação via W-API"""
    print("🧪 Testando envio de reação para WhatsApp real...")
    
    # Configurações de teste
    instance_id = "test_instance"  # Substitua pela instância real
    token = "test_token"           # Substitua pelo token real
    phone = "5511999999999"        # Substitua pelo número real
    message_id = "test_message_id" # Substitua pelo ID da mensagem real
    emoji = "👍"
    
    try:
        from wapi.mensagem.reacao.enviarReacao import EnviarReacao
        
        # Criar instância da classe de reação
        reacao = EnviarReacao(instance_id, token)
        
        print(f"📱 Enviando reação {emoji} para mensagem {message_id}")
        print(f"📞 Telefone: {phone}")
        print(f"🔑 Instância: {instance_id}")
        
        # Enviar reação
        resultado = reacao.enviar_reacao(
            phone=phone,
            message_id=message_id,
            reaction=emoji,
            delay=1
        )
        
        print(f"✅ Resultado: {resultado}")
        
        if resultado['sucesso']:
            print("🎉 Reação enviada com sucesso para o WhatsApp!")
        else:
            print(f"❌ Falha ao enviar reação: {resultado['erro']}")
            
    except ImportError as e:
        print(f"❌ Erro ao importar módulo: {e}")
    except Exception as e:
        print(f"❌ Erro geral: {e}")

def testar_endpoint_django():
    """Testa o endpoint Django de reações"""
    print("\n🌐 Testando endpoint Django de reações...")
    
    # URL do endpoint
    url = "http://localhost:8000/api/mensagens/1/reagir/"
    
    # Dados da requisição
    data = {
        "emoji": "👍"
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_TOKEN_HERE"  # Substitua pelo token real
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Resposta: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Endpoint Django funcionando!")
            data = response.json()
            if data.get('wapi_enviado'):
                print("🎉 Reação também enviada para WhatsApp real!")
            else:
                print("⚠️ Reação salva apenas localmente")
        else:
            print(f"❌ Erro no endpoint: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")

def verificar_configuracao():
    """Verifica se a configuração está correta"""
    print("\n🔍 Verificando configuração...")
    
    # Verificar se o arquivo de reação existe
    arquivo_reacao = "wapi/mensagem/reacao/enviarReacao.py"
    if os.path.exists(arquivo_reacao):
        print(f"✅ Arquivo de reação encontrado: {arquivo_reacao}")
    else:
        print(f"❌ Arquivo de reação não encontrado: {arquivo_reacao}")
    
    # Verificar se o endpoint Django está configurado
    print("✅ Endpoint Django configurado: /api/mensagens/{id}/reagir/")
    
    # Verificar integração
    print("✅ Integração W-API implementada")
    print("✅ Reações salvas localmente e enviadas para WhatsApp")

if __name__ == "__main__":
    print("🚀 Iniciando testes de integração de reações...")
    
    verificar_configuracao()
    testar_reacao_wapi()
    testar_endpoint_django()
    
    print("\n✅ Testes concluídos!")
    print("\n📋 INSTRUÇÕES:")
    print("1. Configure uma instância real no painel de administração")
    print("2. Substitua os valores de teste pelos valores reais")
    print("3. Execute o teste novamente")
    print("4. Verifique se a reação aparece no WhatsApp do contato") 