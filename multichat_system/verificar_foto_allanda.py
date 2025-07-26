#!/usr/bin/env python
"""
Script para verificar se a foto da Allanda Martinelli está sendo salva corretamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem, Cliente

def verificar_foto_allanda():
    """Verifica se a foto da Allanda Martinelli está sendo salva corretamente"""
    print("🔍 Verificando foto da Allanda Martinelli...")
    print("=" * 50)
    
    # Buscar chats que podem ter a foto da Allanda
    chats = Chat.objects.all()
    print(f"Total de chats: {chats.count()}")
    
    for chat in chats:
        print(f"\n📄 Chat ID: {chat.id}")
        print(f"   Chat ID: {chat.chat_id}")
        print(f"   Nome: {chat.chat_name}")
        print(f"   Foto Perfil: {chat.foto_perfil}")
        
        # Verificar se tem foto de perfil
        if chat.foto_perfil:
            print(f"   ✅ Tem foto de perfil!")
            
            # Verificar se é a foto da Allanda
            foto_url = chat.foto_perfil
            if 'allanda' in foto_url.lower() or '470279950_563959906555054' in foto_url:
                print(f"   🎯 ENCONTRADA A FOTO DA ALLANDA!")
                print(f"   📷 URL: {foto_url}")
                
                # Atualizar o chat para garantir que a foto está salva
                if not chat.foto_perfil:
                    chat.foto_perfil = foto_url
                    chat.save(update_fields=['foto_perfil'])
                    print(f"   ✅ Foto salva no campo foto_perfil")
        else:
            print(f"   ❌ Sem foto de perfil")
    
    # Buscar especificamente por chats que podem ter a foto da Allanda
    print(f"\n🔍 Buscando especificamente por chats com foto da Allanda...")
    
    # URL da foto da Allanda
    allanda_url = "https://pps.whatsapp.net/v/t61.24694-24/470279950_563959906555054_2694435684509732436_n.jpg?ccb=11-4&oh=01_Q5Aa2AFcXxh5OXVoEpF0k5-WDzvl42r6lfp3OwApWTmpX3mi6w&oe=6888C476&_nc_sid=5e03e0&_nc_cat=102"
    
    chats_com_foto = Chat.objects.filter(
        foto_perfil__icontains='470279950_563959906555054'
    )
    
    print(f"Chats com foto da Allanda encontrados: {chats_com_foto.count()}")
    
    for chat in chats_com_foto:
        print(f"   📸 Chat {chat.id}: {chat.chat_name}")
        print(f"      Foto: {chat.foto_perfil}")

if __name__ == "__main__":
    verificar_foto_allanda() 