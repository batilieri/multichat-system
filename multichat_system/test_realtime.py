#!/usr/bin/env python
"""
Script para testar o sistema de tempo real completo
"""

import os
import sys
import django
import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem, Cliente
from django.utils import timezone
from django.core.cache import cache

def test_realtime_system():
    """Testa o sistema de tempo real completo"""
    print("🧪 Testando sistema de tempo real completo...")
    
    # Limpar cache
    cache.delete("realtime_updates")
    print("🗑️ Cache limpo")
    
    # Buscar um chat existente
    try:
        chat = Chat.objects.first()
        if not chat:
            print("❌ Nenhum chat encontrado no banco")
            return
        
        print(f"📱 Usando chat: {chat.chat_id}")
        
        # Verificar cache antes
        updates_before = cache.get("realtime_updates", [])
        print(f"📊 Atualizações no cache antes: {len(updates_before)}")
        
        # Criar uma mensagem de teste
        print("📝 Criando mensagem de teste...")
        mensagem = Mensagem.objects.create(
            chat=chat,
            tipo='texto',
            conteudo='Mensagem de teste para verificar tempo real',
            remetente='5511999999999@s.whatsapp.net',
            data_envio=timezone.now(),
            from_me=False,
            lida=False
        )
        
        print(f"✅ Mensagem criada: {mensagem.id}")
        
        # Aguardar um pouco para o signal processar
        time.sleep(1)
        
        # Verificar cache depois
        updates_after = cache.get("realtime_updates", [])
        print(f"📊 Atualizações no cache depois: {len(updates_after)}")
        
        if len(updates_after) > len(updates_before):
            print("🎉 Signal funcionando! Atualizações encontradas no cache:")
            for i, update in enumerate(updates_after):
                print(f"  {i+1}. Tipo: {update.get('type')}")
                print(f"     Chat: {update.get('chat_id')}")
                print(f"     Timestamp: {update.get('timestamp')}")
                if update.get('message'):
                    print(f"     Mensagem ID: {update['message'].get('id')}")
                    print(f"     Conteúdo: {update['message'].get('content')}")
        else:
            print("❌ Signal não funcionou. Nenhuma atualização nova no cache")
            
        # Testar endpoint de polling
        print("\n🌐 Testando endpoint de polling...")
        from django.test import Client
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.first()
        
        if user:
            from rest_framework_simplejwt.tokens import AccessToken
            token = AccessToken.for_user(user)
            
            # Usar timestamp anterior para pegar as atualizações
            last_check = (timezone.now() - timezone.timedelta(minutes=5)).isoformat()
            
            client = Client()
            response = client.get(
                f'/api/chats/check-updates/?last_check={last_check}',
                HTTP_AUTHORIZATION=f'Bearer {token}'
            )
            
            print(f"📡 Status da resposta: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Resposta: {data}")
                if data.get('updates'):
                    print(f"✅ Endpoint retornando {len(data['updates'])} atualizações")
                else:
                    print("⚠️ Endpoint não retornou atualizações")
            else:
                print(f"❌ Erro no endpoint: {response.content}")
        else:
            print("⚠️ Nenhum usuário encontrado para testar endpoint")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Iniciando teste do sistema de tempo real...")
    test_realtime_system()
    print("\n�� Teste concluído!") 