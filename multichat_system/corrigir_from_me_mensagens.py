#!/usr/bin/env python3
"""
Script para corrigir o campo from_me das mensagens existentes no banco de dados.

Este script analisa as mensagens existentes e corrige o campo from_me baseado em:
1. Nome do remetente (se for "Elizeu Batiliere", marca como from_me=True)
2. Padrões de ID do remetente
3. Relação com a instância do WhatsApp

Uso: python manage.py shell < corrigir_from_me_mensagens.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente, WhatsappInstance
from django.db import transaction
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def corrigir_from_me_mensagens():
    """
    Corrige o campo from_me das mensagens existentes
    """
    try:
        # Buscar todas as mensagens
        mensagens = Mensagem.objects.all()
        total_mensagens = mensagens.count()
        
        logger.info(f"🔍 Analisando {total_mensagens} mensagens...")
        
        # Contadores
        corrigidas = 0
        mantidas = 0
        
        with transaction.atomic():
            for mensagem in mensagens:
                from_me_original = mensagem.from_me
                from_me_corrigido = False
                
                # Método 1: Verificar se o remetente é "Elizeu Batiliere"
                if mensagem.remetente == "Elizeu Batiliere":
                    from_me_corrigido = True
                    logger.info(f"✅ Mensagem {mensagem.id}: Remetente 'Elizeu Batiliere' -> from_me=True")
                
                # Método 2: Verificar padrões de ID do remetente
                elif mensagem.remetente and '@' in mensagem.remetente:
                    # Se o remetente contém '@', pode ser um ID do WhatsApp
                    # Verificar se é o mesmo do chat (para chats individuais)
                    if mensagem.chat.chat_id and mensagem.remetente == mensagem.chat.chat_id:
                        from_me_corrigido = True
                        logger.info(f"✅ Mensagem {mensagem.id}: Remetente igual ao chat_id -> from_me=True")
                
                # Método 3: Verificar se o remetente contém números de telefone conhecidos
                elif mensagem.remetente and any(char.isdigit() for char in mensagem.remetente):
                    # Se contém números, pode ser um telefone
                    # Verificar se é o mesmo do cliente da instância
                    try:
                        cliente = mensagem.chat.cliente
                        if cliente and cliente.telefone:
                            # Se o remetente contém o telefone do cliente, é uma mensagem enviada
                            if cliente.telefone in mensagem.remetente:
                                from_me_corrigido = True
                                logger.info(f"✅ Mensagem {mensagem.id}: Remetente contém telefone do cliente -> from_me=True")
                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao verificar cliente para mensagem {mensagem.id}: {e}")
                
                # Atualizar se necessário
                if from_me_corrigido != from_me_original:
                    mensagem.from_me = from_me_corrigido
                    mensagem.save()
                    corrigidas += 1
                    logger.info(f"🔄 Mensagem {mensagem.id} corrigida: from_me {from_me_original} -> {from_me_corrigido}")
                else:
                    mantidas += 1
        
        logger.info(f"✅ Correção concluída!")
        logger.info(f"📊 Total de mensagens: {total_mensagens}")
        logger.info(f"🔄 Mensagens corrigidas: {corrigidas}")
        logger.info(f"⏸️ Mensagens mantidas: {mantidas}")
        
        # Mostrar estatísticas finais
        mensagens_from_me = Mensagem.objects.filter(from_me=True).count()
        mensagens_not_from_me = Mensagem.objects.filter(from_me=False).count()
        
        logger.info(f"📈 Estatísticas finais:")
        logger.info(f"   - Mensagens from_me=True: {mensagens_from_me}")
        logger.info(f"   - Mensagens from_me=False: {mensagens_not_from_me}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao corrigir mensagens: {e}")
        return False

def analisar_mensagens_por_remetente():
    """
    Analisa as mensagens agrupadas por remetente para entender os padrões
    """
    logger.info("🔍 Analisando mensagens por remetente...")
    
    # Agrupar mensagens por remetente
    from django.db.models import Count
    
    remetentes = Mensagem.objects.values('remetente').annotate(
        total=Count('id'),
        from_me_true=Count('id', filter={'from_me': True}),
        from_me_false=Count('id', filter={'from_me': False})
    ).order_by('-total')
    
    logger.info("📊 Estatísticas por remetente:")
    for remetente in remetentes:
        nome = remetente['remetente'] or 'Sem nome'
        total = remetente['total']
        from_me_true = remetente['from_me_true']
        from_me_false = remetente['from_me_false']
        
        logger.info(f"   {nome}:")
        logger.info(f"     - Total: {total}")
        logger.info(f"     - from_me=True: {from_me_true}")
        logger.info(f"     - from_me=False: {from_me_false}")

if __name__ == "__main__":
    logger.info("🚀 Iniciando correção do campo from_me das mensagens...")
    
    # Primeiro, analisar as mensagens existentes
    analisar_mensagens_por_remetente()
    
    # Perguntar se deve continuar
    print("\n" + "="*50)
    print("ANÁLISE CONCLUÍDA")
    print("="*50)
    print("Deseja corrigir as mensagens baseado na análise acima?")
    print("1 - Sim, corrigir mensagens")
    print("2 - Não, apenas analisar")
    
    try:
        opcao = input("Digite sua opção (1 ou 2): ").strip()
        
        if opcao == "1":
            logger.info("🔄 Iniciando correção...")
            sucesso = corrigir_from_me_mensagens()
            
            if sucesso:
                logger.info("✅ Correção concluída com sucesso!")
            else:
                logger.error("❌ Erro durante a correção!")
        else:
            logger.info("⏸️ Correção cancelada pelo usuário.")
            
    except KeyboardInterrupt:
        logger.info("⏸️ Operação cancelada pelo usuário.")
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}") 