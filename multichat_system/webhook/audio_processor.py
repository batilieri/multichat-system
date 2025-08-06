#!/usr/bin/env python3
"""
Processador de áudios do WhatsApp
Baixa, converte e salva áudios recebidos via webhook
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
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import tempfile
import subprocess

logger = logging.getLogger(__name__)

class WhatsAppAudioProcessor:
    """Processador de áudios do WhatsApp"""
    
    def __init__(self, cliente):
        self.cliente = cliente
        self.media_dir = Path(settings.MEDIA_ROOT) / "audios" / str(cliente.id)
        self.media_dir.mkdir(parents=True, exist_ok=True)
    
    def decrypt_audio(self, encrypted_data, media_key, file_sha256):
        """
        Descriptografa o áudio do WhatsApp usando a chave de mídia
        """
        try:
            # Decodificar a chave de mídia
            media_key_bytes = base64.b64decode(media_key)
            
            # Gerar chaves de criptografia
            info = b"WhatsApp Audio Keys"
            key = hashlib.pbkdf2_hmac('sha256', media_key_bytes, info, 256, 32)
            
            # Extrair IV e dados criptografados
            iv = encrypted_data[:16]
            ciphertext = encrypted_data[16:]
            
            # Descriptografar
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Remover padding PKCS7
            padding_length = decrypted_data[-1]
            if padding_length <= 16:
                decrypted_data = decrypted_data[:-padding_length]
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"❌ Erro ao descriptografar áudio: {e}")
            return None
    
    def download_audio(self, url, media_key, file_sha256):
        """
        Baixa e descriptografa o áudio do WhatsApp
        """
        try:
            logger.info(f"🎵 Baixando áudio: {url}")
            
            # Baixar dados criptografados
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            encrypted_data = response.content
            
            # Verificar hash se fornecido
            if file_sha256:
                actual_sha256 = base64.b64encode(hashlib.sha256(encrypted_data).digest()).decode()
                if actual_sha256 != file_sha256:
                    logger.warning(f"⚠️ Hash não confere: esperado {file_sha256}, obtido {actual_sha256}")
            
            # Descriptografar
            decrypted_data = self.decrypt_audio(encrypted_data, media_key, file_sha256)
            
            if decrypted_data:
                logger.info(f"✅ Áudio descriptografado com sucesso: {len(decrypted_data)} bytes")
                return decrypted_data
            else:
                logger.error("❌ Falha ao descriptografar áudio")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao baixar áudio: {e}")
            return None
    
    def convert_to_mp3(self, audio_data, input_format="ogg"):
        """
        Converte o áudio para MP3 usando ffmpeg
        """
        try:
            # Criar arquivo temporário de entrada
            with tempfile.NamedTemporaryFile(suffix=f".{input_format}", delete=False) as temp_input:
                temp_input.write(audio_data)
                temp_input_path = temp_input.name
            
            # Criar arquivo temporário de saída
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_output:
                temp_output_path = temp_output.name
            
            # Comando ffmpeg para conversão
            cmd = [
                "ffmpeg",
                "-i", temp_input_path,
                "-acodec", "libmp3lame",
                "-ab", "128k",
                "-ar", "44100",
                "-y",  # Sobrescrever arquivo de saída
                temp_output_path
            ]
            
            logger.info(f"🔄 Convertendo áudio para MP3...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Ler arquivo convertido
                with open(temp_output_path, 'rb') as f:
                    mp3_data = f.read()
                
                logger.info(f"✅ Conversão concluída: {len(mp3_data)} bytes")
                
                # Limpar arquivos temporários
                os.unlink(temp_input_path)
                os.unlink(temp_output_path)
                
                return mp3_data
            else:
                logger.error(f"❌ Erro na conversão: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao converter áudio: {e}")
            return None
    
    def save_audio(self, audio_data, filename, message_id):
        """
        Salva o áudio no sistema de arquivos
        """
        try:
            # Gerar nome único baseado no message_id
            safe_filename = f"audio_{message_id}_{int(timezone.now().timestamp())}.mp3"
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
        Processa uma mensagem de áudio completa
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
            
            if not url or not media_key:
                logger.error("❌ Dados insuficientes para processar áudio")
                return None
            
            # Baixar e descriptografar
            decrypted_data = self.download_audio(url, media_key, file_sha256)
            if not decrypted_data:
                return None
            
            # Determinar formato de entrada
            input_format = "ogg"
            if "opus" in mimetype:
                input_format = "opus"
            elif "mp4" in mimetype:
                input_format = "m4a"
            
            # Converter para MP3
            mp3_data = self.convert_to_mp3(decrypted_data, input_format)
            if not mp3_data:
                return None
            
            # Salvar arquivo
            file_path = self.save_audio(mp3_data, f"audio_{message_id}", message_id)
            
            if file_path:
                # Retornar informações do áudio processado
                return {
                    'file_path': file_path,
                    'file_size': len(mp3_data),
                    'duration': seconds,
                    'ptt': ptt,
                    'mimetype': 'audio/mpeg',
                    'status': 'success'
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar áudio: {e}")
            return None

def process_audio_from_webhook(webhook_data, cliente):
    """
    Processa áudio recebido via webhook
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
        processor = WhatsAppAudioProcessor(cliente)
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