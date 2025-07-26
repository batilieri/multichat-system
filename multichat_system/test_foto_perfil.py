#!/usr/bin/env python
"""
Script para testar se as fotos de perfil estão sendo enviadas corretamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat
from api.serializers import ChatSerializer

def test_foto_perfil():
    """Testa se as fotos de perfil estão sendo enviadas corretamente"""
    print("🔍 Testando fotos de perfil...")
    
    # Buscar chats com fotos de perfil
    chats_com_foto = Chat.objects.exclude(foto_perfil__isnull=True).exclude(foto_perfil='')
    print(f"\n📱 Chats com foto de perfil: {chats_com_foto.count()}")
    
    if chats_com_foto.exists():
        print("\n📋 Exemplos de chats com foto:")
        for chat in chats_com_foto[:3]:
            print(f"   Chat ID: {chat.chat_id}")
            print(f"   Nome: {chat.chat_name}")
            print(f"   Foto: {chat.foto_perfil}")
            print("   ---")
    
    # Testar serializer
    print("\n🔄 Testando serializer...")
    chats = Chat.objects.all()[:5]
    
    for chat in chats:
        serializer = ChatSerializer(chat)
        data = serializer.data
        
        print(f"\n   Chat: {chat.chat_id}")
        print(f"   Foto no modelo: {chat.foto_perfil}")
        print(f"   Foto no serializer: {data.get('foto_perfil')}")
        print(f"   Contact name: {data.get('contact_name')}")
        print(f"   Sender name: {data.get('sender_name')}")
        print("   ---")
    
    # Verificar se há fotos sendo baixadas
    print("\n📥 Verificando se fotos estão sendo baixadas...")
    from webhook.processors import WebhookProcessor
    
    # Simular busca de foto para um chat
    if chats.exists():
        chat = chats.first()
        print(f"   Testando chat: {chat.chat_id}")
        
        try:
            # Tentar buscar foto via W-API
            from wapi.__whatsAppApi import WhatsAppApi
            from core.models import WhatsappInstance
            
            instance = WhatsappInstance.objects.filter(cliente=chat.cliente).first()
            if instance:
                print(f"   Instância encontrada: {instance.instance_id}")
                
                # Aqui você pode adicionar lógica para buscar a foto
                # Por enquanto, vamos apenas verificar se o campo existe
                print(f"   Campo foto_perfil existe: {hasattr(chat, 'foto_perfil')}")
                print(f"   Valor atual: {chat.foto_perfil}")
            else:
                print("   ❌ Nenhuma instância WhatsApp encontrada")
        except Exception as e:
            print(f"   ❌ Erro ao testar: {e}")

if __name__ == "__main__":
    test_foto_perfil() 