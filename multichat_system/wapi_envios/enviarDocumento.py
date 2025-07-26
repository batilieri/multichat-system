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


class EnviaDocumento:
    """
    Classe para enviar documentos via WhatsApp usando a API W-API.
    
    Esta classe suporta envio de documentos locais e URLs, com validação
    de formatos e tamanhos. Atualizada com as últimas funcionalidades da API W-API.
    
    Formatos suportados: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, RTF, etc.
    Tamanho máximo: 100MB
    """

    def __init__(self, instance_id: str, api_token: str, base_url: str = "https://api.w-api.app/v1/"):
        """
        Inicializa a classe EnviaDocumento.

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
        self.timeout = 60  # Timeout maior para documentos
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.supported_formats = {
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.txt', '.rtf', '.odt', '.ods', '.odp', '.csv', '.zip', '.rar',
            '.7z', '.tar', '.gz', '.mp3', '.mp4', '.avi', '.mov', '.wmv'
        }

    def enviar(self, phone_number: str, caminho_documento: str, caption: str = "", 
               filename: Optional[str] = None, delay_message: int = 1) -> Dict[str, Any]:
        """
        Envia documento via WhatsApp.
        Suporta arquivos locais e URLs.

        Args:
            phone_number (str): Número de telefone do destinatário.
            caminho_documento (str): Caminho local do documento ou URL.
            caption (str): Legenda do documento (opcional).
            filename (str): Nome personalizado do arquivo (opcional).
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
        if self._is_url(caminho_documento):
            return self._enviar_url(phone_number, caminho_documento, caption, filename, delay_message)
        else:
            return self._enviar_arquivo_local(phone_number, caminho_documento, caption, filename, delay_message)

    def enviar_pdf(self, phone_number: str, caminho_pdf: str, caption: str = "", 
                   delay_message: int = 1) -> Dict[str, Any]:
        """
        Envia especificamente um arquivo PDF
        
        Args:
            phone_number (str): Número de telefone do destinatário
            caminho_pdf (str): Caminho do arquivo PDF
            caption (str): Legenda do documento
            delay_message (int): Delay em segundos
            
        Returns:
            dict: Resultado da operação
        """
        if not caminho_pdf.lower().endswith('.pdf'):
            return {
                "success": False,
                "error": "Arquivo não é um PDF",
                "details": "Use o método enviar() para outros tipos de arquivo"
            }
        
        return self.enviar(phone_number, caminho_pdf, caption, None, delay_message)

    def enviar_planilha(self, phone_number: str, caminho_planilha: str, caption: str = "", 
                       delay_message: int = 1) -> Dict[str, Any]:
        """
        Envia especificamente uma planilha (Excel, CSV, etc.)
        
        Args:
            phone_number (str): Número de telefone do destinatário
            caminho_planilha (str): Caminho da planilha
            caption (str): Legenda do documento
            delay_message (int): Delay em segundos
            
        Returns:
            dict: Resultado da operação
        """
        extensoes_planilha = {'.xls', '.xlsx', '.csv', '.ods'}
        extensao = os.path.splitext(caminho_planilha.lower())[1]
        
        if extensao not in extensoes_planilha:
            return {
                "success": False,
                "error": "Arquivo não é uma planilha válida",
                "details": "Formatos suportados: XLS, XLSX, CSV, ODS"
            }
        
        return self.enviar(phone_number, caminho_planilha, caption, None, delay_message)

    def enviar_apresentacao(self, phone_number: str, caminho_apresentacao: str, caption: str = "", 
                           delay_message: int = 1) -> Dict[str, Any]:
        """
        Envia especificamente uma apresentação (PowerPoint, etc.)
        
        Args:
            phone_number (str): Número de telefone do destinatário
            caminho_apresentacao (str): Caminho da apresentação
            caption (str): Legenda do documento
            delay_message (int): Delay em segundos
            
        Returns:
            dict: Resultado da operação
        """
        extensoes_apresentacao = {'.ppt', '.pptx', '.odp'}
        extensao = os.path.splitext(caminho_apresentacao.lower())[1]
        
        if extensao not in extensoes_apresentacao:
            return {
                "success": False,
                "error": "Arquivo não é uma apresentação válida",
                "details": "Formatos suportados: PPT, PPTX, ODP"
            }
        
        return self.enviar(phone_number, caminho_apresentacao, caption, None, delay_message)

    def enviar_compactado(self, phone_number: str, caminho_arquivo: str, caption: str = "", 
                         delay_message: int = 1) -> Dict[str, Any]:
        """
        Envia especificamente um arquivo compactado
        
        Args:
            phone_number (str): Número de telefone do destinatário
            caminho_arquivo (str): Caminho do arquivo compactado
            caption (str): Legenda do documento
            delay_message (int): Delay em segundos
            
        Returns:
            dict: Resultado da operação
        """
        extensoes_compactado = {'.zip', '.rar', '.7z', '.tar', '.gz'}
        extensao = os.path.splitext(caminho_arquivo.lower())[1]
        
        if extensao not in extensoes_compactado:
            return {
                "success": False,
                "error": "Arquivo não é um arquivo compactado válido",
                "details": "Formatos suportados: ZIP, RAR, 7Z, TAR, GZ"
            }
        
        return self.enviar(phone_number, caminho_arquivo, caption, None, delay_message)

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

    def _enviar_arquivo_local(self, phone_number: str, caminho_documento: str, caption: str, 
                             filename: Optional[str], delay_message: int) -> Dict[str, Any]:
        """Processa e envia documento local."""
        try:
            # Verifica se o arquivo existe
            if not os.path.exists(caminho_documento):
                return {
                    "success": False,
                    "error": f"Arquivo não encontrado: {caminho_documento}",
                    "details": "Verifique se o caminho está correto"
                }

            # Verifica se é um arquivo válido
            if not self._is_documento_valido(caminho_documento):
                return {
                    "success": False,
                    "error": "Arquivo não é um documento válido",
                    "details": f"Formatos suportados: {', '.join(sorted(self.supported_formats))}"
                }

            # Verifica tamanho do arquivo
            file_size = os.path.getsize(caminho_documento)
            if file_size > self.max_file_size:
                return {
                    "success": False,
                    "error": "Arquivo muito grande",
                    "details": f"Tamanho máximo: {self.max_file_size // (1024*1024)}MB"
                }

            # Converte para base64
            documento_base64 = self._converter_para_base64(caminho_documento)
            if not documento_base64:
                return {
                    "success": False,
                    "error": "Erro ao converter documento para base64"
                }

            # Determina o nome do arquivo
            if not filename:
                filename = os.path.basename(caminho_documento)

            # Prepara payload
            payload = {
                "phone": phone_number,
                "document": documento_base64,
                "filename": filename,
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

    def _enviar_url(self, phone_number: str, documento_url: str, caption: str, 
                   filename: Optional[str], delay_message: int) -> Dict[str, Any]:
        """Envia URL diretamente."""
        try:
            payload = {
                "phone": phone_number,
                "document": documento_url,
                "delayMessage": delay_message
            }

            if filename:
                payload["filename"] = filename

            if caption:
                payload["caption"] = caption

            return self._fazer_requisicao(payload)

        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao enviar URL: {str(e)}"
            }

    def _is_documento_valido(self, caminho_documento: str) -> bool:
        """Verifica se o arquivo é um documento válido."""
        extensao = os.path.splitext(caminho_documento.lower())[1]
        return extensao in self.supported_formats

    def _converter_para_base64(self, caminho_documento: str) -> Optional[str]:
        """Converte um documento local para base64."""
        try:
            mime_type, _ = mimetypes.guess_type(caminho_documento)
            if not mime_type:
                # Default para application/octet-stream se não conseguir detectar
                mime_type = 'application/octet-stream'

            with open(caminho_documento, "rb") as documento_file:
                encoded_string = base64.b64encode(documento_file.read()).decode('utf-8')

            return f"data:{mime_type};base64,{encoded_string}"

        except Exception as e:
            logger.error(f"Erro ao converter documento para base64: {e}")
            return None

    def _fazer_requisicao(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Faz a requisição HTTP para a API."""
        try:
            url = f"{self.base_url}/message/send-document"
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
                        "message": "Documento enviado com sucesso"
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
        """Retorna os formatos de documento suportados."""
        return self.supported_formats.copy()

    def get_max_file_size(self) -> int:
        """Retorna o tamanho máximo de arquivo em bytes."""
        return self.max_file_size

    def get_file_info(self, caminho_arquivo: str) -> Dict[str, Any]:
        """
        Obtém informações sobre um arquivo
        
        Args:
            caminho_arquivo (str): Caminho do arquivo
            
        Returns:
            dict: Informações do arquivo
        """
        try:
            if not os.path.exists(caminho_arquivo):
                return {
                    "success": False,
                    "error": "Arquivo não encontrado"
                }
            
            file_size = os.path.getsize(caminho_arquivo)
            file_extension = os.path.splitext(caminho_arquivo.lower())[1]
            mime_type, _ = mimetypes.guess_type(caminho_arquivo)
            
            return {
                "success": True,
                "data": {
                    "filename": os.path.basename(caminho_arquivo),
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                    "extension": file_extension,
                    "mime_type": mime_type or "application/octet-stream",
                    "is_supported": file_extension in self.supported_formats,
                    "is_within_limit": file_size <= self.max_file_size
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao obter informações do arquivo: {str(e)}"
            }


