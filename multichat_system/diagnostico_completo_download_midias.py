#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO COMPLETO - SISTEMA DE DOWNLOAD AUTOMÁTICO DE MÍDIAS
Análise separada por tarefas conforme solicitado
"""

import os
import sys
import django
import json
import requests
from pathlib import Path
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Cliente, Chat, Mensagem, WhatsappInstance
from webhook.models import WebhookEvent

class DiagnosticoDownloadMidias:
    def __init__(self):
        self.problemas_encontrados = []
        self.successos = []
        
    def adicionar_problema(self, categoria, problema):
        self.problemas_encontrados.append({
            'categoria': categoria,
            'problema': problema,
            'timestamp': datetime.now()
        })
    
    def adicionar_sucesso(self, categoria, sucesso):
        self.successos.append({
            'categoria': categoria,
            'sucesso': sucesso,
            'timestamp': datetime.now()
        })

    # ==================== TAREFA 1: ANÁLISE DO FLUXO ATUAL ====================
    def tarefa_1_analisar_fluxo_atual(self):
        """TAREFA 1: Analisa como está fazendo e porque não funciona"""
        print("🔍 TAREFA 1: ANÁLISE DO FLUXO ATUAL DE DOWNLOAD")
        print("=" * 80)
        
        print("\n📋 1.1 - MAPEANDO FLUXO DE PROCESSAMENTO AUTOMÁTICO")
        print("-" * 60)
        
        # Analisar fluxo no código
        fluxo_atual = [
            "1. Webhook recebido em /webhook/receive/",
            "2. process_webhook_message() chamada",
            "3. WhatsappInstance.objects.get(instance_id=instance_id)",
            "4. process_media_automatically() chamada",
            "5. Detecta tipo de mídia em msgContent",
            "6. Extrai mediaKey, directPath, mimetype",
            "7. download_media_via_wapi() chamada",
            "8. POST para https://api.w-api.app/v1/message/download-media",
            "9. save_media_file() para salvar arquivo"
        ]
        
        for i, step in enumerate(fluxo_atual, 1):
            print(f"   {step}")
        
        print("\n🔍 1.2 - VERIFICANDO PONTOS DE FALHA")
        print("-" * 60)
        
        # Verificar se existe function de download
        try:
            from webhook.views import download_media_via_wapi
            print("✅ Função download_media_via_wapi encontrada")
        except ImportError:
            print("❌ Função download_media_via_wapi NÃO encontrada")
            self.adicionar_problema("CÓDIGO", "Função download_media_via_wapi não está importável")
        
        # Verificar se existe função de processar mídia
        try:
            from webhook.views import process_media_automatically
            print("✅ Função process_media_automatically encontrada")
        except ImportError:
            print("❌ Função process_media_automatically NÃO encontrada")
            self.adicionar_problema("CÓDIGO", "Função process_media_automatically não está importável")
        
        # Verificar endpoint usado
        print(f"\n📡 Endpoint W-API usado: https://api.w-api.app/v1/message/download-media")
        print(f"📄 Método: POST")
        print(f"📋 Parâmetros: instanceId, mediaKey, directPath, type, mimetype")
        
        # Verificar WebhookEvents recentes
        print("\n📊 1.3 - ANALISANDO WEBHOOKS RECENTES")
        print("-" * 60)
        
        webhooks_recentes = WebhookEvent.objects.all().order_by('-timestamp')[:5]
        print(f"Webhooks encontrados: {webhooks_recentes.count()}")
        
        webhooks_com_midia = 0
        for webhook in webhooks_recentes:
            try:
                # raw_data já é um dict, não precisa de json.loads
                data = webhook.raw_data if isinstance(webhook.raw_data, dict) else json.loads(webhook.raw_data)
                msg_content = data.get('msgContent', {})
                tipos_midia = ['audioMessage', 'imageMessage', 'videoMessage', 'documentMessage', 'stickerMessage']
                
                for tipo in tipos_midia:
                    if tipo in msg_content:
                        webhooks_com_midia += 1
                        print(f"✅ Webhook {webhook.event_id}: {tipo} detectado")
                        
                        # Verificar dados essenciais
                        midia_data = msg_content[tipo]
                        tem_media_key = 'mediaKey' in midia_data
                        tem_direct_path = 'directPath' in midia_data
                        tem_mimetype = 'mimetype' in midia_data
                        
                        print(f"   mediaKey: {'✅' if tem_media_key else '❌'}")
                        print(f"   directPath: {'✅' if tem_direct_path else '❌'}")
                        print(f"   mimetype: {'✅' if tem_mimetype else '❌'}")
                        
                        if not (tem_media_key and tem_direct_path and tem_mimetype):
                            self.adicionar_problema("DADOS", f"Webhook {webhook.event_id} com dados incompletos para {tipo}")
                        
                        break
            except Exception as e:
                print(f"❌ Erro ao analisar webhook {webhook.event_id}: {e}")
        
        print(f"\n📊 RESUMO TAREFA 1:")
        print(f"   Webhooks com mídia: {webhooks_com_midia}/{webhooks_recentes.count()}")
        
        if webhooks_com_midia == 0:
            self.adicionar_problema("DADOS", "Nenhum webhook com mídia encontrado nos últimos registros")
        
        return {
            'fluxo_mapeado': True,
            'funcoes_existem': True,
            'webhooks_com_midia': webhooks_com_midia
        }

    # ==================== TAREFA 2: VERIFICAÇÃO DE ENDPOINTS WAPI ====================
    def tarefa_2_verificar_endpoints_wapi(self):
        """TAREFA 2: Verifica se está usando a WAPI com todos os endpoints corretamente"""
        print("\n🌐 TAREFA 2: VERIFICAÇÃO DE ENDPOINTS W-API")
        print("=" * 80)
        
        print("\n📋 2.1 - ENDPOINTS W-API DISPONÍVEIS")
        print("-" * 60)
        
        endpoints_wapi = {
            'status': '/instance/status-instance',
            'qr_code': '/instance/qr-code', 
            'send_text': '/message/send-text',
            'download_media': '/message/download-media',  # USADO NO SISTEMA
            'send_media': '/message/send-media',
            'webhook_status': '/webhook/status'
        }
        
        for nome, endpoint in endpoints_wapi.items():
            usado = "✅ USADO" if nome == 'download_media' else "⚪ Disponível"
            print(f"   {nome}: {endpoint} - {usado}")
        
        print("\n🔍 2.2 - VERIFICANDO ENDPOINT DE DOWNLOAD")
        print("-" * 60)
        
        # Verificar se cliente tem configuração
        cliente = Cliente.objects.first()
        if not cliente:
            print("❌ Nenhum cliente encontrado!")
            self.adicionar_problema("CONFIGURAÇÃO", "Nenhum cliente configurado no sistema")
            return {'endpoints_corretos': False}
        
        print(f"Cliente: {cliente.nome}")
        print(f"WAPI Instance ID: {cliente.wapi_instance_id}")
        print(f"WAPI Token: {cliente.wapi_token[:20] if cliente.wapi_token else 'NENHUM'}...")
        
        if not cliente.wapi_instance_id or not cliente.wapi_token:
            print("❌ Configuração W-API incompleta no cliente!")
            self.adicionar_problema("CONFIGURAÇÃO", f"Cliente {cliente.nome} sem configuração W-API completa")
            return {'endpoints_corretos': False}
        
        # Testar endpoint de status
        print("\n📡 2.3 - TESTANDO CONECTIVIDADE W-API")
        print("-" * 60)
        
        try:
            status_url = f"https://api.w-api.app/v1/instance/status-instance"
            headers = {
                'Authorization': f'Bearer {cliente.wapi_token}',
                'Content-Type': 'application/json'
            }
            params = {'instanceId': cliente.wapi_instance_id}
            
            response = requests.get(status_url, headers=headers, params=params, timeout=15)
            print(f"Status da instância: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Instância conectada: {data.get('connected', 'N/A')}")
                print(f"✅ Status: {data.get('status', 'N/A')}")
                self.adicionar_sucesso("W-API", "Conectividade com W-API funcionando")
            else:
                print(f"❌ Erro de conectividade: {response.text}")
                self.adicionar_problema("W-API", f"Instância não conectada: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro ao conectar com W-API: {e}")
            self.adicionar_problema("W-API", f"Erro de conexão: {str(e)}")
        
        # Testar endpoint de download com dados de teste
        print("\n🧪 2.4 - TESTANDO ENDPOINT DE DOWNLOAD")
        print("-" * 60)
        
        dados_teste = {
            'mediaKey': 'TEST_MEDIA_KEY_123',
            'directPath': '/v/test-path',
            'type': 'audio',
            'mimetype': 'audio/ogg'
        }
        
        try:
            download_url = f"https://api.w-api.app/v1/message/download-media"
            headers = {
                'Authorization': f'Bearer {cliente.wapi_token}',
                'Content-Type': 'application/json'
            }
            params = {'instanceId': cliente.wapi_instance_id}
            
            response = requests.post(download_url, headers=headers, params=params, json=dados_teste, timeout=15)
            print(f"Endpoint de download: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Endpoint de download acessível")
                self.adicionar_sucesso("W-API", "Endpoint de download acessível")
            else:
                print(f"⚠️ Endpoint responde mas com erro: {response.text}")
                # Não é problema crítico, pode ser dados de teste inválidos
                
        except Exception as e:
            print(f"❌ Erro ao testar endpoint de download: {e}")
            self.adicionar_problema("W-API", f"Endpoint de download inacessível: {str(e)}")
        
        return {
            'endpoints_corretos': True,
            'configuracao_cliente': bool(cliente.wapi_instance_id and cliente.wapi_token),
            'conectividade': True
        }

    # ==================== TAREFA 3: VERIFICAÇÃO DE AUTENTICAÇÃO MULTICLIENTE ====================
    def tarefa_3_verificar_autenticacao_multicliente(self):
        """TAREFA 3: Verifica autenticação por cliente, instância e dados multicliente"""
        print("\n👥 TAREFA 3: VERIFICAÇÃO DE AUTENTICAÇÃO MULTICLIENTE")
        print("=" * 80)
        
        print("\n📋 3.1 - ESTRUTURA MULTICLIENTE")
        print("-" * 60)
        
        # Verificar quantos clientes existem
        total_clientes = Cliente.objects.count()
        total_instancias = WhatsappInstance.objects.count()
        
        print(f"Total de clientes: {total_clientes}")
        print(f"Total de instâncias WhatsApp: {total_instancias}")
        
        if total_clientes == 0:
            print("❌ Nenhum cliente configurado!")
            self.adicionar_problema("MULTICLIENTE", "Sistema sem clientes configurados")
            return {'multicliente_ok': False}
        
        # Analisar cada cliente
        print("\n🔍 3.2 - ANÁLISE POR CLIENTE")
        print("-" * 60)
        
        for cliente in Cliente.objects.all():
            print(f"\n👤 Cliente: {cliente.nome} (ID: {cliente.id})")
            
            # Verificar instâncias do cliente
            instancias_cliente = WhatsappInstance.objects.filter(cliente=cliente)
            print(f"   Instâncias: {instancias_cliente.count()}")
            
            for instancia in instancias_cliente:
                print(f"     - {instancia.instance_id} (Status: {instancia.status})")
            
            # Verificar chats do cliente
            chats_cliente = Chat.objects.filter(cliente=cliente).count()
            print(f"   Chats: {chats_cliente}")
            
            # Verificar configuração W-API no cliente (campo legado)
            tem_wapi_legado = bool(cliente.wapi_instance_id and cliente.wapi_token)
            print(f"   W-API legado: {'✅' if tem_wapi_legado else '❌'}")
            
            if tem_wapi_legado:
                print(f"     Instance ID: {cliente.wapi_instance_id}")
                print(f"     Token: {cliente.wapi_token[:20]}...")
            
            # Verificar se há instância dedicada
            if instancias_cliente.exists():
                instancia_ativa = instancias_cliente.filter(status='connected').first()
                if instancia_ativa:
                    print(f"   ✅ Instância ativa: {instancia_ativa.instance_id}")
                    self.adicionar_sucesso("MULTICLIENTE", f"Cliente {cliente.nome} com instância ativa")
                else:
                    print(f"   ⚠️ Nenhuma instância conectada")
                    self.adicionar_problema("MULTICLIENTE", f"Cliente {cliente.nome} sem instância conectada")
            else:
                print(f"   ❌ Nenhuma instância configurada")
                self.adicionar_problema("MULTICLIENTE", f"Cliente {cliente.nome} sem instâncias")
        
        print("\n🔍 3.3 - VERIFICANDO FLUXO DE AUTENTICAÇÃO NO WEBHOOK")
        print("-" * 60)
        
        # Simular processo de autenticação
        print("Fluxo de autenticação no processo automático:")
        print("1. webhook_data.get('instanceId') -> extrai instance_id")
        print("2. WhatsappInstance.objects.get(instance_id=instance_id)")
        print("3. cliente = instance.cliente")
        print("4. Usa instance.token para W-API")
        
        # Verificar se o fluxo funciona
        instancias_teste = WhatsappInstance.objects.all()[:3]
        for instancia in instancias_teste:
            print(f"\n🧪 Testando instância: {instancia.instance_id}")
            print(f"   Cliente: {instancia.cliente.nome}")
            print(f"   Token: {instancia.token[:20] if instancia.token else 'NENHUM'}...")
            
            if not instancia.token:
                self.adicionar_problema("AUTENTICAÇÃO", f"Instância {instancia.instance_id} sem token")
        
        print("\n📁 3.4 - VERIFICANDO ESTRUTURA DE PASTAS POR CLIENTE")
        print("-" * 60)
        
        media_storage_base = Path("media_storage")
        
        for cliente in Cliente.objects.all():
            pasta_cliente = media_storage_base / f"cliente_{cliente.id}"
            print(f"\n📂 Cliente {cliente.nome} (ID: {cliente.id})")
            print(f"   Pasta: {pasta_cliente}")
            print(f"   Existe: {'✅' if pasta_cliente.exists() else '❌'}")
            
            if pasta_cliente.exists():
                # Verificar pastas de instâncias
                for item in pasta_cliente.iterdir():
                    if item.is_dir() and item.name.startswith('instance_'):
                        instance_id = item.name.replace('instance_', '')
                        print(f"     - Instância: {instance_id}")
                        
                        # Verificar subpastas de mídias
                        for subpasta in ['chats', 'audio', 'imagens', 'videos']:
                            sub_path = item / subpasta
                            if sub_path.exists():
                                print(f"       {subpasta}: ✅")
                            else:
                                print(f"       {subpasta}: ❌")
        
        return {
            'multicliente_ok': total_clientes > 0,
            'instancias_configuradas': total_instancias > 0,
            'estrutura_pastas': media_storage_base.exists()
        }

    # ==================== TAREFA 4: COMPARAÇÃO TESTES VS AUTOMÁTICO ====================
    def tarefa_4_comparar_testes_vs_automatico(self):
        """TAREFA 4: Analisa porque testes funcionam mas automático não"""
        print("\n🆚 TAREFA 4: COMPARAÇÃO TESTES FUNCIONAIS VS SISTEMA AUTOMÁTICO")
        print("=" * 80)
        
        print("\n📋 4.1 - ANÁLISE DOS TESTES QUE FUNCIONAM")
        print("-" * 60)
        
        # Verificar arquivos de teste
        arquivos_teste = [
            '../test_audio_real.py',
            '../test_download_automatico.py', 
            '../test_wapi_direct.py',
            '../test_media_endpoint.py'
        ]
        
        testes_encontrados = []
        for arquivo in arquivos_teste:
            if Path(arquivo).exists():
                testes_encontrados.append(arquivo)
                print(f"✅ {arquivo} encontrado")
            else:
                print(f"❌ {arquivo} não encontrado")
        
        if not testes_encontrados:
            print("❌ Nenhum arquivo de teste encontrado!")
            self.adicionar_problema("TESTES", "Arquivos de teste não encontrados")
            return {'comparacao_ok': False}
        
        print("\n🔍 4.2 - DIFERENÇAS IDENTIFICADAS")
        print("-" * 60)
        
        diferencas = [
            {
                'aspecto': 'Dados de Entrada',
                'teste': 'Usa dados hardcoded/controlados',
                'automatico': 'Usa dados do webhook (podem estar incompletos)',
                'impacto': 'CRÍTICO'
            },
            {
                'aspecto': 'Autenticação',
                'teste': 'Usa credenciais diretas (test_wapi_direct.py)',
                'automatico': 'Busca credenciais do banco via instance_id',
                'impacto': 'ALTO'
            },
            {
                'aspecto': 'Endpoint W-API',
                'teste': 'Testa diretamente sem processamento adicional',
                'automatico': 'Passa por múltiplas funções de processamento',
                'impacto': 'MÉDIO'
            },
            {
                'aspecto': 'Tratamento de Erros',
                'teste': 'Exibe erros diretamente no console',
                'automatico': 'Pode mascarar erros em try/catch',
                'impacto': 'ALTO'
            },
            {
                'aspecto': 'Validação de Dados',
                'teste': 'Dados sempre válidos (controlados)',
                'automatico': 'Precisa validar dados recebidos do webhook',
                'impacto': 'CRÍTICO'
            }
        ]
        
        for diff in diferencas:
            print(f"\n🔍 {diff['aspecto']} - IMPACTO: {diff['impacto']}")
            print(f"   Teste: {diff['teste']}")
            print(f"   Automático: {diff['automatico']}")
        
        print("\n🔍 4.3 - ANALISANDO DADOS DE ENTRADA")
        print("-" * 60)
        
        # Comparar dados de teste vs dados reais de webhook
        print("📊 Dados de teste (test_download_automatico.py):")
        dados_teste = {
            "instanceId": "3B6XIW-ZTS923-GEAY6V",
            "msgContent": {
                "audioMessage": {
                    "mediaKey": "TEST_MEDIA_KEY_123",
                    "directPath": "/v/test-path",
                    "mimetype": "audio/ogg",
                    "fileLength": "4478"
                }
            }
        }
        
        for key, value in dados_teste.items():
            print(f"   {key}: {value}")
        
        # Verificar dados reais de webhooks
        print("\n📊 Dados reais de webhooks:")
        webhook_real = WebhookEvent.objects.first()
        if webhook_real:
            try:
                # raw_data já é um dict, não precisa de json.loads
                data = webhook_real.raw_data if isinstance(webhook_real.raw_data, dict) else json.loads(webhook_real.raw_data)
                instance_id = data.get('instanceId', 'N/A')
                msg_content = data.get('msgContent', {})
                
                print(f"   instanceId: {instance_id}")
                
                for tipo_midia in ['audioMessage', 'imageMessage', 'videoMessage']:
                    if tipo_midia in msg_content:
                        midia_data = msg_content[tipo_midia]
                        print(f"   {tipo_midia}:")
                        for key in ['mediaKey', 'directPath', 'mimetype']:
                            valor = midia_data.get(key, 'AUSENTE')
                            status = '✅' if valor != 'AUSENTE' else '❌'
                            print(f"     {key}: {status} {valor[:50] if valor != 'AUSENTE' else ''}")
                        break
                        
            except Exception as e:
                print(f"   ❌ Erro ao analisar webhook real: {e}")
        else:
            print("   ⚠️ Nenhum webhook real encontrado")
        
        print("\n🔍 4.4 - SIMULANDO TESTE AUTOMÁTICO")
        print("-" * 60)
        
        # Simular o processo automático com dados controlados
        cliente = Cliente.objects.first()
        if cliente and cliente.wapi_instance_id and cliente.wapi_token:
            print("🧪 Simulando download automático com dados de teste...")
            
            dados_simulacao = {
                'mediaKey': 'TEST_MEDIA_KEY_123',
                'directPath': '/v/test-path',
                'type': 'audio',
                'mimetype': 'audio/ogg'
            }
            
            try:
                # Simular chamada para W-API (mesmo endpoint que o automático usa)
                url = f"https://api.w-api.app/v1/message/download-media?instanceId={cliente.wapi_instance_id}"
                headers = {
                    'Authorization': f'Bearer {cliente.wapi_token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.post(url, headers=headers, json=dados_simulacao, timeout=15)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✅ Simulação funcionou - problema não é no endpoint")
                    self.adicionar_sucesso("DIAGNÓSTICO", "Endpoint W-API funciona com dados controlados")
                else:
                    print(f"❌ Simulação falhou: {response.text}")
                    self.adicionar_problema("DIAGNÓSTICO", "Endpoint W-API falha mesmo com dados controlados")
                    
            except Exception as e:
                print(f"❌ Erro na simulação: {e}")
                self.adicionar_problema("DIAGNÓSTICO", f"Erro na simulação: {str(e)}")
        
        return {
            'comparacao_ok': True,
            'testes_encontrados': len(testes_encontrados),
            'diferencas_identificadas': len(diferencas)
        }

    # ==================== RELATÓRIO FINAL ====================
    def gerar_relatorio_final(self):
        """Gera relatório final com todos os problemas e soluções"""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL - DIAGNÓSTICO COMPLETO")
        print("=" * 80)
        
        print(f"\n✅ SUCESSOS IDENTIFICADOS: {len(self.successos)}")
        for sucesso in self.successos:
            print(f"   [{sucesso['categoria']}] {sucesso['sucesso']}")
        
        print(f"\n❌ PROBLEMAS IDENTIFICADOS: {len(self.problemas_encontrados)}")
        problemas_por_categoria = {}
        
        for problema in self.problemas_encontrados:
            categoria = problema['categoria']
            if categoria not in problemas_por_categoria:
                problemas_por_categoria[categoria] = []
            problemas_por_categoria[categoria].append(problema['problema'])
        
        for categoria, problemas in problemas_por_categoria.items():
            print(f"\n🚨 {categoria}:")
            for problema in problemas:
                print(f"   - {problema}")
        
        print("\n🎯 PRINCIPAIS CAUSAS IDENTIFICADAS:")
        print("-" * 60)
        
        causas_principais = [
            "1. DADOS INCOMPLETOS: Webhooks podem não ter mediaKey/directPath/mimetype completos",
            "2. AUTENTICAÇÃO: Possível problema na busca de credenciais por instance_id", 
            "3. ENDPOINT: W-API pode estar retornando erro mesmo com configuração correta",
            "4. PROCESSAMENTO: Funções automáticas podem ter bugs não presentes nos testes",
            "5. VALIDAÇÃO: Sistema automático pode estar rejeitando dados válidos"
        ]
        
        for causa in causas_principais:
            print(f"   {causa}")
        
        print("\n🔧 RECOMENDAÇÕES PRIORITÁRIAS:")
        print("-" * 60)
        
        recomendacoes = [
            "1. LOGS DETALHADOS: Adicionar logs em cada etapa do processo automático",
            "2. VALIDAÇÃO DE DADOS: Verificar se webhooks contêm dados completos",
            "3. TESTE ISOLADO: Testar download_media_via_wapi() isoladamente",
            "4. WEBHOOK REAL: Capturar webhook real e testar manualmente",
            "5. COMPARAÇÃO: Executar teste e automático com mesmos dados"
        ]
        
        for rec in recomendacoes:
            print(f"   {rec}")

def main():
    """Função principal - executa todas as tarefas"""
    print("🔍 DIAGNÓSTICO COMPLETO - SISTEMA DE DOWNLOAD AUTOMÁTICO DE MÍDIAS")
    print("=" * 80)
    print("Separação por tarefas conforme solicitado:")
    print("1. Análise do fluxo atual e porque não funciona")
    print("2. Verificação de endpoints W-API")
    print("3. Verificação de autenticação multicliente")
    print("4. Comparação entre testes funcionais e sistema automático")
    print("=" * 80)
    
    diagnostico = DiagnosticoDownloadMidias()
    
    try:
        # Executar todas as tarefas
        resultado_1 = diagnostico.tarefa_1_analisar_fluxo_atual()
        resultado_2 = diagnostico.tarefa_2_verificar_endpoints_wapi()
        resultado_3 = diagnostico.tarefa_3_verificar_autenticacao_multicliente()
        resultado_4 = diagnostico.tarefa_4_comparar_testes_vs_automatico()
        
        # Gerar relatório final
        diagnostico.gerar_relatorio_final()
        
        print("\n" + "=" * 80)
        print("✅ DIAGNÓSTICO COMPLETO FINALIZADO!")
        print("📋 Use as informações acima para corrigir o sistema de download automático")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERRO NO DIAGNÓSTICO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 