#!/usr/bin/env python3
"""
Servidor Webhook Local para MultiChat System
Baseado na estrutura do betZap para receber dados do WhatsApp
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from pyngrok import conf, ngrok
import threading
import time

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
import django
django.setup()

from webhook.processors import WhatsAppWebhookProcessor, WebhookValidator
from core.models import Cliente

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuração do servidor
NGROK_TOKEN = "249wILexYz7XZWEYPPd4ECjyzzr_2Q8e91e1G9EYEsEtNxNsa"  # Token do betZap
PORT = 5000


class MultiChatWebhookServer:
    """
    Servidor webhook local para MultiChat
    Baseado na estrutura do betZap
    """
    
    def __init__(self, porta=PORT):
        self.porta = porta
        self.app = Flask(__name__)
        self.requisicoes = []
        self.ngrok_url = None
        self.tunnel = None
        self.configurar_rotas()
        
    def configurar_rotas(self):
        """Configura as rotas do Flask"""
        
        @self.app.route('/webhook', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
        def webhook():
            """Endpoint principal do webhook"""
            dados = {
                'timestamp': datetime.now().isoformat(),
                'method': request.method,
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'headers': dict(request.headers),
                'json': request.get_json(silent=True),
                'data': request.get_data(as_text=True),
                'args': dict(request.args),
                'form': dict(request.form),
                'content_type': request.content_type
            }
            
            self.requisicoes.append(dados)
            self.log_requisicao_completa(dados)
            
            # Processar dados se for POST
            if request.method == 'POST':
                try:
                    resultado = self.processar_webhook(dados)
                    return jsonify(resultado)
                except Exception as e:
                    logger.error(f"Erro ao processar webhook: {e}")
                    return jsonify({
                        'status': 'error',
                        'message': str(e),
                        'timestamp': dados['timestamp']
                    }), 500
            
            return jsonify({
                'status': 'success',
                'message': 'Webhook recebido via Ngrok!',
                'timestamp': dados['timestamp'],
                'total': len(self.requisicoes),
                'ngrok_url': self.ngrok_url
            })
        
        @self.app.route('/webhook/send-message', methods=['POST'])
        def webhook_send_message():
            dados = {
                'timestamp': datetime.now().isoformat(),
                'method': request.method,
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'headers': dict(request.headers),
                'json': request.get_json(silent=True),
                'data': request.get_data(as_text=True),
                'args': dict(request.args),
                'form': dict(request.form),
                'content_type': request.content_type
            }
            self.requisicoes.append(dados)
            self.log_requisicao_completa(dados)
            # Processar apenas mensagens enviadas (fromMe true)
            data = dados['json'] or {}
            if data.get('fromMe') or data.get('data', {}).get('fromMe'):
                try:
                    resultado = self.processar_webhook(dados)
                    return jsonify(resultado)
                except Exception as e:
                    logger.error(f"Erro ao processar webhook send-message: {e}")
                    return jsonify({'status': 'error', 'message': str(e), 'timestamp': dados['timestamp']}), 500
            else:
                return jsonify({'status': 'ignored', 'message': 'Não é mensagem enviada', 'timestamp': dados['timestamp']}), 200

        @self.app.route('/webhook/receive-message', methods=['POST'])
        def webhook_receive_message():
            dados = {
                'timestamp': datetime.now().isoformat(),
                'method': request.method,
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'headers': dict(request.headers),
                'json': request.get_json(silent=True),
                'data': request.get_data(as_text=True),
                'args': dict(request.args),
                'form': dict(request.form),
                'content_type': request.content_type
            }
            self.requisicoes.append(dados)
            self.log_requisicao_completa(dados)
            # Processar apenas mensagens recebidas (fromMe false)
            data = dados['json'] or {}
            if not data.get('fromMe') and not data.get('data', {}).get('fromMe'):
                try:
                    resultado = self.processar_webhook(dados)
                    return jsonify(resultado)
                except Exception as e:
                    logger.error(f"Erro ao processar webhook receive-message: {e}")
                    return jsonify({'status': 'error', 'message': str(e), 'timestamp': dados['timestamp']}), 500
            else:
                return jsonify({'status': 'ignored', 'message': 'Não é mensagem recebida', 'timestamp': dados['timestamp']}), 200

        @self.app.route('/status')
        def status():
            return jsonify({
                'status': 'online',
                'total_requisicoes': len(self.requisicoes),
                'ngrok_url': self.ngrok_url,
                'porta': self.porta,
                'tunnel_ativo': self.tunnel is not None,
                'sistema': 'MultiChat Webhook Server'
            })
        
        @self.app.route('/requisicoes')
        def listar_requisicoes():
            return jsonify({
                'total': len(self.requisicoes),
                'requisicoes': self.requisicoes[-10:]  # Últimas 10
            })
        
        @self.app.route('/limpar', methods=['POST'])
        def limpar():
            count = len(self.requisicoes)
            self.requisicoes.clear()
            return jsonify({
                'message': f'{count} requisições removidas',
                'novo_total': 0
            })
        
        @self.app.route('/test')
        def test_webhook():
            """Endpoint para testar o webhook"""
            return jsonify({
                'status': 'success',
                'message': 'Teste do webhook MultiChat',
                'timestamp': datetime.now().isoformat(),
                'url_webhook': f"{self.ngrok_url}/webhook" if self.ngrok_url else None
            })
        
        # Atualizar HTML da home para exibir as novas rotas
        @self.app.route('/')
        def home():
            return f"""
            <h1>🚀 MultiChat Webhook Funcionando!</h1>
            <p><strong>URL Pública:</strong> <a href=\"{self.ngrok_url}\">{self.ngrok_url}</a></p>
            <p><strong>Total de requisições:</strong> {len(self.requisicoes)}</p>
            <h2>📋 Endpoints Disponíveis:</h2>
            <ul>
                <li><strong>Webhook Principal:</strong> <code>{self.ngrok_url}/webhook</code></li>
                <li><strong>Mensagens Enviadas:</strong> <code>{self.ngrok_url}/webhook/send-message</code></li>
                <li><strong>Mensagens Recebidas:</strong> <code>{self.ngrok_url}/webhook/receive-message</code></li>
                <li><strong>Status:</strong> <a href=\"{self.ngrok_url}/status\">{self.ngrok_url}/status</a></li>
                <li><strong>Requisições:</strong> <a href=\"{self.ngrok_url}/requisicoes\">{self.ngrok_url}/requisicoes</a></li>
                <li><strong>Teste:</strong> <a href=\"{self.ngrok_url}/test\">{self.ngrok_url}/test</a></li>
                <li><strong>Limpar:</strong> <code>POST {self.ngrok_url}/limpar</code></li>
            </ul>
            <h2>🧪 Teste Rápido:</h2>
            <pre>
