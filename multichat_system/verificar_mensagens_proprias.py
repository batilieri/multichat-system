#!/usr/bin/env python
"""
Script para verificar se as mensagens estão sendo marcadas corretamente como próprias.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente, WhatsappInstance

def verificar_mensagens_proprias():
    """Verifica se as mensagens estão sendo marcadas corretamente como próprias"""
    
    print("🔍 Verificando mensagens próprias...")
    print("=" * 50)
    
    # 1. Verificar todas as mensagens
    todas_mensagens = Mensagem.objects.all().order_by('-data_envio')[:10]
    
    print(f"📊 Últimas {len(todas_mensagens)} mensagens:")
    for i, msg in enumerate(todas_mensagens):
        print(f"   {i+1}. ID: {msg.id}")
        print(f"      Conteúdo: {msg.conteudo[:50]}...")
        print(f"      from_me: {msg.from_me}")
        print(f"      tipo: {msg.tipo}")
        print(f"      message_id: {msg.message_id}")
        print(f"      chat_id: {msg.chat.chat_id if msg.chat else 'N/A'}")
        print()
    
    # 2. Verificar mensagens próprias
    mensagens_proprias = Mensagem.objects.filter(from_me=True).order_by('-data_envio')[:5]
    
    print(f"✅ Mensagens próprias (from_me=True): {len(mensagens_proprias)}")
    for i, msg in enumerate(mensagens_proprias):
        print(f"   {i+1}. ID: {msg.id}")
        print(f"      Conteúdo: {msg.conteudo[:50]}...")
        print(f"      tipo: {msg.tipo}")
        print(f"      message_id: {msg.message_id}")
        print()
    
    # 3. Verificar mensagens de texto próprias
    mensagens_texto_proprias = Mensagem.objects.filter(
        from_me=True,
        tipo__in=['texto', 'text']
    ).order_by('-data_envio')[:5]
    
    print(f"📝 Mensagens de texto próprias: {len(mensagens_texto_proprias)}")
    for i, msg in enumerate(mensagens_texto_proprias):
        print(f"   {i+1}. ID: {msg.id}")
        print(f"      Conteúdo: {msg.conteudo[:50]}...")
        print(f"      message_id: {msg.message_id}")
        print()
    
    # 4. Verificar mensagens que podem ser editadas
    mensagens_editaveis = Mensagem.objects.filter(
        from_me=True,
        tipo__in=['texto', 'text'],
        message_id__isnull=False
    ).exclude(message_id='').order_by('-data_envio')[:5]
    
    print(f"✏️ Mensagens editáveis: {len(mensagens_editaveis)}")
    for i, msg in enumerate(mensagens_editaveis):
        print(f"   {i+1}. ID: {msg.id}")
        print(f"      Conteúdo: {msg.conteudo[:50]}...")
        print(f"      message_id: {msg.message_id}")
        print()
    
    # 5. Estatísticas gerais
    total_mensagens = Mensagem.objects.count()
    total_proprias = Mensagem.objects.filter(from_me=True).count()
    total_texto_proprias = Mensagem.objects.filter(
        from_me=True,
        tipo__in=['texto', 'text']
    ).count()
    total_editaveis = Mensagem.objects.filter(
        from_me=True,
        tipo__in=['texto', 'text'],
        message_id__isnull=False
    ).exclude(message_id='').count()
    
    print(f"📈 Estatísticas:")
    print(f"   - Total de mensagens: {total_mensagens}")
    print(f"   - Mensagens próprias: {total_proprias} ({total_proprias/total_mensagens*100:.1f}%)")
    print(f"   - Mensagens de texto próprias: {total_texto_proprias}")
    print(f"   - Mensagens editáveis: {total_editaveis}")
    
    if total_editaveis == 0:
        print("\n⚠️ Nenhuma mensagem editável encontrada!")
        print("   Possíveis causas:")
        print("   - Não há mensagens enviadas por você")
        print("   - As mensagens não têm message_id")
        print("   - As mensagens não são do tipo texto")
        print("   - O campo from_me não está sendo definido corretamente")
    else:
        print(f"\n✅ Encontradas {total_editaveis} mensagens editáveis!")
        print("   A opção 'Editar' deve aparecer no menu dessas mensagens.")

if __name__ == "__main__":
    verificar_mensagens_proprias() 