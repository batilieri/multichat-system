#!/usr/bin/env python3
"""
Debug específico para problemas de reação no backend
"""

import sys
import os
import requests
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def testar_importacao_wapi():
    """Testa se a importação da W-API está funcionando"""
    print("🔍 Testando importação da W-API...")
    
    try:
        # Adicionar caminho para wapi
        wapi_path = os.path.join(os.path.dirname(__file__), 'wapi')
        sys.path.append(wapi_path)
        
        print(f"📁 Caminho W-API: {wapi_path}")
        print(f"📋 Arquivos em wapi/: {os.listdir(wapi_path) if os.path.exists(wapi_path) else 'NÃO ENCONTRADO'}")
        
        # Tentar importar
        from mensagem.reacao.enviarReacao import EnviarReacao
        print("✅ Importação da classe EnviarReacao bem-sucedida")
        
        # Testar criação da instância
        reacao = EnviarReacao("test", "test")
        print("✅ Instância da classe criada com sucesso")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

def testar_busca_instancia():
    """Testa a busca de instância no Django"""
    print("\n🔍 Testando busca de instância...")
    
    try:
        # Simular busca de instância
        from django.conf import settings
        import django
        django.setup()
        
        from core.models import WhatsappInstance
        
        # Buscar instâncias
        instances = WhatsappInstance.objects.all()
        print(f"📊 Instâncias encontradas: {instances.count()}")
        
        for instance in instances:
            print(f"  - ID: {instance.id}")
            print(f"    Instance ID: {instance.instance_id}")
            print(f"    Token: {'SIM' if instance.token else 'NÃO'}")
            print(f"    Cliente: {instance.cliente.nome if instance.cliente else 'NENHUM'}")
        
        return instances.count() > 0
        
    except Exception as e:
        print(f"❌ Erro ao buscar instâncias: {e}")
        return False

def testar_busca_mensagem():
    """Testa a busca de mensagem com message_id"""
    print("\n🔍 Testando busca de mensagem...")
    
    try:
        from django.conf import settings
        import django
        django.setup()
        
        from webhook.models import Message
        
        # Buscar mensagens com message_id
        messages = Message.objects.filter(message_id__isnull=False).exclude(message_id='')
        print(f"📊 Mensagens com message_id: {messages.count()}")
        
        for msg in messages[:5]:  # Primeiras 5
            print(f"  - ID: {msg.id}")
            print(f"    Message ID: {msg.message_id}")
            print(f"    Chat ID: {msg.chat.chat_id if msg.chat else 'NENHUM'}")
            print(f"    Cliente: {msg.cliente.nome if msg.cliente else 'NENHUM'}")
        
        return messages.count() > 0
        
    except Exception as e:
        print(f"❌ Erro ao buscar mensagens: {e}")
        return False

def testar_endpoint_reacao():
    """Testa o endpoint de reação diretamente"""
    print("\n🔍 Testando endpoint de reação...")
    
    url = "http://localhost:8000/api/mensagens/1/reagir/"
    data = {"emoji": "👍"}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Resposta: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso: {data.get('sucesso')}")
            print(f"🎯 WAPI Enviado: {data.get('wapi_enviado')}")
            print(f"📝 Mensagem: {data.get('mensagem')}")
        else:
            print(f"❌ Erro no endpoint: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")

def verificar_caminhos():
    """Verifica se os caminhos estão corretos"""
    print("\n🔍 Verificando caminhos...")
    
    # Verificar estrutura de diretórios
    current_dir = os.path.dirname(__file__)
    wapi_dir = os.path.join(current_dir, 'wapi')
    
    print(f"📁 Diretório atual: {current_dir}")
    print(f"📁 Diretório W-API: {wapi_dir}")
    print(f"📁 W-API existe: {os.path.exists(wapi_dir)}")
    
    if os.path.exists(wapi_dir):
        print(f"📋 Conteúdo de wapi/: {os.listdir(wapi_dir)}")
        
        mensagem_dir = os.path.join(wapi_dir, 'mensagem')
        if os.path.exists(mensagem_dir):
            print(f"📋 Conteúdo de wapi/mensagem/: {os.listdir(mensagem_dir)}")
            
            reacao_dir = os.path.join(mensagem_dir, 'reacao')
            if os.path.exists(reacao_dir):
                print(f"📋 Conteúdo de wapi/mensagem/reacao/: {os.listdir(reacao_dir)}")

def main():
    """Executa todos os testes de debug"""
    print("🚀 Iniciando debug do backend de reações...")
    
    verificar_caminhos()
    testar_importacao_wapi()
    testar_busca_instancia()
    testar_busca_mensagem()
    testar_endpoint_reacao()
    
    print("\n✅ Debug concluído!")
    print("\n📋 POSSÍVEIS PROBLEMAS:")
    print("1. Importação da W-API falhando")
    print("2. Instância não encontrada")
    print("3. Mensagem sem message_id")
    print("4. Token inválido")
    print("5. Caminhos incorretos")

if __name__ == "__main__":
    main() 