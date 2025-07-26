#!/usr/bin/env python3
"""
Script para adicionar message_ids únicos às mensagens que não possuem

Este script gera message_ids únicos para mensagens que não possuem,
baseado no ID da mensagem, chat_id e timestamp.
"""

import os
import sys
import django
import hashlib
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente
from django.db import transaction

def gerar_message_id(mensagem):
    """Gera um message_id único baseado nos dados da mensagem"""
    # Criar uma string única baseada nos dados da mensagem
    dados = f"{mensagem.id}_{mensagem.chat.chat_id}_{mensagem.data_envio.isoformat()}_{mensagem.remetente}"
    
    # Gerar hash SHA-256
    hash_obj = hashlib.sha256(dados.encode('utf-8'))
    return hash_obj.hexdigest()[:32]  # Usar apenas os primeiros 32 caracteres

def adicionar_message_ids():
    """Adiciona message_ids únicos às mensagens que não possuem"""
    print("🔧 Adicionando message_ids únicos...")
    
    # Mensagens sem message_id
    mensagens_sem_id = Mensagem.objects.filter(message_id__isnull=True)
    
    print(f"📊 Encontradas {mensagens_sem_id.count()} mensagens sem message_id")
    
    if mensagens_sem_id.count() == 0:
        print("✅ Todas as mensagens já possuem message_id")
        return
    
    with transaction.atomic():
        for mensagem in mensagens_sem_id:
            message_id = gerar_message_id(mensagem)
            
            # Verificar se o message_id já existe
            while Mensagem.objects.filter(message_id=message_id).exists():
                # Se existir, adicionar um sufixo
                message_id = f"{message_id}_{mensagem.id}"
            
            mensagem.message_id = message_id
            mensagem.save()
            
            print(f"   - ID: {mensagem.id}, message_id: {message_id}")
    
    print(f"✅ Adicionados {mensagens_sem_id.count()} message_ids únicos")

def verificar_message_ids():
    """Verifica se todas as mensagens possuem message_id único"""
    print("\n🔍 Verificando message_ids...")
    
    total_mensagens = Mensagem.objects.count()
    mensagens_com_id = Mensagem.objects.filter(message_id__isnull=False).count()
    mensagens_sem_id = Mensagem.objects.filter(message_id__isnull=True).count()
    
    print(f"   - Total de mensagens: {total_mensagens}")
    print(f"   - Com message_id: {mensagens_com_id}")
    print(f"   - Sem message_id: {mensagens_sem_id}")
    
    # Verificar duplicatas
    from django.db.models import Count
    duplicatas = Mensagem.objects.values('message_id').annotate(
        count=Count('id')
    ).filter(
        message_id__isnull=False,
        count__gt=1
    )
    
    if duplicatas.count() > 0:
        print(f"   ⚠️ Encontradas {duplicatas.count()} mensagens com message_id duplicado")
        for dup in duplicatas:
            print(f"     - message_id: {dup['message_id']} (aparece {dup['count']} vezes)")
    else:
        print("   ✅ Todos os message_ids são únicos")

def main():
    """Função principal"""
    print("🚀 Iniciando adição de message_ids...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar estado inicial
    verificar_message_ids()
    
    # Adicionar message_ids
    resposta = input("\n❓ Deseja adicionar message_ids às mensagens que não possuem? (s/N): ").strip().lower()
    if resposta in ['s', 'sim', 'y', 'yes']:
        adicionar_message_ids()
    else:
        print("❌ Operação cancelada pelo usuário")
    
    # Verificar estado final
    print("\n" + "="*50)
    verificar_message_ids()
    
    print("\n✅ Processo concluído!")

if __name__ == "__main__":
    main() 