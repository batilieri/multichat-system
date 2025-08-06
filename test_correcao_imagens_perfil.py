#!/usr/bin/env python3
"""
Script para testar a correção das imagens de perfil
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
django.setup()

from webhook.models import WebhookEvent, Chat, Sender
from webhook.views import extract_profile_picture_robust, process_chat_and_sender
from webhook.processors import WhatsAppWebhookProcessor
from core.models import Cliente
import json

def test_extract_profile_picture():
    """Testa a extração de imagens de perfil"""
    print("🧪 TESTANDO EXTRAÇÃO DE IMAGENS DE PERFIL")
    print("=" * 60)
    
    # Dados de teste - mensagem enviada pelo usuário
    webhook_data_from_me = {
        "fromMe": True,
        "chat": {
            "id": "556999267344",
            "profilePicture": "https://pps.whatsapp.net/v/t61.24694-24/462429652_2229319410767469_7773187573644695635_n.jpg?ccb=11-4&oh=01_Q5Aa2AE5OOQugwo4m88csmkTQpNDwDyEXPePZcqA4oELniMqig&oe=689B38AF&_nc_sid=5e03e0&_nc_cat=100"
        },
        "sender": {
            "id": "556993291093",
            "profilePicture": "https://pps.whatsapp.net/v/t61.24694-24/462189315_448942584891093_7781840178101974754_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoXklUo9Xh-ciywvfPd3oicMRVv0tIzOHHtY6V0iG9kw&oe=689B5B12&_nc_sid=5e03e0&_nc_cat=103",
            "pushName": "Elizeu",
            "verifiedBizName": ""
        }
    }
    
    # Dados de teste - mensagem recebida
    webhook_data_received = {
        "fromMe": False,
        "chat": {
            "id": "556999267344",
            "profilePicture": "https://pps.whatsapp.net/v/t61.24694-24/462429652_2229319410767469_7773187573644695635_n.jpg?ccb=11-4&oh=01_Q5Aa2AE5OOQugwo4m88csmkTQpNDwDyEXPePZcqA4oELniMqig&oe=689B38AF&_nc_sid=5e03e0&_nc_cat=100"
        },
        "sender": {
            "id": "556993291093",
            "profilePicture": "https://pps.whatsapp.net/v/t61.24694-24/462189315_448942584891093_7781840178101974754_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoXklUo9Xh-ciywvfPd3oicMRVv0tIzOHHtY6V0iG9kw&oe=689B5B12&_nc_sid=5e03e0&_nc_cat=103",
            "pushName": "João Silva",
            "verifiedBizName": ""
        }
    }
    
    print("📤 Testando mensagem enviada pelo usuário (fromMe: true)...")
    profile_picture_from_me = extract_profile_picture_robust(webhook_data_from_me)
    print(f"✅ Foto extraída: {profile_picture_from_me}")
    
    print("\n📥 Testando mensagem recebida (fromMe: false)...")
    profile_picture_received = extract_profile_picture_robust(webhook_data_received)
    print(f"✅ Foto extraída: {profile_picture_received}")
    
    # Verificar se as fotos são diferentes
    if profile_picture_from_me != profile_picture_received:
        print("✅ CORREÇÃO FUNCIONANDO: Fotos diferentes extraídas corretamente!")
    else:
        print("❌ PROBLEMA: Fotos iguais - correção não funcionou")

def test_processor_logic():
    """Testa a lógica do processador"""
    print("\n🧪 TESTANDO LÓGICA DO PROCESSADOR")
    print("=" * 60)
    
    # Obter cliente de teste
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado")
        return
    
    processor = WhatsAppWebhookProcessor(cliente)
    
    # Dados de teste
    webhook_data = {
        "fromMe": True,
        "chat": {
            "id": "556999267344",
            "profilePicture": "https://pps.whatsapp.net/v/t61.24694-24/462429652_2229319410767469_7773187573644695635_n.jpg?ccb=11-4&oh=01_Q5Aa2AE5OOQugwo4m88csmkTQpNDwDyEXPePZcqA4oELniMqig&oe=689B38AF&_nc_sid=5e03e0&_nc_cat=100"
        },
        "sender": {
            "id": "556993291093",
            "profilePicture": "https://pps.whatsapp.net/v/t61.24694-24/462189315_448942584891093_7781840178101974754_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoXklUo9Xh-ciywvfPd3oicMRVv0tIzOHHtY6V0iG9kw&oe=689B5B12&_nc_sid=5e03e0&_nc_cat=103",
            "pushName": "Elizeu"
        },
        "msgContent": {
            "conversation": "Teste de mensagem"
        },
        "messageTimestamp": "1748872244"
    }
    
    # Criar evento de webhook
    event = WebhookEvent.objects.create(
        cliente=cliente,
        raw_data=webhook_data,
        event_type='message'
    )
    
    print("🔄 Processando webhook...")
    processor.process_whatsapp_data(event, webhook_data)
    
    # Verificar se o chat foi criado com a foto correta
    chat = Chat.objects.filter(chat_id="556999267344", cliente=cliente).first()
    if chat:
        print(f"✅ Chat criado: {chat.chat_id}")
        print(f"🖼️ Foto do chat: {chat.foto_perfil}")
        
        # Verificar se a foto é a do chat (não do sender)
        expected_foto = webhook_data['chat']['profilePicture']
        if chat.foto_perfil == expected_foto:
            print("✅ CORREÇÃO FUNCIONANDO: Chat criado com foto correta!")
        else:
            print(f"❌ PROBLEMA: Foto incorreta. Esperada: {expected_foto}, Obtida: {chat.foto_perfil}")
    else:
        print("❌ Chat não foi criado")

def main():
    """Função principal"""
    print("🔧 TESTE DA CORREÇÃO DE IMAGENS DE PERFIL")
    print("=" * 60)
    
    try:
        # Testar extração de imagens
        test_extract_profile_picture()
        
        # Testar lógica do processador
        test_processor_logic()
        
        print("\n✅ Testes concluídos!")
        
    except Exception as e:
        print(f"❌ Erro nos testes: {e}")

if __name__ == "__main__":
    main() 