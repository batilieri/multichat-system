#!/usr/bin/env python
"""
Script para verificar mensagens e identificar por que a opção de edição não está aparecendo.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente
from authentication.models import Usuario

def verificar_mensagens_edicao():
    """Verifica mensagens que podem ser editadas."""
    
    print("🔍 Verificando mensagens para edição...")
    
    # Buscar mensagens de texto enviadas pelo usuário
    mensagens_editaveis = Mensagem.objects.filter(
        tipo__in=['texto', 'text'],
        from_me=True,
        message_id__isnull=False
    ).order_by('-data_envio')[:10]
    
    print(f"📊 Total de mensagens editáveis encontradas: {mensagens_editaveis.count()}")
    
    if mensagens_editaveis.count() == 0:
        print("❌ Nenhuma mensagem editável encontrada!")
        print("\n🔍 Verificando todas as mensagens...")
        
        todas_mensagens = Mensagem.objects.all()[:20]
        print(f"📊 Total de mensagens no banco: {Mensagem.objects.count()}")
        
        for msg in todas_mensagens:
            print(f"\n📝 Mensagem ID: {msg.id}")
            print(f"   - Tipo: {msg.tipo}")
            print(f"   - from_me: {msg.from_me}")
            print(f"   - message_id: {msg.message_id}")
            print(f"   - Conteúdo: {msg.conteudo[:50]}...")
            print(f"   - Chat: {msg.chat.chat_id}")
            print(f"   - Data: {msg.data_envio}")
        
        return
    
    print("\n✅ Mensagens que podem ser editadas:")
    for msg in mensagens_editaveis:
        print(f"\n📝 Mensagem ID: {msg.id}")
        print(f"   - Tipo: {msg.tipo}")
        print(f"   - from_me: {msg.from_me}")
        print(f"   - message_id: {msg.message_id}")
        print(f"   - Conteúdo: {msg.conteudo[:50]}...")
        print(f"   - Chat: {msg.chat.chat_id}")
        print(f"   - Data: {msg.data_envio}")
        
        # Verificar se seria detectada como própria no frontend
        isMe = msg.from_me or False
        isTextMessage = msg.tipo in ['texto', 'text']
        canEdit = isMe and isTextMessage
        
        print(f"   - isMe: {isMe}")
        print(f"   - isTextMessage: {isTextMessage}")
        print(f"   - canEdit: {canEdit}")
        print(f"   - ✅ Opção editar deve aparecer: {'SIM' if canEdit else 'NÃO'}")

def verificar_dados_frontend():
    """Simula como os dados são processados no frontend."""
    
    print("\n🖥️ Simulando processamento no frontend...")
    
    # Buscar algumas mensagens para simular
    mensagens = Mensagem.objects.all()[:5]
    
    for msg in mensagens:
        # Simular transformação do ChatView
        transformed_message = {
            'id': msg.id,
            'type': msg.tipo,
            'content': msg.conteudo,
            'isOwn': msg.from_me,
            'from_me': msg.from_me,
            'fromMe': msg.from_me,
            'timestamp': msg.data_envio,
            'sender': msg.remetente
        }
        
        # Simular lógica do componente Message
        isMe = transformed_message['isOwn'] or transformed_message['from_me'] or transformed_message['fromMe'] or False
        isTextMessage = (transformed_message['type'] == 'text' or 
                        transformed_message['type'] == 'texto')
        canEdit = isMe and isTextMessage
        
        print(f"\n📱 Frontend - Mensagem {msg.id}:")
        print(f"   - Tipo: {transformed_message['type']}")
        print(f"   - isOwn: {transformed_message['isOwn']}")
        print(f"   - from_me: {transformed_message['from_me']}")
        print(f"   - fromMe: {transformed_message['fromMe']}")
        print(f"   - isMe: {isMe}")
        print(f"   - isTextMessage: {isTextMessage}")
        print(f"   - canEdit: {canEdit}")
        print(f"   - ✅ Opção editar deve aparecer: {'SIM' if canEdit else 'NÃO'}")

if __name__ == "__main__":
    verificar_mensagens_edicao()
    verificar_dados_frontend() 