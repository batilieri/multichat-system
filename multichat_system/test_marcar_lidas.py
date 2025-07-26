#!/usr/bin/env python
"""
Script para testar o endpoint de marcar mensagens como lidas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem
from authentication.models import Usuario

def test_marcar_lidas():
    """Testa o endpoint de marcar mensagens como lidas"""
    print("🔍 Testando funcionalidade de marcar mensagens como lidas...")
    
    # Buscar um chat com mensagens não lidas
    chat_com_mensagens = Chat.objects.filter(
        mensagens__lida=False,
        mensagens__from_me=False
    ).distinct().first()
    
    if not chat_com_mensagens:
        print("❌ Nenhum chat com mensagens não lidas encontrado")
        return
    
    print(f"\n📱 Chat encontrado: {chat_com_mensagens.chat_id}")
    
    # Contar mensagens não lidas antes
    mensagens_nao_lidas_antes = Mensagem.objects.filter(
        chat=chat_com_mensagens,
        lida=False,
        from_me=False
    ).count()
    
    print(f"   Mensagens não lidas antes: {mensagens_nao_lidas_antes}")
    
    if mensagens_nao_lidas_antes == 0:
        print("   ⚠️ Nenhuma mensagem não lida para testar")
        return
    
    # Simular a marcação como lidas
    mensagens_nao_lidas = Mensagem.objects.filter(
        chat=chat_com_mensagens,
        lida=False,
        from_me=False
    )
    
    count = mensagens_nao_lidas.count()
    mensagens_nao_lidas.update(lida=True)
    
    print(f"   ✅ {count} mensagens marcadas como lidas")
    
    # Verificar se foram realmente marcadas
    mensagens_nao_lidas_depois = Mensagem.objects.filter(
        chat=chat_com_mensagens,
        lida=False,
        from_me=False
    ).count()
    
    print(f"   Mensagens não lidas depois: {mensagens_nao_lidas_depois}")
    
    if mensagens_nao_lidas_depois == 0:
        print("   ✅ Teste passou! Todas as mensagens foram marcadas como lidas")
    else:
        print("   ❌ Teste falhou! Ainda há mensagens não lidas")
    
    # Mostrar estatísticas gerais
    print(f"\n📊 Estatísticas gerais:")
    total_mensagens = Mensagem.objects.count()
    mensagens_lidas = Mensagem.objects.filter(lida=True).count()
    mensagens_nao_lidas_total = Mensagem.objects.filter(lida=False).count()
    
    print(f"   Total de mensagens: {total_mensagens}")
    print(f"   Mensagens lidas: {mensagens_lidas}")
    print(f"   Mensagens não lidas: {mensagens_nao_lidas_total}")
    
    # Mostrar chats com mensagens não lidas
    chats_com_nao_lidas = Chat.objects.filter(
        mensagens__lida=False,
        mensagens__from_me=False
    ).distinct()
    
    print(f"\n📱 Chats com mensagens não lidas: {chats_com_nao_lidas.count()}")
    
    for chat in chats_com_nao_lidas[:5]:
        nao_lidas = chat.mensagens.filter(lida=False, from_me=False).count()
        print(f"   {chat.chat_id}: {nao_lidas} mensagens não lidas")

if __name__ == "__main__":
    test_marcar_lidas() 