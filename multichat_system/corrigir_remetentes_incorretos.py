#!/usr/bin/env python
"""
Script para corrigir mensagens com remetentes incorretos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Cliente
from webhook.models import WebhookEvent

def corrigir_remetentes_incorretos():
    """Corrige mensagens com remetentes incorretos de forma genérica"""
    print("🔧 CORRIGINDO REMETENTES INCORRETOS")
    print("=" * 60)
    
    # 1. Identificar mensagens incorretas (qualquer mensagem recebida que tenha nome de cliente)
    mensagens_incorretas = []
    
    # Buscar todos os clientes para verificar nomes incorretos
    clientes = Cliente.objects.all()
    for cliente in clientes:
        # Buscar mensagens recebidas que tenham qualquer parte do nome do cliente como remetente
        nome_partes = cliente.nome.split()
        for parte in nome_partes:
            if len(parte) > 2:  # Ignorar palavras muito pequenas
                msgs_incorretas = Mensagem.objects.filter(
                    from_me=False, 
                    remetente__icontains=parte
                )
                mensagens_incorretas.extend(msgs_incorretas)
    
    # Remover duplicatas
    mensagens_incorretas = list(set(mensagens_incorretas))
    
    print(f"📊 Mensagens incorretas encontradas: {len(mensagens_incorretas)}")
    
    # 2. Corrigir cada mensagem
    for msg in mensagens_incorretas:
        print(f"🔍 Corrigindo mensagem ID: {msg.id} (Chat: {msg.chat.chat_id})")
        
        # Buscar eventos de webhook relacionados
        eventos = WebhookEvent.objects.filter(
            chat_id=msg.chat.chat_id,
            timestamp__date=msg.data_envio.date()
        ).order_by('timestamp')
        
        # Tentar encontrar o nome correto do remetente
        nome_correto = None
        
        # Método 1: Buscar em eventos de webhook
        for evento in eventos:
            if evento.sender_name and evento.sender_name != msg.remetente:
                # Verificar se o nome do evento não contém partes do nome do cliente
                cliente_nome_partes = msg.chat.cliente.nome.split()
                if not any(parte in evento.sender_name for parte in cliente_nome_partes if len(parte) > 2):
                    nome_correto = evento.sender_name
                    break
        
        # Método 2: Se não encontrar, usar um nome padrão baseado no chat_id
        if not nome_correto:
            chat_id = msg.chat.chat_id
            if chat_id and '@' in chat_id:
                nome_correto = f"Contato {chat_id.split('@')[0]}"
            else:
                nome_correto = "Contato"
        
        # Corrigir a mensagem
        msg.remetente = nome_correto
        msg.save()
        
        print(f"   ✅ Corrigido: {msg.remetente}")
    
    print()
    print("🔍 VERIFICANDO CORREÇÕES")
    print("=" * 60)
    
    # 3. Verificar se as correções foram aplicadas
    mensagens_apos_correcao = []
    for cliente in clientes:
        msgs_incorretas = Mensagem.objects.filter(
            from_me=False, 
            remetente__icontains=cliente.nome
        )
        mensagens_apos_correcao.extend(msgs_incorretas)
    
    print(f"📊 Mensagens ainda incorretas: {len(mensagens_apos_correcao)}")
    
    if len(mensagens_apos_correcao) == 0:
        print("✅ Todas as mensagens foram corrigidas!")
    else:
        print("⚠️ Ainda existem mensagens incorretas:")
        for msg in mensagens_apos_correcao:
            print(f"   ID: {msg.id}, Remetente: {msg.remetente}, FromMe: {msg.from_me}")
    
    # 4. Mostrar estatísticas por chat
    print()
    print("📋 Estatísticas por chat:")
    chats_unicos = set(msg.chat.chat_id for msg in mensagens_incorretas)
    
    for chat_id in chats_unicos:
        mensagens_chat = Mensagem.objects.filter(
            chat__chat_id=chat_id
        ).order_by('-data_envio')[:3]
        
        print(f"   Chat {chat_id}:")
        for msg in mensagens_chat:
            print(f"     ID: {msg.id}, Remetente: {msg.remetente}, FromMe: {msg.from_me}, Conteúdo: {msg.conteudo[:30]}...")

if __name__ == "__main__":
    corrigir_remetentes_incorretos() 