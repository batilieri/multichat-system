#!/usr/bin/env python
"""
Script para debug detalhado do problema de exclusão de mensagens.
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

def debug_exclusao_detalhado():
    """Debug detalhado do problema de exclusão"""
    
    print("🔍 Debug detalhado do problema de exclusão...")
    print("=" * 60)
    
    # 1. Verificar mensagens disponíveis
    print("📊 Mensagens disponíveis para exclusão:")
    mensagens = Mensagem.objects.filter(
        from_me=True,
        message_id__isnull=False
    ).exclude(message_id='').order_by('-data_envio')[:5]
    
    for i, msg in enumerate(mensagens):
        print(f"   {i+1}. ID: {msg.id}, message_id: {msg.message_id}, from_me: {msg.from_me}")
    
    if not mensagens:
        print("❌ Nenhuma mensagem encontrada para exclusão")
        return
    
    # 2. Testar API de exclusão
    print("\n🧪 Testando API de exclusão...")
    
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
    
    # Testar exclusão da primeira mensagem
    primeira_mensagem = mensagens[0]
    print(f"\n📝 Testando exclusão da primeira mensagem:")
    print(f"   - ID interno: {primeira_mensagem.id}")
    print(f"   - message_id: {primeira_mensagem.message_id}")
    
    delete_response = requests.delete(
        f"http://localhost:8000/api/mensagens/{primeira_mensagem.id}/",
        headers=headers
    )
    
    print(f"   📡 Status: {delete_response.status_code}")
    if delete_response.status_code != 204 and delete_response.status_code != 200:
        print(f"   ❌ Erro: {delete_response.text}")
    else:
        print(f"   ✅ Primeira exclusão bem-sucedida!")
    
    # Verificar se a mensagem foi removida do banco
    try:
        Mensagem.objects.get(id=primeira_mensagem.id)
        print(f"   ⚠️ Mensagem ainda existe no banco!")
    except Mensagem.DoesNotExist:
        print(f"   ✅ Mensagem removida do banco!")
    
    # Testar exclusão da segunda mensagem (se existir)
    if len(mensagens) > 1:
        segunda_mensagem = mensagens[1]
        print(f"\n📝 Testando exclusão da segunda mensagem:")
        print(f"   - ID interno: {segunda_mensagem.id}")
        print(f"   - message_id: {segunda_mensagem.message_id}")
        
        delete_response2 = requests.delete(
            f"http://localhost:8000/api/mensagens/{segunda_mensagem.id}/",
            headers=headers
        )
        
        print(f"   📡 Status: {delete_response2.status_code}")
        if delete_response2.status_code != 204 and delete_response2.status_code != 200:
            print(f"   ❌ Erro: {delete_response2.text}")
        else:
            print(f"   ✅ Segunda exclusão bem-sucedida!")
    
    # 3. Verificar logs do servidor
    print(f"\n📋 Verificando logs do servidor...")
    print(f"   - Verifique os logs do servidor Django para mais detalhes")
    print(f"   - Procure por erros relacionados à exclusão")

if __name__ == "__main__":
    debug_exclusao_detalhado() 