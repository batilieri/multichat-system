#!/usr/bin/env python3
"""
Script para criar instância do WhatsApp associada ao cliente ELIZEU BATILIERE DOS SANTOS
Usando as credenciais dos exemplos da WAPI
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Cliente, WhatsappInstance
from django.utils import timezone

def criar_instancia_whatsapp():
    """Cria instância do WhatsApp para o cliente ELIZEU BATILIERE DOS SANTOS"""
    
    # Buscar o cliente
    try:
        cliente = Cliente.objects.get(nome__icontains='ELIZEU BATILIERE DOS SANTOS')
        print(f"✅ Cliente encontrado: {cliente.nome}")
    except Cliente.DoesNotExist:
        print("❌ Cliente 'ELIZEU BATILIERE DOS SANTOS' não encontrado!")
        return False
    
    # Credenciais da WAPI dos exemplos
    instance_id = "3B6XIW-ZTS923-GEAY6V"
    token = "Q8EOH07SJkXhg4iT6Qmhz1BJdLl8nL9WF"
    
    # Verificar se já existe uma instância com esse ID
    try:
        instancia_existente = WhatsappInstance.objects.get(instance_id=instance_id)
        print(f"⚠️  Instância já existe: {instancia_existente}")
        
        # Atualizar para associar ao cliente correto
        if instancia_existente.cliente != cliente:
            instancia_existente.cliente = cliente
            instancia_existente.save()
            print(f"✅ Instância atualizada para o cliente: {cliente.nome}")
        else:
            print(f"✅ Instância já está associada ao cliente correto")
        
        return instancia_existente
        
    except WhatsappInstance.DoesNotExist:
        # Criar nova instância
        instancia = WhatsappInstance.objects.create(
            instance_id=instance_id,
            token=token,
            cliente=cliente,
            status='disconnected',  # Será atualizado quando conectar
            created_at=timezone.now()
        )
        print(f"✅ Nova instância criada: {instancia}")
        return instancia

def atualizar_cliente_wapi():
    """Atualiza o cliente com as informações da WAPI"""
    
    try:
        cliente = Cliente.objects.get(nome__icontains='ELIZEU BATILIERE DOS SANTOS')
        
        # Atualizar campos da WAPI no cliente
        cliente.wapi_instance_id = "3B6XIW-ZTS923-GEAY6V"
        cliente.wapi_token = "Q8EOH07SJkXhg4iT6Qmhz1BJdLl8nL9WF"
        cliente.save()
        
        print(f"✅ Cliente atualizado com credenciais WAPI: {cliente.nome}")
        return True
        
    except Cliente.DoesNotExist:
        print("❌ Cliente não encontrado!")
        return False

if __name__ == "__main__":
    print("🚀 Configurando instância do WhatsApp para ELIZEU BATILIERE DOS SANTOS...")
    print("=" * 60)
    
    # Atualizar cliente com credenciais WAPI
    if atualizar_cliente_wapi():
        # Criar instância do WhatsApp
        instancia = criar_instancia_whatsapp()
        
        if instancia:
            print("\n✅ Configuração concluída!")
            print(f"📱 Instância: {instancia.instance_id}")
            print(f"👤 Cliente: {instancia.cliente.nome}")
            print(f"🔑 Token: {instancia.token[:10]}...")
            print(f"📊 Status: {instancia.status}")
            
            print("\n🎯 Próximos passos:")
            print("1. Ativar o webhook para receber mensagens")
            print("2. Conectar a instância do WhatsApp")
            print("3. Testar recebimento de mensagens no frontend")
        else:
            print("❌ Erro ao criar instância!")
    else:
        print("❌ Erro ao configurar cliente!") 