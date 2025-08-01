#!/usr/bin/env python3
"""
Script para corrigir IDs de chats incorretos
Converte IDs como '111141053288574@lid' para números de telefone válidos
"""

import os
import sys
import django
import re

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem
from django.db import transaction

def normalize_chat_id(chat_id):
    """
    Normaliza o chat_id para garantir que seja um número de telefone válido
    Remove sufixos como @lid, @c.us, etc e extrai apenas o número
    """
    if not chat_id:
        return None
    
    # Remover sufixos comuns do WhatsApp
    chat_id = re.sub(r'@[^.]+\.us$', '', chat_id)  # Remove @c.us, @lid, etc
    chat_id = re.sub(r'@[^.]+$', '', chat_id)      # Remove outros sufixos
    
    # Extrair apenas números
    numbers_only = re.sub(r'[^\d]', '', chat_id)
    
    # Validar se é um número de telefone válido (mínimo 10 dígitos)
    if len(numbers_only) >= 10:
        return numbers_only
    
    print(f"⚠️ Chat ID inválido após normalização: {chat_id} -> {numbers_only}")
    return chat_id  # Retornar original se não conseguir normalizar

def corrigir_chat_ids():
    """
    Corrige os IDs dos chats que estão incorretos
    """
    print("🔧 CORRIGINDO IDs DOS CHATS...")
    print("=" * 50)
    
    # Buscar chats com IDs incorretos (que contêm @)
    chats_incorretos = Chat.objects.filter(chat_id__contains='@')
    
    print(f"📋 Encontrados {chats_incorretos.count()} chats com IDs incorretos:")
    
    for chat in chats_incorretos:
        print(f"  - ID atual: {chat.chat_id}")
    
    if not chats_incorretos.exists():
        print("✅ Nenhum chat com ID incorreto encontrado!")
        return
    
    # Processar cada chat
    corrigidos = 0
    erros = 0
    
    for chat in chats_incorretos:
        try:
            with transaction.atomic():
                # Normalizar o ID
                novo_id = normalize_chat_id(chat.chat_id)
                
                if novo_id and novo_id != chat.chat_id:
                    # Verificar se já existe um chat com o novo ID
                    chat_existente = Chat.objects.filter(chat_id=novo_id).first()
                    
                    if chat_existente:
                        print(f"⚠️ Chat com ID {novo_id} já existe. Migrando mensagens...")
                        
                        # Migrar mensagens para o chat correto
                        mensagens = Mensagem.objects.filter(chat=chat)
                        for mensagem in mensagens:
                            mensagem.chat = chat_existente
                            mensagem.save()
                        
                        # Deletar chat incorreto
                        chat.delete()
                        print(f"✅ Mensagens migradas e chat incorreto removido")
                        
                    else:
                        # Atualizar o ID do chat
                        chat.chat_id = novo_id
                        chat.save()
                        print(f"✅ Chat ID corrigido: {chat.chat_id} -> {novo_id}")
                    
                    corrigidos += 1
                else:
                    print(f"⚠️ Chat ID não pôde ser normalizado: {chat.chat_id}")
                    erros += 1
                    
        except Exception as e:
            print(f"❌ Erro ao corrigir chat {chat.chat_id}: {e}")
            erros += 1
    
    print("\n📊 RESUMO DA CORREÇÃO:")
    print("=" * 50)
    print(f"✅ Chats corrigidos: {corrigidos}")
    print(f"❌ Erros: {erros}")
    
    if corrigidos > 0:
        print("\n🎉 Correção concluída com sucesso!")
        print("💡 Agora os chats devem funcionar corretamente para envio de mensagens")
    else:
        print("\n⚠️ Nenhum chat foi corrigido")

def verificar_chats_corrigidos():
    """
    Verifica se os chats foram corrigidos corretamente
    """
    print("\n🔍 VERIFICANDO CHATS CORRIGIDOS...")
    print("=" * 50)
    
    # Buscar chats com IDs válidos (apenas números)
    chats_validos = Chat.objects.filter(chat_id__regex=r'^\d+$')
    chats_invalidos = Chat.objects.filter(chat_id__regex=r'[^\d]')
    
    print(f"✅ Chats com IDs válidos: {chats_validos.count()}")
    print(f"❌ Chats com IDs inválidos: {chats_invalidos.count()}")
    
    if chats_validos.exists():
        print("\n📋 Exemplos de chats válidos:")
        for chat in chats_validos[:5]:
            print(f"  - {chat.chat_id} (Cliente: {chat.cliente.nome})")
    
    if chats_invalidos.exists():
        print("\n⚠️ Chats com IDs inválidos:")
        for chat in chats_invalidos[:5]:
            print(f"  - {chat.chat_id} (Cliente: {chat.cliente.nome})")

if __name__ == "__main__":
    print("🚀 INICIANDO CORREÇÃO DE IDs DOS CHATS...")
    print("=" * 60)
    
    # Corrigir chats
    corrigir_chat_ids()
    
    # Verificar resultado
    verificar_chats_corrigidos()
    
    print("\n✅ Processo concluído!") 