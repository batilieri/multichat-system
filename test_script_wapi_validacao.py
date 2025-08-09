#!/usr/bin/env python3
"""
🧪 TESTE DE VALIDAÇÃO - Script W-API vs Sistema Atual
Compara se o problema está na W-API ou nos parâmetros enviados
"""

import requests
import json
import time
import os
import base64
from datetime import datetime
from pathlib import Path

class TestWAPIValidacao:
    def __init__(self):
        self.instance_id = "3B6XIW-ZTS923-GEAY6V"
        self.bearer_token = "Q8EOH07SJkXhg4iT6Qmhz1BJdLl8nL9WF"
        self.base_url = "https://api.w-api.app/v1"
        self.pasta_teste = Path("teste_downloads")
        self.pasta_teste.mkdir(exist_ok=True)
        
    def testar_endpoint_original_script(self, info_midia):
        """Testa usando exatamente como o script original faz"""
        print("\n🧪 TESTE 1: Método do Script Original")
        print("-" * 60)
        
        # Exatamente como no script original
        url = f"{self.base_url}/message/download-media"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.bearer_token}'
        }
        params = {'instanceId': self.instance_id}
        
        payload = {
            'mediaKey': info_midia['mediaKey'],
            'directPath': info_midia['directPath'],
            'type': info_midia['type'],
            'mimetype': info_midia['mimetype']
        }
        
        print(f"URL: {url}")
        print(f"Params: {params}")
        print(f"Headers: {headers}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(url, headers=headers, params=params, json=payload, timeout=30)
            print(f"\n📡 Status: {response.status_code}")
            print(f"📨 Response Headers: {dict(response.headers)}")
            print(f"📄 Response Body: {response.text}")
            
            return response.status_code == 200, response.text
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False, str(e)
    
    def testar_endpoint_sistema_atual(self, info_midia):
        """Testa usando o método do sistema atual corrigido"""
        print("\n🧪 TESTE 2: Método Sistema Atual (Corrigido)")
        print("-" * 60)
        
        # Como o sistema atual faz (corrigido)
        url = f"{self.base_url}/message/download-media?instanceId={self.instance_id}"
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'mediaKey': info_midia['mediaKey'],
            'directPath': info_midia['directPath'],
            'type': info_midia['type'],
            'mimetype': info_midia['mimetype']
        }
        
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            print(f"\n📡 Status: {response.status_code}")
            print(f"📨 Response Headers: {dict(response.headers)}")
            print(f"📄 Response Body: {response.text}")
            
            return response.status_code == 200, response.text
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False, str(e)
    
    def testar_endpoint_alternativo(self, info_midia):
        """Testa endpoint alternativo /media/download"""
        print("\n🧪 TESTE 3: Endpoint Alternativo (/media/download)")
        print("-" * 60)
        
        url = f"{self.base_url}/media/download?instanceId={self.instance_id}"
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'mediaKey': info_midia['mediaKey'],
            'directPath': info_midia['directPath'],
            'type': info_midia['type'],
            'mimetype': info_midia['mimetype']
        }
        
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            print(f"\n📡 Status: {response.status_code}")
            print(f"📨 Response Headers: {dict(response.headers)}")
            print(f"📄 Response Body: {response.text}")
            
            return response.status_code == 200, response.text
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False, str(e)
    
    def testar_endpoint_get(self, info_midia):
        """Testa com método GET"""
        print("\n🧪 TESTE 4: Método GET")
        print("-" * 60)
        
        # Testar com GET em vez de POST
        params = {
            'instanceId': self.instance_id,
            'mediaKey': info_midia['mediaKey'],
            'directPath': info_midia['directPath'],
            'type': info_midia['type'],
            'mimetype': info_midia['mimetype']
        }
        
        url = f"{self.base_url}/message/download-media"
        headers = {
            'Authorization': f'Bearer {self.bearer_token}'
        }
        
        print(f"URL: {url}")
        print(f"Params: {params}")
        print(f"Headers: {headers}")
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            print(f"\n📡 Status: {response.status_code}")
            print(f"📨 Response Headers: {dict(response.headers)}")
            print(f"📄 Response Body: {response.text}")
            
            return response.status_code == 200, response.text
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False, str(e)
    
    def testar_status_instancia(self):
        """Testa se a instância está realmente conectada"""
        print("\n🔍 VERIFICANDO STATUS DA INSTÂNCIA")
        print("-" * 60)
        
        url = f"{self.base_url}/instance/status-instance"
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }
        params = {'instanceId': self.instance_id}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            print(f"📡 Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Conectada: {data.get('connected', 'N/A')}")
                print(f"✅ Status: {data.get('status', 'N/A')}")
                return data.get('connected', False)
            else:
                print(f"❌ Erro no status da instância")
                return False
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def testar_diferentes_parametros(self, info_midia):
        """Testa com diferentes combinações de parâmetros"""
        print("\n🧪 TESTE 5: Diferentes Combinações de Parâmetros")
        print("-" * 60)
        
        # Teste 1: Apenas campos essenciais
        print("\n🔸 Teste 5.1: Apenas campos essenciais")
        payload_minimo = {
            'mediaKey': info_midia['mediaKey'],
            'directPath': info_midia['directPath']
        }
        
        url = f"{self.base_url}/message/download-media?instanceId={self.instance_id}"
        headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload_minimo, timeout=30)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"Erro: {e}")
        
        # Teste 2: Com todos os campos disponíveis
        print("\n🔸 Teste 5.2: Com todos os campos")
        payload_completo = {
            'mediaKey': info_midia['mediaKey'],
            'directPath': info_midia['directPath'],
            'type': info_midia['type'],
            'mimetype': info_midia['mimetype'],
            'fileEncSha256': info_midia.get('fileEncSha256', ''),
            'fileSha256': info_midia.get('fileSha256', ''),
            'fileLength': info_midia.get('fileLength', 0)
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload_completo, timeout=30)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"Erro: {e}")
    
    def executar_teste_completo(self):
        """Executa bateria completa de testes"""
        print("🔍 TESTE COMPLETO DE VALIDAÇÃO W-API")
        print("=" * 80)
        print("Objetivo: Identificar se o problema é na W-API ou nos parâmetros")
        print("=" * 80)
        
        # Verificar status da instância primeiro
        instancia_ok = self.testar_status_instancia()
        
        if not instancia_ok:
            print("\n❌ INSTÂNCIA NÃO CONECTADA - Parando testes")
            return
        
        # Dados de teste reais de webhook
        info_midia_real = {
            'mediaKey': 'O9DM61a9JCpaYl3hkzAGE6yiEDL0R1fmR68SXFJsCU4=',
            'directPath': '/o1/v/t24/f2/m233/AQNKUg_ba9qqNjq8a29zPrI8IwDMynEsYjBJoLdqoGW8cFn2-FxFSlpNs2GfqGzUJbsF8WoyBt8gew',
            'type': 'image',
            'mimetype': 'image/jpeg',
            'fileEncSha256': 'test_enc_sha',
            'fileSha256': 'test_sha',
            'fileLength': '45123'
        }
        
        print(f"\n📋 Dados de teste:")
        print(json.dumps(info_midia_real, indent=2))
        
        # Executar todos os testes
        resultados = []
        
        # Teste 1: Script original
        sucesso1, resp1 = self.testar_endpoint_original_script(info_midia_real)
        resultados.append(("Script Original (params separados)", sucesso1, resp1))
        
        # Teste 2: Sistema atual
        sucesso2, resp2 = self.testar_endpoint_sistema_atual(info_midia_real)
        resultados.append(("Sistema Atual (instanceId na URL)", sucesso2, resp2))
        
        # Teste 3: Endpoint alternativo
        sucesso3, resp3 = self.testar_endpoint_alternativo(info_midia_real)
        resultados.append(("Endpoint Alternativo (/media/download)", sucesso3, resp3))
        
        # Teste 4: Método GET
        sucesso4, resp4 = self.testar_endpoint_get(info_midia_real)
        resultados.append(("Método GET", sucesso4, resp4))
        
        # Teste 5: Diferentes parâmetros
        self.testar_diferentes_parametros(info_midia_real)
        
        # Resumo dos resultados
        print("\n" + "=" * 80)
        print("📊 RESUMO DOS RESULTADOS")
        print("=" * 80)
        
        for i, (nome, sucesso, resposta) in enumerate(resultados, 1):
            status = "✅ SUCESSO" if sucesso else "❌ FALHA"
            print(f"\n{i}. {nome}: {status}")
            if not sucesso:
                # Mostrar apenas o início da resposta de erro
                erro_curto = resposta[:100] + "..." if len(resposta) > 100 else resposta
                print(f"   Erro: {erro_curto}")
        
        # Análise final
        print("\n" + "=" * 80)
        print("🎯 ANÁLISE FINAL")
        print("=" * 80)
        
        sucessos = sum(1 for _, sucesso, _ in resultados if sucesso)
        total = len(resultados)
        
        if sucessos == 0:
            print("❌ TODOS OS TESTES FALHARAM")
            print("   Diagnóstico: Problema definitivamente na W-API")
            print("   Recomendação: Contatar suporte W-API")
        elif sucessos == total:
            print("✅ TODOS OS TESTES FUNCIONARAM")
            print("   Diagnóstico: Sistema estava usando parâmetros incorretos")
            print("   Recomendação: Usar método que funcionou")
        else:
            print(f"⚠️ SUCESSOS PARCIAIS: {sucessos}/{total}")
            print("   Diagnóstico: Alguns métodos funcionam, outros não")
            print("   Recomendação: Usar método que funcionou")
            
            # Identificar qual método funcionou
            for nome, sucesso, _ in resultados:
                if sucesso:
                    print(f"   ✅ Método que funcionou: {nome}")

def main():
    """Função principal"""
    teste = TestWAPIValidacao()
    teste.executar_teste_completo()

if __name__ == "__main__":
    main() 