#!/usr/bin/env python
"""
Script para testar se o signal de mensagem está funcionando
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem, Cliente
from django.utils import timezone
from django.core.cache import cache

def test_signal():
    """Testa se o signal está funcionando"""
    print("🧪 Testando signal de mensagem...")
    
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
        
        # Criar uma mensagem de teste
        mensagem = Mensagem.objects.create(
            chat=chat,
            tipo='texto',
            conteudo='Mensagem de teste para verificar signal',
            remetente='5511999999999@s.whatsapp.net',
            data_envio=timezone.now(),
            from_me=False,
            lida=False
        )
        
        print(f"✅ Mensagem criada: {mensagem.id}")
        
        # Verificar se foi salva no cache
        updates = cache.get("realtime_updates", [])
        print(f"📊 Atualizações no cache: {len(updates)}")
        
        if updates:
            print("🎉 Signal funcionando! Atualizações encontradas no cache:")
            for update in updates:
                print(f"  - Tipo: {update.get('type')}")
                print(f"  - Chat: {update.get('chat_id')}")
                print(f"  - Timestamp: {update.get('timestamp')}")
        else:
            print("❌ Signal não funcionou. Nenhuma atualização no cache")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

def test_cache():
    """Testa se o cache está funcionando"""
    print("\n🧪 Testando cache...")
    
    # Testar escrita no cache
    test_data = {'test': 'data'}
    cache.set("test_key", test_data, 60)
    
    # Testar leitura do cache
    cached_data = cache.get("test_key")
    
    if cached_data == test_data:
        print("✅ Cache funcionando corretamente")
    else:
        print("❌ Cache não está funcionando")
        print(f"Esperado: {test_data}")
        print(f"Recebido: {cached_data}")

if __name__ == "__main__":
    print("🚀 Iniciando testes...")
    
    # Testar cache primeiro
    test_cache()
    
    # Testar signal
    test_signal()
    
    print("\n🏁 Testes concluídos!") 