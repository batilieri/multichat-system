#!/usr/bin/env python3
"""
Processador de Mídias para Webhook do MultiChat
Integra o sistema de mídias com os webhooks recebidos
"""

import os
import sys
import django
from pathlib import Path
import logging
from typing import Dict, Optional
from datetime import datetime

# Configurar Django
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Cliente, WhatsappInstance
from core.media_manager import MultiChatMediaManager
from webhook.models import WebhookEvent, Message, MessageMedia

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebhookMediaProcessor:
    """
    Processa mídias de webhooks recebidos e integra com o sistema MultiChat
    """
    
    def __init__(self):
        self.media_managers = {}  # Cache de gerenciadores por cliente/instância
        
    def get_media_manager(self, cliente_id: int, instance_id: str, bearer_token: str) -> MultiChatMediaManager:
        """
        Obtém ou cria um gerenciador de mídias para um cliente/instância específica
        
        Args:
            cliente_id: ID do cliente
            instance_id: ID da instância WhatsApp
            bearer_token: Token de autenticação
            
        Returns:
            MultiChatMediaManager: Gerenciador de mídias
        """
        cache_key = f"{cliente_id}_{instance_id}"
        
        if cache_key not in self.media_managers:
            logger.info(f"🆕 Criando MediaManager para Cliente {cliente_id}, Instância {instance_id}")
            self.media_managers[cache_key] = MultiChatMediaManager(
                cliente_id=cliente_id,
                instance_id=instance_id,
                bearer_token=bearer_token
            )
        
        return self.media_managers[cache_key]
    
    def process_webhook_event(self, event: WebhookEvent) -> bool:
        """
        Processa um evento de webhook e extrai mídias se necessário
        
        Args:
            event: Evento de webhook do Django
            
        Returns:
            bool: True se processado com sucesso
        """
        try:
            # Verificar se já foi processado
            if event.processed:
                logger.debug(f"ℹ️ Evento {event.event_id} já processado")
                return True
            
            # Extrair dados do evento
            raw_data = event.raw_data
            
            # Verificar se é uma mensagem com mídia
            if not self._is_media_message(raw_data):
                logger.debug(f"ℹ️ Evento {event.event_id} não contém mídia")
                event.processed = True
                event.save()
                return True
            
            # Buscar cliente e instância
            cliente = event.cliente
            instance = WhatsappInstance.objects.filter(
                cliente=cliente,
                instance_id=event.instance_id
            ).first()
            
            if not instance:
                logger.error(f"❌ Instância {event.instance_id} não encontrada para cliente {cliente.id}")
                event.error_message = f"Instância {event.instance_id} não encontrada"
                event.save()
                return False
            
            # Obter gerenciador de mídias
            media_manager = self.get_media_manager(
                cliente_id=cliente.id,
                instance_id=instance.instance_id,
                bearer_token=instance.token
            )
            
            # Processar mídia
            success = self._process_media_from_event(event, media_manager)
            
            # Marcar como processado
            event.processed = True
            if not success:
                event.error_message = "Erro ao processar mídia"
            event.save()
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar evento {event.event_id}: {e}")
            event.error_message = str(e)
            event.save()
            return False
    
    def _is_media_message(self, raw_data: Dict) -> bool:
        """
        Verifica se a mensagem contém mídia
        
        Args:
            raw_data: Dados brutos do webhook
            
        Returns:
            bool: True se contém mídia
        """
        try:
            # Verificar diferentes estruturas de webhook
            msg_content = None
            
            if 'msgContent' in raw_data:
                msg_content = raw_data['msgContent']
            elif 'payload' in raw_data and 'msgContent' in raw_data['payload']:
                msg_content = raw_data['payload']['msgContent']
            
            if not msg_content:
                return False
            
            # Verificar tipos de mídia
            media_types = [
                'imageMessage', 'videoMessage', 'audioMessage',
                'documentMessage', 'stickerMessage'
            ]
            
            return any(media_type in msg_content for media_type in media_types)
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar mídia: {e}")
            return False
    
    def _process_media_from_event(self, event: WebhookEvent, media_manager: MultiChatMediaManager) -> bool:
        """
        Processa mídia de um evento específico
        
        Args:
            event: Evento de webhook
            media_manager: Gerenciador de mídias
            
        Returns:
            bool: True se processado com sucesso
        """
        try:
            raw_data = event.raw_data
            
            # Extrair dados da mensagem
            message_data = self._extract_message_data(raw_data)
            if not message_data:
                logger.warning(f"⚠️ Não foi possível extrair dados da mensagem do evento {event.event_id}")
                return False
            
            # Processar com o gerenciador de mídias
            media_manager.processar_mensagem_whatsapp(raw_data)
            
            # Buscar mídias processadas no banco local
            message_id = message_data.get('messageId')
            if message_id:
                self._link_media_to_message(event, message_id, media_manager)
            
            logger.info(f"✅ Mídia processada com sucesso para evento {event.event_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar mídia do evento {event.event_id}: {e}")
            return False
    
    def _extract_message_data(self, raw_data: Dict) -> Optional[Dict]:
        """
        Extrai dados da mensagem do webhook
        
        Args:
            raw_data: Dados brutos do webhook
            
        Returns:
            Dict: Dados da mensagem ou None
        """
        try:
            # Diferentes formatos de webhook
            if 'msgContent' in raw_data:
                return {
                    'messageId': raw_data.get('messageId'),
                    'sender': raw_data.get('sender', {}),
                    'chat': raw_data.get('chat', {}),
                    'msgContent': raw_data.get('msgContent', {}),
                    'isGroup': raw_data.get('isGroup', False),
                    'fromMe': raw_data.get('fromMe', False),
                    'moment': raw_data.get('moment')
                }
            elif 'payload' in raw_data:
                payload = raw_data.get('payload', {})
                return {
                    'messageId': payload.get('messageId'),
                    'sender': payload.get('sender', {}),
                    'chat': payload.get('chat', {}),
                    'msgContent': payload.get('msgContent', {}),
                    'isGroup': payload.get('isGroup', False),
                    'fromMe': payload.get('fromMe', False),
                    'moment': payload.get('moment')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados da mensagem: {e}")
            return None
    
    def _link_media_to_message(self, event: WebhookEvent, message_id: str, media_manager: MultiChatMediaManager):
        """
        Vincula mídias baixadas à mensagem no sistema MultiChat
        
        Args:
            event: Evento de webhook
            message_id: ID da mensagem
            media_manager: Gerenciador de mídias
        """
        try:
            # Buscar mídias no banco local do gerenciador
            import sqlite3
            with sqlite3.connect(media_manager.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT media_type, file_path, mimetype, file_size, download_status
                    FROM midias 
                    WHERE message_id = ? AND download_status = 'success'
                ''', (message_id,))
                
                midias = cursor.fetchall()
            
            # Criar registros MessageMedia no Django
            for media_type, file_path, mimetype, file_size, status in midias:
                if file_path and status == 'success':
                    # Verificar se já existe
                    existing = MessageMedia.objects.filter(
                        event=event,
                        media_type=media_type
                    ).first()
                    
                    if existing:
                        # Atualizar caminho se necessário
                        if existing.media_path != file_path:
                            existing.media_path = file_path
                            existing.download_status = 'success'
                            existing.save()
                    else:
                        # Criar novo registro
                        MessageMedia.objects.create(
                            event=event,
                            media_path=file_path,
                            media_type=media_type,
                            mimetype=mimetype,
                            file_size=file_size,
                            download_status='success'
                        )
            
            logger.info(f"✅ Mídias vinculadas à mensagem {message_id}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao vincular mídias à mensagem {message_id}: {e}")
    
    def process_pending_events(self, limit: int = 100) -> int:
        """
        Processa eventos pendentes em lote
        
        Args:
            limit: Limite de eventos a processar
            
        Returns:
            int: Número de eventos processados
        """
        try:
            # Buscar eventos pendentes
            pending_events = WebhookEvent.objects.filter(
                processed=False
            ).order_by('timestamp')[:limit]
            
            processed_count = 0
            
            for event in pending_events:
                try:
                    if self.process_webhook_event(event):
                        processed_count += 1
                except Exception as e:
                    logger.error(f"❌ Erro ao processar evento {event.event_id}: {e}")
                    event.error_message = str(e)
                    event.save()
            
            logger.info(f"✅ Processados {processed_count} eventos pendentes")
            return processed_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar eventos pendentes: {e}")
            return 0
    
    def reprocess_failed_events(self, limit: int = 50) -> int:
        """
        Reprocessa eventos que falharam
        
        Args:
            limit: Limite de eventos a reprocessar
            
        Returns:
            int: Número de eventos reprocessados
        """
        try:
            # Buscar eventos com erro
            failed_events = WebhookEvent.objects.filter(
                processed=False,
                error_message__isnull=False
            ).order_by('timestamp')[:limit]
            
            reprocessed_count = 0
            
            for event in failed_events:
                try:
                    # Limpar erro anterior
                    event.error_message = None
                    event.save()
                    
                    if self.process_webhook_event(event):
                        reprocessed_count += 1
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao reprocessar evento {event.event_id}: {e}")
                    event.error_message = str(e)
                    event.save()
            
            logger.info(f"✅ Reprocessados {reprocessed_count} eventos com falha")
            return reprocessed_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao reprocessar eventos: {e}")
            return 0
    
    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas do processador
        
        Returns:
            Dict: Estatísticas
        """
        try:
            stats = {
                'total_events': WebhookEvent.objects.count(),
                'processed_events': WebhookEvent.objects.filter(processed=True).count(),
                'pending_events': WebhookEvent.objects.filter(processed=False).count(),
                'failed_events': WebhookEvent.objects.filter(
                    processed=False,
                    error_message__isnull=False
                ).count(),
                'media_managers': len(self.media_managers),
                'media_managers_stats': {}
            }
            
            # Estatísticas por gerenciador de mídias
            for cache_key, manager in self.media_managers.items():
                manager_stats = manager.obter_estatisticas()
                stats['media_managers_stats'][cache_key] = manager_stats
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}


# Instância global do processador
media_processor = WebhookMediaProcessor()


def process_webhook_media(event_data: Dict, cliente_id: int, instance_id: str) -> bool:
    """
    Função de conveniência para processar mídia de webhook
    
    Args:
        event_data: Dados do webhook
        cliente_id: ID do cliente
        instance_id: ID da instância
        
    Returns:
        bool: True se processado com sucesso
    """
    try:
        # Buscar instância para obter token
        instance = WhatsappInstance.objects.filter(
            cliente_id=cliente_id,
            instance_id=instance_id
        ).first()
        
        if not instance:
            logger.error(f"❌ Instância {instance_id} não encontrada para cliente {cliente_id}")
            return False
        
        # Obter gerenciador de mídias
        media_manager = media_processor.get_media_manager(
            cliente_id=cliente_id,
            instance_id=instance_id,
            bearer_token=instance.token
        )
        
        # Processar mídia
        media_manager.processar_mensagem_whatsapp(event_data)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar mídia de webhook: {e}")
        return False


def run_media_processor():
    """
    Executa o processador de mídias em modo contínuo
    """
    import time
    
    logger.info("🚀 Iniciando processador de mídias em modo contínuo...")
    
    try:
        while True:
            # Processar eventos pendentes
            processed = media_processor.process_pending_events(limit=50)
            
            # Reprocessar eventos com falha
            reprocessed = media_processor.reprocess_failed_events(limit=25)
            
            # Mostrar estatísticas a cada 5 minutos
            if processed > 0 or reprocessed > 0:
                stats = media_processor.get_statistics()
                logger.info(f"📊 Estatísticas: {stats}")
            
            # Aguardar antes da próxima execução
            time.sleep(30)  # 30 segundos
            
    except KeyboardInterrupt:
        logger.info("⏹️ Processador de mídias interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro no processador de mídias: {e}")


if __name__ == "__main__":
    run_media_processor() 