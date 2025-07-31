import requests
import json
import base64


class EnviarImagem:
    def __init__(self, instance_id, token):
        """
        Inicializa o enviador de imagens

        Args:
            instance_id (str): ID da instância do WhatsApp
            token (str): Token de autorização da API
        """
        self.instance_id = instance_id
        self.token = token
        self.base_url = "https://api.w-api.app/v1/message/send-image"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def enviar_imagem_url(self, phone, image_url, caption="", message_id=None, delay=0):
        """
        Envia uma imagem via URL

        Args:
            phone (str): Número do telefone ou grupo (formato: 5569999267344)
            image_url (str): URL da imagem
            caption (str): Legenda da imagem (opcional)
            message_id (str): ID da mensagem para responder (opcional)
            delay (int): Atraso opcional em segundos (padrão: 0)

        Returns:
            dict: Resposta da API com status e dados
        """
        params = {
            "instanceId": self.instance_id
        }

        payload = {
            "phone": phone,
            "image": image_url
        }

        # Adicionar parâmetros opcionais
        if caption:
            payload["caption"] = caption
        if message_id:
            payload["messageId"] = message_id
        if delay > 0:
            payload["delayMessage"] = delay

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                params=params,
                data=json.dumps(payload)
            )

            resultado = {
                "sucesso": response.status_code == 200,
                "status_code": response.status_code,
                "dados": response.json() if response.status_code == 200 else None,
                "erro": response.text if response.status_code != 200 else None
            }

            return resultado

        except requests.exceptions.RequestException as e:
            return {
                "sucesso": False,
                "status_code": None,
                "dados": None,
                "erro": f"Erro na requisição: {str(e)}"
            }
        except json.JSONDecodeError:
            return {
                "sucesso": False,
                "status_code": response.status_code,
                "dados": None,
                "erro": "Erro ao decodificar resposta JSON"
            }

    def enviar_imagem_base64(self, phone, image_base64, caption="", message_id=None, delay=0):
        """
        Envia uma imagem via Base64

        Args:
            phone (str): Número do telefone ou grupo (formato: 5569999267344)
            image_base64 (str): Imagem em formato Base64
            caption (str): Legenda da imagem (opcional)
            message_id (str): ID da mensagem para responder (opcional)
            delay (int): Atraso opcional em segundos (padrão: 0)

        Returns:
            dict: Resposta da API com status e dados
        """
        params = {
            "instanceId": self.instance_id
        }

        payload = {
            "phone": phone,
            "image": image_base64
        }

        # Adicionar parâmetros opcionais
        if caption:
            payload["caption"] = caption
        if message_id:
            payload["messageId"] = message_id
        if delay > 0:
            payload["delayMessage"] = delay

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                params=params,
                data=json.dumps(payload)
            )

            resultado = {
                "sucesso": response.status_code == 200,
                "status_code": response.status_code,
                "dados": response.json() if response.status_code == 200 else None,
                "erro": response.text if response.status_code != 200 else None
            }

            return resultado

        except requests.exceptions.RequestException as e:
            return {
                "sucesso": False,
                "status_code": None,
                "dados": None,
                "erro": f"Erro na requisição: {str(e)}"
            }
        except json.JSONDecodeError:
            return {
                "sucesso": False,
                "status_code": response.status_code,
                "dados": None,
                "erro": "Erro ao decodificar resposta JSON"
            }

    def enviar_imagem_arquivo(self, phone, file_path, caption="", message_id=None, delay=0):
        """
        Envia uma imagem a partir de um arquivo local

        Args:
            phone (str): Número do telefone ou grupo (formato: 5569999267344)
            file_path (str): Caminho para o arquivo de imagem
            caption (str): Legenda da imagem (opcional)
            message_id (str): ID da mensagem para responder (opcional)
            delay (int): Atraso opcional em segundos (padrão: 0)

        Returns:
            dict: Resposta da API com status e dados
        """
        try:
            # Ler arquivo e converter para Base64
            with open(file_path, "rb") as image_file:
                image_data = image_file.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            return self.enviar_imagem_base64(phone, image_base64, caption, message_id, delay)
            
        except FileNotFoundError:
            return {
                "sucesso": False,
                "status_code": None,
                "dados": None,
                "erro": f"Arquivo não encontrado: {file_path}"
            }
        except Exception as e:
            return {
                "sucesso": False,
                "status_code": None,
                "dados": None,
                "erro": f"Erro ao ler arquivo: {str(e)}"
            }

    def enviar_imagem_simples(self, phone, image_data, caption="", message_id=None, delay=0):
        """
        Versão simplificada que detecta automaticamente se é URL ou Base64

        Args:
            phone (str): Número do telefone ou grupo
            image_data (str): URL da imagem ou Base64
            caption (str): Legenda da imagem (opcional)
            message_id (str): ID da mensagem para responder (opcional)
            delay (int): Atraso opcional em segundos (padrão: 0)

        Returns:
            dict: Resposta da API com status e dados
        """
        # Detectar se é URL ou Base64
        if image_data.startswith(('http://', 'https://')):
            return self.enviar_imagem_url(phone, image_data, caption, message_id, delay)
        else:
            return self.enviar_imagem_base64(phone, image_data, caption, message_id, delay)

    def formatos_suportados(self):
        """
        Retorna os formatos de imagem suportados

        Returns:
            list: Lista de formatos suportados
        """
        return ["PNG", "JPEG", "JPG"]

    def tamanho_maximo(self):
        """
        Retorna o tamanho máximo suportado para imagens

        Returns:
            str: Tamanho máximo em MB
        """
        return "16 MB"

