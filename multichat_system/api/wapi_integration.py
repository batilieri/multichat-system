"""
Módulo de integração com a API W-APi do WhatsApp.

Este módulo fornece funcionalidades para:
- Conectar e gerenciar instâncias do WhatsApp
- Verificar status de conexão
- Enviar mensagens de diferentes tipos
- Processar webhooks recebidos
- Gerenciar QR Codes para autenticação

Autor: Sistema MultiChat
Data: 2025-07-11
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from django.conf import settings
from core.models import WhatsappInstance, Cliente
from core.models import Chat as CoreChat, Mensagem as CoreMensagem


logger = logging.getLogger(__name__)


class WApiIntegration:
    """
    Classe principal para integração com a W-APi do WhatsApp.
    
    Esta classe encapsula todas as operações necessárias para interagir
    com a API W-APi, incluindo autenticação, envio de mensagens e
    gerenciamento de instâncias.
    """

    def __init__(self, instance_id: str = None, token: str = None):
        """
        Inicializa a integração com a W-APi.

        Args:
            instance_id (str, opcional): ID da instância do WhatsApp.
            token (str, opcional): Token de autenticação da instância.
        """
        self.base_url = "https://api.w-api.app/v1/"
        self.instance_id = instance_id
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}" if token else ""
        }

    def verificar_status_conexao(self) -> Dict[str, Any]:
        """
        Verifica o status de conexão da instância do WhatsApp.

        Returns:
            Dict[str, Any]: Dicionário contendo o status da conexão e informações adicionais.
                - status (str): 'conectado', 'desconectado', 'qrcode_gerado', 'erro'
                - message (str): Mensagem descritiva do status
                - qr_code (str, opcional): QR Code para conexão (se aplicável)
                - phone_number (str, opcional): Número do telefone conectado
        """
        if not self.instance_id or not self.token:
            return {
                "status": "erro",
                "message": "ID da instância ou token não fornecidos"
            }

        try:
            # Endpoint correto conforme documentação:
            url = f"{self.base_url}instance/status-instance"
            params = {"instanceId": self.instance_id}
            response = requests.get(url, headers=self.headers, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                # Exemplo de resposta esperada:
                # {
                #     "instanceId": "T34398-VYR3QD-MS29SL",
                #     "connected": true
                # }
                if data.get("connected") is True:
                    return {
                        "status": "conectado",
                        "message": "WhatsApp conectado com sucesso",
                        "instance_id": data.get("instanceId"),
                        "connected": True
                    }
                else:
                    return {
                        "status": "desconectado",
                        "message": "WhatsApp desconectado",
                        "instance_id": data.get("instanceId"),
                        "connected": False
                    }
            else:
                logger.error(f"Erro ao verificar status: {response.status_code} - {response.text}")
                return {
                    "status": "erro",
                    "message": f"Erro na API: {response.status_code}",
                    "instance_id": self.instance_id
                }

        except requests.exceptions.Timeout:
            logger.error("Timeout ao verificar status da instância")
            return {
                "status": "erro",
                "message": "Timeout na conexão com a API",
                "instance_id": self.instance_id
            }
        except Exception as e:
            logger.error(f"Erro inesperado ao verificar status: {str(e)}")
            return {
                "status": "erro",
                "message": f"Erro inesperado: {str(e)}",
                "instance_id": self.instance_id
            }

    def gerar_qr_code(self) -> Dict[str, Any]:
        """
        Gera um novo QR Code para conexão do WhatsApp.

        Returns:
            Dict[str, Any]: Dicionário contendo o QR Code e informações de status.
        """
        if not self.instance_id or not self.token:
            return {
                "success": False,
                "message": "ID da instância ou token não fornecidos"
            }

        try:
            # Endpoint correto conforme documentação da WAPI:
            url = f"{self.base_url}instance/qr-code"
            params = {"instanceId": self.instance_id}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "qr_code": data.get("qrcode"),
                    "message": "QR Code gerado com sucesso"
                }
            else:
                return {
                    "success": False,
                    "message": f"Erro ao gerar QR Code: {response.status_code}"
                }

        except Exception as e:
            logger.error(f"Erro ao gerar QR Code: {str(e)}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    def enviar_mensagem_texto(self, numero_destino: str, mensagem: str, delay: int = 1) -> Dict[str, Any]:
        """
        Envia uma mensagem de texto via WhatsApp.

        Args:
            numero_destino (str): Número do destinatário (formato: 5511999999999).
            mensagem (str): Texto da mensagem a ser enviada.
            delay (int, opcional): Delay em segundos antes do envio. Padrão: 1.

        Returns:
            Dict[str, Any]: Resultado do envio da mensagem.
                - success (bool): True se a mensagem foi enviada com sucesso
                - message_id (str, opcional): ID da mensagem enviada
                - message (str): Mensagem de status
        """
        if not self.instance_id or not self.token:
            return {
                "success": False,
                "message": "ID da instância ou token não fornecidos"
            }

        try:
            # Endpoint correto conforme EnviaTexto
            url = f"{self.base_url}message/send-text?instanceId={self.instance_id}"
            payload = {
                "phone": numero_destino,
                "message": mensagem,
                "delayMessage": delay
            }
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message_id": data.get("messageId"),
                    "message": "Mensagem enviada com sucesso",
                    "data": data
                }
            else:
                logger.error(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "message": f"Erro no envio: {response.status_code}",
                    "response_text": response.text
                }
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {str(e)}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    def enviar_imagem(self, numero_destino: str, url_imagem: str, legenda: str = "", delay: int = 1) -> Dict[str, Any]:
        """
        Envia uma imagem via WhatsApp.

        Args:
            numero_destino (str): Número do destinatário.
            url_imagem (str): URL da imagem a ser enviada.
            legenda (str, opcional): Legenda da imagem.
            delay (int, opcional): Delay em segundos antes do envio.

        Returns:
            Dict[str, Any]: Resultado do envio da imagem.
        """
        if not self.instance_id or not self.token:
            return {
                "success": False,
                "message": "ID da instância ou token não fornecidos"
            }

        try:
            url = f"{self.base_url}sendImage"
            
            payload = {
                "instanceId": self.instance_id,
                "phone": numero_destino,
                "image": url_imagem,
                "caption": legenda,
                "delayMessage": delay
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message_id": data.get("messageId"),
                    "message": "Imagem enviada com sucesso"
                }
            else:
                return {
                    "success": False,
                    "message": f"Erro no envio: {response.status_code}"
                }

        except Exception as e:
            logger.error(f"Erro ao enviar imagem: {str(e)}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    def configurar_webhook(self, webhook_url: str) -> Dict[str, Any]:
        """
        Configura a URL do webhook para receber eventos da instância.

        Args:
            webhook_url (str): URL completa do webhook (ex: https://167.86.75.207/webhook).

        Returns:
            Dict[str, Any]: Resultado da configuração do webhook.
        """
        if not self.instance_id or not self.token:
            return {
                "success": False,
                "message": "ID da instância ou token não fornecidos"
            }

        try:
            url = f"{self.base_url}webhook"
            
            payload = {
                "instanceId": self.instance_id,
                "webhookUrl": webhook_url,
                "enabled": True
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Webhook configurado com sucesso"
                }
            else:
                return {
                    "success": False,
                    "message": f"Erro ao configurar webhook: {response.status_code}"
                }

        except Exception as e:
            logger.error(f"Erro ao configurar webhook: {str(e)}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    @staticmethod
    def criar_instancia_para_cliente(cliente_id: int, instance_id: str, token: str) -> Dict[str, Any]:
        """
        Cria uma nova instância do WhatsApp para um cliente específico.

        Args:
            cliente_id (int): ID do cliente no sistema.
            instance_id (str): ID da instância fornecido pela W-APi.
            token (str): Token de autenticação da instância.

        Returns:
            Dict[str, Any]: Resultado da criação da instância.
        """
        try:
            cliente = Cliente.objects.get(id=cliente_id)
            
            # Verificar se já existe uma instância com este ID
            if WhatsappInstance.objects.filter(instance_id=instance_id).exists():
                return {
                    "success": False,
                    "message": "Já existe uma instância com este ID"
                }

            # Criar nova instância
            instancia = WhatsappInstance.objects.create(
                instance_id=instance_id,
                token=token,
                cliente=cliente,
                status="pendente"
            )

            # Atualizar campos do cliente
            cliente.wapi_instance_id = instance_id
            cliente.wapi_token = token
            cliente.save()

            # Verificar status inicial
            wapi = WApiIntegration(instance_id, token)
            status_result = wapi.verificar_status_conexao()
            
            instancia.status = status_result.get("status", "pendente")
            if status_result.get("qr_code"):
                instancia.qr_code = status_result["qr_code"]
            instancia.save()

            return {
                "success": True,
                "message": "Instância criada com sucesso",
                "instance_id": instance_id,
                "status": instancia.status
            }

        except Cliente.DoesNotExist:
            return {
                "success": False,
                "message": "Cliente não encontrado"
            }
        except Exception as e:
            logger.error(f"Erro ao criar instância: {str(e)}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    @staticmethod
    def atualizar_status_instancia(instance_id: str) -> Dict[str, Any]:
        """
        Atualiza o status de uma instância existente.

        Args:
            instance_id (str): ID da instância a ser atualizada.

        Returns:
            Dict[str, Any]: Resultado da atualização.
        """
        try:
            instancia = WhatsappInstance.objects.get(instance_id=instance_id)
            
            wapi = WApiIntegration(instancia.instance_id, instancia.token)
            status_result = wapi.verificar_status_conexao()
            
            instancia.status = status_result.get("status", "erro")
            if status_result.get("qr_code"):
                instancia.qr_code = status_result["qr_code"]
            instancia.save()

            return {
                "success": True,
                "status": instancia.status,
                "message": "Status atualizado com sucesso"
            }

        except WhatsappInstance.DoesNotExist:
            return {
                "success": False,
                "message": "Instância não encontrada"
            }
        except Exception as e:
            logger.error(f"Erro ao atualizar status: {str(e)}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    @staticmethod
    def listar_instancias_cliente(cliente_id: int) -> List[Dict[str, Any]]:
        """
        Lista todas as instâncias de um cliente específico.

        Args:
            cliente_id (int): ID do cliente.

        Returns:
            List[Dict[str, Any]]: Lista de instâncias do cliente.
        """
        try:
            instancias = WhatsappInstance.objects.filter(cliente_id=cliente_id)
            
            resultado = []
            for instancia in instancias:
                resultado.append({
                    "id": instancia.id,
                    "instance_id": instancia.instance_id,
                    "status": instancia.status,
                    "created_at": instancia.created_at.isoformat(),
                    "last_seen": instancia.last_seen.isoformat() if instancia.last_seen else None
                })
            
            return resultado

        except Exception as e:
            logger.error(f"Erro ao listar instâncias: {str(e)}")
            return []


class WebhookProcessor:
    """
    Classe responsável por processar webhooks recebidos da W-APi.
    
    Esta classe analisa os dados recebidos via webhook e os converte
    em registros apropriados no sistema MultiChat.
    """

    @staticmethod
    def processar_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa um webhook recebido da W-APi.

        Args:
            payload (Dict[str, Any]): Dados do webhook recebido.

        Returns:
            Dict[str, Any]: Resultado do processamento.
        """
        try:
            event_type = payload.get("event")
            instance_id = payload.get("instanceId")

            if not event_type or not instance_id:
                return {
                    "success": False,
                    "message": "Dados do webhook incompletos"
                }

            # Verificar se a instância existe no sistema
            try:
                instancia = WhatsappInstance.objects.get(instance_id=instance_id)
            except WhatsappInstance.DoesNotExist:
                logger.warning(f"Webhook recebido para instância não cadastrada: {instance_id}")
                return {
                    "success": False,
                    "message": "Instância não encontrada no sistema"
                }

            # Processar diferentes tipos de eventos
            if event_type == "message":
                return WebhookProcessor._processar_mensagem(payload, instancia)
            elif event_type == "status":
                return WebhookProcessor._processar_status(payload, instancia)
            elif event_type == "connection":
                return WebhookProcessor._processar_conexao(payload, instancia)
            else:
                logger.info(f"Tipo de evento não processado: {event_type}")
                return {
                    "success": True,
                    "message": f"Evento {event_type} recebido mas não processado"
                }

        except Exception as e:
            logger.error(f"Erro ao processar webhook: {str(e)}")
            return {
                "success": False,
                "message": f"Erro no processamento: {str(e)}"
            }

    @staticmethod
    def _processar_mensagem(payload: Dict[str, Any], instancia: WhatsappInstance) -> Dict[str, Any]:
        """
        Processa uma mensagem recebida via webhook.

        Args:
            payload (Dict[str, Any]): Dados da mensagem.
            instancia (WhatsappInstance): Instância do WhatsApp.

        Returns:
            Dict[str, Any]: Resultado do processamento.
        """
        try:
            # Extrair informações da mensagem
            sender = payload.get("sender", {})
            msg_content = payload.get("msgContent", {})
            
            # LÓGICA MELHORADA PARA DETERMINAR from_me
            from_me = False
            
            # Método 1: Verificar campo fromMe no payload raiz
            if payload.get('fromMe') is not None:
                from_me = payload.get('fromMe', False)
            # Método 2: Verificar campo fromMe no key (se existir)
            elif payload.get('key', {}).get('fromMe') is not None:
                from_me = payload.get('key', {}).get('fromMe', False)
            # Método 3: Verificar se o sender_id é o mesmo da instância (usuário atual)
            else:
                sender_id = sender.get('id', '')
                instance_id = payload.get('instanceId', '')
                
                # Se o sender_id contém o instance_id, é uma mensagem enviada pelo usuário
                if sender_id and instance_id and instance_id in sender_id:
                    from_me = True
                # Se o sender_id é o mesmo do chat_id (para chats individuais), pode ser do usuário
                elif sender_id and payload.get('chat', {}).get('id') and sender_id == payload.get('chat', {}).get('id'):
                    from_me = True
            
            logger.info(f"🔍 W-API Determinação from_me: sender_id={sender.get('id', '')}, instance_id={payload.get('instanceId', '')}, from_me={from_me}")
            
            timestamp = payload.get("timestamp")

            # Determinar tipo da mensagem
            tipo_mensagem = "texto"
            conteudo = ""

            if "conversation" in msg_content:
                tipo_mensagem = "texto"
                conteudo = msg_content["conversation"]
            elif "imageMessage" in msg_content:
                tipo_mensagem = "imagem"
                conteudo = msg_content["imageMessage"].get("caption", "Imagem")
            elif "audioMessage" in msg_content:
                tipo_mensagem = "audio"
                conteudo = "Mensagem de áudio"
            elif "videoMessage" in msg_content:
                tipo_mensagem = "video"
                conteudo = msg_content["videoMessage"].get("caption", "Vídeo")
            elif "documentMessage" in msg_content:
                tipo_mensagem = "documento"
                conteudo = msg_content["documentMessage"].get("title", "Documento")
            elif "stickerMessage" in msg_content:
                tipo_mensagem = "sticker"
                conteudo = "Sticker"
            elif "locationMessage" in msg_content:
                tipo_mensagem = "localizacao"
                conteudo = "Localização compartilhada"

            # Buscar ou criar chat corretamente
            chat_id = payload.get('chat', {}).get('id')
            is_group = payload.get('isGroup', False)
            sender = payload.get('sender', {})
            chat_name = None
            if is_group:
                chat_name = payload.get('chat', {}).get('name') or chat_id
            else:
                chat_name = sender.get('pushName') or chat_id

            try:
                chat, created = CoreChat.objects.get_or_create(
                    chat_id=chat_id,
                    cliente=instancia.cliente,
                    defaults={
                        'chat_name': chat_name,
                        'is_group': is_group,
                        'canal': 'whatsapp',
                        'status': 'active',
                        'last_message_at': None,
                    }
                )
                if not created:
                    # Atualiza nome se mudou (ex: grupo renomeado)
                    if chat.chat_name != chat_name:
                        chat.chat_name = chat_name
                        chat.save()
                logger.info(f"Chat {'criado' if created else 'encontrado'}: {chat_id} - {chat_name}")
            except Exception as e:
                logger.error(f"Falha ao criar ou buscar chat: {str(e)}")
                return {
                    "success": False,
                    "message": f"Erro ao criar/buscar chat: {str(e)}"
                }

            # Criar mensagem
            try:
                # Determinar remetente baseado em from_me
                if from_me:
                    remetente = "Elizeu Batiliere"  # Nome do usuário atual
                else:
                    remetente = sender.get("pushName", "") or sender.get("name", "") or chat_id
                
                mensagem = CoreMensagem.objects.create(
                    chat=chat,
                    remetente=remetente,
                    conteudo=conteudo,
                    tipo=tipo_mensagem,
                    lida=False,
                    from_me=from_me  # Adicionar campo from_me
                )
            except Exception as e:
                logger.error(f"Falha ao criar mensagem: {str(e)}")
                return {
                    "success": False,
                    "message": f"Erro ao criar mensagem: {str(e)}"
                }

            # Atualizar última mensagem do chat
            try:
                chat.last_message_at = mensagem.data_envio
                chat.save()
            except Exception as e:
                logger.error(f"Falha ao atualizar last_message_at do chat: {str(e)}")

            return {
                "success": True,
                "message": "Mensagem processada com sucesso",
                "chat_id": chat.id,
                "message_id": mensagem.id
            }

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    @staticmethod
    def _processar_status(payload: Dict[str, Any], instancia: WhatsappInstance) -> Dict[str, Any]:
        """
        Processa um evento de status via webhook.

        Args:
            payload (Dict[str, Any]): Dados do status.
            instancia (WhatsappInstance): Instância do WhatsApp.

        Returns:
            Dict[str, Any]: Resultado do processamento.
        """
        try:
            status = payload.get("status")
            
            if status == "connected":
                instancia.status = "conectado"
                instancia.last_seen = payload.get("timestamp")
            elif status == "disconnected":
                instancia.status = "desconectado"
            
            instancia.save()

            return {
                "success": True,
                "message": f"Status atualizado para: {instancia.status}"
            }

        except Exception as e:
            logger.error(f"Erro ao processar status: {str(e)}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

    @staticmethod
    def _processar_conexao(payload: Dict[str, Any], instancia: WhatsappInstance) -> Dict[str, Any]:
        """
        Processa um evento de conexão via webhook.

        Args:
            payload (Dict[str, Any]): Dados da conexão.
            instancia (WhatsappInstance): Instância do WhatsApp.

        Returns:
            Dict[str, Any]: Resultado do processamento.
        """
        try:
            connection_status = payload.get("connectionStatus")
            
            if connection_status == "open":
                instancia.status = "conectado"
            elif connection_status == "close":
                instancia.status = "desconectado"
            elif connection_status == "qr":
                instancia.status = "qrcode_gerado"
                if payload.get("qrCode"):
                    instancia.qr_code = payload["qrCode"]
            
            instancia.save()

            return {
                "success": True,
                "message": f"Conexão atualizada: {connection_status}"
            }

        except Exception as e:
            logger.error(f"Erro ao processar conexão: {str(e)}")
            return {
                "success": False,
                "message": f"Erro: {str(e)}"
            }

