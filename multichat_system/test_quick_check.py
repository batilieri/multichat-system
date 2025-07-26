#!/usr/bin/env python3
"""
Script rápido para verificar o status das fotos de perfil
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

def quick_check():
    """Verificação rápida do status das fotos de perfil"""
    print("🔍 Verificação rápida das fotos de perfil...")
    
    # Verificar chats sem foto
    from core.models import Chat
    total_chats = Chat.objects.count()
    chats_with_photo = Chat.objects.exclude(foto_perfil__isnull=True).exclude(foto_perfil='').count()
    print(f"📊 Total de chats: {total_chats}")
    print(f"📊 Chats com foto: {chats_with_photo}")
    print(f"📊 Chats sem foto: {total_chats - chats_with_photo}")
    
    # Verificar último webhook
    from webhook.models import WebhookEvent
    last_event = WebhookEvent.objects.order_by('-timestamp').first()
    if last_event:
        print(f"\n📤 Último webhook: {last_event.timestamp}")
        print(f"📤 Dados do webhook: {list(last_event.raw_data.keys())}")
        if 'sender' in last_event.raw_data:
            print(f"📤 Dados do sender: {list(last_event.raw_data['sender'].keys())}")
            if 'profilePicture' in last_event.raw_data['sender']:
                print(f"🖼️ Foto encontrada no sender: {last_event.raw_data['sender']['profilePicture']}")
    
    # Verificar API response
    from api.serializers import ChatSerializer
    chat = Chat.objects.first()
    if chat:
        print(f"\n🌐 Testando serializer para chat: {chat.chat_id}")
        serializer = ChatSerializer(chat)
        profile_picture = serializer.data.get('profile_picture')
        foto_perfil = serializer.data.get('foto_perfil')
        print(f"🖼️ Profile picture no serializer: {profile_picture}")
        print(f"🖼️ Foto perfil no serializer: {foto_perfil}")
    
    print("\n✅ Verificação concluída!")

if __name__ == "__main__":
    quick_check() 