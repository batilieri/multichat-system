#!/usr/bin/env python3
"""
Script para testar o isolamento entre clientes no sistema MultiChat
Verifica se cada cliente está usando apenas suas próprias instâncias
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
django.setup()

from core.models import Cliente, WhatsappInstance, Chat, Mensagem
from core.utils import (
    get_client_whatsapp_instance,
    get_whatsapp_instance_by_chat,
    get_whatsapp_instance_by_message,
    validate_client_isolation
)

def testar_isolamento_clientes():
    """Testa o isolamento entre clientes"""
    print("🧪 TESTANDO ISOLAMENTO ENTRE CLIENTES")
    print("=" * 60)
    
    # Buscar todos os clientes
    clientes = Cliente.objects.all()
    print(f"👥 Total de clientes encontrados: {clientes.count()}")
    
    for cliente in clientes:
        print(f"\n👤 Cliente: {cliente.nome} (ID: {cliente.id})")
        print("-" * 40)
        
        # Testar função get_client_whatsapp_instance
        instancia = get_client_whatsapp_instance(cliente, prefer_connected=True)
        if instancia:
            print(f"✅ Instância encontrada: {instancia.instance_id}")
            print(f"   Status: {instancia.status}")
            print(f"   Cliente da instância: {instancia.cliente.nome}")
            
            # Verificar se a instância pertence ao cliente correto
            if instancia.cliente == cliente:
                print(f"   ✅ Isolamento correto: instância pertence ao cliente")
            else:
                print(f"   ❌ VIOLAÇÃO DE ISOLAMENTO: instância pertence a outro cliente!")
        else:
            print(f"⚠️  Nenhuma instância encontrada para o cliente")
        
        # Testar função get_all_client_instances
        from core.utils import get_all_client_instances
        todas_instancias = get_all_client_instances(cliente)
        print(f"   📱 Total de instâncias do cliente: {len(todas_instancias)}")
        
        for inst in todas_instancias:
            print(f"      - {inst.instance_id} (Status: {inst.status})")
            if inst.cliente != cliente:
                print(f"        ❌ VIOLAÇÃO: instância pertence a {inst.cliente.nome}!")
    
    print("\n" + "=" * 60)
    print("🧪 TESTANDO FUNÇÕES POR CHAT E MENSAGEM")
    print("=" * 60)
    
    # Testar com chats
    chats = Chat.objects.all()[:5]  # Primeiros 5 chats
    for chat in chats:
        print(f"\n💬 Chat: {chat.chat_id} - Cliente: {chat.cliente.nome}")
        
        instancia_chat = get_whatsapp_instance_by_chat(chat, prefer_connected=True)
        if instancia_chat:
            print(f"   ✅ Instância encontrada: {instancia_chat.instance_id}")
            if instancia_chat.cliente == chat.cliente:
                print(f"   ✅ Isolamento correto")
            else:
                print(f"   ❌ VIOLAÇÃO: instância pertence a {instancia_chat.cliente.nome}")
        else:
            print(f"   ⚠️  Nenhuma instância encontrada")
    
    # Testar com mensagens
    mensagens = Mensagem.objects.all()[:5]  # Primeiras 5 mensagens
    for msg in mensagens:
        print(f"\n📝 Mensagem: {msg.id} - Chat: {msg.chat.chat_id}")
        
        instancia_msg = get_whatsapp_instance_by_message(msg, prefer_connected=True)
        if instancia_msg:
            print(f"   ✅ Instância encontrada: {instancia_msg.instance_id}")
            if instancia_msg.cliente == msg.chat.cliente:
                print(f"   ✅ Isolamento correto")
            else:
                print(f"   ❌ VIOLAÇÃO: instância pertence a {instancia_msg.cliente.nome}")
        else:
            print(f"   ⚠️  Nenhuma instância encontrada")
    
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO INTEGRIDADE DO BANCO")
    print("=" * 60)
    
    # Verificar se há instâncias sem cliente
    instancias_sem_cliente = WhatsappInstance.objects.filter(cliente__isnull=True)
    if instancias_sem_cliente.exists():
        print(f"❌ Encontradas {instancias_sem_cliente.count()} instâncias sem cliente!")
        for inst in instancias_sem_cliente:
            print(f"   - {inst.instance_id}")
    else:
        print("✅ Todas as instâncias têm cliente associado")
    
    # Verificar se há chats sem cliente
    chats_sem_cliente = Chat.objects.filter(cliente__isnull=True)
    if chats_sem_cliente.exists():
        print(f"❌ Encontrados {chats_sem_cliente.count()} chats sem cliente!")
        for chat in chats_sem_cliente:
            print(f"   - {chat.chat_id}")
    else:
        print("✅ Todos os chats têm cliente associado")
    
    # Verificar se há mensagens em chats de clientes diferentes
    mensagens_problema = []
    for msg in Mensagem.objects.select_related('chat__cliente').all():
        if msg.chat and msg.chat.cliente:
            # Verificar se a mensagem tem instância associada
            instancia_msg = get_whatsapp_instance_by_message(msg, prefer_connected=False)
            if instancia_msg and instancia_msg.cliente != msg.chat.cliente:
                mensagens_problema.append(msg)
    
    if mensagens_problema:
        print(f"❌ Encontradas {len(mensagens_problema)} mensagens com problema de isolamento!")
        for msg in mensagens_problema[:5]:  # Mostrar apenas as primeiras 5
            print(f"   - Msg {msg.id}: Chat {msg.chat.chat_id} (Cliente: {msg.chat.cliente.nome})")
            instancia = get_whatsapp_instance_by_message(msg, prefer_connected=False)
            print(f"     Instância: {instancia.instance_id} (Cliente: {instancia.cliente.nome})")
    else:
        print("✅ Todas as mensagens estão com isolamento correto")
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DO TESTE")
    print("=" * 60)
    
    total_clientes = Cliente.objects.count()
    total_instancias = WhatsappInstance.objects.count()
    total_chats = Chat.objects.count()
    total_mensagens = Mensagem.objects.count()
    
    print(f"👥 Clientes: {total_clientes}")
    print(f"📱 Instâncias: {total_instancias}")
    print(f"💬 Chats: {total_chats}")
    print(f"📝 Mensagens: {total_mensagens}")
    
    # Verificar se cada cliente tem pelo menos uma instância
    clientes_sem_instancia = []
    for cliente in clientes:
        if not WhatsappInstance.objects.filter(cliente=cliente).exists():
            clientes_sem_instancia.append(cliente)
    
    if clientes_sem_instancia:
        print(f"\n⚠️  Clientes sem instância: {len(clientes_sem_instancia)}")
        for cliente in clientes_sem_instancia:
            print(f"   - {cliente.nome}")
    else:
        print(f"\n✅ Todos os clientes têm pelo menos uma instância")
    
    print("\n🎯 Teste de isolamento concluído!")

if __name__ == "__main__":
    testar_isolamento_clientes() 