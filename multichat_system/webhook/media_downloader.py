#!/usr/bin/env python3
"""
Sistema de Download e Descriptografia de Mídias para MultiChat
Baseado no baixarMidias.py, adaptado para Django
"""

import requests
import json
import time
import os
import base64
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import logging

from django.conf import settings
from django.utils import timezone
from django.db import transaction

from .models import WebhookEvent, MessageMedia
from core.models import Cliente, Chat, Mensagem

logger = logging.getLogger(__name__)


class MultiChatMediaDownloader:
    """
    Sistema de download e descriptografia de mídias para MultiChat
    Baseado no baixarMidias.py, adaptado para Django
    """
    
    def __init__(self, cliente: Cliente, instance_id: str = None, bearer_token: str = None):
        self.cliente = cliente
        self.instance_id = instance_id or cliente.wapi_instance_id
        self.bearer_token = bearer_token or cliente.wapi_token
        self.base_url = "https://api.w-api.app/v1"
        
        # Configurar pastas de mídia por cliente (nova estrutura)
        self._setup_media_folders()
        
        # Contadores
        self.contador_mensagens = 0
        self.contador_midias = 0
        
    def _setup_media_folders(self):
        """Configura as pastas de mídia organizadas por cliente"""
        # Pasta base para mídias (usar media_storage como na migração)
        media_base = Path(__file__).parent.parent / "media_storage"
        media_base.mkdir(exist_ok=True)
        
        # Pasta específica do cliente e instância
        cliente_folder = media_base / f"cliente_{self.cliente.id}"
        instance_folder = cliente_folder / f"instance_{self.instance_id}"
        instance_folder.mkdir(parents=True, exist_ok=True)
        
        # Nova estrutura: pasta base de chats
        self.chats_path = instance_folder / "chats"
        self.chats_path.mkdir(exist_ok=True)
        
        # Cache para pastas de chat criadas
        self._chat_folders_cache = {}
        
        # Manter compatibilidade com estrutura antiga
        self.pastas_midia_legacy = {
            'image': cliente_folder / "imagens",
            'video': cliente_folder / "videos", 
            'audio': cliente_folder / "audios",
            'document': cliente_folder / "documentos",
            'sticker': cliente_folder / "stickers"
        }
            
        logger.info(f"📁 Pastas de mídia configuradas para cliente {self.cliente.nome}")
        
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
        """
        Normaliza chat_id para uso como nome de pasta
        Usa a mesma lógica do webhook views.normalize_chat_id
        """
        if not chat_id:
            return "unknown"
            
        # Verificar se é um grupo (contém @g.us)
        if '@g.us' in chat_id:
            # Para grupos, usar identificador especial
            numbers_only = re.sub(r'[^\d]', '', chat_id)
            if len(numbers_only) > 12:
                return f"group_{numbers_only[-12:]}"  # Últimos 12 dígitos
            else:
                clean_id = re.sub(r'[^\w\-]', '_', str(chat_id))
                return f"group_{clean_id}"
            
        # Remover sufixos comuns do WhatsApp
        chat_id = re.sub(r'@[^.]+\.us$', '', chat_id)  # Remove @c.us, @lid, etc
        chat_id = re.sub(r'@[^.]+$', '', chat_id)      # Remove outros sufixos
        
        # Extrair apenas números
        numbers_only = re.sub(r'[^\d]', '', chat_id)
        
        # Verificar se é um grupo baseado no padrão (números longos que começam com 120363)
        if len(numbers_only) > 15 and numbers_only.startswith('120363'):
            return f"group_{numbers_only[-12:]}"  # Últimos 12 dígitos
            
        # Validar se é um número de telefone válido (mínimo 10 dígitos)
        if len(numbers_only) >= 10:
            return numbers_only
            
        # Fallback para chat_id original limpo se não conseguir normalizar
        clean_id = re.sub(r'[^\w\-]', '_', str(chat_id))
        return clean_id or "unknown"
        
    def extrair_informacoes_midia(self, msg_content: Dict) -> List[Dict]:
        """Extrai informações de mídia para download"""
        midias_info = []
        
        tipos_midia = {
            'imageMessage': 'image',
            'videoMessage': 'video', 
            'audioMessage': 'audio',
            'documentMessage': 'document',
            'stickerMessage': 'sticker'
        }
        
        for tipo_msg, tipo_midia in tipos_midia.items():
            if tipo_msg in msg_content:
                midia_data = msg_content[tipo_msg]
                
                # Verificar campos obrigatórios para descriptografia
                campos_obrigatorios = ['mediaKey', 'directPath', 'fileEncSha256', 'fileSha256']
                if not all(midia_data.get(campo) for campo in campos_obrigatorios):
                    logger.warning(f"⚠️ {tipo_midia} sem dados completos para descriptografia")
                    continue
                    
                info_midia = {
                    'type': tipo_midia,
                    'mediaKey': midia_data.get('mediaKey'),
                    'directPath': midia_data.get('directPath'),
                    'mimetype': midia_data.get('mimetype'),
                    'url': midia_data.get('url'),
                    'fileLength': midia_data.get('fileLength'),
                    'fileName': midia_data.get('fileName'),
                    'caption': midia_data.get('caption', ''),
                    'fileSha256': midia_data.get('fileSha256'),
                    'fileEncSha256': midia_data.get('fileEncSha256'),
                    'jpegThumbnail': midia_data.get('jpegThumbnail'),
                    'mediaKeyTimestamp': midia_data.get('mediaKeyTimestamp')
                }
                
                # Adicionar dados específicos por tipo
                if tipo_midia in ['image', 'video']:
                    info_midia.update({
                        'width': midia_data.get('width'),
                        'height': midia_data.get('height')
                    })
                    
                if tipo_midia in ['video', 'audio']:
                    info_midia['seconds'] = midia_data.get('seconds')
                    
                if tipo_midia == 'audio':
                    info_midia.update({
                        'ptt': midia_data.get('ptt', False),
                        'waveform': midia_data.get('waveform')
                    })
                    
                if tipo_midia == 'document':
                    info_midia.update({
                        'title': midia_data.get('title'),
                        'pageCount': midia_data.get('pageCount')
                    })
                    
                if tipo_midia == 'sticker':
                    info_midia.update({
                        'isAnimated': midia_data.get('isAnimated', False),
                        'isAvatar': midia_data.get('isAvatar', False)
                    })
                    
                midias_info.append(info_midia)
                
        return midias_info
        
    def _validar_dados_midia(self, info_midia: Dict) -> bool:
        """Valida se os dados de mídia estão completos"""
        campos_obrigatorios = ['mediaKey', 'directPath', 'type', 'mimetype']
        
        for campo in campos_obrigatorios:
            if not info_midia.get(campo):
                logger.error(f"❌ Campo obrigatório ausente: {campo}")
                return False
                
        # Validar se mediaKey tem formato válido (base64)
        media_key = info_midia['mediaKey']
        if len(media_key) < 32:  # MediaKey muito curta
            logger.error(f"❌ MediaKey muito curta: {len(media_key)} chars")
            return False
            
        # Validar directPath
        direct_path = info_midia['directPath']
        if not direct_path.startswith('/'):
            logger.error(f"❌ DirectPath inválido: {direct_path}")
            return False
            
        return True
        
    def _validar_magic_numbers(self, data: bytes, mimetype: str) -> bool:
        """Valida magic numbers para verificar integridade do arquivo"""
        if len(data) < 12:  # Muito pequeno para ter magic numbers
            return False
            
        # Magic numbers específicos
        magic_numbers = {
            'audio/ogg': [b'OggS'],
            'audio/mpeg': [b'\xff\xfb', b'\xff\xf3', b'\xff\xf2', b'ID3'],
            'audio/mp4': [b'ftyp', b'ftypM4A'],
            'audio/wav': [b'RIFF'],
            'audio/webm': [b'\x1a\x45\xdf\xa3'],
            'image/jpeg': [b'\xff\xd8\xff'],
            'image/png': [b'\x89PNG\r\n\x1a\n'],
            'image/gif': [b'GIF87a', b'GIF89a'],
            'image/webp': [b'RIFF', b'WEBP'],
            'video/mp4': [b'ftyp', b'moov', b'mdat'],
            'video/webm': [b'\x1a\x45\xdf\xa3'],
            'video/3gpp': [b'ftyp3g'],
            'application/pdf': [b'%PDF']
        }
        
        expected_magic = magic_numbers.get(mimetype, [])
        if not expected_magic:
            logger.warning(f"⚠️ Magic number não definido para {mimetype}")
            return True  # Assumir válido se não soubermos
            
        # Verificar primeiros 20 bytes para magic numbers
        header = data[:20]
        
        for magic in expected_magic:
            if header.startswith(magic) or magic in header:
                logger.info(f"✅ Magic number válido: {magic}")
                return True
                
        logger.error(f"❌ Magic number inválido para {mimetype}")
        return False
        
    def _obter_extensao_correta(self, mimetype: str, filename: str = None) -> str:
        """Obtém extensão correta, priorizando filename original"""
        
        # Se tem filename original, usar sua extensão
        if filename and '.' in filename:
            ext_original = os.path.splitext(filename)[1].lower()
            if ext_original:
                return ext_original
                
        # Mapeamento de mimetypes
        mimetypes_map = {
            # Áudios
            'audio/ogg': '.ogg',
            'audio/ogg; codecs=opus': '.ogg',
            'audio/mpeg': '.mp3',
            'audio/mp4': '.m4a',
            'audio/wav': '.wav',
            'audio/webm': '.webm',
            'audio/aac': '.aac',
            'audio/flac': '.flac',
            
            # Imagens
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/svg+xml': '.svg',
            
            # Vídeos
            'video/mp4': '.mp4',
            'video/webm': '.webm',
            'video/avi': '.avi',
            'video/mov': '.mov',
            'video/3gpp': '.3gp',
            'video/quicktime': '.mov',
            
            # Documentos
            'application/pdf': '.pdf',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'text/plain': '.txt'
        }
        
        return mimetypes_map.get(mimetype, '.bin')
        
    def gerar_nome_arquivo(self, info_midia: Dict, message_id: str, sender_name: str) -> str:
        """Gera nome único para o arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Limpar nome do remetente
        sender_clean = "".join(c for c in sender_name if c.isalnum() or c in (' ', '-', '_')).strip()
        sender_clean = sender_clean.replace(' ', '_')[:20]
        
        # Obter extensão correta
        extensao = self._obter_extensao_correta(info_midia['mimetype'], info_midia.get('fileName'))
        
        # Se tem nome original, usar
        if info_midia.get('fileName'):
            nome_original = info_midia['fileName']
            nome_sem_ext = os.path.splitext(nome_original)[0][:30]
            return f"{timestamp}_{sender_clean}_{nome_sem_ext}{extensao}"
            
        # Senão, usar tipo e ID da mensagem
        tipo = info_midia['type']
        message_short = message_id[:8] if message_id else "unknown"
        
        return f"msg_{message_short}_{timestamp}{extensao}"
        
    def descriptografar_e_baixar_midia(self, info_midia: Dict, message_id: str, sender_name: str) -> Optional[str]:
        """Descriptografa e baixa mídia usando a API W-API"""
        if not self.instance_id or not self.bearer_token:
            logger.warning(f"⚠️ API não configurada - Instance ID: {self.instance_id}, Token: {'***' if self.bearer_token else 'None'}")
            logger.warning(f"   Cliente: {self.cliente.nome} (ID: {self.cliente.id})")
            logger.warning(f"   wapi_instance_id: {self.cliente.wapi_instance_id}")
            logger.warning(f"   wapi_token: {'***' if self.cliente.wapi_token else 'None'}")
            return None
            
        # Validar campos obrigatórios para descriptografia
        campos_necessarios = ['mediaKey', 'directPath', 'fileEncSha256', 'fileSha256']
        for campo in campos_necessarios:
            if not info_midia.get(campo):
                logger.error(f"❌ {campo} ausente - necessário para descriptografia")
                return None
                
        # URL da API de download
        url = f"{self.base_url}/message/download-media"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        params = {'instanceId': self.instance_id}
        
        # Payload para descriptografia
        payload = {
            'mediaKey': info_midia['mediaKey'],
            'directPath': info_midia['directPath'],
            'type': info_midia['type'],
            'mimetype': info_midia['mimetype']
        }
        
        try:
            logger.info(f"🔓 Descriptografando {info_midia['type']}...")
            
            response = requests.post(url, headers=headers, params=params, json=payload, timeout=60)
            logger.info(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                
                if 'application/json' in content_type:
                    # Resposta JSON com dados base64
                    result = response.json()
                    
                    # Verificar se há erro na resposta da API
                    if 'error' in result:
                        error_msg = result.get('error', 'Erro desconhecido')
                        logger.error(f"❌ Erro da API: {error_msg}")
                        
                        # Se há fileLink, tentar download direto
                        if 'fileLink' in result and result['fileLink']:
                            logger.info(f"   🔄 Tentando download direto via fileLink...")
                            return self._baixar_via_filelink(result['fileLink'], info_midia, message_id, sender_name)
                            
                        return None
                        
                    # Verificar estrutura da resposta
                    media_data = None
                    if 'data' in result:
                        media_data = result['data']
                    elif 'media' in result:
                        media_data = result['media']
                    elif 'buffer' in result:
                        media_data = result['buffer']
                    elif 'file' in result:
                        media_data = result['file']
                    elif 'fileLink' in result and result['fileLink']:
                        # API retornou link direto
                        logger.info(f"   🔄 API retornou fileLink, fazendo download direto...")
                        return self._baixar_via_filelink(result['fileLink'], info_midia, message_id, sender_name)
                        
                    if not media_data:
                        logger.error(f"❌ Dados de mídia não encontrados na resposta")
                        return None
                        
                    # Processar dados base64
                    media_base64 = None
                    if isinstance(media_data, str):
                        media_base64 = media_data
                    elif isinstance(media_data, dict):
                        # Procurar em diferentes campos possíveis
                        for field in ['media', 'buffer', 'data', 'content', 'file']:
                            if field in media_data:
                                media_base64 = media_data[field]
                                break
                                
                    if not media_base64:
                        logger.error(f"❌ String base64 não encontrada")
                        return None
                        
                    # Decodificação base64 robusta
                    try:
                        # Limpar dados base64
                        if media_base64.startswith('data:'):
                            media_base64 = media_base64.split(',', 1)[1]
                            
                        # Remover espaços e quebras de linha
                        media_base64 = media_base64.strip().replace('\n', '').replace('\r', '').replace(' ', '')
                        
                        # Validar caracteres base64
                        if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', media_base64):
                            logger.error(f"❌ Caracteres inválidos na string base64")
                            return None
                            
                        # Adicionar padding se necessário
                        padding = len(media_base64) % 4
                        if padding:
                            media_base64 += '=' * (4 - padding)
                            
                        media_bytes = base64.b64decode(media_base64)
                        
                        if len(media_bytes) == 0:
                            logger.error(f"❌ Decodificação resultou em dados vazios")
                            return None
                            
                        logger.info(f"   ✅ Decodificado: {len(media_bytes)} bytes")
                        
                    except Exception as e:
                        logger.error(f"❌ Erro ao decodificar base64: {e}")
                        return None
                        
                else:
                    # Resposta binária direta
                    media_bytes = response.content
                    if len(media_bytes) == 0:
                        logger.error(f"❌ Resposta binária vazia")
                        return None
                    logger.info(f"   ✅ Dados binários: {len(media_bytes)} bytes")
                    
                # Validar magic numbers
                if not self._validar_magic_numbers(media_bytes, info_midia['mimetype']):
                    logger.error(f"❌ Arquivo corrompido - magic numbers inválidos")
                    return None
                    
                # Validar tamanho esperado se disponível
                if info_midia.get('fileLength'):
                    tamanho_esperado = int(info_midia['fileLength'])
                    tamanho_real = len(media_bytes)
                    
                    # Tolerância de 10% ou 1KB (o que for maior)
                    tolerancia = max(1024, tamanho_esperado * 0.1)
                    
                    if abs(tamanho_real - tamanho_esperado) > tolerancia:
                        logger.error(f"❌ Tamanho incorreto - Esperado: {tamanho_esperado}, Real: {tamanho_real}")
                        return None
                        
                # Obter chat_id (deve ser passado como parâmetro)
                chat_id = getattr(self, '_current_chat_id', 'unknown')
                
                # Gerar nome e salvar arquivo na nova estrutura
                nome_arquivo = self.gerar_nome_arquivo(info_midia, message_id, sender_name)
                pasta_tipo = self.get_chat_media_path(chat_id, info_midia['type'])
                caminho_arquivo = pasta_tipo / nome_arquivo
                
                # Salvamento atômico
                caminho_temp = pasta_tipo / f"temp_{nome_arquivo}"
                
                try:
                    with open(caminho_temp, 'wb') as f:
                        f.write(media_bytes)
                        
                    # Verificar se o arquivo temporário foi salvo corretamente
                    if caminho_temp.stat().st_size != len(media_bytes):
                        logger.error(f"❌ Erro na gravação do arquivo")
                        caminho_temp.unlink(missing_ok=True)
                        return None
                        
                    # Mover arquivo temporário para definitivo
                    caminho_temp.rename(caminho_arquivo)
                    
                    logger.info(f"✅ {info_midia['type'].title()} salvo: {caminho_arquivo}")
                    return str(caminho_arquivo)
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao salvar arquivo: {e}")
                    caminho_temp.unlink(missing_ok=True)
                    return None
                    
            else:
                logger.error(f"❌ Erro na API: {response.status_code}")
                try:
                    error_detail = response.json()
                    logger.error(f"   📄 Detalhes: {error_detail}")
                except:
                    logger.error(f"   📄 Resposta: {response.text[:200]}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na descriptografia: {e}")
            return None
            
    def _baixar_via_filelink(self, file_url: str, info_midia: Dict, message_id: str, sender_name: str) -> Optional[str]:
        """Baixa mídia usando URL direta fornecida pela API"""
        try:
            logger.info(f"📥 Baixando via fileLink: {file_url[:50]}...")
            
            headers = {
                'Authorization': f'Bearer {self.bearer_token}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(file_url, headers=headers, stream=True, timeout=60)
            
            if response.status_code == 200:
                # Ler dados
                media_bytes = response.content
                
                if len(media_bytes) == 0:
                    logger.error(f"❌ Arquivo vazio recebido")
                    return None
                    
                # Validar magic numbers
                if not self._validar_magic_numbers(media_bytes, info_midia['mimetype']):
                    logger.error(f"❌ Magic numbers inválidos para {info_midia['mimetype']}")
                    return None
                    
                # Obter chat_id (deve ser passado como parâmetro)  
                chat_id = getattr(self, '_current_chat_id', 'unknown')
                
                # Gerar nome e salvar arquivo na nova estrutura
                nome_arquivo = self.gerar_nome_arquivo(info_midia, message_id, sender_name)
                pasta_tipo = self.get_chat_media_path(chat_id, info_midia['type'])
                caminho_arquivo = pasta_tipo / nome_arquivo
                
                # Salvamento atômico
                caminho_temp = pasta_tipo / f"temp_{nome_arquivo}"
                
                with open(caminho_temp, 'wb') as f:
                    f.write(media_bytes)
                    
                # Verificar se foi salvo corretamente
                if caminho_temp.stat().st_size != len(media_bytes):
                    logger.error(f"❌ Erro na gravação do arquivo")
                    caminho_temp.unlink(missing_ok=True)
                    return None
                    
                # Mover para definitivo
                caminho_temp.rename(caminho_arquivo)
                
                logger.info(f"✅ {info_midia['type'].title()} baixado via fileLink: {caminho_arquivo}")
                return str(caminho_arquivo)
            else:
                logger.error(f"❌ Erro no download via fileLink: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro no download via fileLink: {e}")
            return None
            
    def processar_mensagem_com_midia(self, webhook_event: WebhookEvent, message_data: Dict) -> bool:
        """Processa uma mensagem e baixa suas mídias"""
        try:
            self.contador_mensagens += 1
            
            # Extrair informações da mensagem
            message_id = message_data.get('messageId', '')
            sender = message_data.get('sender', {})
            sender_name = sender.get('pushName', 'Sem nome')
            msg_content = message_data.get('msgContent', {})
            
            # Extrair chat_id e armazenar para uso nos métodos
            chat_data = message_data.get('chat', {})
            chat_id = chat_data.get('id', 'unknown')
            self._current_chat_id = chat_id
            
            logger.info(f"📱 Processando mensagem #{self.contador_mensagens}: {message_id} (chat: {self._normalize_chat_id(chat_id)})")
            
            if not msg_content:
                return False
                
            # Extrair informações de mídia
            midias_info = self.extrair_informacoes_midia(msg_content)
            
            if not midias_info:
                return False
                
            logger.info(f"📎 {len(midias_info)} mídia(s) detectada(s)")
            
            # Processar cada mídia
            for i, info_midia in enumerate(midias_info, 1):
                self.contador_midias += 1
                
                logger.info(f"📄 Processando mídia #{i}: {info_midia['type']}")
                
                # Validar dados da mídia
                if not self._validar_dados_midia(info_midia):
                    logger.error(f"❌ Dados de mídia inválidos - pulando")
                    continue
                    
                # Criar registro MessageMedia (pendente)
                message_media = MessageMedia.objects.create(
                    event=webhook_event,
                    media_path="",  # Será atualizado após download
                    media_type=info_midia['type'],
                    mimetype=info_midia['mimetype'],
                    file_size=info_midia.get('fileLength'),
                    download_status='pending'
                )
                
                # Tentar download
                caminho_arquivo = None
                if self.instance_id and self.bearer_token:
                    caminho_arquivo = self.descriptografar_e_baixar_midia(
                        info_midia, message_id, sender_name
                    )
                    
                    # Se falhar, tentar método alternativo com URL direta
                    if not caminho_arquivo and info_midia.get('url'):
                        logger.info("🔄 Tentando download direto da URL...")
                        caminho_arquivo = self._baixar_via_filelink(
                            info_midia['url'], info_midia, message_id, sender_name
                        )
                        
                # Atualizar status
                if caminho_arquivo:
                    message_media.media_path = caminho_arquivo
                    message_media.download_status = 'success'
                    message_media.save()
                    logger.info(f"✅ Mídia salva: {caminho_arquivo}")
                else:
                    message_media.download_status = 'failed'
                    message_media.save()
                    logger.error(f"❌ Falha no download da mídia")
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar mensagem: {e}")
            return False
            
    def reprocessar_midias_pendentes(self) -> int:
        """Reprocessa mídias que falharam no download"""
        try:
            # Buscar mídias pendentes ou falhadas
            midias_pendentes = MessageMedia.objects.filter(
                event__cliente=self.cliente,
                download_status__in=['pending', 'failed']
            ).select_related('event')
            
            if not midias_pendentes:
                logger.info("✅ Não há mídias pendentes para reprocessar")
                return 0
                
            logger.info(f"🔄 Reprocessando {len(midias_pendentes)} mídias pendentes...")
            
            sucessos = 0
            for message_media in midias_pendentes:
                try:
                    # Extrair dados da mensagem do evento
                    message_data = message_media.event.raw_data
                    
                    # Extrair informações de mídia
                    msg_content = message_data.get('msgContent', {})
                    midias_info = self.extrair_informacoes_midia(msg_content)
                    
                    # Encontrar a mídia correspondente
                    info_midia = None
                    for midia in midias_info:
                        if midia['type'] == message_media.media_type:
                            info_midia = midia
                            break
                            
                    if not info_midia:
                        logger.warning(f"⚠️ Informações de mídia não encontradas para {message_media.id}")
                        continue
                        
                    # Tentar download novamente
                    message_id = message_data.get('messageId', '')
                    sender = message_data.get('sender', {})
                    sender_name = sender.get('pushName', 'Sem nome')
                    
                    caminho_arquivo = self.descriptografar_e_baixar_midia(
                        info_midia, message_id, sender_name
                    )
                    
                    if caminho_arquivo:
                        message_media.media_path = caminho_arquivo
                        message_media.download_status = 'success'
                        message_media.save()
                        sucessos += 1
                        logger.info(f"✅ Reprocessado com sucesso: {caminho_arquivo}")
                    else:
                        logger.error(f"❌ Falha no reprocessamento")
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao reprocessar mídia {message_media.id}: {e}")
                    
            logger.info(f"✅ Reprocessamento concluído: {sucessos}/{len(midias_pendentes)} sucessos")
            return sucessos
            
        except Exception as e:
            logger.error(f"❌ Erro no reprocessamento: {e}")
            return 0
            
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas das mídias do cliente"""
        try:
            midias = MessageMedia.objects.filter(event__cliente=self.cliente)
            
            estatisticas = {}
            for midia in midias:
                tipo = midia.media_type
                if tipo not in estatisticas:
                    estatisticas[tipo] = {
                        'total': 0,
                        'sucesso': 0,
                        'falhas': 0,
                        'pendentes': 0
                    }
                    
                estatisticas[tipo]['total'] += 1
                
                if midia.download_status == 'success':
                    estatisticas[tipo]['sucesso'] += 1
                elif midia.download_status == 'failed':
                    estatisticas[tipo]['falhas'] += 1
                elif midia.download_status == 'pending':
                    estatisticas[tipo]['pendentes'] += 1
                    
            return estatisticas
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {}


