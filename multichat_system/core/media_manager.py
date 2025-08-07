#!/usr/bin/env python3
"""
Sistema de Gerenciamento de Mídias para MultiChat
Monitora mensagens, descriptografa e organiza automaticamente imagens, vídeos, documentos e áudios
Separado por usuário e instância do WhatsApp
"""

import requests
import json
import time
import os
import base64
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import hashlib
import mimetypes
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiChatMediaManager:
    def __init__(self, cliente_id: int, instance_id: str, bearer_token: str, base_path: str = None):
        """
        Inicializa o gerenciador de mídias para um cliente específico
        
        Args:
            cliente_id: ID do cliente no sistema MultiChat
            instance_id: ID da instância do WhatsApp
            bearer_token: Token de autenticação da API W-APi
            base_path: Caminho base para armazenamento (opcional)
        """
        self.cliente_id = cliente_id
        self.instance_id = instance_id
        self.bearer_token = bearer_token
        self.mensagens_processadas = set()
        self.contador_mensagens = 0
        self.contador_midias = 0
        self.base_url = "https://api.w-api.app/v1"

        # Configurar caminhos de armazenamento
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Usar caminho padrão no projeto multichat
            self.base_path = Path(__file__).parent.parent / "media_storage"
        
        # Criar estrutura de pastas por cliente e instância
        self.cliente_path = self.base_path / f"cliente_{cliente_id}"
        self.instance_path = self.cliente_path / f"instance_{instance_id}"
        self.instance_path.mkdir(parents=True, exist_ok=True)

        # Configurar pasta base de chats (nova estrutura)
        self.chats_path = self.instance_path / "chats"
        self.chats_path.mkdir(exist_ok=True)
        
        # Cache para pastas de chat criadas
        self._chat_folders_cache = {}
        
        # Manter compatibilidade com estrutura antiga (para migração)
        self.pastas_midia_legacy = {
            'image': self.instance_path / "imagens",
            'video': self.instance_path / "videos", 
            'audio': self.instance_path / "audios",
            'document': self.instance_path / "documentos",
            'sticker': self.instance_path / "stickers"
        }

        # Configurar banco de dados
        self.db_path = self.instance_path / "media_database.db"
        self._init_database()

        logger.info(f"✅ MediaManager inicializado para Cliente {cliente_id}, Instância {instance_id}")

    def get_chat_media_path(self, chat_id: str, media_type: str) -> Path:
        """Obtém caminho da pasta de mídia para um chat específico"""
        # Normalizar chat_id
        chat_id_clean = self._normalize_chat_id(chat_id)
        
        # Verificar cache
        cache_key = f"{chat_id_clean}_{media_type}"
        if cache_key in self._chat_folders_cache:
            return self._chat_folders_cache[cache_key]
            
        # Criar estrutura de pastas para o chat
        chat_folder = self.chats_path / chat_id_clean
        media_folder = chat_folder / media_type
        media_folder.mkdir(parents=True, exist_ok=True)
        
        # Armazenar em cache
        self._chat_folders_cache[cache_key] = media_folder
        
        return media_folder
        
    def _normalize_chat_id(self, chat_id: str) -> str:
        """Normaliza chat_id para uso como nome de pasta"""
        if not chat_id:
            return "unknown"
            
        import re
        
        # Remover sufixos do WhatsApp
        chat_id = re.sub(r'@[^.]+\.us$', '', chat_id)
        chat_id = re.sub(r'@[^.]+$', '', chat_id)
        
        # Extrair apenas números
        numbers_only = re.sub(r'[^\d]', '', chat_id)
        
        # Se é um grupo (padrão 120363), usar identificador especial
        if len(numbers_only) > 15 and numbers_only.startswith('120363'):
            return f"group_{numbers_only[-12:]}"  # Últimos 12 dígitos
            
        # Se é número válido, usar como está
        if len(numbers_only) >= 10:
            return numbers_only
            
        # Fallback para chat_id original limpo
        clean_id = re.sub(r'[^\w\-]', '_', str(chat_id))
        return clean_id or "unknown"

    def _init_database(self):
        """Inicializa o banco de dados SQLite para armazenar informações das mídias"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Tabela principal de mídias
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS midias (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message_id TEXT UNIQUE NOT NULL,
                        sender_name TEXT NOT NULL,
                        sender_id TEXT NOT NULL,
                        chat_id TEXT NOT NULL,
                        is_group BOOLEAN NOT NULL,
                        from_me BOOLEAN NOT NULL,
                        media_type TEXT NOT NULL,
                        mimetype TEXT NOT NULL,
                        file_name TEXT,
                        file_path TEXT,
                        file_size INTEGER,
                        caption TEXT,
                        width INTEGER,
                        height INTEGER,
                        duration_seconds INTEGER,
                        is_ptt BOOLEAN,
                        download_status TEXT DEFAULT 'pending',
                        download_timestamp DATETIME,
                        message_timestamp DATETIME,
                        media_key TEXT,
                        direct_path TEXT,
                        file_sha256 TEXT,
                        file_enc_sha256 TEXT,
                        media_key_timestamp TEXT,
                        cliente_id INTEGER NOT NULL,
                        instance_id TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Índices para otimizar consultas
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_message_id ON midias(message_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_media_type ON midias(media_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_download_status ON midias(download_status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sender_id ON midias(sender_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_id ON midias(chat_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_cliente_instance ON midias(cliente_id, instance_id)')

                conn.commit()
                logger.info("✅ Banco de dados de mídias inicializado")

        except Exception as e:
            logger.error(f"❌ Erro ao inicializar banco de mídias: {e}")

    def salvar_midia_no_banco(self, message_data: Dict, info_midia: Dict, file_path: str = None) -> bool:
        """Salva informações da mídia no banco de dados local"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Extrair informações da mensagem
                message_id = message_data.get('messageId', '')
                sender = message_data.get('sender', {})
                chat = message_data.get('chat', {})
                moment = message_data.get('moment')

                message_timestamp = None
                if moment:
                    message_timestamp = datetime.fromtimestamp(moment)

                # Preparar dados para inserção
                dados = (
                    message_id,
                    sender.get('pushName', 'Sem nome'),
                    sender.get('id', ''),
                    chat.get('id', ''),
                    message_data.get('isGroup', False),
                    message_data.get('fromMe', False),
                    info_midia['type'],
                    info_midia['mimetype'],
                    info_midia.get('fileName'),
                    file_path,
                    info_midia.get('fileLength'),
                    info_midia.get('caption', ''),
                    info_midia.get('width'),
                    info_midia.get('height'),
                    info_midia.get('seconds'),
                    info_midia.get('ptt', False),
                    'success' if file_path else 'pending',
                    datetime.now() if file_path else None,
                    message_timestamp,
                    info_midia.get('mediaKey'),
                    info_midia.get('directPath'),
                    info_midia.get('fileSha256'),
                    info_midia.get('fileEncSha256'),
                    info_midia.get('mediaKeyTimestamp'),
                    self.cliente_id,
                    self.instance_id
                )

                cursor.execute('''
                    INSERT OR REPLACE INTO midias (
                        message_id, sender_name, sender_id, chat_id, is_group, from_me,
                        media_type, mimetype, file_name, file_path, file_size, caption,
                        width, height, duration_seconds, is_ptt, download_status,
                        download_timestamp, message_timestamp, media_key, direct_path,
                        file_sha256, file_enc_sha256, media_key_timestamp, cliente_id, instance_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', dados)

                conn.commit()
                logger.info(f"✅ Mídia salva no banco: {message_id}")
                return True

        except Exception as e:
            logger.error(f"❌ Erro ao salvar mídia no banco: {e}")
            return False

    def buscar_midias_pendentes(self) -> List[Dict]:
        """Busca mídias com download pendente no banco local"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM midias 
                    WHERE download_status = 'pending' OR download_status = 'failed'
                    ORDER BY created_at DESC
                ''')

                colunas = [desc[0] for desc in cursor.description]
                resultados = cursor.fetchall()

                return [dict(zip(colunas, row)) for row in resultados]

        except Exception as e:
            logger.error(f"❌ Erro ao buscar mídias pendentes: {e}")
            return []

    def atualizar_status_download(self, message_id: str, status: str, file_path: str = None):
        """Atualiza status do download no banco local"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if file_path:
                    cursor.execute('''
                        UPDATE midias 
                        SET download_status = ?, file_path = ?, download_timestamp = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE message_id = ?
                    ''', (status, file_path, datetime.now(), message_id))
                else:
                    cursor.execute('''
                        UPDATE midias 
                        SET download_status = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE message_id = ?
                    ''', (status, message_id))

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Erro ao atualizar status: {e}")

    def extrair_informacoes_midia(self, msg_content: Dict) -> List[Dict]:
        """Extrai informações de mídia de uma mensagem"""
        midias = []
        
        # Verificar diferentes tipos de mídia
        media_types = {
            'imageMessage': 'image',
            'videoMessage': 'video', 
            'audioMessage': 'audio',
            'documentMessage': 'document',
            'stickerMessage': 'sticker'
        }

        for msg_type, media_type in media_types.items():
            if msg_type in msg_content:
                media_data = msg_content[msg_type]
                
                info_midia = {
                    'type': media_type,
                    'mimetype': media_data.get('mimetype', ''),
                    'fileName': media_data.get('fileName'),
                    'fileLength': media_data.get('fileLength'),
                    'caption': media_data.get('caption', ''),
                    'mediaKey': media_data.get('mediaKey'),
                    'directPath': media_data.get('directPath'),
                    'fileSha256': media_data.get('fileSha256'),
                    'fileEncSha256': media_data.get('fileEncSha256'),
                    'mediaKeyTimestamp': media_data.get('mediaKeyTimestamp')
                }

                # Adicionar campos específicos por tipo
                if media_type == 'image':
                    info_midia.update({
                        'width': media_data.get('width'),
                        'height': media_data.get('height'),
                        'jpegThumbnail': media_data.get('jpegThumbnail')
                    })
                elif media_type == 'video':
                    info_midia.update({
                        'width': media_data.get('width'),
                        'height': media_data.get('height'),
                        'seconds': media_data.get('seconds'),
                        'jpegThumbnail': media_data.get('jpegThumbnail')
                    })
                elif media_type == 'audio':
                    info_midia.update({
                        'seconds': media_data.get('seconds'),
                        'ptt': media_data.get('ptt', False)
                    })
                elif media_type == 'document':
                    info_midia.update({
                        'pageCount': media_data.get('pageCount')
                    })

                midias.append(info_midia)

        return midias

    def obter_extensao_mimetype(self, mimetype: str) -> str:
        """Obtém a extensão baseada no mimetype"""
        extensoes = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'video/mp4': '.mp4',
            'video/avi': '.avi',
            'video/mov': '.mov',
            'video/wmv': '.wmv',
            'audio/mp3': '.mp3',
            'audio/mpeg': '.mp3',
            'audio/wav': '.wav',
            'audio/ogg': '.ogg',
            'audio/m4a': '.m4a',
            'audio/aac': '.aac',
            'application/pdf': '.pdf',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'text/plain': '.txt'
        }
        
        return extensoes.get(mimetype, '.bin')

    def gerar_nome_arquivo(self, info_midia: Dict, message_id: str, sender_name: str) -> str:
        """Gera nome único para o arquivo de mídia"""
        # Obter extensão
        extensao = self.obter_extensao_mimetype(info_midia['mimetype'])
        
        # Novo formato: msg_[message_id]_[timestamp].extensao
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        message_short = message_id[-8:] if len(message_id) > 8 else message_id
        
        nome_base = f"msg_{message_short}_{timestamp}{extensao}"
        
        return nome_base

    def descriptografar_e_baixar_midia(self, info_midia: Dict, message_id: str, sender_name: str, chat_id: str = 'unknown') -> Optional[str]:
        """Descriptografa e baixa uma mídia do WhatsApp"""
        try:
            # Verificar se já temos dados necessários
            if not self._validar_dados_midia(info_midia):
                logger.warning(f"⚠️ Dados de mídia inválidos para {message_id}")
                return None

            # Gerar nome do arquivo e obter pasta do chat
            nome_arquivo = self.gerar_nome_arquivo(info_midia, message_id, sender_name)
            pasta_destino = self.get_chat_media_path(chat_id, info_midia['type'])
            caminho_completo = pasta_destino / nome_arquivo

            # Verificar se arquivo já existe
            if caminho_completo.exists():
                logger.info(f"✅ Arquivo já existe: {nome_arquivo}")
                return str(caminho_completo)

            # Tentar baixar via directPath primeiro
            if info_midia.get('directPath'):
                arquivo_baixado = self._baixar_via_direct_path(info_midia, caminho_completo)
                if arquivo_baixado:
                    return arquivo_baixado

            # Tentar baixar via mediaKey
            if info_midia.get('mediaKey'):
                arquivo_baixado = self._baixar_via_media_key(info_midia, caminho_completo)
                if arquivo_baixado:
                    return arquivo_baixado

            logger.error(f"❌ Não foi possível baixar mídia: {message_id}")
            return None

        except Exception as e:
            logger.error(f"❌ Erro ao baixar mídia {message_id}: {e}")
            return None

    def _baixar_via_direct_path(self, info_midia: Dict, caminho_destino: Path) -> Optional[str]:
        """Tenta baixar mídia usando directPath"""
        try:
            headers = {
                'Authorization': f'Bearer {self.bearer_token}',
                'Content-Type': 'application/json'
            }

            # Endpoint para baixar via directPath
            url = f"{self.base_url}/media/download"
            
            payload = {
                'instanceId': self.instance_id,
                'directPath': info_midia['directPath'],
                'mediaKey': info_midia['mediaKey'],
                'fileSha256': info_midia['fileSha256'],
                'fileEncSha256': info_midia['fileEncSha256']
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                # Salvar arquivo
                with open(caminho_destino, 'wb') as f:
                    f.write(response.content)
                
                # Validar arquivo baixado
                if self.validar_arquivo_baixado(caminho_destino, info_midia):
                    logger.info(f"✅ Mídia baixada via directPath: {caminho_destino.name}")
                    return str(caminho_destino)
                else:
                    caminho_destino.unlink(missing_ok=True)
                    logger.warning(f"⚠️ Arquivo baixado inválido: {caminho_destino.name}")
                    return None
            else:
                logger.warning(f"⚠️ Falha ao baixar via directPath: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Erro ao baixar via directPath: {e}")
            return None

    def _baixar_via_media_key(self, info_midia: Dict, caminho_destino: Path) -> Optional[str]:
        """Tenta baixar mídia usando mediaKey"""
        try:
            headers = {
                'Authorization': f'Bearer {self.bearer_token}',
                'Content-Type': 'application/json'
            }

            # Endpoint para baixar via mediaKey
            url = f"{self.base_url}/media/download"
            
            payload = {
                'instanceId': self.instance_id,
                'mediaKey': info_midia['mediaKey'],
                'fileSha256': info_midia['fileSha256'],
                'fileEncSha256': info_midia['fileEncSha256'],
                'mimetype': info_midia['mimetype']
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                # Salvar arquivo
                with open(caminho_destino, 'wb') as f:
                    f.write(response.content)
                
                # Validar arquivo baixado
                if self.validar_arquivo_baixado(caminho_destino, info_midia):
                    logger.info(f"✅ Mídia baixada via mediaKey: {caminho_destino.name}")
                    return str(caminho_destino)
                else:
                    caminho_destino.unlink(missing_ok=True)
                    logger.warning(f"⚠️ Arquivo baixado inválido: {caminho_destino.name}")
                    return None
            else:
                logger.warning(f"⚠️ Falha ao baixar via mediaKey: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Erro ao baixar via mediaKey: {e}")
            return None

    def _validar_dados_midia(self, info_midia: Dict) -> bool:
        """Valida se os dados da mídia são suficientes para download"""
        campos_obrigatorios = ['type', 'mimetype']
        campos_um_ou_outro = [
            ('mediaKey', 'directPath'),
            ('fileSha256', 'fileEncSha256')
        ]

        # Verificar campos obrigatórios
        for campo in campos_obrigatorios:
            if not info_midia.get(campo):
                return False

        # Verificar se tem pelo menos um dos pares de campos
        tem_campos_validos = False
        for campo1, campo2 in campos_um_ou_outro:
            if info_midia.get(campo1) and info_midia.get(campo2):
                tem_campos_validos = True
                break

        return tem_campos_validos

    def validar_arquivo_baixado(self, caminho_arquivo: Path, info_midia: Dict) -> bool:
        """Valida se o arquivo baixado é válido"""
        try:
            if not caminho_arquivo.exists():
                return False

            # Verificar tamanho mínimo
            tamanho = caminho_arquivo.stat().st_size
            if tamanho < 100:  # Arquivo muito pequeno
                return False

            # Verificar magic numbers para tipos conhecidos
            with open(caminho_arquivo, 'rb') as f:
                header = f.read(16)

            mimetype = info_midia['mimetype']
            
            # Validar por tipo
            if mimetype.startswith('image/'):
                return self._validar_imagem(header)
            elif mimetype.startswith('video/'):
                return self._validar_video(header)
            elif mimetype.startswith('audio/'):
                return self._validar_audio(header)
            elif mimetype == 'application/pdf':
                return self._validar_pdf(header)
            else:
                # Para outros tipos, apenas verificar se não está vazio
                return tamanho > 0

        except Exception as e:
            logger.error(f"❌ Erro ao validar arquivo: {e}")
            return False

    def _validar_imagem(self, header: bytes) -> bool:
        """Valida se é uma imagem válida"""
        magic_numbers = {
            b'\xff\xd8\xff': 'JPEG',
            b'\x89PNG\r\n\x1a\n': 'PNG',
            b'GIF87a': 'GIF',
            b'GIF89a': 'GIF',
            b'RIFF': 'WEBP'
        }
        
        for magic, format_name in magic_numbers.items():
            if header.startswith(magic):
                return True
        return False

    def _validar_video(self, header: bytes) -> bool:
        """Valida se é um vídeo válido"""
        magic_numbers = {
            b'ftyp': 'MP4',
            b'RIFF': 'AVI',
            b'\x00\x00\x00\x18': 'MP4'
        }
        
        for magic, format_name in magic_numbers.items():
            if magic in header:
                return True
        return False

    def _validar_audio(self, header: bytes) -> bool:
        """Valida se é um áudio válido"""
        magic_numbers = {
            b'ID3': 'MP3',
            b'\xff\xfb': 'MP3',
            b'\xff\xf3': 'MP3',
            b'\xff\xf2': 'MP3',
            b'RIFF': 'WAV',
            b'OggS': 'OGG'
        }
        
        for magic, format_name in magic_numbers.items():
            if header.startswith(magic):
                return True
        return False

    def _validar_pdf(self, header: bytes) -> bool:
        """Valida se é um PDF válido"""
        return header.startswith(b'%PDF')

    def processar_mensagem_whatsapp(self, data: Dict, chat_id: str = None):
        """Processa uma mensagem do WhatsApp e baixa mídias se necessário"""
        try:
            # Verificar se é uma mensagem válida
            if not self.eh_mensagem_whatsapp(data):
                return

            # Extrair dados da mensagem
            message_data = self._extrair_dados_mensagem(data)
            if not message_data:
                return

            message_id = message_data.get('messageId')
            if not message_id or message_id in self.mensagens_processadas:
                return

            # Marcar como processada
            self.mensagens_processadas.add(message_id)
            self.contador_mensagens += 1

            # Extrair informações de mídia
            msg_content = message_data.get('msgContent', {})
            midias = self.extrair_informacoes_midia(msg_content)

            if not midias:
                return

            # Processar cada mídia
            for info_midia in midias:
                self.contador_midias += 1
                
                # Salvar no banco primeiro
                self.salvar_midia_no_banco(message_data, info_midia)
                
                # Tentar baixar (passar chat_id)
                extracted_chat_id = chat_id or message_data.get('chat', {}).get('id', 'unknown')
                file_path = self.descriptografar_e_baixar_midia(
                    info_midia, 
                    message_id, 
                    message_data.get('sender', {}).get('pushName', 'Desconhecido'),
                    extracted_chat_id
                )
                
                # Atualizar status
                if file_path:
                    self.atualizar_status_download(message_id, 'success', file_path)
                    logger.info(f"✅ Mídia processada com sucesso: {message_id}")
                else:
                    self.atualizar_status_download(message_id, 'failed')
                    logger.warning(f"⚠️ Falha ao processar mídia: {message_id}")

        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}")

    def eh_mensagem_whatsapp(self, data: Dict) -> bool:
        """Verifica se é uma mensagem válida do WhatsApp"""
        if isinstance(data, dict):
            return any([
                data.get('event') == 'webhookDelivery',
                data.get('event') == 'webhookReceived',
                data.get('event') == 'message',
                'instanceId' in data,
                'msgContent' in data,
                'sender' in data and 'chat' in data
            ])
        return False

    def _extrair_dados_mensagem(self, data: Dict) -> Optional[Dict]:
        """Extrai dados da mensagem do webhook"""
        try:
            # Diferentes formatos de webhook
            if 'msgContent' in data:
                return {
                    'messageId': data.get('messageId'),
                    'sender': data.get('sender', {}),
                    'chat': data.get('chat', {}),
                    'msgContent': data.get('msgContent', {}),
                    'isGroup': data.get('isGroup', False),
                    'fromMe': data.get('fromMe', False),
                    'moment': data.get('moment')
                }
            elif 'payload' in data:
                payload = data.get('payload', {})
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

    def reprocessar_midias_pendentes(self):
        """Reprocessa mídias que falharam no download"""
        try:
            midias_pendentes = self.buscar_midias_pendentes()
            
            if not midias_pendentes:
                logger.info("ℹ️ Nenhuma mídia pendente para reprocessar")
                return

            logger.info(f"🔄 Reprocessando {len(midias_pendentes)} mídias pendentes...")

            for midia in midias_pendentes:
                try:
                    # Recriar info_midia
                    info_midia = {
                        'type': midia['media_type'],
                        'mimetype': midia['mimetype'],
                        'fileName': midia['file_name'],
                        'fileLength': midia['file_size'],
                        'caption': midia['caption'],
                        'mediaKey': midia['media_key'],
                        'directPath': midia['direct_path'],
                        'fileSha256': midia['file_sha256'],
                        'fileEncSha256': midia['file_enc_sha256'],
                        'mediaKeyTimestamp': midia['media_key_timestamp']
                    }

                    # Tentar baixar novamente
                    file_path = self.descriptografar_e_baixar_midia(
                        info_midia,
                        midia['message_id'],
                        midia['sender_name']
                    )

                    if file_path:
                        self.atualizar_status_download(midia['message_id'], 'success', file_path)
                        logger.info(f"✅ Mídia reprocessada com sucesso: {midia['message_id']}")
                    else:
                        self.atualizar_status_download(midia['message_id'], 'failed')
                        logger.warning(f"⚠️ Falha ao reprocessar mídia: {midia['message_id']}")

                except Exception as e:
                    logger.error(f"❌ Erro ao reprocessar mídia {midia['message_id']}: {e}")

        except Exception as e:
            logger.error(f"❌ Erro ao reprocessar mídias pendentes: {e}")

    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas do gerenciador de mídias"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Estatísticas gerais
                cursor.execute('SELECT COUNT(*) FROM midias')
                total_midias = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM midias WHERE download_status = "success"')
                midias_baixadas = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM midias WHERE download_status = "pending"')
                midias_pendentes = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM midias WHERE download_status = "failed"')
                midias_falhadas = cursor.fetchone()[0]
                
                # Por tipo de mídia
                cursor.execute('''
                    SELECT media_type, COUNT(*) 
                    FROM midias 
                    GROUP BY media_type
                ''')
                por_tipo = dict(cursor.fetchall())
                
                # Tamanho total dos arquivos
                cursor.execute('SELECT SUM(file_size) FROM midias WHERE download_status = "success"')
                tamanho_total = cursor.fetchone()[0] or 0
                
                return {
                    'cliente_id': self.cliente_id,
                    'instance_id': self.instance_id,
                    'total_midias': total_midias,
                    'midias_baixadas': midias_baixadas,
                    'midias_pendentes': midias_pendentes,
                    'midias_falhadas': midias_falhadas,
                    'por_tipo': por_tipo,
                    'tamanho_total_bytes': tamanho_total,
                    'tamanho_total_mb': round(tamanho_total / (1024 * 1024), 2),
                    'mensagens_processadas': self.contador_mensagens,
                    'midias_processadas': self.contador_midias
                }

        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}

    def limpar_arquivos_antigos(self, dias: int = 30):
        """Remove arquivos de mídia mais antigos que X dias"""
        try:
            from datetime import timedelta
            data_limite = datetime.now() - timedelta(days=dias)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Buscar arquivos antigos
                cursor.execute('''
                    SELECT file_path FROM midias 
                    WHERE created_at < ? AND file_path IS NOT NULL
                ''', (data_limite,))
                
                arquivos_antigos = cursor.fetchall()
                
                for (file_path,) in arquivos_antigos:
                    try:
                        path = Path(file_path)
                        if path.exists():
                            path.unlink()
                            logger.info(f"🗑️ Arquivo removido: {path.name}")
                    except Exception as e:
                        logger.error(f"❌ Erro ao remover arquivo {file_path}: {e}")
                
                # Atualizar banco
                cursor.execute('''
                    UPDATE midias 
                    SET file_path = NULL, download_status = 'expired'
                    WHERE created_at < ?
                ''', (data_limite,))
                
                conn.commit()
                logger.info(f"✅ Limpeza concluída: {len(arquivos_antigos)} arquivos removidos")

        except Exception as e:
            logger.error(f"❌ Erro na limpeza de arquivos: {e}")

    def executar(self):
        """Método principal para executar o gerenciador"""
        logger.info(f"🚀 Iniciando MediaManager para Cliente {self.cliente_id}, Instância {self.instance_id}")
        
        try:
            # Reprocessar mídias pendentes
            self.reprocessar_midias_pendentes()
            
            # Mostrar estatísticas
            stats = self.obter_estatisticas()
            logger.info(f"📊 Estatísticas: {stats}")
            
        except Exception as e:
            logger.error(f"❌ Erro na execução: {e}")


# Função de conveniência para criar instância
def criar_media_manager(cliente_id: int, instance_id: str, bearer_token: str, base_path: str = None) -> MultiChatMediaManager:
    """
    Cria uma instância do gerenciador de mídias
    
    Args:
        cliente_id: ID do cliente no sistema MultiChat
        instance_id: ID da instância do WhatsApp
        bearer_token: Token de autenticação da API W-APi
        base_path: Caminho base para armazenamento (opcional)
    
    Returns:
        MultiChatMediaManager: Instância do gerenciador
    """
    return MultiChatMediaManager(cliente_id, instance_id, bearer_token, base_path) 