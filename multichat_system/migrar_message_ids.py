#!/usr/bin/env python
"""
Script para migrar message_ids do WebhookEvent para o CoreMensagem.
Este script busca mensagens que não têm message_id e tenta encontrá-lo no WebhookEvent.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente
from webhook.models import WebhookEvent
from django.db import transaction

def migrar_message_ids():
    """
    Migra message_ids do WebhookEvent para mensagens que não têm.
    """
    print("🔄 Iniciando migração de message_ids...")
    
    # Buscar mensagens sem message_id
    mensagens_sem_id = Mensagem.objects.filter(message_id__isnull=True)
    print(f"📊 Mensagens sem message_id encontradas: {mensagens_sem_id.count()}")
    
    if mensagens_sem_id.count() == 0:
        print("✅ Todas as mensagens já têm message_id!")
        return
    
    # Buscar eventos de webhook com message_id
    eventos_com_id = WebhookEvent.objects.filter(
        message_id__isnull=False,
        message_id__gt=''  # Não vazio
    ).exclude(message_id='')
    
    print(f"📊 Eventos de webhook com message_id encontrados: {eventos_com_id.count()}")
    
    # Criar mapeamento de chat_id -> message_id
    mapeamento = {}
    for evento in eventos_com_id:
        if evento.chat_id and evento.message_id:
            chave = f"{evento.cliente.id}_{evento.chat_id}"
            if chave not in mapeamento:
                mapeamento[chave] = []
            mapeamento[chave].append({
                'message_id': evento.message_id,
                'timestamp': evento.timestamp,
                'content': evento.message_content
            })
    
    print(f"📊 Mapeamentos criados: {len(mapeamento)}")
    
    # Migrar mensagens
    migradas = 0
    nao_encontradas = 0
    
    for mensagem in mensagens_sem_id:
        try:
            # Buscar o cliente da mensagem
            cliente = mensagem.chat.cliente
            chat_id = mensagem.chat.chat_id
            
            if not chat_id:
                print(f"⚠️ Mensagem {mensagem.id} sem chat_id")
                nao_encontradas += 1
                continue
            
            chave = f"{cliente.id}_{chat_id}"
            
            if chave in mapeamento:
                # Encontrar o message_id mais próximo baseado no timestamp
                candidatos = mapeamento[chave]
                
                # Ordenar por proximidade de timestamp
                candidatos_ordenados = sorted(
                    candidatos,
                    key=lambda x: abs((x['timestamp'] - mensagem.data_envio).total_seconds())
                )
                
                if candidatos_ordenados:
                    message_id = candidatos_ordenados[0]['message_id']
                    
                    # Verificar se não há conflito
                    if not Mensagem.objects.filter(message_id=message_id).exists():
                        with transaction.atomic():
                            mensagem.message_id = message_id
                            mensagem.save()
                        
                        print(f"✅ Mensagem {mensagem.id} migrada com message_id: {message_id}")
                        migradas += 1
                    else:
                        print(f"⚠️ Message_id {message_id} já existe para outra mensagem")
                        nao_encontradas += 1
                else:
                    print(f"⚠️ Nenhum candidato encontrado para mensagem {mensagem.id}")
                    nao_encontradas += 1
            else:
                print(f"⚠️ Nenhum mapeamento encontrado para mensagem {mensagem.id} (cliente: {cliente.id}, chat: {chat_id})")
                nao_encontradas += 1
                
        except Exception as e:
            print(f"❌ Erro ao migrar mensagem {mensagem.id}: {e}")
            nao_encontradas += 1
    
    print(f"\n📊 Resumo da migração:")
    print(f"✅ Mensagens migradas: {migradas}")
    print(f"⚠️ Mensagens não encontradas: {nao_encontradas}")
    print(f"📊 Total processado: {migradas + nao_encontradas}")

def verificar_message_ids():
    """
    Verifica o status dos message_ids.
    """
    print("🔍 Verificando status dos message_ids...")
    
    total_mensagens = Mensagem.objects.count()
    mensagens_com_id = Mensagem.objects.filter(message_id__isnull=False).exclude(message_id='').count()
    mensagens_sem_id = Mensagem.objects.filter(message_id__isnull=True).count()
    mensagens_id_vazio = Mensagem.objects.filter(message_id='').count()
    
    print(f"📊 Total de mensagens: {total_mensagens}")
    print(f"✅ Mensagens com message_id: {mensagens_com_id}")
    print(f"⚠️ Mensagens sem message_id: {mensagens_sem_id}")
    print(f"⚠️ Mensagens com message_id vazio: {mensagens_id_vazio}")
    
    # Mostrar alguns exemplos
    print(f"\n📝 Exemplos de message_ids:")
    exemplos = Mensagem.objects.filter(
        message_id__isnull=False
    ).exclude(
        message_id=''
    ).values_list('id', 'message_id', 'conteudo')[:5]
    
    for msg_id, message_id, conteudo in exemplos:
        print(f"   - ID: {msg_id}, message_id: {message_id}, conteúdo: {conteudo[:50]}...")

if __name__ == "__main__":
    print("🚀 Script de migração de message_ids")
    print("=" * 50)
    
    # Verificar status atual
    verificar_message_ids()
    
    print("\n" + "=" * 50)
    
    # Perguntar se deve migrar
    resposta = input("\nDeseja executar a migração? (s/n): ").lower().strip()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        migrar_message_ids()
        
        print("\n" + "=" * 50)
        print("🔍 Verificação final:")
        verificar_message_ids()
    else:
        print("❌ Migração cancelada.") 