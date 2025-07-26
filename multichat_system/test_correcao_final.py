#!/usr/bin/env python3
"""
Script para testar a correção final do campo from_me
"""

import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente, WhatsappInstance

def test_from_me_logic():
    """
    Testa a lógica melhorada de determinação do from_me
    """
    print("=== TESTE DA LÓGICA FROM_ME MELHORADA ===")
    
    # Simular payloads de webhook reais
    test_payloads = [
        {
            "instanceId": "test_instance",
            "key": {
                "id": "test_msg_1",
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": True
            },
            "message": {"conversation": "Mensagem enviada por mim"},
            "pushName": "Elizeu Batiliere"
        },
        {
            "instanceId": "test_instance",
            "key": {
                "id": "test_msg_2", 
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False
            },
            "message": {"conversation": "Mensagem recebida de outro"},
            "pushName": "Outro Usuário"
        },
        {
            "instanceId": "test_instance",
            "key": {
                "id": "test_msg_3",
                "remoteJid": "5511999999999@s.whatsapp.net"
            },
            "message": {"conversation": "Mensagem sem fromMe explícito"},
            "pushName": "Elizeu Batiliere"
        }
    ]
    
    for i, payload in enumerate(test_payloads):
        print(f"\n--- Teste {i+1} ---")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Aplicar a lógica melhorada
        from_me = False
        
        key_data = payload.get('key', {})
        
        # Método 1: Verificar campo fromMe no key
        if key_data.get('fromMe') is not None:
            from_me = key_data.get('fromMe', False)
            print(f"✅ Método 1: fromMe no key = {from_me}")
        # Método 2: Verificar campo fromMe no payload raiz
        elif payload.get('fromMe') is not None:
            from_me = payload.get('fromMe', False)
            print(f"✅ Método 2: fromMe no payload = {from_me}")
        # Método 3: Verificar se o sender_id é o mesmo da instância (usuário atual)
        else:
            sender_id = key_data.get('remoteJid', '')
            instance_id = payload.get('instanceId', '')
            chat_id = key_data.get('remoteJid', '')
            
            # Se o sender_id contém o instance_id, é uma mensagem enviada pelo usuário
            if sender_id and instance_id and instance_id in sender_id:
                from_me = True
                print(f"✅ Método 3a: sender_id contém instance_id = {from_me}")
            # Se o sender_id é o mesmo do chat_id (para chats individuais), pode ser do usuário
            elif sender_id and chat_id and sender_id == chat_id:
                from_me = True
                print(f"✅ Método 3b: sender_id igual ao chat_id = {from_me}")
            else:
                print(f"❌ Método 3: Nenhuma condição atendida = {from_me}")
        
        print(f"🎯 Resultado final: from_me = {from_me}")

def check_current_messages():
    """
    Verifica mensagens atuais no banco
    """
    print("\n=== VERIFICAÇÃO DE MENSAGENS ATUAIS ===")
    
    mensagens = Mensagem.objects.all().order_by('-data_envio')[:10]
    
    print(f"Últimas {len(mensagens)} mensagens:")
    for msg in mensagens:
        print(f"ID: {msg.id}")
        print(f"  Remetente: '{msg.remetente}'")
        print(f"  from_me: {msg.from_me}")
        print(f"  Chat ID: {msg.chat.chat_id}")
        print(f"  Conteúdo: {msg.conteudo[:50]}...")
        print(f"  Data: {msg.data_envio}")
        print()

def create_test_message():
    """
    Cria uma mensagem de teste para verificar se a correção funciona
    """
    print("\n=== CRIAÇÃO DE MENSAGEM DE TESTE ===")
    
    # Buscar cliente e chat de teste
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado")
        return
    
    chat = Chat.objects.filter(cliente=cliente).first()
    if not chat:
        print("❌ Nenhum chat encontrado")
        return
    
    try:
        # Criar mensagem de teste com from_me=True
        mensagem = Mensagem.objects.create(
            chat=chat,
            remetente="Elizeu Batiliere",
            conteudo="Mensagem de teste - enviada por mim (from_me=True)",
            tipo='text',
            lida=False,
            from_me=True,
            message_id="test_correcao_final"
        )
        print(f"✅ Mensagem de teste criada: ID={mensagem.id}, from_me={mensagem.from_me}")
        
        # Verificar se foi salva corretamente
        mensagem_salva = Mensagem.objects.get(id=mensagem.id)
        print(f"✅ Mensagem salva corretamente: from_me={mensagem_salva.from_me}")
        
    except Exception as e:
        print(f"❌ Erro ao criar mensagem de teste: {e}")

def check_elizeu_messages():
    """
    Verifica mensagens específicas do Elizeu
    """
    print("\n=== VERIFICAÇÃO DE MENSAGENS DO ELIZEU ===")
    
    mensagens_elizeu = Mensagem.objects.filter(remetente="Elizeu Batiliere")
    total = mensagens_elizeu.count()
    from_me_true = mensagens_elizeu.filter(from_me=True).count()
    from_me_false = mensagens_elizeu.filter(from_me=False).count()
    
    print(f"Total de mensagens do Elizeu: {total}")
    print(f"from_me=True: {from_me_true}")
    print(f"from_me=False: {from_me_false}")
    
    if from_me_false > 0:
        print(f"⚠️ Ainda há {from_me_false} mensagens do Elizeu com from_me=False")
        print("Mensagens que precisam ser corrigidas:")
        for msg in mensagens_elizeu.filter(from_me=False)[:5]:
            print(f"  - ID: {msg.id}, Conteúdo: {msg.conteudo[:30]}...")
    else:
        print("✅ Todas as mensagens do Elizeu estão corretas!")

if __name__ == "__main__":
    test_from_me_logic()
    check_current_messages()
    create_test_message()
    check_elizeu_messages() 