curl -X POST {self.ngrok_url}/webhook \\
  -H \"Content-Type: application/json\" \\
  -d '{{"mensagem": "teste", "timestamp": "{datetime.now().isoformat()}"}}'
            </pre>
            <h2>📱 Para WhatsApp Business API:</h2>
            <p>Use estas URLs no webhook:</p>
            <ul>
                <li><strong>Principal:</strong> <code>{self.ngrok_url}/webhook</code></li>
                <li><strong>Mensagens Enviadas:</strong> <code>{self.ngrok_url}/webhook/send-message</code></li>
                <li><strong>Mensagens Recebidas:</strong> <code>{self.ngrok_url}/webhook/receive-message</code></li>
            </ul>
            <h2>💾 Banco de Dados:</h2>
            <p>Sistema: <strong>MultiChat</strong></p>
            <p>Dados são salvos automaticamente no banco Django</p>
            """
    
    def log_requisicao_completa(self, dados):
        """Log detalhado da requisição"""
        print(f"\n🔔 NOVA REQUISIÇÃO - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        # Informações básicas
        print(f"📡 Método: {dados['method']}")
        print(f"🌐 IP: {dados['ip']}")
        print(f"📱 User-Agent: {dados['user_agent'][:100]}...")
        
        # Análise do conteúdo
        print(f"📄 ANÁLISE DO CONTEÚDO:")
        
        conteudo_encontrado = False
        
        # JSON direto
        if dados['json']:
            print(f"✅ JSON encontrado:")
            print(json.dumps(dados['json'], indent=2, ensure_ascii=False))
            conteudo_encontrado = True
            
            # Verificar se é WhatsApp
            if self.detectar_whatsapp(dados['json']):
                print("🎯 WhatsApp detectado!")
                self.processar_whatsapp(dados['json'])
        
        # Raw data
        elif dados['data']:
            print(f"📝 Raw data encontrado ({len(dados['data'])} chars):")
            print(f"   Conteúdo: {dados['data'][:500]}...")
            
            # Tentar converter para JSON
            try:
                json_data = json.loads(dados['data'])
                print(f"✅ JSON válido no raw data:")
                print(json.dumps(json_data, indent=2, ensure_ascii=False))
                
                if self.detectar_whatsapp(json_data):
                    print("🎯 WhatsApp detectado!")
                    self.processar_whatsapp(json_data)
                
                conteudo_encontrado = True
            except json.JSONDecodeError:
                print(f"❌ Não é JSON válido")
        
        # Formato de outras APIs (W-API, etc.)
        else:
            print("📋 Verificando outros formatos...")
            data = dados.get('json', {}) or dados.get('data', {})
            
            campos_importantes = {
                'sender': 'Remetente',
                'chat': 'Chat',
                'msgContent': 'Conteúdo',
                'message': 'Mensagem',
                'messageId': 'ID da Mensagem',
                'fromMe': 'De mim',
                'isGroup': 'É grupo',
                'moment': 'Momento'
            }
            
            for campo, nome in campos_importantes.items():
                if campo in data:
                    valor = data[campo]
                    if isinstance(valor, dict):
                        if 'conversation' in valor:
                            valor = valor['conversation']
                        elif 'text' in valor:
                            valor = valor['text']
                    print(f"   {nome}: {valor}")
        
        if not conteudo_encontrado:
            print("⚠️ Nenhum conteúdo encontrado")
        
        print("=" * 60)
    
    def detectar_whatsapp(self, data):
        """Detecta se os dados são do WhatsApp"""
        # Verificar campos específicos do WhatsApp
        whatsapp_fields = [
            'key', 'message', 'messageTimestamp', 'status',
            'sender', 'chat', 'msgContent', 'fromMe'
        ]
        
        # Verificar se contém campos do WhatsApp
        has_whatsapp_fields = any(field in data for field in whatsapp_fields)
        
        # Verificar estrutura específica
        if 'key' in data and 'message' in data:
            return True
            
        if 'sender' in data and 'msgContent' in data:
            return True
            
        if 'messageTimestamp' in data:
            return True
            
        return has_whatsapp_fields
    
    def processar_whatsapp(self, data):
        """Processa dados do WhatsApp"""
        try:
            print("🔄 Processando dados do WhatsApp...")
            
            # Determinar cliente
            cliente = self.determinar_cliente(data)
            if not cliente:
                print("❌ Cliente não encontrado")
                return
            
            print(f"👤 Cliente: {cliente.nome}")
            
            # Processar com o processor
            processor = WhatsAppWebhookProcessor(cliente)
            webhook_event = processor.process_webhook_data(data)
            
            print(f"✅ Webhook processado com sucesso!")
            print(f"   Event ID: {webhook_event.event_id}")
            print(f"   Tipo: {webhook_event.event_type}")
            print(f"   Processado: {webhook_event.processed}")
            
        except Exception as e:
            print(f"❌ Erro ao processar WhatsApp: {e}")
    
    def determinar_cliente(self, data):
        """Determina qual cliente deve receber os dados"""
        # Tentar encontrar por instance_id
        instance_id = data.get('instanceId') or data.get('instance_id')
        if instance_id:
            try:
                cliente = Cliente.objects.get(wapi_instance_id=instance_id)
                return cliente
            except Cliente.DoesNotExist:
                pass
        
        # Tentar encontrar por outros campos
        cliente_id = data.get('cliente_id') or data.get('client_id')
        if cliente_id:
            try:
                cliente = Cliente.objects.get(id=cliente_id)
                return cliente
            except Cliente.DoesNotExist:
                pass
        
        # Se não encontrar, usar o primeiro cliente ativo
        try:
            cliente = Cliente.objects.filter(ativo=True).first()
            return cliente
        except:
            return None
    
    def processar_webhook(self, dados):
        """Processa webhook e salva no banco"""
        try:
            # Obter dados JSON
            data = dados.get('json')
            if not data:
                # Tentar parsear raw data
                try:
                    data = json.loads(dados.get('data', '{}'))
                except json.JSONDecodeError:
                    return {
                        'status': 'error',
                        'message': 'Invalid JSON data',
                        'timestamp': dados['timestamp']
                    }
            
            # Validar dados
            if not WebhookValidator.validate_webhook_data(data):
                return {
                    'status': 'error',
                    'message': 'Invalid webhook data',
                    'timestamp': dados['timestamp']
                }
            
            # Sanitizar dados
            sanitized_data = WebhookValidator.sanitize_data(data)
            
            # Determinar cliente
            cliente = self.determinar_cliente(sanitized_data)
            if not cliente:
                return {
                    'status': 'error',
                    'message': 'Client not found',
                    'timestamp': dados['timestamp']
                }
            
            # Processar webhook
            processor = WhatsAppWebhookProcessor(cliente)
            webhook_event = processor.process_webhook_data(
                sanitized_data,
                ip_address=dados['ip'],
                user_agent=dados['user_agent']
            )
            
            return {
                'status': 'success',
                'message': 'Webhook processed successfully',
                'event_id': str(webhook_event.event_id),
                'cliente': cliente.nome,
                'timestamp': dados['timestamp']
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': dados['timestamp']
            }
    
    def configurar_ngrok(self):
        """Configura o token do ngrok"""
        try:
            print("🔧 Configurando token do ngrok...")
            
            # Configurar token
            conf.get_default().auth_token = NGROK_TOKEN
            
            print("✅ Token configurado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao configurar token: {e}")
            return False
    
    def iniciar_ngrok(self):
        """Inicia o túnel ngrok com HTTPS forçado"""
        try:
            print("🚀 Iniciando túnel ngrok com HTTPS...")
            
            # Configurar ngrok para forçar HTTPS
            ngrok_config = conf.get_default()
            ngrok_config.auth_token = NGROK_TOKEN
            
            # Criar túnel com configuração específica para HTTPS
            self.tunnel = ngrok.connect(
                addr=self.porta,
                bind_tls=True,  # Forçar HTTPS
                domain=None,     # Usar domínio padrão do ngrok
                name=None,       # Nome automático
                proto='https'    # Protocolo HTTPS
            )
            
            # Garantir que a URL seja HTTPS
            self.ngrok_url = self.tunnel.public_url
            if not self.ngrok_url.startswith('https://'):
                self.ngrok_url = self.ngrok_url.replace('http://', 'https://')
            
            print(f"✅ Túnel HTTPS criado: {self.ngrok_url}")
            print(f"🔒 Protocolo: HTTPS")
            print(f"🌐 URL Pública: {self.ngrok_url}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar túnel HTTPS: {e}")
            print("🔄 Tentando configuração alternativa...")
            
            try:
                # Tentativa alternativa com configuração manual
                self.tunnel = ngrok.connect(
                    addr=f"http://localhost:{self.porta}",
                    bind_tls=True
                )
                self.ngrok_url = self.tunnel.public_url
                
                if not self.ngrok_url.startswith('https://'):
                    self.ngrok_url = self.ngrok_url.replace('http://', 'https://')
                
                print(f"✅ Túnel HTTPS criado (alternativo): {self.ngrok_url}")
                return True
                
            except Exception as e2:
                print(f"❌ Erro na configuração alternativa: {e2}")
                return False
    
    def parar_ngrok(self):
        """Para o túnel ngrok"""
        if self.tunnel:
            try:
                ngrok.disconnect(self.tunnel.public_url)
                print("🛑 Túnel ngrok parado")
            except Exception as e:
                print(f"❌ Erro ao parar túnel: {e}")
    
    def iniciar(self):
        """Inicia o servidor"""
        try:
            print("🚀 INICIANDO MULTICHAT WEBHOOK SERVER")
            print("=" * 60)
            
            # Configurar ngrok
            if not self.configurar_ngrok():
                print("⚠️ Continuando sem ngrok...")
            
            # Iniciar túnel
            if not self.iniciar_ngrok():
                print("⚠️ Servidor rodando apenas localmente")
                self.ngrok_url = f"https://localhost:{self.porta}"
            
            print(f"🌐 URL Pública: {self.ngrok_url}")
            print(f"🔧 Porta Local: {self.porta}")
            print("=" * 60)
            print("📱 Aguardando requisições...")
            print("💡 Para testar, acesse: /test")
            print("=" * 60)
            
            # Iniciar servidor Flask
            self.app.run(
                host='0.0.0.0',
                port=self.porta,
                debug=False,
                threaded=True
            )
            
        except KeyboardInterrupt:
            print(f"\n\n👋 Encerrando servidor...")
            self.parar_ngrok()
            print(f"📊 Total de requisições processadas: {len(self.requisicoes)}")
            print(f"✅ Servidor encerrado com sucesso!")


def main():
    """Função principal"""
    print("🚀 MULTICHAT WEBHOOK SERVER")
    print("=" * 60)
    print("✅ Baseado na estrutura do betZap")
    print("✅ Integração com Django MultiChat")
    print("✅ Processamento automático de WhatsApp")
    print("✅ Salvamento no banco de dados")
    print("=" * 60)
    
    # Verificar dependências
    try:
        import flask
        import pyngrok
        print("✅ Dependências OK")
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("💡 Execute: pip install flask pyngrok")
        return 1
    
    # Verificar Django
    try:
        from django.conf import settings
        print("✅ Django configurado")
    except Exception as e:
        print(f"❌ Erro no Django: {e}")
        return 1
    
    # Verificar clientes
    try:
        clientes = Cliente.objects.filter(ativo=True)
        print(f"✅ {clientes.count()} clientes ativos encontrados")
    except Exception as e:
        print(f"⚠️ Erro ao verificar clientes: {e}")
    
    # Iniciar servidor
    servidor = MultiChatWebhookServer()
    servidor.iniciar()


if __name__ == '__main__':
    sys.exit(main()) 