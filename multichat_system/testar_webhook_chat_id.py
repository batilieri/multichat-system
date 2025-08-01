#!/usr/bin/env python3
"""
Script para testar o processamento de webhooks com chat_id normalizado
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from webhook.views import normalize_chat_id, save_message_to_chat_with_from_me
from core.models import Cliente, WhatsappInstance

def testar_normalizacao_chat_id():
    """
    Testa a normalização de chat_id
    """
    print("🧪 TESTANDO NORMALIZAÇÃO DE CHAT_ID")
    print("=" * 60)
    
    # Testes com diferentes formatos
    testes = [
        ("111141053288574@lid", "111141053288574"),
        ("556992962029-1415646286@g.us", "5569929620291415646286"),
        ("556999171919-1524353875@g.us", "5569991719191524353875"),
        ("120363373541551792@g.us", "120363373541551792"),
        ("5511999999999", "5511999999999"),
        ("5511888888888@c.us", "5511888888888"),
    ]
    
    sucessos = 0
    for chat_id_incorreto, chat_id_esperado in testes:
        resultado = normalize_chat_id(chat_id_incorreto)
        sucesso = resultado == chat_id_esperado
        
        print(f"📱 {chat_id_incorreto} -> {resultado}")
        print(f"   Esperado: {chat_id_esperado}")
        print(f"   ✅ {'PASSOU' if sucesso else '❌ FALHOU'}")
        print()
        
        if sucesso:
            sucessos += 1
    
    print(f"📊 Normalização: {sucessos}/{len(testes)} testes passaram")
    return sucessos == len(testes)

def simular_webhook_mensagem():
    """
    Simula um webhook de mensagem para testar o processamento
    """
    print("\n📨 SIMULANDO WEBHOOK DE MENSAGEM")
    print("=" * 60)
    
    # Buscar cliente e instância para teste
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado")
        return False
    
    instance = WhatsappInstance.objects.filter(cliente=cliente).first()
    if not instance:
        print("❌ Nenhuma instância encontrada")
        return False
    
    print(f"👤 Cliente: {cliente.nome}")
    print(f"📱 Instância: {instance.instance_id}")
    
    # Simular payload de webhook
    webhook_payload = {
        "instanceId": instance.instance_id,
        "messageId": "test_message_123",
        "chat": {
            "id": "111141053288574@lid"  # ID incorreto para testar normalização
        },
        "sender": {
            "id": "111141053288574@lid",
            "pushName": "Teste Contato",
            "verifiedName": "Teste Contato"
        },
        "message": {
            "conversation": "Olá! Esta é uma mensagem de teste."
        },
        "messageTimestamp": 1234567890,
        "fromMe": False
    }
    
    print(f"📦 Payload simulado:")
    print(f"   Chat ID original: {webhook_payload['chat']['id']}")
    print(f"   Mensagem: {webhook_payload['message']['conversation']}")
    print(f"   FromMe: {webhook_payload['fromMe']}")
    
    # Testar normalização
    chat_id_normalizado = normalize_chat_id(webhook_payload['chat']['id'])
    print(f"📱 Chat ID normalizado: {webhook_payload['chat']['id']} -> {chat_id_normalizado}")
    
    if chat_id_normalizado == "111141053288574":
        print("✅ Normalização funcionando corretamente!")
        return True
    else:
        print("❌ Normalização falhou!")
        return False

def testar_salvamento_mensagem():
    """
    Testa o salvamento de mensagem com chat_id normalizado
    """
    print("\n💾 TESTANDO SALVAMENTO DE MENSAGEM")
    print("=" * 60)
    
    # Buscar cliente e instância
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado")
        return False
    
    instance = WhatsappInstance.objects.filter(cliente=cliente).first()
    if not instance:
        print("❌ Nenhuma instância encontrada")
        return False
    
    # Criar evento de webhook para teste
    from webhook.models import WebhookEvent
    from django.utils import timezone
    
    event = WebhookEvent.objects.create(
        cliente=cliente,
        instance_id=instance.instance_id,
        event_type="test_message",
        raw_data={"test": "data"},
        ip_address="127.0.0.1",
        user_agent="Test Agent"
    )
    
    # Payload com chat_id incorreto
    payload = {
        "instanceId": instance.instance_id,
        "messageId": f"test_msg_{timezone.now().timestamp()}",
        "chat": {
            "id": "111141053288574@lid"  # ID incorreto
        },
        "sender": {
            "id": "111141053288574@lid",
            "pushName": "Teste Contato"
        },
        "message": {
            "conversation": "Mensagem de teste com chat_id normalizado"
        },
        "messageTimestamp": int(timezone.now().timestamp()),
        "fromMe": False
    }
    
    print(f"📦 Salvando mensagem com payload:")
    print(f"   Chat ID: {payload['chat']['id']}")
    print(f"   Mensagem: {payload['message']['conversation']}")
    
    try:
        # Tentar salvar a mensagem
        success = save_message_to_chat_with_from_me(payload, event, False, cliente)
        
        if success:
            print("✅ Mensagem salva com sucesso!")
            
            # Verificar se o chat foi criado com ID normalizado
            from core.models import Chat
            chat = Chat.objects.filter(cliente=cliente).order_by('-data_inicio').first()
            
            if chat and chat.chat_id == "111141053288574":
                print("✅ Chat criado com ID normalizado corretamente!")
                return True
            else:
                print(f"❌ Chat criado com ID incorreto: {chat.chat_id if chat else 'N/A'}")
                return False
        else:
            print("❌ Falha ao salvar mensagem")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao salvar mensagem: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DE WEBHOOK COM CHAT_ID NORMALIZADO...")
    print("=" * 60)
    
    # Testar normalização
    normalizacao_ok = testar_normalizacao_chat_id()
    
    # Simular webhook
    webhook_ok = simular_webhook_mensagem()
    
    # Testar salvamento
    salvamento_ok = testar_salvamento_mensagem()
    
    print("\n🎯 RESULTADO FINAL:")
    print("=" * 60)
    
    if normalizacao_ok and webhook_ok and salvamento_ok:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("🎉 O processamento de webhooks está funcionando corretamente")
        print("📱 Chat IDs serão normalizados automaticamente")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("🔧 Verifique a implementação")
    
    print("\n✅ Testes concluídos!") 