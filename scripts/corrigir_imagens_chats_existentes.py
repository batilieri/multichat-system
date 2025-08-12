#!/usr/bin/env python3
"""
Script para corrigir imagens de perfil dos chats já existentes
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
django.setup()

from webhook.models import WebhookEvent, Chat, Sender
from core.models import CoreChat, Cliente
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)

def extract_profile_picture_robust(webhook_data):
    """Extrai foto de perfil de forma mais robusta do webhook"""
    # Verificar se é uma mensagem enviada pelo usuário (fromMe: true)
    from_me = webhook_data.get('fromMe', False)
    
    # Lista de possíveis locais onde a foto pode estar
    extraction_paths = []
    
    if from_me:
        # Se é mensagem enviada pelo usuário, PRIORIZAR a foto do CHAT (contato/grupo)
        # e evitar usar a foto do SENDER (usuário)
        extraction_paths = [
            # PRIORIDADE 1: Foto do chat (contato/grupo)
            ('chat.profilePicture', lambda data: data.get('chat', {}).get('profilePicture')),
            ('chat.profile_picture', lambda data: data.get('chat', {}).get('profile_picture')),
            
            # PRIORIDADE 2: Nível raiz (pode ser do chat)
            ('root.profilePicture', lambda data: data.get('profilePicture')),
            ('root.profile_picture', lambda data: data.get('profile_picture')),
            
            # PRIORIDADE 3: Dentro de msgContent
            ('msgContent.profilePicture', lambda data: data.get('msgContent', {}).get('profilePicture')),
            
            # PRIORIDADE 4: Dentro de data (estrutura aninhada)
            ('data.chat.profilePicture', lambda data: data.get('data', {}).get('chat', {}).get('profilePicture')),
            
            # ÚLTIMA OPÇÃO: Sender (apenas se não houver outras opções)
            ('sender.profilePicture', lambda data: data.get('sender', {}).get('profilePicture')),
            ('sender.profile_picture', lambda data: data.get('sender', {}).get('profile_picture')),
            ('data.sender.profilePicture', lambda data: data.get('data', {}).get('sender', {}).get('profilePicture')),
        ]
    else:
        # Se é mensagem recebida, usar a lógica normal
        extraction_paths = [
            # Dados do sender
            ('sender.profilePicture', lambda data: data.get('sender', {}).get('profilePicture')),
            ('sender.profile_picture', lambda data: data.get('sender', {}).get('profile_picture')),
            
            # Dados do chat
            ('chat.profilePicture', lambda data: data.get('chat', {}).get('profilePicture')),
            ('chat.profile_picture', lambda data: data.get('chat', {}).get('profile_picture')),
            
            # Nível raiz
            ('root.profilePicture', lambda data: data.get('profilePicture')),
            ('root.profile_picture', lambda data: data.get('profile_picture')),
            
            # Dentro de msgContent (algumas APIs colocam aqui)
            ('msgContent.profilePicture', lambda data: data.get('msgContent', {}).get('profilePicture')),
            
            # Dentro de data (estrutura aninhada)
            ('data.sender.profilePicture', lambda data: data.get('data', {}).get('sender', {}).get('profilePicture')),
            ('data.chat.profilePicture', lambda data: data.get('data', {}).get('chat', {}).get('profilePicture')),
        ]
    
    for path_name, extractor in extraction_paths:
        try:
            result = extractor(webhook_data)
            if result and isinstance(result, str) and result.strip():
                profile_url = result.strip()
                
                # Validar se parece uma URL válida
                if profile_url.startswith(('http://', 'https://', 'data:image/')):
                    return profile_url
        except Exception as e:
            logger.error(f"❌ Erro ao extrair de {path_name}: {e}")
    
    return None

def corrigir_imagens_chats_existentes():
    """Corrige as imagens de perfil dos chats já existentes"""
    print("🔧 CORRIGINDO IMAGENS DE PERFIL DOS CHATS EXISTENTES")
    print("=" * 60)
    
    # Obter todos os clientes
    clientes = Cliente.objects.all()
    
    total_corrigidos = 0
    total_verificados = 0
    
    for cliente in clientes:
        print(f"\n👤 Processando cliente: {cliente.nome}")
        
        # Buscar chats do cliente
        chats = Chat.objects.filter(cliente=cliente)
        core_chats = CoreChat.objects.filter(cliente=cliente)
        
        print(f"📊 Encontrados {chats.count()} chats webhook e {core_chats.count()} chats core")
        
        # Processar chats webhook
        for chat in chats:
            total_verificados += 1
            print(f"\n🔍 Verificando chat: {chat.chat_id} - {chat.chat_name}")
            print(f"🖼️ Foto atual: {chat.foto_perfil}")
            
            # Buscar webhooks relacionados a este chat
            webhook_events = WebhookEvent.objects.filter(
                chat_id=chat.chat_id,
                cliente=cliente
            ).order_by('-received_at')
            
            if webhook_events.exists():
                # Buscar o webhook mais recente com dados válidos
                for event in webhook_events:
                    if event.raw_data:
                        webhook_data = event.raw_data
                        
                        # Verificar se é uma mensagem enviada pelo usuário
                        from_me = webhook_data.get('fromMe', False)
                        
                        if from_me:
                            print(f"🔄 Encontrada mensagem enviada pelo usuário (fromMe: true)")
                            
                            # Extrair foto correta do chat
                            chat_data = webhook_data.get('chat', {})
                            correct_profile_picture = chat_data.get('profilePicture')
                            
                            if correct_profile_picture and correct_profile_picture != chat.foto_perfil:
                                print(f"🖼️ Foto correta encontrada: {correct_profile_picture}")
                                
                                # Atualizar chat
                                chat.foto_perfil = correct_profile_picture
                                chat.save()
                                
                                print(f"✅ Chat atualizado com foto correta!")
                                total_corrigidos += 1
                                break
                            else:
                                print(f"ℹ️ Foto já está correta ou não há foto disponível")
                                break
                        else:
                            print(f"📥 Mensagem recebida (fromMe: false) - mantendo foto atual")
                            break
            else:
                print(f"⚠️ Nenhum webhook encontrado para este chat")
        
        # Processar chats core
        for core_chat in core_chats:
            total_verificados += 1
            print(f"\n🔍 Verificando core chat: {core_chat.chat_id} - {core_chat.chat_name}")
            print(f"🖼️ Foto atual: {core_chat.foto_perfil}")
            
            # Buscar webhooks relacionados a este chat
            webhook_events = WebhookEvent.objects.filter(
                chat_id=core_chat.chat_id,
                cliente=cliente
            ).order_by('-received_at')
            
            if webhook_events.exists():
                # Buscar o webhook mais recente com dados válidos
                for event in webhook_events:
                    if event.raw_data:
                        webhook_data = event.raw_data
                        
                        # Verificar se é uma mensagem enviada pelo usuário
                        from_me = webhook_data.get('fromMe', False)
                        
                        if from_me:
                            print(f"🔄 Encontrada mensagem enviada pelo usuário (fromMe: true)")
                            
                            # Extrair foto correta do chat
                            chat_data = webhook_data.get('chat', {})
                            correct_profile_picture = chat_data.get('profilePicture')
                            
                            if correct_profile_picture and correct_profile_picture != core_chat.foto_perfil:
                                print(f"🖼️ Foto correta encontrada: {correct_profile_picture}")
                                
                                # Atualizar core chat
                                core_chat.foto_perfil = correct_profile_picture
                                core_chat.save()
                                
                                print(f"✅ Core chat atualizado com foto correta!")
                                total_corrigidos += 1
                                break
                            else:
                                print(f"ℹ️ Foto já está correta ou não há foto disponível")
                                break
                        else:
                            print(f"📥 Mensagem recebida (fromMe: false) - mantendo foto atual")
                            break
            else:
                print(f"⚠️ Nenhum webhook encontrado para este core chat")
    
    print(f"\n✅ CORREÇÃO CONCLUÍDA!")
    print(f"📊 Total de chats verificados: {total_verificados}")
    print(f"🔧 Total de chats corrigidos: {total_corrigidos}")

def verificar_correcoes():
    """Verifica se as correções foram aplicadas corretamente"""
    print("\n🔍 VERIFICANDO CORREÇÕES APLICADAS")
    print("=" * 60)
    
    # Buscar chats com fotos de perfil
    chats_com_foto = Chat.objects.exclude(foto_perfil__isnull=True).exclude(foto_perfil='')
    core_chats_com_foto = CoreChat.objects.exclude(foto_perfil__isnull=True).exclude(foto_perfil='')
    
    print(f"📊 Chats webhook com foto: {chats_com_foto.count()}")
    print(f"📊 Core chats com foto: {core_chats_com_foto.count()}")
    
    # Mostrar alguns exemplos
    print("\n📋 Exemplos de chats corrigidos:")
    
    for i, chat in enumerate(chats_com_foto[:5]):
        print(f"  {i+1}. {chat.chat_id} - {chat.chat_name}")
        print(f"     🖼️ Foto: {chat.foto_perfil[:50]}...")
    
    for i, core_chat in enumerate(core_chats_com_foto[:5]):
        print(f"  {i+1}. {core_chat.chat_id} - {core_chat.chat_name}")
        print(f"     🖼️ Foto: {core_chat.foto_perfil[:50]}...")

def main():
    """Função principal"""
    print("🔧 CORREÇÃO DE IMAGENS DE PERFIL DOS CHATS EXISTENTES")
    print("=" * 60)
    
    try:
        # Aplicar correções
        corrigir_imagens_chats_existentes()
        
        # Verificar correções
        verificar_correcoes()
        
        print("\n✅ Processo concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 