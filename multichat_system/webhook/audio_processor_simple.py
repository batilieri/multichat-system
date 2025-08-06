#!/usr/bin/env python3
"""
Processador de áudios simplificado (sem FFmpeg)
Para testes e desenvolvimento
"""

import os
import requests
import base64
import hashlib
import json
import logging
from pathlib import Path
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

class SimpleAudioProcessor:
    """Processador de áudio simplificado para testes"""
    
    def __init__(self, cliente):
        self.cliente = cliente
        self.media_dir = Path(settings.MEDIA_ROOT) / "audios" / str(cliente.id)
        self.media_dir.mkdir(parents=True, exist_ok=True)
    
    def download_audio(self, url, media_key, file_sha256):
        """
        Baixa o áudio do WhatsApp (versão simplificada)
        """
        try:
            logger.info(f"🎵 Baixando áudio: {url}")
            
            # Baixar dados
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            audio_data = response.content
            
            # Verificar hash se fornecido
            if file_sha256:
                actual_sha256 = base64.b64encode(hashlib.sha256(audio_data).digest()).decode()
                if actual_sha256 != file_sha256:
                    logger.warning(f"⚠️ Hash não confere: esperado {file_sha256}, obtido {actual_sha256}")
            
            logger.info(f"✅ Áudio baixado com sucesso: {len(audio_data)} bytes")
            return audio_data
                
        except Exception as e:
            logger.error(f"❌ Erro ao baixar áudio: {e}")
            return None
    
    def save_audio(self, audio_data, filename, message_id):
        """
        Salva o áudio no sistema de arquivos (formato original)
        """
        try:
            # Gerar nome único baseado no message_id
            safe_filename = f"audio_{message_id}_{int(timezone.now().timestamp())}.ogg"
            file_path = self.media_dir / safe_filename
            
            # Salvar arquivo
            with open(file_path, 'wb') as f:
                f.write(audio_data)
            
            logger.info(f"💾 Áudio salvo: {file_path}")
            
            # Retornar URL relativa
            relative_path = f"audios/{self.cliente.id}/{safe_filename}"
            return relative_path
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar áudio: {e}")
            return None
    
    def process_audio_message(self, audio_data, message_id):
        """
        Processa uma mensagem de áudio (versão simplificada)
        """
        try:
            logger.info(f"🎵 Processando áudio para mensagem: {message_id}")
            
            # Extrair dados do áudio
            url = audio_data.get('url')
            media_key = audio_data.get('mediaKey')
            file_sha256 = audio_data.get('fileSha256')
            mimetype = audio_data.get('mimetype', 'audio/ogg')
            seconds = audio_data.get('seconds', 0)
            ptt = audio_data.get('ptt', False)
            
            if not url:
                logger.error("❌ URL não fornecida para processar áudio")
                return None
            
            # Baixar áudio (sem descriptografia para testes)
            audio_data = self.download_audio(url, media_key, file_sha256)
            if not audio_data:
                return None
            
            # Salvar arquivo
            file_path = self.save_audio(audio_data, f"audio_{message_id}", message_id)
            
            if file_path:
                # Retornar informações do áudio processado
                return {
                    'file_path': file_path,
                    'file_size': len(audio_data),
                    'duration': seconds,
                    'ptt': ptt,
                    'mimetype': mimetype,
                    'status': 'success',
                    'note': 'Versão simplificada - sem conversão'
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar áudio: {e}")
            return None

def process_audio_from_webhook_simple(webhook_data, cliente):
    """
    Processa áudio recebido via webhook (versão simplificada)
    """
    try:
        # Extrair dados do webhook
        msg_content = webhook_data.get('msgContent', {})
        audio_message = msg_content.get('audioMessage')
        
        if not audio_message:
            logger.warning("⚠️ Nenhum áudio encontrado no webhook")
            return None
        
        # Obter message_id
        message_id = webhook_data.get('messageId', f"audio_{int(timezone.now().timestamp())}")
        
        # Processar áudio
        processor = SimpleAudioProcessor(cliente)
        result = processor.process_audio_message(audio_message, message_id)
        
        if result:
            logger.info(f"✅ Áudio processado com sucesso: {result['file_path']}")
            return result
        else:
            logger.error("❌ Falha ao processar áudio")
            return None
            
    except Exception as e:
        logger.error(f"❌ Erro ao processar áudio do webhook: {e}")
        return None 