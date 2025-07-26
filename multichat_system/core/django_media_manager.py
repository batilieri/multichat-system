#!/usr/bin/env python3
"""
Sistema de Gerenciamento de Mídias para MultiChat - Versão Django
Usa o banco principal do Django em vez de SQLite separado
"""

import requests
import json
import time
import os
import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import hashlib
import mimetypes
import logging

# Django imports
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from core.models import Cliente, WhatsappInstance, Chat, MediaFile

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DjangoMediaManager:
    def __init__(self, cliente_id: int, instance_id: str, bearer_token: str, base_path: str = None):
        """
        Inicializa o gerenciador de mídias usando o banco Django principal
        
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

        # Buscar objetos Django
        try:
            self.cliente = Cliente.objects.get(id=cliente_id)
            self.instance = WhatsappInstance.objects.get(
                instance_id=instance_id,
                cliente=cliente_id
            )
        except ObjectDoesNotExist as e:
            raise ValueError(f"Cliente ou instância não encontrados: {e}")

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

        # Configurar pastas de mídia por tipo
        self.pastas_midia = {
            'image': self.instance_path / "imagens",
            'video': self.instance_path / "videos", 
            'audio': self.instance_path / "audios",
            'document': self.instance_path / "documentos",
            'sticker': self.instance_path / "stickers"
        }

        for pasta in self.pastas_midia.values():
            pasta.mkdir(exist_ok=True)

        logger.info(f"✅ DjangoMediaManager inicializado para Cliente {cliente_id}, Instância {instance_id}")

    def salvar_midia_no_banco(self, message_data: Dict, info_midia: Dict, file_path: str = None) -> bool:
        """Salva informações da mídia no banco Django principal"""
        try:
            with transaction.atomic():
                # Extrair informações da mensagem
                message_id = message_data.get('messageId', '')
                sender = message_data.get('sender', {})
                chat = message_data.get('chat', {})
                moment = message_data.get('moment')

                message_timestamp = None
                if moment:
                    message_timestamp = datetime.fromtimestamp(moment)

                # Buscar ou criar chat
                chat_obj = None
                if chat.get('id'):
                    chat_obj, created = Chat.objects.get_or_create(
                        chat_id=chat['id'],
                        cliente=self.cliente,
                        defaults={
                            'status': 'active',
                            'canal': 'whatsapp',
                            'data_inicio': timezone.now(),
                            'last_message_at': timezone.now()
                        }
                    )

                # Preparar dados para o modelo Django
                media_data = {
                    'cliente': self.cliente,
                    'instance': self.instance,
                    'chat': chat_obj,
                    'message_id': message_id,
                    'sender_name': sender.get('pushName', 'Sem nome'),
                    'sender_id': sender.get('id', ''),
                    'media_type': info_midia['type'],
                    'mimetype': info_midia['mimetype'],
                    'file_name': info_midia.get('fileName'),
                    'file_path': file_path,
                    'file_size': info_midia.get('fileLength'),
                    'caption': info_midia.get('caption', ''),
                    'width': info_midia.get('width'),
                    'height': info_midia.get('height'),
                    'duration_seconds': info_midia.get('seconds'),
                    'is_ptt': info_midia.get('ptt', False),
                    'download_status': 'success' if file_path else 'pending',
                    'is_group': message_data.get('isGroup', False),
                    'from_me': message_data.get('fromMe', False),
                    'media_key': info_midia.get('mediaKey'),
                    'direct_path': info_midia.get('directPath'),
                    'file_sha256': info_midia.get('fileSha256'),
                    'file_enc_sha256': info_midia.get('fileEncSha256'),
                    'media_key_timestamp': info_midia.get('mediaKeyTimestamp'),
                    'message_timestamp': message_timestamp,
                    'download_timestamp': timezone.now() if file_path else None
                }

                # Criar ou atualizar registro
                media_file, created = MediaFile.objects.update_or_create(
                    message_id=message_id,
                    defaults=media_data
                )

                if created:
                    logger.info(f"✅ Mídia criada no banco Django: {message_id}")
                else:
                    logger.info(f"✅ Mídia atualizada no banco Django: {message_id}")

                return True

        except Exception as e:
            logger.error(f"❌ Erro ao salvar mídia no banco Django: {e}")
            return False

    def buscar_midias_pendentes(self) -> List[MediaFile]:
        """Busca mídias com download pendente no banco Django"""
        try:
            return MediaFile.objects.filter(
                cliente=self.cliente,
                instance=self.instance,
                download_status__in=['pending', 'failed']
            ).order_by('-created_at')
        except Exception as e:
            logger.error(f"❌ Erro ao buscar mídias pendentes: {e}")
            return []

    def atualizar_status_download(self, message_id: str, status: str, file_path: str = None):
        """Atualiza status do download no banco Django"""
        try:
            with transaction.atomic():
                media_file = MediaFile.objects.get(
                    message_id=message_id,
                    cliente=self.cliente,
                    instance=self.instance
                )
                
                media_file.download_status = status
                if file_path:
                    media_file.file_path = file_path
                    media_file.download_timestamp = timezone.now()
                
                media_file.save()
                logger.info(f"✅ Status atualizado: {message_id} -> {status}")

        except MediaFile.DoesNotExist:
            logger.warning(f"⚠️ Mídia não encontrada: {message_id}")
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
        # Limpar nome do remetente
        sender_clean = "".join(c for c in sender_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        sender_clean = sender_clean.replace(' ', '_')
        
        # Obter extensão
        extensao = self.obter_extensao_mimetype(info_midia['mimetype'])
        
        # Gerar nome baseado no timestamp e message_id
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        message_short = message_id[-8:] if len(message_id) > 8 else message_id
        
        nome_base = f"{timestamp}_{sender_clean}_{message_short}{extensao}"
        
        return nome_base

    def descriptografar_e_baixar_midia(self, info_midia: Dict, message_id: str, sender_name: str) -> Optional[str]:
        """Descriptografa e baixa uma mídia do WhatsApp"""
        try:
            # Verificar se já temos dados necessários
            if not self._validar_dados_midia(info_midia):
                logger.warning(f"⚠️ Dados de mídia inválidos para {message_id}")
                return None

            # Gerar nome do arquivo
            nome_arquivo = self.gerar_nome_arquivo(info_midia, message_id, sender_name)
            pasta_destino = self.pastas_midia[info_midia['type']]
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

    def processar_mensagem_whatsapp(self, data: Dict):
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
                
                # Tentar baixar
                file_path = self.descriptografar_e_baixar_midia(
                    info_midia, 
                    message_id, 
                    message_data.get('sender', {}).get('pushName', 'Desconhecido')
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

            for media_file in midias_pendentes:
                try:
                    # Recriar info_midia
                    info_midia = {
                        'type': media_file.media_type,
                        'mimetype': media_file.mimetype,
                        'fileName': media_file.file_name,
                        'fileLength': media_file.file_size,
                        'caption': media_file.caption,
                        'mediaKey': media_file.media_key,
                        'directPath': media_file.direct_path,
                        'fileSha256': media_file.file_sha256,
                        'fileEncSha256': media_file.file_enc_sha256,
                        'mediaKeyTimestamp': media_file.media_key_timestamp
                    }

                    # Tentar baixar novamente
                    file_path = self.descriptografar_e_baixar_midia(
                        info_midia,
                        media_file.message_id,
                        media_file.sender_name
                    )

                    if file_path:
                        self.atualizar_status_download(media_file.message_id, 'success', file_path)
                        logger.info(f"✅ Mídia reprocessada com sucesso: {media_file.message_id}")
                    else:
                        self.atualizar_status_download(media_file.message_id, 'failed')
                        logger.warning(f"⚠️ Falha ao reprocessar mídia: {media_file.message_id}")

                except Exception as e:
                    logger.error(f"❌ Erro ao reprocessar mídia {media_file.message_id}: {e}")

        except Exception as e:
            logger.error(f"❌ Erro ao reprocessar mídias pendentes: {e}")

    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas do gerenciador de mídias"""
        try:
            # Estatísticas do banco Django
            total_midias = MediaFile.objects.filter(
                cliente=self.cliente,
                instance=self.instance
            ).count()
            
            midias_baixadas = MediaFile.objects.filter(
                cliente=self.cliente,
                instance=self.instance,
                download_status='success'
            ).count()
            
            midias_pendentes = MediaFile.objects.filter(
                cliente=self.cliente,
                instance=self.instance,
                download_status='pending'
            ).count()
            
            midias_falhadas = MediaFile.objects.filter(
                cliente=self.cliente,
                instance=self.instance,
                download_status='failed'
            ).count()
            
            # Por tipo de mídia
            por_tipo = {}
            for media_type in ['image', 'video', 'audio', 'document', 'sticker']:
                count = MediaFile.objects.filter(
                    cliente=self.cliente,
                    instance=self.instance,
                    media_type=media_type
                ).count()
                if count > 0:
                    por_tipo[media_type] = count
            
            # Tamanho total dos arquivos
            tamanho_total = MediaFile.objects.filter(
                cliente=self.cliente,
                instance=self.instance,
                download_status='success'
            ).aggregate(
                total_size=models.Sum('file_size')
            )['total_size'] or 0
            
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
            data_limite = timezone.now() - timedelta(days=dias)
            
            # Buscar arquivos antigos
            midias_antigas = MediaFile.objects.filter(
                cliente=self.cliente,
                instance=self.instance,
                created_at__lt=data_limite,
                file_path__isnull=False
            )
            
            for media_file in midias_antigas:
                try:
                    path = Path(media_file.file_path)
                    if path.exists():
                        path.unlink()
                        logger.info(f"🗑️ Arquivo removido: {path.name}")
                except Exception as e:
                    logger.error(f"❌ Erro ao remover arquivo {media_file.file_path}: {e}")
            
            # Atualizar banco
            midias_antigas.update(
                file_path=None,
                download_status='expired'
            )
            
            logger.info(f"✅ Limpeza concluída: {len(midias_antigas)} arquivos removidos")

        except Exception as e:
            logger.error(f"❌ Erro na limpeza de arquivos: {e}")

    def executar(self):
        """Método principal para executar o gerenciador"""
        logger.info(f"🚀 Iniciando DjangoMediaManager para Cliente {self.cliente_id}, Instância {self.instance_id}")
        
        try:
            # Reprocessar mídias pendentes
            self.reprocessar_midias_pendentes()
            
            # Mostrar estatísticas
            stats = self.obter_estatisticas()
            logger.info(f"📊 Estatísticas: {stats}")
            
        except Exception as e:
            logger.error(f"❌ Erro na execução: {e}")


# Função de conveniência para criar instância
def criar_django_media_manager(cliente_id: int, instance_id: str, bearer_token: str, base_path: str = None) -> DjangoMediaManager:
    """
    Cria uma instância do gerenciador de mídias Django
    
    Args:
        cliente_id: ID do cliente no sistema MultiChat
        instance_id: ID da instância do WhatsApp
        bearer_token: Token de autenticação da API W-APi
        base_path: Caminho base para armazenamento (opcional)
    
    Returns:
        DjangoMediaManager: Instância do gerenciador
    """
    return DjangoMediaManager(cliente_id, instance_id, bearer_token, base_path) 