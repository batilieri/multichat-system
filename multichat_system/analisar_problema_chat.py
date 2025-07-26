#!/usr/bin/env python
"""
Script para analisar o problema com criação de chats
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from webhook.models import Chat as WebhookChat, Cliente
from core.models import Chat as CoreChat, Cliente
from django.db import IntegrityError

def analisar_problema_chat():
    """Analisa o problema com a criação de chats"""
    
    print("=== ANÁLISE DO PROBLEMA DE CRIAÇÃO DE CHATS ===\n")
    
    # 1. Verificar chats existentes
    print("1. CHATS EXISTENTES:")
    chats = WebhookChat.objects.all()
    for chat in chats:
        print(f"   - ID: {chat.id}, chat_id: '{chat.chat_id}', cliente: {chat.cliente.nome}, chat_name: '{chat.chat_name}'")
    
    print(f"\n   Total de chats: {chats.count()}")
    
    # 2. Verificar se existe chat com o ID problemático
    chat_id_problematico = "556993291093"
    print(f"\n2. VERIFICANDO CHAT PROBLEMÁTICO: {chat_id_problematico}")
    
    try:
        chat_existente = WebhookChat.objects.get(chat_id=chat_id_problematico)
        print(f"   ✅ Chat encontrado: ID={chat_existente.id}, cliente={chat_existente.cliente.nome}")
        print(f"   - chat_name: '{chat_existente.chat_name}'")
        print(f"   - is_group: {chat_existente.is_group}")
        print(f"   - status: {chat_existente.status}")
        print(f"   - created_at: {chat_existente.created_at}")
        print(f"   - last_message_at: {chat_existente.last_message_at}")
    except WebhookChat.DoesNotExist:
        print(f"   ❌ Chat com chat_id '{chat_id_problematico}' não encontrado")
    
    # 3. Tentar criar um chat com o mesmo ID para simular o erro
    print(f"\n3. SIMULANDO CRIAÇÃO DE CHAT DUPLICADO:")
    
    # Pegar o primeiro cliente
    cliente = Cliente.objects.first()
    if not cliente:
        print("   ❌ Nenhum cliente encontrado no banco")
        return
    
    print(f"   Usando cliente: {cliente.nome}")
    
    try:
        # Tentar criar um chat com o mesmo ID
        novo_chat = WebhookChat.objects.create(
            chat_id=chat_id_problematico,
            cliente=cliente,
            chat_name="Teste Duplicado",
            is_group=False,
            status='active'
        )
        print(f"   ❌ ERRO: Chat foi criado quando deveria falhar!")
        # Deletar o chat criado incorretamente
        novo_chat.delete()
        print(f"   Chat de teste deletado")
        
    except IntegrityError as e:
        print(f"   ✅ CORRETO: Erro de integridade capturado: {e}")
    except Exception as e:
        print(f"   ⚠️ Outro erro: {e}")
    
    # 4. Testar get_or_create
    print(f"\n4. TESTANDO get_or_create:")
    
    try:
        chat, created = WebhookChat.objects.get_or_create(
            chat_id=chat_id_problematico,
            cliente=cliente,
            defaults={
                'chat_name': 'Teste Get or Create',
                'is_group': False,
                'status': 'active'
            }
        )
        print(f"   - created: {created}")
        print(f"   - chat_id: {chat.chat_id}")
        print(f"   - chat_name: {chat.chat_name}")
        
        if not created:
            print(f"   ✅ CORRETO: Chat existente foi recuperado")
        else:
            print(f"   ❌ ERRO: Novo chat foi criado quando deveria recuperar o existente")
            
    except Exception as e:
        print(f"   ❌ Erro no get_or_create: {e}")
    
    # 5. Verificar se há problemas na estrutura do modelo
    print(f"\n5. VERIFICANDO ESTRUTURA DO MODELO:")
    
    # Verificar se há campos obrigatórios
    campos_obrigatorios = []
    for field in WebhookChat._meta.fields:
        if not field.blank and not field.null and not field.primary_key:
            campos_obrigatorios.append(field.name)
    
    print(f"   Campos obrigatórios: {campos_obrigatorios}")
    
    # Verificar constraints únicas
    constraints_unicas = []
    for field in WebhookChat._meta.fields:
        if field.unique:
            constraints_unicas.append(field.name)
    
    print(f"   Campos únicos: {constraints_unicas}")
    
    # Verificar unique_together
    if hasattr(WebhookChat._meta, 'unique_together') and WebhookChat._meta.unique_together:
        print(f"   Unique together: {WebhookChat._meta.unique_together}")
    else:
        print(f"   Unique together: Nenhum")
    
    print(f"\n=== FIM DA ANÁLISE ===")

if __name__ == "__main__":
    analisar_problema_chat() 