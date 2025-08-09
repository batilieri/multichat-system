#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO AUTENTICAÇÃO MULTICLIENTE
Verifica se o problema é tentativa de baixar mídia de um cliente usando credenciais de outro
"""

import os
import sys
import django
import json
import requests

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

from core.models import Cliente, WhatsappInstance
from webhook.models import WebhookEvent

class DiagnosticoAutenticacaoMulticliente:
    def __init__(self):
        self.base_url = "https://api.w-api.app/v1"
        
    def verificar_estrutura_multicliente(self):
        """Verifica a estrutura multicliente atual"""
        print("🔍 VERIFICAÇÃO DA ESTRUTURA MULTICLIENTE")
        print("=" * 80)
        
        # Verificar clientes
        clientes = Cliente.objects.all()
        print(f"📊 Total de clientes: {clientes.count()}")
        
        for cliente in clientes:
            print(f"\n👤 Cliente: {cliente.nome} (ID: {cliente.id})")
            print(f"   WAPI Instance ID (legado): {cliente.wapi_instance_id}")
            print(f"   WAPI Token (legado): {cliente.wapi_token[:20] if cliente.wapi_token else 'None'}...")
            
            # Verificar instâncias do cliente
            instancias = WhatsappInstance.objects.filter(cliente=cliente)
            print(f"   Instâncias WhatsApp: {instancias.count()}")
            
            for instancia in instancias:
                print(f"     - Instance ID: {instancia.instance_id}")
                print(f"       Token: {instancia.token[:20]}...")
                print(f"       Status: {instancia.status}")
                
                # Verificar se há webhooks para esta instância
                webhooks = WebhookEvent.objects.filter(
                    cliente=cliente,
                    instance_id=instancia.instance_id
                ).count()
                print(f"       Webhooks: {webhooks}")
        
        return clientes, WhatsappInstance.objects.all()
    
    def analisar_webhooks_com_midia(self):
        """Analisa webhooks que contêm mídias e suas origens"""
        print("\n🔍 ANÁLISE DE WEBHOOKS COM MÍDIA")
        print("=" * 80)
        
        # Buscar webhooks com mídia
        webhooks_com_midia = []
        
        for webhook in WebhookEvent.objects.all().order_by('-timestamp')[:20]:
            try:
                if isinstance(webhook.raw_data, dict):
                    data = webhook.raw_data
                else:
                    data = json.loads(webhook.raw_data)
                
                msg_content = data.get('msgContent', {})
                tipos_midia = ['audioMessage', 'imageMessage', 'videoMessage', 'documentMessage', 'stickerMessage']
                
                for tipo in tipos_midia:
                    if tipo in msg_content:
                        webhooks_com_midia.append({
                            'webhook': webhook,
                            'tipo_midia': tipo,
                            'instance_id': webhook.instance_id,
                            'cliente': webhook.cliente,
                            'dados_midia': msg_content[tipo]
                        })
                        break
                        
            except Exception as e:
                print(f"❌ Erro ao analisar webhook {webhook.event_id}: {e}")
        
        print(f"📊 Webhooks com mídia encontrados: {len(webhooks_com_midia)}")
        
        return webhooks_com_midia
    
    def verificar_compatibilidade_credenciais(self, webhooks_com_midia):
        """Verifica se as credenciais usadas são compatíveis com a origem da mídia"""
        print("\n🔍 VERIFICAÇÃO DE COMPATIBILIDADE DE CREDENCIAIS")
        print("=" * 80)
        
        problemas_encontrados = []
        
        for item in webhooks_com_midia[:5]:  # Verificar apenas os 5 primeiros
            webhook = item['webhook']
            tipo_midia = item['tipo_midia']
            dados_midia = item['dados_midia']
            
            print(f"\n📡 Webhook {webhook.event_id}")
            print(f"   Tipo: {tipo_midia}")
            print(f"   Instance ID: {webhook.instance_id}")
            print(f"   Cliente: {webhook.cliente.nome}")
            
            # Verificar se existe instância correspondente
            try:
                instancia_correta = WhatsappInstance.objects.get(
                    instance_id=webhook.instance_id,
                    cliente=webhook.cliente
                )
                print(f"   ✅ Instância encontrada no banco")
                print(f"   Token correto: {instancia_correta.token[:20]}...")
                
                # Testar download com credenciais corretas
                resultado = self.testar_download_especifico(
                    webhook.instance_id,
                    instancia_correta.token,
                    dados_midia,
                    tipo_midia
                )
                
                if not resultado:
                    problemas_encontrados.append({
                        'webhook_id': webhook.event_id,
                        'instance_id': webhook.instance_id,
                        'cliente': webhook.cliente.nome,
                        'problema': 'Download falha com credenciais corretas'
                    })
                
            except WhatsappInstance.DoesNotExist:
                print(f"   ❌ Instância NÃO encontrada no banco!")
                problemas_encontrados.append({
                    'webhook_id': webhook.event_id,
                    'instance_id': webhook.instance_id,
                    'cliente': webhook.cliente.nome,
                    'problema': 'Instância não cadastrada no banco'
                })
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                problemas_encontrados.append({
                    'webhook_id': webhook.event_id,
                    'instance_id': webhook.instance_id,
                    'cliente': webhook.cliente.nome,
                    'problema': f'Erro: {str(e)}'
                })
        
        return problemas_encontrados
    
    def testar_download_especifico(self, instance_id, token, dados_midia, tipo_midia):
        """Testa download de mídia específica com credenciais específicas"""
        print(f"     🧪 Testando download de {tipo_midia}...")
        
        # Extrair dados necessários
        media_key = dados_midia.get('mediaKey')
        direct_path = dados_midia.get('directPath')
        mimetype = dados_midia.get('mimetype')
        
        if not all([media_key, direct_path, mimetype]):
            print(f"     ❌ Dados incompletos para download")
            return False
        
        # Preparar requisição
        url = f"{self.base_url}/message/download-media?instanceId={instance_id}"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'mediaKey': media_key,
            'directPath': direct_path,
            'type': tipo_midia.replace('Message', ''),  # audioMessage -> audio
            'mimetype': mimetype
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            
            print(f"     📡 Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"     ✅ Download funcionou!")
                return True
            elif response.status_code == 403:
                print(f"     ❌ Erro 403: Credenciais inválidas ou sem permissão")
                return False
            elif response.status_code == 404:
                print(f"     ❌ Erro 404: Mídia não encontrada ou expirada")
                return False
            elif response.status_code == 500:
                print(f"     ❌ Erro 500: Problema no servidor W-API")
                return False
            else:
                print(f"     ❌ Erro {response.status_code}: {response.text[:100]}")
                return False
                
        except Exception as e:
            print(f"     ❌ Erro na requisição: {e}")
            return False
    
    def testar_autenticacao_cruzada(self, webhooks_com_midia):
        """Testa se usar credenciais de um cliente em mídia de outro causa problema"""
        print("\n🔍 TESTE DE AUTENTICAÇÃO CRUZADA")
        print("=" * 80)
        
        if len(webhooks_com_midia) < 2:
            print("❌ Não há webhooks suficientes para teste cruzado")
            return
        
        # Pegar duas mídias de clientes diferentes (se houver)
        clientes_diferentes = {}
        for item in webhooks_com_midia:
            cliente_id = item['cliente'].id
            if cliente_id not in clientes_diferentes:
                clientes_diferentes[cliente_id] = item
            
            if len(clientes_diferentes) >= 2:
                break
        
        if len(clientes_diferentes) < 2:
            print("ℹ️ Todos os webhooks são do mesmo cliente - não há problema de autenticação cruzada")
            return
        
        items = list(clientes_diferentes.values())
        item1, item2 = items[0], items[1]
        
        print(f"🧪 Testando autenticação cruzada:")
        print(f"   Mídia do Cliente A: {item1['cliente'].nome}")
        print(f"   Credenciais do Cliente B: {item2['cliente'].nome}")
        
        # Tentar baixar mídia do cliente A usando credenciais do cliente B
        try:
            instancia_b = WhatsappInstance.objects.get(
                instance_id=item2['instance_id'],
                cliente=item2['cliente']
            )
            
            resultado = self.testar_download_especifico(
                item2['instance_id'],  # Instance do cliente B
                instancia_b.token,     # Token do cliente B
                item1['dados_midia'],  # Mídia do cliente A
                item1['tipo_midia']
            )
            
            if resultado:
                print("⚠️ PROBLEMA DE SEGURANÇA: Cliente B conseguiu baixar mídia do Cliente A!")
            else:
                print("✅ Segurança OK: Cliente B não consegue baixar mídia do Cliente A")
                
        except Exception as e:
            print(f"❌ Erro no teste cruzado: {e}")
    
    def verificar_sistema_atual(self):
        """Verifica como o sistema atual está fazendo a autenticação"""
        print("\n🔍 VERIFICAÇÃO DO SISTEMA ATUAL")
        print("=" * 80)
        
        print("📋 Fluxo de autenticação no sistema:")
        print("1. Webhook recebido com instanceId")
        print("2. Busca: WhatsappInstance.objects.get(instance_id=instanceId)")
        print("3. Obtém: cliente = instance.cliente")
        print("4. Usa: instance.token para W-API")
        
        # Verificar se há inconsistências
        print(f"\n🔍 Verificando consistência...")
        
        instancias = WhatsappInstance.objects.all()
        for instancia in instancias:
            # Verificar se cliente também tem configuração legada
            cliente = instancia.cliente
            
            print(f"\n📱 Instância: {instancia.instance_id}")
            print(f"   Cliente: {cliente.nome}")
            print(f"   Token instância: {instancia.token[:20]}...")
            print(f"   Token cliente (legado): {cliente.wapi_token[:20] if cliente.wapi_token else 'None'}...")
            
            if cliente.wapi_token and cliente.wapi_token != instancia.token:
                print(f"   ⚠️ INCONSISTÊNCIA: Tokens diferentes entre cliente e instância!")
            elif cliente.wapi_token == instancia.token:
                print(f"   ✅ Tokens consistentes")
            else:
                print(f"   ℹ️ Cliente sem token legado (normal)")
    
    def executar_diagnostico_completo(self):
        """Executa diagnóstico completo de autenticação multicliente"""
        print("🔍 DIAGNÓSTICO COMPLETO - AUTENTICAÇÃO MULTICLIENTE")
        print("=" * 80)
        print("Objetivo: Verificar se problema é autenticação entre clientes")
        print("=" * 80)
        
        # 1. Verificar estrutura
        clientes, instancias = self.verificar_estrutura_multicliente()
        
        # 2. Analisar webhooks com mídia
        webhooks_com_midia = self.analisar_webhooks_com_midia()
        
        if not webhooks_com_midia:
            print("\n❌ Nenhum webhook com mídia encontrado para análise")
            return
        
        # 3. Verificar compatibilidade de credenciais
        problemas = self.verificar_compatibilidade_credenciais(webhooks_com_midia)
        
        # 4. Testar autenticação cruzada
        self.testar_autenticacao_cruzada(webhooks_com_midia)
        
        # 5. Verificar sistema atual
        self.verificar_sistema_atual()
        
        # 6. Relatório final
        self.gerar_relatorio_final(clientes, instancias, webhooks_com_midia, problemas)
    
    def gerar_relatorio_final(self, clientes, instancias, webhooks_com_midia, problemas):
        """Gera relatório final do diagnóstico"""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL - AUTENTICAÇÃO MULTICLIENTE")
        print("=" * 80)
        
        print(f"📊 Estatísticas:")
        print(f"   Clientes: {clientes.count()}")
        print(f"   Instâncias: {instancias.count()}")
        print(f"   Webhooks com mídia: {len(webhooks_com_midia)}")
        print(f"   Problemas encontrados: {len(problemas)}")
        
        if problemas:
            print(f"\n🚨 PROBLEMAS IDENTIFICADOS:")
            for problema in problemas:
                print(f"   ❌ Webhook {problema['webhook_id']}")
                print(f"      Cliente: {problema['cliente']}")
                print(f"      Instance: {problema['instance_id']}")
                print(f"      Problema: {problema['problema']}")
        
        print(f"\n🎯 DIAGNÓSTICO:")
        if len(clientes) == 1:
            print("   ✅ Sistema com apenas 1 cliente - sem risco de autenticação cruzada")
        else:
            print("   ⚠️ Sistema multicliente - verificar se há problemas de autenticação cruzada")
        
        if not problemas:
            print("   ✅ Nenhum problema de autenticação identificado")
            print("   💡 O problema do download não é de autenticação multicliente")
        else:
            print("   ❌ Problemas de autenticação identificados")
            print("   🔧 Corrigir inconsistências antes de investigar W-API")

def main():
    """Função principal"""
    diagnostico = DiagnosticoAutenticacaoMulticliente()
    diagnostico.executar_diagnostico_completo()

if __name__ == "__main__":
    main() 