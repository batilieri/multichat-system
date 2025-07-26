#!/usr/bin/env python3
"""
Script para verificar e corrigir clientes, associando a instância do WhatsApp corretamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Cliente, WhatsappInstance
from django.utils import timezone

def listar_clientes():
    """Lista todos os clientes existentes"""
    print("📋 CLIENTES EXISTENTES:")
    print("=" * 50)
    
    clientes = Cliente.objects.all()
    for i, cliente in enumerate(clientes, 1):
        print(f"{i}. ID: {cliente.id}")
        print(f"   Nome: {cliente.nome}")
        print(f"   Email: {cliente.email}")
        print(f"   WAPI Instance: {cliente.wapi_instance_id}")
        print(f"   Ativo: {cliente.ativo}")
        print()
    
    return clientes

def associar_instancia_elizeu():
    """Associa a instância do WhatsApp ao cliente ELIZEU BATILIERE DOS SANTOS"""
    
    # Buscar o cliente ELIZEU
    try:
        cliente_elizeu = Cliente.objects.get(nome__icontains='ELIZEU BATILIERE DOS SANTOS')
        print(f"✅ Cliente ELIZEU encontrado: {cliente_elizeu.nome}")
    except Cliente.DoesNotExist:
        print("❌ Cliente 'ELIZEU BATILIERE DOS SANTOS' não encontrado!")
        return False
    except Cliente.MultipleObjectsReturned:
        print("⚠️  Múltiplos clientes com 'ELIZEU BATILIERE DOS SANTOS' encontrados!")
        clientes = Cliente.objects.filter(nome__icontains='ELIZEU BATILIERE DOS SANTOS')
        for i, cliente in enumerate(clientes, 1):
            print(f"   {i}. {cliente.nome} (ID: {cliente.id})")
        
        # Usar o primeiro encontrado
        cliente_elizeu = clientes.first()
        print(f"✅ Usando o primeiro: {cliente_elizeu.nome}")
    
    # Credenciais da WAPI dos exemplos
    instance_id = "3B6XIW-ZTS923-GEAY6V"
    token = "Q8EOH07SJkXhg4iT6Qmhz1BJdLl8nL9WF"
    
    # Atualizar cliente com credenciais WAPI
    cliente_elizeu.wapi_instance_id = instance_id
    cliente_elizeu.wapi_token = token
    cliente_elizeu.save()
    print(f"✅ Cliente atualizado com credenciais WAPI")
    
    # Criar ou atualizar instância do WhatsApp
    try:
        instancia = WhatsappInstance.objects.get(instance_id=instance_id)
        print(f"⚠️  Instância já existe: {instancia}")
        
        # Atualizar para associar ao cliente correto
        if instancia.cliente != cliente_elizeu:
            instancia.cliente = cliente_elizeu
            instancia.save()
            print(f"✅ Instância atualizada para o cliente: {cliente_elizeu.nome}")
        else:
            print(f"✅ Instância já está associada ao cliente correto")
        
    except WhatsappInstance.DoesNotExist:
        # Criar nova instância
        instancia = WhatsappInstance.objects.create(
            instance_id=instance_id,
            token=token,
            cliente=cliente_elizeu,
            status='connected',  # Baseado nos logs, parece estar conectado
            created_at=timezone.now()
        )
        print(f"✅ Nova instância criada: {instancia}")
    
    return instancia

def limpar_clientes_duplicados():
    """Remove clientes duplicados ou desnecessários"""
    print("\n🧹 VERIFICANDO CLIENTES DUPLICADOS:")
    print("=" * 50)
    
    # Listar todos os clientes
    clientes = Cliente.objects.all()
    
    # Agrupar por nome similar
    nomes_similares = {}
    for cliente in clientes:
        nome_limpo = cliente.nome.lower().strip()
        if nome_limpo not in nomes_similares:
            nomes_similares[nome_limpo] = []
        nomes_similares[nome_limpo].append(cliente)
    
    # Verificar duplicados
    for nome, lista_clientes in nomes_similares.items():
        if len(lista_clientes) > 1:
            print(f"⚠️  Encontrados {len(lista_clientes)} clientes com nome similar: '{nome}'")
            for i, cliente in enumerate(lista_clientes, 1):
                print(f"   {i}. ID: {cliente.id} | Nome: {cliente.nome} | Email: {cliente.email}")
            
            # Manter apenas o primeiro (mais antigo)
            cliente_manter = lista_clientes[0]
            clientes_remover = lista_clientes[1:]
            
            print(f"✅ Mantendo: {cliente_manter.nome}")
            for cliente in clientes_remover:
                print(f"🗑️  Removendo: {cliente.nome}")
                cliente.delete()

if __name__ == "__main__":
    print("🔍 VERIFICANDO E CORRIGINDO CLIENTES...")
    print("=" * 60)
    
    # Listar clientes existentes
    clientes = listar_clientes()
    
    # Limpar duplicados se necessário
    if clientes.count() > 1:
        limpar_clientes_duplicados()
    
    # Associar instância ao cliente ELIZEU
    instancia = associar_instancia_elizeu()
    
    if instancia:
        print("\n✅ CONFIGURAÇÃO CONCLUÍDA!")
        print("=" * 60)
        print(f"📱 Instância: {instancia.instance_id}")
        print(f"👤 Cliente: {instancia.cliente.nome}")
        print(f"🔑 Token: {instancia.token[:10]}...")
        print(f"📊 Status: {instancia.status}")
        
        print("\n🎯 Agora o webhook deve funcionar corretamente!")
        print("📨 Teste enviando uma mensagem no WhatsApp")
        print("🌐 Verifique se os chats aparecem no frontend")
    else:
        print("\n❌ Erro na configuração!") 