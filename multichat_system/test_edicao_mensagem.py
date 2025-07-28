#!/usr/bin/env python
"""
Script para testar a funcionalidade de edição de mensagens.
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

def test_edicao_mensagem():
    """Testa a funcionalidade de edição de mensagens"""
    
    print("🧪 Testando funcionalidade de edição de mensagens...")
    print("=" * 60)
    
    # 1. Verificar mensagens disponíveis para edição
    print("📊 Mensagens disponíveis para edição:")
    mensagens = Mensagem.objects.filter(
        from_me=True,
        tipo__in=['texto', 'text'],
        message_id__isnull=False
    ).exclude(message_id='').order_by('-data_envio')[:3]
    
    for i, msg in enumerate(mensagens):
        print(f"   {i+1}. ID: {msg.id}, message_id: {msg.message_id}, tipo: {msg.tipo}")
        print(f"      Conteúdo: {msg.conteudo[:50]}...")
    
    if not mensagens:
        print("❌ Nenhuma mensagem encontrada para edição")
        return
    
    # 2. Testar API de edição
    print("\n🧪 Testando API de edição...")
    
    # Login
    login_data = {
        "email": "admin@multichat.com",
        "password": "admin123"
    }
    
    login_response = requests.post(
        "http://localhost:8000/api/auth/login/",
        json=login_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Erro no login: {login_response.status_code}")
        return
    
    token = login_response.json().get('access')
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Testar edição da primeira mensagem
    primeira_mensagem = mensagens[0]
    novo_texto = f"[EDITADO] {primeira_mensagem.conteudo}"
    
    print(f"\n📝 Testando edição da primeira mensagem:")
    print(f"   - ID interno: {primeira_mensagem.id}")
    print(f"   - message_id: {primeira_mensagem.message_id}")
    print(f"   - Texto original: {primeira_mensagem.conteudo[:50]}...")
    print(f"   - Novo texto: {novo_texto[:50]}...")
    
    edit_data = {
        'novo_texto': novo_texto
    }
    
    edit_response = requests.post(
        f"http://localhost:8000/api/mensagens/{primeira_mensagem.id}/editar/",
        json=edit_data,
        headers=headers
    )
    
    print(f"   📡 Status: {edit_response.status_code}")
    if edit_response.status_code == 200:
        print(f"   ✅ Edição bem-sucedida!")
        response_data = edit_response.json()
        print(f"   📋 Resposta: {response_data}")
    else:
        print(f"   ❌ Erro na edição: {edit_response.text}")
    
    # 3. Verificar se a mensagem foi atualizada no banco
    try:
        mensagem_atualizada = Mensagem.objects.get(id=primeira_mensagem.id)
        print(f"\n📋 Verificação no banco:")
        print(f"   - Conteúdo atualizado: {mensagem_atualizada.conteudo[:50]}...")
        if mensagem_atualizada.conteudo == novo_texto:
            print(f"   ✅ Mensagem atualizada corretamente no banco!")
        else:
            print(f"   ⚠️ Mensagem não foi atualizada no banco")
    except Mensagem.DoesNotExist:
        print(f"   ❌ Mensagem não encontrada no banco")

if __name__ == "__main__":
    test_edicao_mensagem() 