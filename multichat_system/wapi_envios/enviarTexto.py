import requests
import json
import logging
from typing import Dict, Any, Optional

# Configuração de logging para melhor depuração
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnviaTexto:
    """
    Classe para envio de mensagens de texto via WhatsApp usando a API W-API.
    
    Esta classe fornece métodos para enviar mensagens de texto simples e formatadas,
    incluindo suporte a emojis, formatação básica e links.
    
    Atualizado com as últimas funcionalidades da API W-API.
    """

    def __init__(self, instance_id: str, api_token: str, base_url: str = "https://api.w-api.app/v1/"):
        """
        Inicializa a classe WhatsAppAPI para interagir com a API W-API do WhatsApp

        Args:
            instance_id (str): ID da instância do WhatsApp
            api_token (str): Token de autenticação da API
            base_url (str): URL base da API (padrão: https://api.w-api.app/v1/)
        """
        self.instance_id = instance_id
        self.api_token = api_token
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}"
        }

        # Configurações de timeout e retry
        self.timeout = 30
        self.max_retries = 3
        self.retry_delay = 1

    def envia_mensagem_texto(self, phone_number: str, message: str, delay_message: int = 1) -> Dict[str, Any]:
        """
        Envia uma mensagem de texto para um contato via WhatsApp

        Args:
            phone_number (str): Número de telefone do destinatário (com código do país, sem símbolos)
            message (str): Mensagem a ser enviada (suporta emojis e formatação básica)
            delay_message (int, optional): Delay em segundos. Default: 1.

        Returns:
            dict: Resposta da API com estrutura padronizada
        """
        # Validação dos parâmetros
        if not self._validar_parametros(phone_number, message):
            return {
                "success": False,
                "error": "Parâmetros inválidos",
                "details": "Verifique o número de telefone e a mensagem"
            }

        url = f"{self.base_url}/message/send-text"
        params = {"instanceId": self.instance_id}

        payload = {
            "phone": phone_number,
            "message": message,
            "delayMessage": delay_message
        }

        return self._fazer_requisicao(url, payload, params)

    def envia_mensagem_formatada(self, phone_number: str, message: str,
                                 format_type: str = "text", delay_message: int = 1) -> Dict[str, Any]:
        """
        Envia uma mensagem com formatação específica
        
        Args:
            phone_number (str): Número de telefone do destinatário
            message (str): Mensagem a ser enviada
            format_type (str): Tipo de formatação ('text', 'bold', 'italic', 'code')
            delay_message (int): Delay em segundos
            
        Returns:
            dict: Resposta da API
        """
        # Aplicar formatação baseada no tipo
        if format_type == "bold":
            message = f"*{message}*"
        elif format_type == "italic":
            message = f"_{message}_"
        elif format_type == "code":
            message = f"`{message}`"
        elif format_type == "strikethrough":
            message = f"~{message}~"

        return self.envia_mensagem_texto(phone_number, message, delay_message)

    def envia_mensagem_com_link(self, phone_number: str, message: str,
                                link: str, delay_message: int = 1) -> Dict[str, Any]:
        """
        Envia uma mensagem com link incorporado
        
        Args:
            phone_number (str): Número de telefone do destinatário
            message (str): Mensagem a ser enviada
            link (str): Link a ser incluído na mensagem
            delay_message (int): Delay em segundos
            
        Returns:
            dict: Resposta da API
        """
        # Formatar mensagem com link
        formatted_message = f"{message}\n\n{link}"
        return self.envia_mensagem_texto(phone_number, formatted_message, delay_message)

    def _fazer_requisicao(self, url: str, payload: Dict[str, Any],
                          params: Dict[str, str]) -> Dict[str, Any]:
        """
        Faz a requisição HTTP para a API com retry automático
        
        Args:
            url (str): URL da requisição
            payload (dict): Dados da requisição
            params (dict): Parâmetros da URL
            
        Returns:
            dict: Resposta processada
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Enviando mensagem (tentativa {attempt + 1}/{self.max_retries})")

                response = requests.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    params=params,
                    timeout=self.timeout
                )

                # Processar resposta
                return self._processar_resposta(response)

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout na tentativa {attempt + 1}")
                if attempt == self.max_retries - 1:
                    return {
                        "success": False,
                        "error": "Timeout na requisição",
                        "details": "A API não respondeu no tempo esperado"
                    }

            except requests.exceptions.RequestException as e:
                logger.error(f"Erro de requisição na tentativa {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    return {
                        "success": False,
                        "error": f"Erro de requisição: {str(e)}"
                    }

        return {
            "success": False,
            "error": "Número máximo de tentativas excedido"
        }
