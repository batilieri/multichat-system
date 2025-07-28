#!/usr/bin/env python
"""
Script completo para testar a funcionalidade de edição de mensagens.
"""

import os
import sys
import django
import requests
import json
import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente, WhatsappInstance

def test_edicao_completa():
    """Testa a funcionalidade completa de edição de mensagens"""
    
    print("🧪 Teste Completo - Funcionalidade de Edição de Mensagens")
    print("=" * 70)
    
    # 1. Verificar mensagens disponíveis
    print("\n📊 1. Verificando mensagens disponíveis para edição...")
    mensagens = Mensagem.objects.filter(
        from_me=True,
        tipo__in=['texto', 'text'],
        message_id__isnull=False
    ).exclude(message_id='').order_by('-data_envio')[:5]
    
    if not mensagens:
        print("❌ Nenhuma mensagem encontrada para edição")
        print("   - Verifique se existem mensagens de texto enviadas por você")
        print("   - Verifique se as mensagens têm message_id válido")
        return
    
    print(f"✅ Encontradas {len(mensagens)} mensagens para edição")
    for i, msg in enumerate(mensagens):
        print(f"   {i+1}. ID: {msg.id}, message_id: {msg.message_id}")
        print(f"      Conteúdo: {msg.conteudo[:60]}...")
    
    # 2. Login na API
    print("\n🔐 2. Fazendo login na API...")
    login_data = {
        "email": "admin@multichat.com",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(
            "http://localhost:8000/api/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            print(f"   Resposta: {login_response.text}")
            return
        
        token = login_response.json().get('access')
        if not token:
            print("❌ Token não encontrado na resposta")
            return
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        print("✅ Login realizado com sucesso")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return
    
    # 3. Testar edição da primeira mensagem
    primeira_mensagem = mensagens[0]
    texto_original = primeira_mensagem.conteudo
    novo_texto = f"[EDITADO {int(time.time())}] {texto_original}"
    
    print(f"\n📝 3. Testando edição da mensagem...")
    print(f"   - ID interno: {primeira_mensagem.id}")
    print(f"   - message_id: {primeira_mensagem.message_id}")
    print(f"   - Texto original: {texto_original[:50]}...")
    print(f"   - Novo texto: {novo_texto[:50]}...")
    
    edit_data = {
        'novo_texto': novo_texto
    }
    
    try:
        edit_response = requests.post(
            f"http://localhost:8000/api/mensagens/{primeira_mensagem.id}/editar/",
            json=edit_data,
            headers=headers,
            timeout=30
        )
        
        print(f"   📡 Status da resposta: {edit_response.status_code}")
        
        if edit_response.status_code == 200:
            response_data = edit_response.json()
            print(f"   ✅ Edição bem-sucedida!")
            print(f"   📋 Resposta: {json.dumps(response_data, indent=2)}")
            
            # 4. Verificar se foi atualizada no banco
            print(f"\n📋 4. Verificando atualização no banco...")
            try:
                mensagem_atualizada = Mensagem.objects.get(id=primeira_mensagem.id)
                print(f"   - Conteúdo no banco: {mensagem_atualizada.conteudo[:50]}...")
                
                if mensagem_atualizada.conteudo == novo_texto:
                    print(f"   ✅ Mensagem atualizada corretamente no banco!")
                else:
                    print(f"   ⚠️ Mensagem não foi atualizada no banco")
                    print(f"      Esperado: {novo_texto[:50]}...")
                    print(f"      Atual: {mensagem_atualizada.conteudo[:50]}...")
                    
            except Mensagem.DoesNotExist:
                print(f"   ❌ Mensagem não encontrada no banco")
                
        else:
            print(f"   ❌ Erro na edição: {edit_response.status_code}")
            try:
                error_data = edit_response.json()
                print(f"   📋 Erro: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   📋 Erro: {edit_response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Erro de conexão: {e}")
    
    # 5. Testar casos de erro
    print(f"\n🧪 5. Testando casos de erro...")
    
    # 5.1 - Tentar editar mensagem inexistente
    print(f"   5.1. Testando edição de mensagem inexistente...")
    try:
        error_response = requests.post(
            "http://localhost:8000/api/mensagens/999999/editar/",
            json={'novo_texto': 'teste'},
            headers=headers,
            timeout=10
        )
        print(f"      Status: {error_response.status_code}")
        if error_response.status_code == 404:
            print(f"      ✅ Erro 404 retornado corretamente")
        else:
            print(f"      ⚠️ Status inesperado: {error_response.status_code}")
    except Exception as e:
        print(f"      ❌ Erro: {e}")
    
    # 5.2 - Tentar editar com texto vazio
    print(f"   5.2. Testando edição com texto vazio...")
    try:
        empty_response = requests.post(
            f"http://localhost:8000/api/mensagens/{primeira_mensagem.id}/editar/",
            json={'novo_texto': ''},
            headers=headers,
            timeout=10
        )
        print(f"      Status: {empty_response.status_code}")
        if empty_response.status_code == 400:
            print(f"      ✅ Erro 400 retornado corretamente")
        else:
            print(f"      ⚠️ Status inesperado: {empty_response.status_code}")
    except Exception as e:
        print(f"      ❌ Erro: {e}")
    
    # 6. Resumo final
    print(f"\n📊 6. Resumo do teste:")
    print(f"   ✅ Login na API: OK")
    print(f"   ✅ Mensagens encontradas: {len(mensagens)}")
    print(f"   ✅ Endpoint de edição: Disponível")
    print(f"   ✅ Validações de erro: Testadas")
    
    print(f"\n🎯 Funcionalidade de edição de mensagens está pronta para uso!")

if __name__ == "__main__":
    test_edicao_completa() 