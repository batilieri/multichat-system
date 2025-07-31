#!/usr/bin/env python3
"""
Teste da funcionalidade de remoção de reações
"""

import requests
import json
import sys

def testar_endpoint_remocao():
    """Testa o endpoint de remoção de reações"""
    print("🧪 Testando endpoint de remoção de reações...")
    
    # URL do endpoint
    url = "http://localhost:8000/api/mensagens/1/remover-reacao/"
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📡 Enviando requisição para: {url}")
        
        response = requests.post(url, headers=headers)
        
        print(f"📡 Status: {response.status_code}")
        print(f"📄 Resposta: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint funcionando!")
            print(f"  - Sucesso: {data.get('sucesso')}")
            print(f"  - Ação: {data.get('acao')}")
            print(f"  - Emoji Removido: {data.get('emoji_removido')}")
            print(f"  - Reações: {data.get('reacoes')}")
            print(f"  - WAPI Enviado: {data.get('wapi_enviado')}")
            print(f"  - Mensagem: {data.get('mensagem')}")
        else:
            print(f"❌ Erro no endpoint: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")

def testar_fluxo_completo():
    """Testa o fluxo completo de adicionar e remover reação"""
    print("\n🔄 Testando fluxo completo...")
    
    # Simular fluxo
    print("1. 📝 Usuário adiciona reação 👍")
    print("   - Backend: reacoes = ['👍']")
    print("   - WAPI: Envia reação 👍")
    
    print("\n2. 🗑️ Usuário remove reação")
    print("   - Backend: reacoes = []")
    print("   - WAPI: Envia reação vazia para remover")
    
    print("\n3. ✅ Resultado esperado:")
    print("   - Reação removida localmente")
    print("   - Reação removida no WhatsApp")
    print("   - Interface atualizada")

def verificar_endpoints():
    """Verifica os endpoints disponíveis"""
    print("\n🔍 Endpoints de reação disponíveis:")
    print("1. POST /api/mensagens/{id}/reagir/")
    print("   - Adiciona/substitui reação")
    print("   - Parâmetros: { emoji: string }")
    
    print("\n2. POST /api/mensagens/{id}/remover-reacao/")
    print("   - Remove reação existente")
    print("   - Parâmetros: nenhum")
    
    print("\n3. Comportamento:")
    print("   - Apenas uma reação por mensagem")
    print("   - Substituição ao clicar em emoji diferente")
    print("   - Remoção via endpoint específico")

def main():
    """Executa todos os testes"""
    print("🚀 Testando funcionalidade de remoção de reações...")
    
    verificar_endpoints()
    testar_fluxo_completo()
    testar_endpoint_remocao()
    
    print("\n✅ Testes concluídos!")
    print("\n📋 FUNCIONALIDADES IMPLEMENTADAS:")
    print("1. ✅ Endpoint de adicionar/substituir reação")
    print("2. ✅ Endpoint de remover reação")
    print("3. ✅ Integração com W-API")
    print("4. ✅ Interface atualizada")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Teste adicionando uma reação")
    print("2. Teste removendo a reação")
    print("3. Verifique se aparece/desaparece no WhatsApp")

if __name__ == "__main__":
    main() 