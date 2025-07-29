import requests
import json
import logging

# Configurar logging
logger = logging.getLogger(__name__)

class EditarMensagem:
    def __init__(self, instance_id, token):
        """
        Inicializa o editor de mensagens

        Args:
            instance_id (str): ID da instância do WhatsApp
            token (str): Token de autorização da API
        """
        self.instance_id = instance_id
        self.token = token
        self.base_url = "https://api.w-api.app/v1/message"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        
        # Validar parâmetros obrigatórios
        if not instance_id:
            raise ValueError("instance_id é obrigatório")
        if not token:
            raise ValueError("token é obrigatório")

    def editar_mensagem(self, phone, message_id, new_text):
        """
        Edita uma mensagem já enviada

        Args:
            phone (str): Número do telefone (formato: 5569999267344)
            message_id (str): ID da mensagem a ser editada
            new_text (str): Novo texto da mensagem

        Returns:
            dict: Resposta da API
        """
        # Validações de entrada
        if not phone:
            return {"erro": "Número do telefone é obrigatório"}
        
        if not message_id:
            return {"erro": "ID da mensagem é obrigatório"}
        
        if not new_text or not new_text.strip():
            return {"erro": "Novo texto é obrigatório"}
        
        # Validar formato do telefone (deve conter apenas números)
        if not phone.isdigit():
            return {"erro": "Número do telefone deve conter apenas números"}
        
        # Validar tamanho do texto (limite do WhatsApp)
        if len(new_text) > 4096:
            return {"erro": "Texto muito longo (máximo 4096 caracteres)"}
        
        # Limpar o texto
        new_text = new_text.strip()
        
        url = f'{self.base_url}/edit-message?instanceId={self.instance_id}'

        data = {
            "phone": phone,
            "text": new_text,
            "messageId": message_id
        }

        logger.info(f'🔄 Editando mensagem: phone={phone}, message_id={message_id}, text_length={len(new_text)}')

        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)
            
            logger.info(f'📡 Resposta da API: status={response.status_code}')
            
            # Log da resposta para debug
            try:
                response_data = response.json()
                logger.info(f'📋 Dados da resposta: {response_data}')
            except:
                logger.warning(f'⚠️ Resposta não é JSON válido: {response.text}')
            
            response.raise_for_status()  # Levanta exceção para códigos de erro HTTP
            
            return response.json()

        except requests.exceptions.Timeout:
            logger.error('⏰ Timeout na requisição para W-API')
            return {"erro": "Timeout na requisição para W-API"}
        except requests.exceptions.ConnectionError:
            logger.error('🔌 Erro de conexão com W-API')
            return {"erro": "Erro de conexão com W-API"}
        except requests.exceptions.RequestException as e:
            logger.error(f'❌ Erro na requisição: {str(e)}')
            return {"erro": f"Erro na requisição: {str(e)}"}
        except json.JSONDecodeError:
            logger.error('📄 Erro ao decodificar resposta JSON')
            return {"erro": "Erro ao decodificar resposta JSON"}
        except Exception as e:
            logger.error(f'💥 Erro inesperado: {str(e)}')
            return {"erro": f"Erro inesperado: {str(e)}"}

    def editar_mensagem_simples(self, phone, message_id, new_text):
        """
        Versão simplificada que retorna apenas sucesso/erro

        Returns:
            bool: True se editou com sucesso, False caso contrário
        """
        resultado = self.editar_mensagem(phone, message_id, new_text)
        return "erro" not in resultado

    def testar_conexao(self):
        """
        Testa a conexão com a W-API
        
        Returns:
            dict: Resultado do teste de conexão
        """
        try:
            # Fazer uma requisição simples para testar a conexão
            test_url = f'{self.base_url}/status?instanceId={self.instance_id}'
            response = requests.get(test_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return {"sucesso": True, "mensagem": "Conexão com W-API OK"}
            else:
                return {"erro": f"Status da W-API: {response.status_code}"}
                
        except Exception as e:
            return {"erro": f"Erro ao testar conexão: {str(e)}"}



