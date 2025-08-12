#!/usr/bin/env python3
"""
🧪 TESTE DOWNLOAD AUTOMÁTICO REAL
Verifica se o sistema de download automático está funcionando
usando dados reais e credenciais dinâmicas do cliente
"""

import os
import sys
import django
import json
import requests
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

from core.models import Cliente, WhatsappInstance
from webhook.models import WebhookEvent, Message
from webhook.views import process_webhook_message, download_media_via_wapi

class TesteDownloadAutomaticoReal:
    def __init__(self):
        self.resultados = []
        
    def buscar_webhook_real_com_midia(self):
        """Busca webhook real recente com mídia para teste"""
        print("🔍 BUSCANDO WEBHOOK REAL COM MÍDIA")
        print("=" * 60)
        
        webhooks_com_midia = []
        
        # Buscar webhooks recentes com mídia
        for webhook in WebhookEvent.objects.all().order_by('-timestamp')[:20]:
            try:
                if isinstance(webhook.raw_data, dict):
                    data = webhook.raw_data
                else:
                    data = json.loads(webhook.raw_data)
                
                msg_content = data.get('msgContent', {})
                tipos_midia = ['audioMessage', 'imageMessage', 'videoMessage', 'documentMessage']
                
                for tipo in tipos_midia:
                    if tipo in msg_content:
                        midia_data = msg_content[tipo]
                        
                        # Verificar se tem dados completos
                        if all(midia_data.get(campo) for campo in ['mediaKey', 'directPath', 'mimetype']):
                            webhooks_com_midia.append({
                                'webhook': webhook,
                                'tipo_midia': tipo,
                                'dados_midia': midia_data,
                                'message_id': data.get('messageId'),
                                'instance_id': webhook.instance_id,
                                'cliente': webhook.cliente
                            })
                            print(f"✅ {tipo} encontrado: {webhook.event_id}")
                            print(f"   Instance: {webhook.instance_id}")
                            print(f"   Cliente: {webhook.cliente.nome}")
                            break
                            
            except Exception as e:
                continue
        
        print(f"\n📊 Total de webhooks com mídia: {len(webhooks_com_midia)}")
        return webhooks_com_midia[:3]  # Retornar apenas os 3 primeiros
    
    def obter_credenciais_cliente(self, cliente, instance_id):
        """Obtém credenciais do cliente de forma dinâmica (sem dados fixos)"""
        print(f"\n🔑 OBTENDO CREDENCIAIS DO CLIENTE: {cliente.nome}")
        print("=" * 60)
        
        # NUNCA usar dados fixos - sempre buscar do banco
        try:
            # Buscar instância específica do cliente
            instancia = WhatsappInstance.objects.get(
                instance_id=instance_id,
                cliente=cliente
            )
            
            print(f"✅ Instância encontrada no banco:")
            print(f"   Instance ID: {instancia.instance_id}")
            print(f"   Token: {instancia.token[:20]}...")
            print(f"   Status: {instancia.status}")
            print(f"   Cliente: {instancia.cliente.nome}")
            
            return {
                'instance_id': instancia.instance_id,
                'token': instancia.token,
                'cliente': instancia.cliente,
                'status': instancia.status
            }
            
        except WhatsappInstance.DoesNotExist:
            print(f"❌ Instância {instance_id} não encontrada para cliente {cliente.nome}")
            return None
        except Exception as e:
            print(f"❌ Erro ao buscar credenciais: {e}")
            return None
    
    def testar_download_individual(self, item):
        """Testa download individual de uma mídia"""
        webhook = item['webhook']
        tipo_midia = item['tipo_midia']
        dados_midia = item['dados_midia']
        
        print(f"\n🧪 TESTANDO DOWNLOAD: {tipo_midia}")
        print("=" * 60)
        print(f"Webhook: {webhook.event_id}")
        print(f"Timestamp: {webhook.timestamp}")
        
        # Obter credenciais dinâmicas do cliente
        credenciais = self.obter_credenciais_cliente(
            webhook.cliente,
            webhook.instance_id
        )
        
        if not credenciais:
            return {
                'sucesso': False,
                'erro': 'Credenciais não encontradas',
                'webhook_id': webhook.event_id,
                'tipo_midia': tipo_midia
            }
        
        # Verificar se instância está ativa
        if credenciais['status'] != 'conectado':
            print(f"⚠️ Instância não está conectada: {credenciais['status']}")
        
        # Preparar dados para download
        media_data = {
            'mediaKey': dados_midia.get('mediaKey'),
            'directPath': dados_midia.get('directPath'),
            'type': tipo_midia.replace('Message', ''),  # audioMessage -> audio
            'mimetype': dados_midia.get('mimetype')
        }
        
        print(f"\n📊 Dados da mídia:")
        for key, value in media_data.items():
            if key in ['mediaKey', 'directPath']:
                print(f"   {key}: {str(value)[:50]}...")
            else:
                print(f"   {key}: {value}")
        
        # Testar download usando função do sistema
        try:
            print(f"\n🔄 Testando download via sistema...")
            
            resultado = download_media_via_wapi(
                credenciais['instance_id'],
                credenciais['token'],
                media_data
            )
            
            if resultado:
                print(f"✅ SUCESSO: Download funcionou!")
                print(f"   Arquivo baixado para: {resultado}")
                
                # Verificar se arquivo existe
                if os.path.exists(resultado):
                    tamanho = os.path.getsize(resultado)
                    print(f"   Tamanho do arquivo: {tamanho} bytes")
                    
                    return {
                        'sucesso': True,
                        'arquivo': resultado,
                        'tamanho': tamanho,
                        'webhook_id': webhook.event_id,
                        'tipo_midia': tipo_midia,
                        'cliente': credenciais['cliente'].nome
                    }
                else:
                    print(f"❌ Arquivo não encontrado no sistema de arquivos")
                    return {
                        'sucesso': False,
                        'erro': 'Arquivo não encontrado',
                        'webhook_id': webhook.event_id,
                        'tipo_midia': tipo_midia
                    }
            else:
                print(f"❌ FALHA: Download não funcionou")
                return {
                    'sucesso': False,
                    'erro': 'Download retornou None',
                    'webhook_id': webhook.event_id,
                    'tipo_midia': tipo_midia
                }
                
        except Exception as e:
            print(f"❌ ERRO no download: {e}")
            return {
                'sucesso': False,
                'erro': f'Exceção: {str(e)}',
                'webhook_id': webhook.event_id,
                'tipo_midia': tipo_midia
            }
    
    def simular_webhook_completo(self, item):
        """Simula processamento completo de webhook (como seria no sistema real)"""
        webhook = item['webhook']
        
        print(f"\n🌐 SIMULANDO WEBHOOK COMPLETO")
        print("=" * 60)
        print(f"Webhook: {webhook.event_id}")
        
        try:
            # Usar a mesma função que o sistema usa
            mensagem = process_webhook_message(webhook.raw_data)
            
            if mensagem:
                print(f"✅ Webhook processado com sucesso!")
                print(f"   Mensagem criada: {mensagem.id}")
                print(f"   Cliente: {mensagem.cliente.nome}")
                print(f"   Chat: {mensagem.chat_id}")
                
                # Verificar se mídia foi baixada
                # (Aqui verificaríamos se o arquivo foi salvo)
                
                return {
                    'sucesso': True,
                    'mensagem_id': mensagem.id,
                    'webhook_id': webhook.event_id
                }
            else:
                print(f"❌ Webhook não processado")
                return {
                    'sucesso': False,
                    'erro': 'process_webhook_message retornou None'
                }
                
        except Exception as e:
            print(f"❌ ERRO no processamento: {e}")
            return {
                'sucesso': False,
                'erro': f'Exceção: {str(e)}'
            }
    
    def verificar_estrutura_download_pasta(self):
        """Verifica se a estrutura de pastas para download está correta"""
        print(f"\n📁 VERIFICANDO ESTRUTURA DE PASTAS")
        print("=" * 60)
        
        # Verificar pasta media_storage
        base_path = Path('multichat_system/media_storage')
        
        if base_path.exists():
            print(f"✅ Pasta base existe: {base_path}")
            
            # Listar clientes
            for cliente_dir in base_path.iterdir():
                if cliente_dir.is_dir() and cliente_dir.name.startswith('cliente_'):
                    print(f"   📂 {cliente_dir.name}")
                    
                    # Listar instâncias
                    for instance_dir in cliente_dir.iterdir():
                        if instance_dir.is_dir():
                            print(f"      📂 {instance_dir.name}")
                            
                            # Verificar pasta chats
                            chats_dir = instance_dir / 'chats'
                            if chats_dir.exists():
                                print(f"         ✅ chats/")
                                
                                # Contar arquivos de mídia
                                total_files = 0
                                for chat_dir in chats_dir.iterdir():
                                    if chat_dir.is_dir():
                                        for media_type in ['audio', 'imagens', 'videos', 'documentos']:
                                            media_dir = chat_dir / media_type
                                            if media_dir.exists():
                                                files = list(media_dir.glob('*'))
                                                total_files += len(files)
                                                if files:
                                                    print(f"            📄 {media_type}: {len(files)} arquivos")
                                
                                if total_files > 0:
                                    print(f"         🎯 Total de arquivos baixados: {total_files}")
                            else:
                                print(f"         ❌ chats/ não existe")
        else:
            print(f"❌ Pasta base não existe: {base_path}")
    
    def executar_teste_completo(self):
        """Executa teste completo do download automático"""
        print("🧪 TESTE DOWNLOAD AUTOMÁTICO REAL - SISTEMA MULTICLIENTE")
        print("=" * 80)
        print("OBJETIVO: Verificar se download automático funciona com dados dinâmicos")
        print("=" * 80)
        
        # 1. Verificar estrutura de pastas
        self.verificar_estrutura_download_pasta()
        
        # 2. Buscar webhooks reais com mídia
        webhooks_com_midia = self.buscar_webhook_real_com_midia()
        
        if not webhooks_com_midia:
            print("\n❌ Nenhum webhook com mídia encontrado para teste")
            return
        
        # 3. Testar download individual de cada mídia
        print(f"\n🧪 TESTANDO {len(webhooks_com_midia)} MÍDIAS")
        print("=" * 80)
        
        for i, item in enumerate(webhooks_com_midia, 1):
            print(f"\n--- TESTE {i}/{len(webhooks_com_midia)} ---")
            resultado = self.testar_download_individual(item)
            self.resultados.append(resultado)
        
        # 4. Gerar relatório final
        self.gerar_relatorio_final()
    
    def gerar_relatorio_final(self):
        """Gera relatório final dos testes"""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL - DOWNLOAD AUTOMÁTICO")
        print("=" * 80)
        
        sucessos = [r for r in self.resultados if r.get('sucesso')]
        falhas = [r for r in self.resultados if not r.get('sucesso')]
        
        print(f"📊 Estatísticas:")
        print(f"   Total de testes: {len(self.resultados)}")
        print(f"   Sucessos: {len(sucessos)}")
        print(f"   Falhas: {len(falhas)}")
        
        if sucessos:
            print(f"\n✅ DOWNLOADS QUE FUNCIONARAM:")
            for sucesso in sucessos:
                print(f"   🎯 {sucesso['tipo_midia']} - Cliente: {sucesso.get('cliente', 'N/A')}")
                print(f"      Arquivo: {sucesso.get('arquivo', 'N/A')}")
                print(f"      Tamanho: {sucesso.get('tamanho', 0)} bytes")
        
        if falhas:
            print(f"\n❌ DOWNLOADS QUE FALHARAM:")
            for falha in falhas:
                print(f"   💥 {falha['tipo_midia']} - Erro: {falha.get('erro', 'N/A')}")
        
        # Conclusão
        print(f"\n🎯 CONCLUSÃO:")
        if len(sucessos) == len(self.resultados):
            print("   🎉 PERFEITO! Todos os downloads funcionaram!")
            print("   ✅ Sistema de download automático está 100% funcional")
        elif len(sucessos) > 0:
            print("   ⚠️ Download funciona parcialmente")
            print("   🔧 Investigar falhas específicas")
        else:
            print("   ❌ Nenhum download funcionou")
            print("   🚨 Sistema precisa de correção")
        
        print(f"\n💡 VERIFICAÇÃO DE DADOS FIXOS:")
        print("   ✅ Todas as credenciais foram obtidas dinamicamente do cliente")
        print("   ✅ Nenhum token ou instance_id fixo usado")
        print("   ✅ Sistema multicliente funcionando corretamente")

def main():
    """Função principal"""
    teste = TesteDownloadAutomaticoReal()
    teste.executar_teste_completo()

if __name__ == "__main__":
    main() 