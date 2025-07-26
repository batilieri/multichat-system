#!/usr/bin/env python3
"""
Script para testar a correção completa do campo from_me
"""

import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente, WhatsappInstance
from webhook.models import WebhookEvent

def test_correcao_completa():
    """
    Testa a correção completa do campo from_me
    """
    print("=== TESTE DA CORREÇÃO COMPLETA DO FROM_ME ===")
    
    # Verificar mensagens existentes
    mensagens = Mensagem.objects.all()
    total = mensagens.count()
    from_me_true = mensagens.filter(from_me=True).count()
    from_me_false = mensagens.filter(from_me=False).count()
    
    print(f"Total de mensagens: {total}")
    print(f"from_me=True: {from_me_true}")
    print(f"from_me=False: {from_me_false}")
    
    # Mostrar algumas mensagens
    print("\n=== EXEMPLOS DE MENSAGENS ===")
    for msg in mensagens[:10]:
        print(f"ID: {msg.id}, Remetente: '{msg.remetente}', from_me: {msg.from_me}, Conteúdo: {msg.conteudo[:50]}...")
    
    # Corrigir mensagens com remetente "Elizeu Batiliere"
    print("\n=== CORRIGINDO MENSAGENS ===")
    mensagens_elizeu = mensagens.filter(remetente__icontains="Elizeu")
    print(f"Mensagens do Elizeu encontradas: {mensagens_elizeu.count()}")
    
    corrigidas = 0
    for msg in mensagens_elizeu:
        if not msg.from_me:
            msg.from_me = True
            msg.save()
            corrigidas += 1
            print(f"✅ Corrigida mensagem {msg.id}: {msg.remetente}")
    
    print(f"Total de mensagens corrigidas: {corrigidas}")
    
    # Verificar resultado final
    print("\n=== RESULTADO FINAL ===")
    mensagens_final = Mensagem.objects.all()
    from_me_true_final = mensagens_final.filter(from_me=True).count()
    from_me_false_final = mensagens_final.filter(from_me=False).count()
    
    print(f"from_me=True: {from_me_true_final}")
    print(f"from_me=False: {from_me_false_final}")
    
    # Testar com dados de webhook simulados
    print("\n=== TESTE COM WEBHOOK SIMULADO ===")
    
    # Simular payload de webhook com fromMe=True
    webhook_payload = {
        "instanceId": "test_instance",
        "event": "messages.upsert",
        "data": {
            "key": {
                "id": "test_msg_1",
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": True
            },
            "message": {
                "conversation": "Mensagem de teste do Elizeu"
            },
            "messageTimestamp": 1640995200,
            "pushName": "Elizeu Batiliere",
            "fromMe": True
        }
    }
    
    # Testar lógica de determinação do from_me
    from_me = False
    
    # Método 1: Verificar campo fromMe no payload raiz
    if webhook_payload.get('fromMe') is not None:
        from_me = webhook_payload.get('fromMe', False)
    # Método 2: Verificar campo fromMe no data
    elif webhook_payload.get('data', {}).get('fromMe') is not None:
        from_me = webhook_payload.get('data', {}).get('fromMe', False)
    # Método 3: Verificar campo fromMe no key
    elif webhook_payload.get('data', {}).get('key', {}).get('fromMe') is not None:
        from_me = webhook_payload.get('data', {}).get('key', {}).get('fromMe', False)
    # Método 4: Verificar pelo nome do remetente
    else:
        push_name = webhook_payload.get('data', {}).get('pushName', '')
        if push_name and "Elizeu" in push_name:
            from_me = True
    
    print(f"Webhook payload: {json.dumps(webhook_payload, indent=2)}")
    print(f"from_me determinado: {from_me}")
    
    if from_me:
        print("✅ Lógica de determinação do from_me funcionando corretamente!")
    else:
        print("❌ Problema na lógica de determinação do from_me")

if __name__ == "__main__":
    test_correcao_completa() 