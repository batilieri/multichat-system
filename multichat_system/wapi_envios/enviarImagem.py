import requests
import json
import base64
import os
import mimetypes
from urllib.parse import urlparse
from typing import Dict, Any, Optional
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnviaImagem:
    """
    Classe para enviar imagens via WhatsApp usando a API W-API.
    
    Esta classe suporta envio de imagens locais e URLs, com validação
    de formatos e tamanhos. Atualizada com as últimas funcionalidades da API W-API.
    
    Formatos suportados: JPG, JPEG, PNG, GIF, WebP, BMP
    Tamanho máximo: 16MB
    """

    def __init__(self, instance_id: str, api_token: str, base_url: str = "https://api.w-api.app/v1/"):
        """
        Inicializa a classe EnviaImagem.

        Args:
            instance_id (str): ID da instância do WhatsApp.
            api_token (str): Token de autenticação da API.
            base_url (str): URL base da API (padrão: https://api.w-api.app/v1/).
        """
        self.instance_id = instance_id
        self.api_token = api_token
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
        
        # Configurações
        self.timeout = 30
        self.max_file_size = 16 * 1024 * 1024  # 16MB
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}

    def enviar(self, phone_number: str, caminho_imagem: str, caption: str = "", delay_message: int = 1) -> Dict[str, Any]:
        """
        Envia imagem via WhatsApp.
        Suporta arquivos locais e URLs.

        Args:
            phone_number (str): Número de telefone do destinatário.
            caminho_imagem (str): Caminho local da imagem ou URL.
            caption (str): Legenda da imagem (opcional).
            delay_message (int): Delay em segundos.

        Returns:
            dict: Resultado da operação com estrutura padronizada.
        """
        # Valida o número de telefone
        if not self._validar_numero(phone_number):
            return {
                "success": False,
                "error": "Número de telefone inválido",
                "details": "O número deve ter pelo menos 10 dígitos"
            }

        # Detecta se é uma URL ou arquivo local
        if self._is_url(caminho_imagem):
            return self._enviar_url(phone_number, caminho_imagem, caption, delay_message)
        else:
            return self._enviar_arquivo_local(phone_number, caminho_imagem, caption, delay_message)

    def enviar_com_compressao(self, phone_number: str, caminho_imagem: str, 
                             caption: str = "", quality: int = 85, delay_message: int = 1) -> Dict[str, Any]:
        """
        Envia imagem com compressão para otimizar o tamanho
        
        Args:
            phone_number (str): Número de telefone do destinatário
            caminho_imagem (str): Caminho da imagem
            caption (str): Legenda da imagem
            quality (int): Qualidade da compressão (1-100)
            delay_message (int): Delay em segundos
            
        Returns:
            dict: Resultado da operação
        """
        try:
            from PIL import Image
            import io
            
            # Abrir e comprimir a imagem
            with Image.open(caminho_imagem) as img:
                # Converter para RGB se necessário
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Salvar em buffer com compressão
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality, optimize=True)
                buffer.seek(0)
                
                # Converter para base64
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                mime_type = 'image/jpeg'
                
                # Preparar payload
                payload = {
                    "phone": phone_number,
                    "image": f"data:{mime_type};base64,{image_base64}",
                    "delayMessage": delay_message
                }

                if caption:
                    payload["caption"] = caption

                return self._fazer_requisicao(payload)
                
        except ImportError:
            logger.warning("PIL não disponível, enviando sem compressão")
            return self.enviar(phone_number, caminho_imagem, caption, delay_message)
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na compressão: {str(e)}"
            }

    def enviar_thumbnail(self, phone_number: str, caminho_imagem: str, 
                        caption: str = "", thumbnail_size: tuple = (100, 100), delay_message: int = 1) -> Dict[str, Any]:
        """
        Envia imagem com thumbnail personalizado
        
        Args:
            phone_number (str): Número de telefone do destinatário
            caminho_imagem (str): Caminho da imagem
            caption (str): Legenda da imagem
            thumbnail_size (tuple): Tamanho do thumbnail (largura, altura)
            delay_message (int): Delay em segundos
            
        Returns:
            dict: Resultado da operação
        """
        try:
            from PIL import Image
            
            # Criar thumbnail
            with Image.open(caminho_imagem) as img:
                img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                
                # Salvar thumbnail temporário
                temp_path = f"temp_thumb_{os.path.basename(caminho_imagem)}"
                img.save(temp_path, "JPEG")
                
                # Enviar thumbnail
                result = self.enviar(phone_number, temp_path, caption, delay_message)
                
                # Limpar arquivo temporário
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                return result
                
        except ImportError:
            logger.warning("PIL não disponível, enviando imagem original")
            return self.enviar(phone_number, caminho_imagem, caption, delay_message)
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao criar thumbnail: {str(e)}"
            }

    def _is_url(self, string: str) -> bool:
        """Verifica se a string é uma URL válida."""
        try:
            result = urlparse(string)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _validar_numero(self, phone_number: str) -> bool:
        """Valida se o número de telefone está no formato correto."""
        numero_limpo = ''.join(filter(str.isdigit, phone_number))

        if len(numero_limpo) < 10:
            return False

        # Para números brasileiros
        if numero_limpo.startswith('55') and len(numero_limpo) >= 12:
            return True

        return len(numero_limpo) >= 10

    def _enviar_arquivo_local(self, phone_number: str, caminho_imagem: str, caption: str, delay_message: int) -> Dict[str, Any]:
        """Processa e envia imagem local."""
        try:
            # Verifica se o arquivo existe
            if not os.path.exists(caminho_imagem):
                return {
                    "success": False,
                    "error": f"Arquivo não encontrado: {caminho_imagem}",
                    "details": "Verifique se o caminho está correto"
                }

            # Verifica se é um arquivo de imagem
            if not self._is_imagem_valida(caminho_imagem):
                return {
                    "success": False,
                    "error": "Arquivo não é uma imagem válida",
                    "details": f"Formatos suportados: {', '.join(self.supported_formats)}"
                }

            # Verifica tamanho do arquivo
            file_size = os.path.getsize(caminho_imagem)
            if file_size > self.max_file_size:
                return {
                    "success": False,
                    "error": "Arquivo muito grande",
                    "details": f"Tamanho máximo: {self.max_file_size // (1024*1024)}MB"
                }

            # Converte para base64
            image_base64 = self._converter_para_base64(caminho_imagem)
            if not image_base64:
                return {
                    "success": False,
                    "error": "Erro ao converter imagem para base64"
                }

            # Prepara payload
            payload = {
                "phone": phone_number,
                "image": image_base64,
                "delayMessage": delay_message
            }

            if caption:
                payload["caption"] = caption

            return self._fazer_requisicao(payload)

        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao processar arquivo local: {str(e)}"
            }

    def _enviar_url(self, phone_number: str, image_url: str, caption: str, delay_message: int) -> Dict[str, Any]:
        """Envia URL diretamente."""
        try:
            payload = {
                "phone": phone_number,
                "image": image_url,
                "delayMessage": delay_message
            }

            if caption:
                payload["caption"] = caption

            return self._fazer_requisicao(payload)

        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao enviar URL: {str(e)}"
            }

    def _is_imagem_valida(self, caminho_imagem: str) -> bool:
        """Verifica se o arquivo é uma imagem válida."""
        extensao = os.path.splitext(caminho_imagem.lower())[1]
        return extensao in self.supported_formats

    def _converter_para_base64(self, caminho_imagem: str) -> Optional[str]:
        """Converte uma imagem local para base64."""
        try:
            mime_type, _ = mimetypes.guess_type(caminho_imagem)
            if not mime_type or not mime_type.startswith('image/'):
                # Default para JPEG se não conseguir detectar
                mime_type = 'image/jpeg'

            with open(caminho_imagem, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            return f"data:{mime_type};base64,{encoded_string}"

        except Exception as e:
            logger.error(f"Erro ao converter imagem para base64: {e}")
            return None

    def _fazer_requisicao(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Faz a requisição HTTP para a API."""
        try:
            url = f"{self.base_url}/message/send-image"
            params = {"instanceId": self.instance_id}

            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                params=params,
                timeout=self.timeout
            )

            try:
                result = response.json()

                if response.status_code == 200:
                    return {
                        "success": True,
                        "data": result,
                        "status_code": response.status_code,
                        "message": "Imagem enviada com sucesso"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Erro HTTP {response.status_code}",
                        "details": result,
                        "status_code": response.status_code
                    }

            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Resposta não é um JSON válido",
                    "response_text": response.text,
                    "status_code": response.status_code
                }

        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Timeout na requisição",
                "details": "A API não respondeu no tempo esperado"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Erro de requisição: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro inesperado: {str(e)}"
            }

    def get_supported_formats(self) -> set:
        """Retorna os formatos de imagem suportados."""
        return self.supported_formats.copy()

    def get_max_file_size(self) -> int:
        """Retorna o tamanho máximo de arquivo em bytes."""
        return self.max_file_size

