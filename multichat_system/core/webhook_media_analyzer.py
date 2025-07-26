#!/usr/bin/env python3
"""
Analisador Completo de Webhooks para Mídias WhatsApp
Extrai todas as informações necessárias para download e descriptografia
Baseado no sistema original wapi/mensagem/baixarmidias/baixarMidias.py
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from django.db import transaction
from django.utils import timezone

from core.models import Cliente, WhatsappInstance, Chat, MediaFile
from core.django_media_manager import DjangoMediaManager

logger = logging.getLogger(__name__)


class WebhookMediaAnalyzer:
    """
    Analisador completo de webhooks para extrair informações de mídia
    Baseado no sistema original baixarMidias.py
    """
    
    def __init__(self):
        self.mimetypes_map = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'video/mp4': '.mp4',
            'video/avi': '.avi',
            'video/mov': '.mov',
            'video/3gpp': '.3gp',
            'video/webm': '.webm',
            'audio/mpeg': '.mp3',
            'audio/ogg': '.ogg',
            'audio/wav': '.wav',
            'audio/mp4': '.m4a',
            'audio/aac': '.aac',
            'audio/ogg; codecs=opus': '.ogg',
            'application/pdf': '.pdf',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'text/plain': '.txt',
            'application/zip': '.zip',
            'application/x-rar-compressed': '.rar'
        }

    def analisar_webhook_completo(self, webhook_data: Dict) -> Dict:
        """
        Analisa webhook completo e extrai todas as informações necessárias
        """
        try:
            logger.info("🔍 Analisando webhook completo...")
            
            # 1. Extrair informações básicas do webhook
            info_basica = self._extrair_info_basica(webhook_data)
            
            # 2. Buscar cliente e instância no banco
            cliente_info = self._buscar_cliente_instancia(webhook_data)
            
            # 3. Extrair informações de mídia detalhadas
            midias_info = self._extrair_midias_detalhadas(webhook_data)
            
            # 4. Processar chat e sender
            chat_info = self._processar_chat_sender(webhook_data)
            
            # 5. Montar resultado completo
            resultado = {
                'webhook_info': info_basica,
                'cliente_info': cliente_info,
                'chat_info': chat_info,
                'midias': midias_info,
                'tem_midias': len(midias_info) > 0,
                'total_midias': len(midias_info)
            }
            
            logger.info(f"✅ Webhook analisado: {len(midias_info)} mídias encontradas")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar webhook: {e}")
            return {}

    def _extrair_info_basica(self, webhook_data: Dict) -> Dict:
        """Extrai informações básicas do webhook"""
        return {
            'event': webhook_data.get('event'),
            'instanceId': webhook_data.get('instanceId'),
            'messageId': webhook_data.get('messageId'),
            'timestamp': webhook_data.get('moment'),
            'isGroup': webhook_data.get('isGroup', False),
            'fromMe': webhook_data.get('fromMe', False),
            'raw_data': webhook_data
        }

    def _buscar_cliente_instancia(self, webhook_data: Dict) -> Dict:
        """Busca cliente e instância no banco baseado no instanceId"""
        try:
            instance_id = webhook_data.get('instanceId')
            if not instance_id:
                return {'erro': 'instanceId não fornecido'}

            # Buscar instância no banco
            instance = WhatsappInstance.objects.select_related('cliente').get(
                instance_id=instance_id
            )
            
            return {
                'cliente_id': instance.cliente.id,
                'cliente_nome': instance.cliente.nome,
                'instance_id': instance.instance_id,
                'instance_token': instance.token,
                'instance_status': instance.status,
                'encontrado': True
            }
            
        except WhatsappInstance.DoesNotExist:
            logger.warning(f"⚠️ Instância não encontrada: {webhook_data.get('instanceId')}")
            return {
                'erro': f'Instância {webhook_data.get("instanceId")} não encontrada',
                'encontrado': False
            }
        except Exception as e:
            logger.error(f"❌ Erro ao buscar cliente/instância: {e}")
            return {'erro': str(e), 'encontrado': False}

    def _processar_chat_sender(self, webhook_data: Dict) -> Dict:
        """Processa informações de chat e sender"""
        try:
            sender = webhook_data.get('sender', {})
            chat = webhook_data.get('chat', {})
            
            return {
                'sender_id': sender.get('id'),
                'sender_name': sender.get('pushName', 'Desconhecido'),
                'chat_id': chat.get('id'),
                'is_group': webhook_data.get('isGroup', False)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar chat/sender: {e}")
            return {}

    def _extrair_midias_detalhadas(self, webhook_data: Dict) -> List[Dict]:
        """
        Extrai informações detalhadas de mídia baseado no sistema original
        """
        midias = []
        msg_content = webhook_data.get('msgContent', {})
        
        # Mapeamento de tipos de mensagem para tipos de mídia
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
                
                # Extrair informações básicas obrigatórias
                info_midia = self._extrair_info_basica_midia(midia_data, tipo_midia)
                
                # Adicionar informações específicas por tipo
                info_midia.update(self._extrair_info_especifica_tipo(midia_data, tipo_midia))
                
                # Validar campos obrigatórios para descriptografia
                campos_validos = self._validar_campos_obrigatorios(info_midia)
                if campos_validos:
                    info_midia['valido_para_download'] = True
                    midias.append(info_midia)
                else:
                    info_midia['valido_para_download'] = False
                    logger.warning(f"⚠️ {tipo_midia} sem dados completos para descriptografia")
                    midias.append(info_midia)

        return midias

    def _extrair_info_basica_midia(self, midia_data: Dict, tipo_midia: str) -> Dict:
        """Extrai informações básicas da mídia"""
        return {
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
            'mediaKeyTimestamp': midia_data.get('mediaKeyTimestamp'),
            'extensao': self.obter_extensao_mimetype(midia_data.get('mimetype', ''))
        }

    def _extrair_info_especifica_tipo(self, midia_data: Dict, tipo_midia: str) -> Dict:
        """Extrai informações específicas por tipo de mídia"""
        info_especifica = {}
        
        if tipo_midia in ['image', 'video']:
            info_especifica.update({
                'width': midia_data.get('width'),
                'height': midia_data.get('height')
            })

        if tipo_midia in ['video', 'audio']:
            info_especifica['seconds'] = midia_data.get('seconds')

        if tipo_midia == 'audio':
            info_especifica.update({
                'ptt': midia_data.get('ptt', False),
                'waveform': midia_data.get('waveform')
            })

        if tipo_midia == 'document':
            info_especifica.update({
                'title': midia_data.get('title'),
                'pageCount': midia_data.get('pageCount')
            })

        if tipo_midia == 'sticker':
            info_especifica.update({
                'isAnimated': midia_data.get('isAnimated', False),
                'isAvatar': midia_data.get('isAvatar', False)
            })

        return info_especifica

    def _validar_campos_obrigatorios(self, info_midia: Dict) -> bool:
        """Valida se tem todos os campos obrigatórios para descriptografia"""
        campos_necessarios = ['mediaKey', 'directPath', 'fileEncSha256', 'fileSha256']
        return all(info_midia.get(campo) for campo in campos_necessarios)

    def obter_extensao_mimetype(self, mimetype: str) -> str:
        """Obtém extensão baseada no mimetype"""
        return self.mimetypes_map.get(mimetype, '.bin')

    def processar_webhook_com_midias(self, webhook_data: Dict) -> Dict:
        """
        Processa webhook completo incluindo download de mídias
        """
        try:
            # 1. Analisar webhook
            analise = self.analisar_webhook_completo(webhook_data)
            
            if not analise.get('cliente_info', {}).get('encontrado'):
                return {
                    'sucesso': False,
                    'erro': 'Cliente/instância não encontrado',
                    'analise': analise
                }

            # 2. Criar gerenciador de mídias
            cliente_info = analise['cliente_info']
            media_manager = DjangoMediaManager(
                cliente_id=cliente_info['cliente_id'],
                instance_id=cliente_info['instance_id'],
                bearer_token=cliente_info['instance_token']
            )

            # 3. Processar cada mídia
            resultados_midias = []
            for midia_info in analise.get('midias', []):
                if midia_info.get('valido_para_download'):
                    resultado = self._processar_midia_individual(
                        media_manager, webhook_data, midia_info
                    )
                    resultados_midias.append(resultado)
                else:
                    resultados_midias.append({
                        'tipo': midia_info['type'],
                        'sucesso': False,
                        'erro': 'Dados insuficientes para download'
                    })

            return {
                'sucesso': True,
                'analise': analise,
                'resultados_midias': resultados_midias,
                'total_processadas': len(resultados_midias)
            }

        except Exception as e:
            logger.error(f"❌ Erro ao processar webhook: {e}")
            return {
                'sucesso': False,
                'erro': str(e)
            }

    def _processar_midia_individual(self, media_manager: DjangoMediaManager, 
                                  webhook_data: Dict, midia_info: Dict) -> Dict:
        """Processa uma mídia individual"""
        try:
            message_id = webhook_data.get('messageId')
            sender_name = webhook_data.get('sender', {}).get('pushName', 'Desconhecido')
            
            # Processar via gerenciador Django
            media_manager.processar_mensagem_whatsapp(webhook_data)
            
            # Verificar se foi salvo no banco
            try:
                media_file = MediaFile.objects.get(
                    message_id=message_id,
                    media_type=midia_info['type']
                )
                
                return {
                    'tipo': midia_info['type'],
                    'sucesso': True,
                    'message_id': message_id,
                    'download_status': media_file.download_status,
                    'file_path': media_file.file_path,
                    'file_size_mb': media_file.file_size_mb
                }
                
            except MediaFile.DoesNotExist:
                return {
                    'tipo': midia_info['type'],
                    'sucesso': False,
                    'erro': 'Mídia não encontrada no banco após processamento'
                }

        except Exception as e:
            logger.error(f"❌ Erro ao processar mídia {midia_info['type']}: {e}")
            return {
                'tipo': midia_info['type'],
                'sucesso': False,
                'erro': str(e)
            }

    def gerar_relatorio_webhook(self, webhook_data: Dict) -> str:
        """Gera relatório detalhado do webhook"""
        try:
            analise = self.analisar_webhook_completo(webhook_data)
            
            relatorio = []
            relatorio.append("📋 RELATÓRIO DE ANÁLISE DE WEBHOOK")
            relatorio.append("=" * 50)
            
            # Informações básicas
            webhook_info = analise.get('webhook_info', {})
            relatorio.append(f"📨 Evento: {webhook_info.get('event')}")
            relatorio.append(f"📱 Instance ID: {webhook_info.get('instanceId')}")
            relatorio.append(f"🆔 Message ID: {webhook_info.get('messageId')}")
            relatorio.append(f"⏰ Timestamp: {webhook_info.get('timestamp')}")
            relatorio.append(f"👥 É Grupo: {webhook_info.get('isGroup')}")
            relatorio.append(f"📤 De Mim: {webhook_info.get('fromMe')}")
            
            # Cliente e Instância
            cliente_info = analise.get('cliente_info', {})
            if cliente_info.get('encontrado'):
                relatorio.append(f"\n👤 Cliente: {cliente_info.get('cliente_nome')}")
                relatorio.append(f"🔑 Token: {cliente_info.get('instance_token', '')[:20]}...")
                relatorio.append(f"📊 Status: {cliente_info.get('instance_status')}")
            else:
                relatorio.append(f"\n❌ Cliente/Instância: {cliente_info.get('erro')}")
            
            # Chat e Sender
            chat_info = analise.get('chat_info', {})
            relatorio.append(f"\n💬 Chat ID: {chat_info.get('chat_id')}")
            relatorio.append(f"👤 Sender: {chat_info.get('sender_name')} ({chat_info.get('sender_id')})")
            
            # Mídias
            midias = analise.get('midias', [])
            relatorio.append(f"\n📎 Mídias Encontradas: {len(midias)}")
            
            for i, midia in enumerate(midias, 1):
                relatorio.append(f"\n  {i}. {midia['type'].upper()}:")
                relatorio.append(f"     📄 Mimetype: {midia.get('mimetype')}")
                relatorio.append(f"     📁 Extensão: {midia.get('extensao')}")
                relatorio.append(f"     📏 Tamanho: {midia.get('fileLength', 'N/A')} bytes")
                relatorio.append(f"     📝 Legenda: {midia.get('caption', 'N/A')}")
                relatorio.append(f"     ✅ Válido para download: {midia.get('valido_para_download')}")
                
                if midia.get('width') and midia.get('height'):
                    relatorio.append(f"     📐 Dimensões: {midia['width']}x{midia['height']}")
                
                if midia.get('seconds'):
                    relatorio.append(f"     ⏱️ Duração: {midia['seconds']} segundos")
                
                if midia.get('ptt'):
                    relatorio.append(f"     🎤 Push to Talk: Sim")
                
                if midia.get('isAnimated'):
                    relatorio.append(f"     🎬 Animado: Sim")
                
                # Campos de descriptografia
                campos_obrigatorios = ['mediaKey', 'directPath', 'fileSha256', 'fileEncSha256']
                relatorio.append(f"     🔐 Campos de descriptografia:")
                for campo in campos_obrigatorios:
                    valor = midia.get(campo, 'N/A')
                    if valor != 'N/A':
                        valor = f"{valor[:20]}..." if len(str(valor)) > 20 else valor
                    relatorio.append(f"        - {campo}: {valor}")
            
            return "\n".join(relatorio)
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            return f"❌ Erro ao gerar relatório: {e}"


# Função de conveniência
def analisar_webhook_whatsapp(webhook_data: Dict) -> Dict:
    """
    Função de conveniência para analisar webhook do WhatsApp
    """
    analyzer = WebhookMediaAnalyzer()
    return analyzer.analisar_webhook_completo(webhook_data)


def processar_webhook_whatsapp(webhook_data: Dict) -> Dict:
    """
    Função de conveniência para processar webhook completo
    """
    analyzer = WebhookMediaAnalyzer()
    return analyzer.processar_webhook_com_midias(webhook_data)


def gerar_relatorio_webhook(webhook_data: Dict) -> str:
    """
    Função de conveniência para gerar relatório
    """
    analyzer = WebhookMediaAnalyzer()
    return analyzer.gerar_relatorio_webhook(webhook_data) 