def processar_midias_automaticamente(webhook_event: WebhookEvent):
    """
    Função para processar mídias automaticamente quando um webhook é recebido
    """
    try:
        # Verificar se é uma mensagem com mídia
        message_data = webhook_event.raw_data
        msg_content = message_data.get('msgContent', {})
        
        # Verificar se há mídia na mensagem
        tipos_midia = ['imageMessage', 'videoMessage', 'audioMessage', 'documentMessage', 'stickerMessage']
        tem_midia = any(tipo in msg_content for tipo in tipos_midia)
        
        if not tem_midia:
            logger.debug("📭 Nenhuma mídia encontrada na mensagem")
            return
            
        # Extrair chat_id do webhook_event (usar o chat_id já processado)
        chat_id = webhook_event.chat_id or message_data.get('chat', {}).get('id', 'unknown')
        
        logger.info(f"📱 Processando mídia automaticamente - Chat ID: {chat_id}")
        logger.info(f"   Cliente: {webhook_event.cliente.nome} (ID: {webhook_event.cliente.id})")
        logger.info(f"   Tipos de mídia encontrados: {[tipo for tipo in tipos_midia if tipo in msg_content]}")
        
        # Criar downloader e processar com chat_id
        downloader = MultiChatMediaDownloader(webhook_event.cliente)
        
        # Definir chat_id no downloader ANTES do processamento
        downloader._current_chat_id = chat_id
        
        # Log das configurações do downloader
        logger.info(f"   Instance ID: {downloader.instance_id}")
        logger.info(f"   Bearer Token: {'Configurado' if downloader.bearer_token else 'NÃO CONFIGURADO'}")
        
        resultado = downloader.processar_mensagem_com_midia(webhook_event, message_data)
        
        if resultado:
            logger.info("✅ Processamento de mídia automático concluído com sucesso")
        else:
            logger.warning("⚠️ Processamento de mídia automático falhou")
        
    except Exception as e:
        logger.error(f"❌ Erro no processamento automático de mídias: {e}")


def reprocessar_midias_cliente(cliente_id: int) -> int:
    """
    Função para reprocessar mídias de um cliente específico
    """
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        downloader = MultiChatMediaDownloader(cliente)
        return downloader.reprocessar_midias_pendentes()
    except Cliente.DoesNotExist:
        logger.error(f"❌ Cliente {cliente_id} não encontrado")
        return 0
    except Exception as e:
        logger.error(f"❌ Erro ao reprocessar mídias: {e}")
        return 0 