#!/usr/bin/env python
"""
Script para verificar se o admin está registrado corretamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from django.contrib import admin
from core.models import Mensagem, Chat, Cliente
from webhook.models import Message, WebhookEvent

def test_admin_registration():
    """Testa se os modelos estão registrados no admin"""
    print("🔍 Verificando registros no admin...")
    
    # Verificar modelos registrados
    registered_models = admin.site._registry.keys()
    
    print("\n📋 Modelos registrados no admin:")
    for model in registered_models:
        print(f"   ✅ {model._meta.app_label}.{model._meta.model_name}")
    
    # Verificar se Mensagem está registrado
    if Mensagem in admin.site._registry:
        print(f"\n✅ Mensagem (core) está registrado no admin")
        admin_class = admin.site._registry[Mensagem]
        print(f"   Admin class: {admin_class.__class__.__name__}")
        print(f"   List display: {admin_class.list_display}")
    else:
        print(f"\n❌ Mensagem (core) NÃO está registrado no admin")
    
    # Verificar se Message está registrado
    if Message in admin.site._registry:
        print(f"\n✅ Message (webhook) está registrado no admin")
        admin_class = admin.site._registry[Message]
        print(f"   Admin class: {admin_class.__class__.__name__}")
        print(f"   List display: {admin_class.list_display}")
    else:
        print(f"\n❌ Message (webhook) NÃO está registrado no admin")
    
    # Verificar dados
    print(f"\n📊 Dados nos modelos:")
    print(f"   Mensagem (core): {Mensagem.objects.count()} registros")
    print(f"   Message (webhook): {Message.objects.count()} registros")
    print(f"   Chat: {Chat.objects.count()} registros")
    print(f"   Cliente: {Cliente.objects.count()} registros")
    print(f"   WebhookEvent: {WebhookEvent.objects.count()} registros")

if __name__ == "__main__":
    test_admin_registration() 