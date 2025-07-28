#!/usr/bin/env python
"""
Script para testar a API de edição diretamente.
"""

import os
import sys
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente, WhatsappInstance

def test_api_edicao_direto():
    """Testa a API de edição diretamente"""
    
    print("🧪 Testando API de edição diretamente...")
    print("=" * 50)
    
    # 1. Encontrar uma mensagem editável
    mensagem_editavel = Mensagem.objects.filter(
        from_me=True,
        tipo__in=['texto', 'text'],
        message_id__isnull=False
    ).exclude(message_id='').first()
    
    if not mensagem_editavel:
        print("❌ Nenhuma mensagem editável encontrada")
        return
    
    print(f"📝 Mensagem encontrada para teste:")
    print(f"   - ID: {mensagem_editavel.id}")
    print(f"   - Conteúdo: {mensagem_editavel.conteudo}")
    print(f"   - from_me: {mensagem_editavel.from_me}")
    print(f"   - message_id: {mensagem_editavel.message_id}")
    print(f"   - tipo: {mensagem_editavel.tipo}")
    
    # 2. Login na API
    print(f"\n🔐 Fazendo login...")
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
            return
        
        token = login_response.json().get('access')
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        print("✅ Login realizado com sucesso")
        
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return
    
    # 3. Testar endpoint de edição
    print(f"\n📝 Testando endpoint de edição...")
    
    novo_texto = f"[TESTE API] {mensagem_editavel.conteudo}"
    edit_data = {
        'novo_texto': novo_texto
    }
    
    try:
        edit_response = requests.post(
            f"http://localhost:8000/api/mensagens/{mensagem_editavel.id}/editar/",
            json=edit_data,
            headers=headers,
            timeout=30
        )
        
        print(f"📡 Status: {edit_response.status_code}")
        print(f"📋 Headers: {dict(edit_response.headers)}")
        
        try:
            response_data = edit_response.json()
            print(f"📋 Resposta: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📋 Resposta (texto): {edit_response.text}")
        
        if edit_response.status_code == 200:
            print("✅ Edição bem-sucedida via API!")
            
            # Verificar se foi atualizada no banco
            mensagem_editavel.refresh_from_db()
            print(f"📋 Conteúdo atualizado no banco: {mensagem_editavel.conteudo}")
            
        else:
            print("❌ Erro na edição via API")
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
    
    # 4. Testar endpoint de listagem para verificar se a mensagem aparece
    print(f"\n📋 Testando listagem de mensagens...")
    
    try:
        list_response = requests.get(
            f"http://localhost:8000/api/mensagens/?chat_id={mensagem_editavel.chat.chat_id}",
            headers=headers,
            timeout=10
        )
        
        print(f"📡 Status da listagem: {list_response.status_code}")
        
        if list_response.status_code == 200:
            try:
                list_data = list_response.json()
                mensagens = list_data.get('results', list_data)
                
                # Procurar a mensagem editada
                mensagem_encontrada = None
                for msg in mensagens:
                    if msg.get('id') == mensagem_editavel.id:
                        mensagem_encontrada = msg
                        break
                
                if mensagem_encontrada:
                    print(f"✅ Mensagem encontrada na listagem:")
                    print(f"   - ID: {mensagem_encontrada.get('id')}")
                    print(f"   - Conteúdo: {mensagem_encontrada.get('conteudo', mensagem_encontrada.get('content'))}")
                    print(f"   - from_me: {mensagem_encontrada.get('from_me')}")
                    print(f"   - tipo: {mensagem_encontrada.get('tipo')}")
                else:
                    print("❌ Mensagem não encontrada na listagem")
                    
            except Exception as e:
                print(f"❌ Erro ao processar resposta da listagem: {e}")
        else:
            print(f"❌ Erro na listagem: {list_response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar listagem: {e}")

if __name__ == "__main__":
    test_api_edicao_direto() 