#!/usr/bin/env python3
"""
Teste final para verificar a detecção melhorada de grupos
"""

import os
import sys
import django
import logging

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from webhook.views import normalize_chat_id, save_message_to_chat_with_from_me
from core.models import Cliente, Chat, Mensagem
from django.utils import timezone
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def testar_grupos_melhorado():
    """
    Testa a detecção melhorada de grupos
    """
    print("🧪 TESTE FINAL - DETECÇÃO MELHORADA DE GRUPOS")
    print("=" * 60)
    
    # Testes de normalização
    test_cases = [
        # Grupos com @g.us (devem retornar None)
        ("556992962029-1415646286@g.us", None, "Grupo @g.us"),
        ("120363373541551792@g.us", None, "Grupo @g.us"),
        ("5511999999999-123456789@g.us", None, "Grupo @g.us"),
        
        # Grupos por padrão 120363 (devem retornar None)
        ("120363023932459345", None, "Grupo padrão 120363"),
        ("120363123456789012", None, "Grupo padrão 120363"),
        ("120363987654321098", None, "Grupo padrão 120363"),
        
        # Chats individuais válidos (devem retornar número normalizado)
        ("111141053288574@lid", "111141053288574", "Chat individual"),
        ("5511999999999@c.us", "5511999999999", "Chat individual"),
        ("5511888888888", "5511888888888", "Chat individual"),
        ("5511999999999", "5511999999999", "Chat individual"),
    ]
    
    print("📱 TESTANDO NORMALIZAÇÃO DE CHAT_ID")
    print("-" * 50)
    
    passed = 0
    total = len(test_cases)
    
    for chat_id, expected, description in test_cases:
        result = normalize_chat_id(chat_id)
        status = "✅ PASSOU" if result == expected else "❌ FALHOU"
        
        print(f"📱 {chat_id}")
        print(f"   Resultado: {result}")
        print(f"   Esperado: {expected}")
        print(f"   Tipo: {description}")
        print(f"   {status}")
        print()
        
        if result == expected:
            passed += 1
    
    print(f"📊 Normalização: {passed}/{total} testes passaram")
    print()
    
    # Teste de salvamento de mensagem de grupo
    print("📨 TESTANDO SALVAMENTO DE MENSAGEM DE GRUPO")
    print("-" * 50)
    
    # Buscar cliente para teste
    try:
        cliente = Cliente.objects.first()
        if not cliente:
            print("❌ Nenhum cliente encontrado no banco")
            return
        
        print(f"👤 Cliente: {cliente.nome}")
        
        # Simular payload de grupo (padrão 120363)
        grupo_payload = {
            "chat": {
                "id": "120363023932459345"
            },
            "key": {
                "id": "teste_grupo_melhorado_123"
            },
            "message": {
                "conversation": "Mensagem de teste do grupo melhorado"
            },
            "messageTimestamp": int(timezone.now().timestamp()),
            "sender": {
                "id": "5511999999999@c.us",
                "pushName": "Participante do Grupo"
            }
        }
        
        print(f"📦 Payload de grupo simulado:")
        print(f"   Chat ID: {grupo_payload['chat']['id']}")
        print(f"   Mensagem: {grupo_payload['message']['conversation']}")
        
        # Tentar salvar mensagem de grupo
        result = save_message_to_chat_with_from_me(grupo_payload, "messages.upsert", False, cliente)
        
        if result == False:
            print("✅ Grupo ignorado corretamente!")
        else:
            print("❌ Grupo não foi ignorado!")
        
        # Verificar se chat foi criado
        chat_criado = Chat.objects.filter(chat_id__contains="120363023932459345").exists()
        if chat_criado:
            print("❌ Chat de grupo foi criado (não deveria)")
        else:
            print("✅ Chat de grupo não foi criado (correto)")
        
        # Verificar se mensagem foi salva
        mensagem_salva = Mensagem.objects.filter(message_id="teste_grupo_melhorado_123").exists()
        if mensagem_salva:
            print("❌ Mensagem de grupo foi salva (não deveria)")
        else:
            print("✅ Mensagem de grupo não foi salva (correto)")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
    
    print()
    print("🎯 RESULTADO FINAL:")
    print("=" * 60)
    
    if passed == total and not chat_criado and not mensagem_salva:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("🎉 Detecção melhorada de grupos está funcionando")
        print("📱 Grupos com @g.us são ignorados")
        print("📱 Grupos com padrão 120363 são ignorados")
        print("📱 Chats individuais funcionam normalmente")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("⚠️ Verificar implementação")
    
    print()
    print("✅ Testes concluídos!")

if __name__ == "__main__":
    testar_grupos_melhorado() 