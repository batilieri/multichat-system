#!/usr/bin/env python3
"""
Script para processar mídias existentes no sistema MultiChat

Este script analisa mensagens existentes no banco de dados e processa
as mídias que ainda não foram baixadas ou processadas.
"""

import os
import sys
import django
import json
import logging
from pathlib import Path

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat
from webhook.models import WebhookEvent
from core.media_manager import MultiChatMediaManager
from core.django_media_manager import DjangoMediaManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def processar_midias_existentes():
    """
    Processa mídias existentes no sistema
    """
    logger.info("🎵 Iniciando processamento de mídias existentes...")
    
    # Buscar mensagens com mídia que não foram processadas
    mensagens_com_midia = Mensagem.objects.filter(
        tipo__in=['audio', 'imagem', 'video', 'sticker', 'documento']
    ).exclude(
        conteudo__isnull=True
    ).exclude(
        conteudo=''
    )
    
    logger.info(f"📊 Encontradas {mensagens_com_midia.count()} mensagens com mídia")
    
    # Contadores
    processadas = 0
    erros = 0
    
    for mensagem in mensagens_com_midia:
        try:
            logger.info(f"🔄 Processando mensagem {mensagem.id} (tipo: {mensagem.tipo})")
            
            # Tentar extrair dados da mensagem
            dados_mensagem = extrair_dados_mensagem(mensagem)
            if not dados_mensagem:
                logger.warning(f"⚠️ Não foi possível extrair dados da mensagem {mensagem.id}")
                continue
            
            # Processar mídia
            sucesso = processar_midia_mensagem(mensagem, dados_mensagem)
            
            if sucesso:
                processadas += 1
                logger.info(f"✅ Mídia processada com sucesso: {mensagem.id}")
            else:
                erros += 1
                logger.error(f"❌ Falha ao processar mídia: {mensagem.id}")
                
        except Exception as e:
            erros += 1
            logger.error(f"❌ Erro ao processar mensagem {mensagem.id}: {e}")
    
    logger.info(f"🎯 Processamento concluído: {processadas} processadas, {erros} erros")

def extrair_dados_mensagem(mensagem):
    """
    Extrai dados da mensagem para processamento de mídia
    """
    try:
        # Tentar extrair conteúdo JSON
        if mensagem.conteudo:
            if isinstance(mensagem.conteudo, str):
                try:
                    return json.loads(mensagem.conteudo)
                except json.JSONDecodeError:
                    # Se não for JSON, criar estrutura básica
                    return {
                        'messageId': str(mensagem.id),
                        'msgContent': {
                            f'{mensagem.tipo}Message': {
                                'url': mensagem.media_url or '',
                                'mimetype': mensagem.media_mimetype or '',
                                'fileLength': mensagem.media_size or 0
                            }
                        }
                    }
            else:
                return mensagem.conteudo
        
        # Se não há conteúdo, tentar extrair do webhook
        if mensagem.webhook_event:
            return mensagem.webhook_event.raw_data
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Erro ao extrair dados da mensagem {mensagem.id}: {e}")
        return None

def processar_midia_mensagem(mensagem, dados_mensagem):
    """
    Processa mídia de uma mensagem específica
    """
    try:
        # Determinar cliente e instância
        cliente = mensagem.chat.cliente if mensagem.chat else None
        if not cliente:
            logger.warning(f"⚠️ Mensagem {mensagem.id} sem cliente")
            return False
        
        # Buscar instância ativa
        from core.models import WhatsappInstance
        instancia = WhatsappInstance.objects.filter(
            cliente=cliente,
            ativo=True
        ).first()
        
        if not instancia:
            logger.warning(f"⚠️ Nenhuma instância ativa encontrada para cliente {cliente.id}")
            return False
        
        # Criar gerenciador de mídias
        media_manager = MultiChatMediaManager(
            cliente_id=cliente.id,
            instance_id=instancia.instance_id,
            bearer_token=instancia.token
        )
        
        # Processar mídia
        media_manager.processar_mensagem_whatsapp(dados_mensagem)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar mídia da mensagem {mensagem.id}: {e}")
        return False

def verificar_midias_baixadas():
    """
    Verifica quais mídias já foram baixadas
    """
    logger.info("🔍 Verificando mídias baixadas...")
    
    # Diretórios onde as mídias podem estar
    diretorios_midia = [
        'media/audios',
        'media/images', 
        'media/videos',
        'media/stickers',
        'media/documents',
        'wapi/midias/audios',
        'wapi/midias/images',
        'wapi/midias/videos',
        'wapi/midias/stickers',
        'wapi/midias/documents'
    ]
    
    midias_encontradas = []
    
    for diretorio in diretorios_midia:
        if os.path.exists(diretorio):
            arquivos = os.listdir(diretorio)
            logger.info(f"📁 {diretorio}: {len(arquivos)} arquivos")
            midias_encontradas.extend([f"{diretorio}/{arquivo}" for arquivo in arquivos])
    
    logger.info(f"📊 Total de mídias encontradas: {len(midias_encontradas)}")
    return midias_encontradas

def criar_diretorios_midia():
    """
    Cria diretórios necessários para armazenar mídias
    """
    logger.info("📁 Criando diretórios de mídia...")
    
    diretorios = [
        'media/audios',
        'media/images',
        'media/videos', 
        'media/stickers',
        'media/documents',
        'wapi/midias/audios',
        'wapi/midias/images',
        'wapi/midias/videos',
        'wapi/midias/stickers',
        'wapi/midias/documents'
    ]
    
    for diretorio in diretorios:
        Path(diretorio).mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Diretório criado: {diretorio}")

def main():
    """
    Função principal
    """
    logger.info("🚀 Iniciando processamento de mídias do MultiChat")
    
    # Criar diretórios se não existirem
    criar_diretorios_midia()
    
    # Verificar mídias já baixadas
    midias_baixadas = verificar_midias_baixadas()
    
    # Processar mídias existentes
    processar_midias_existentes()
    
    logger.info("✅ Processamento de mídias concluído!")

if __name__ == '__main__':
    main() 