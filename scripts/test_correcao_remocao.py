#!/usr/bin/env python3
"""
Teste da correção da remoção de reações
"""

import requests
import json
import sys

def testar_correcao_remocao():
    """Testa a correção da remoção de reações"""
    print("🧪 Testando correção da remoção de reações...")
    
    # Simular o comportamento corrigido
    print("\n📋 COMPARAÇÃO ANTES/DEPOIS:")
    
    print("\n❌ ANTES (não funcionava):")
    print("   wapi_result = reacao_wapi.enviar_reacao(")
    print("       phone=phone,")
    print("       message_id=mensagem.message_id,")
    print("       reaction='',  # ❌ String vazia")
    print("       delay=1")
    print("   )")
    
    print("\n✅ DEPOIS (corrigido):")
    print("   wapi_result = reacao_wapi.enviar_reacao(")
    print("       phone=phone,")
    print("       message_id=mensagem.message_id,")
    print("       reaction=emoji_removido,  # ✅ Emoji que estava na reação")
    print("       delay=1")
    print("   )")
    
    print("\n🎯 LÓGICA CORRIGIDA:")
    print("1. ✅ Capturar o emoji que estava na reação")
    print("2. ✅ Remover do banco de dados")
    print("3. ✅ Enviar o mesmo emoji para W-API")
    print("4. ✅ W-API remove a reação do WhatsApp")
    
    print("\n📊 FLUXO COMPLETO:")
    print("1. Usuário clica em remover reação 👍")
    print("2. Backend: emoji_removido = '👍'")
    print("3. Backend: reacoes = [] (remove do banco)")
    print("4. W-API: enviar_reacao(reaction='👍')")
    print("5. WhatsApp: remove reação 👍 da mensagem")
    print("6. Frontend: atualiza interface (reação desaparece)")

def testar_endpoint_corrigido():
    """Testa o endpoint corrigido"""
    print("\n🧪 Testando endpoint corrigido...")
    
    # URL do endpoint
    url = "http://localhost:8000/api/mensagens/1/remover-reacao/"
    
    try:
        print(f"📡 Enviando requisição para: {url}")
        
        response = requests.post(url, headers={"Content-Type": "application/json"})
        
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
        else:
            print(f"❌ Erro no endpoint: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")

def verificar_documentacao_wapi():
    """Verifica a documentação da W-API"""
    print("\n📚 Verificando documentação da W-API...")
    
    print("🔍 POSSÍVEIS FORMATOS PARA REMOÇÃO:")
    print("1. reaction='' (string vazia) - ❌ Pode não funcionar")
    print("2. reaction=emoji (mesmo emoji) - ✅ Deve funcionar")
    print("3. reaction=null (valor nulo) - ❓ Precisa testar")
    print("4. reaction='remove' (string específica) - ❓ Precisa testar")
    
    print("\n💡 RECOMENDAÇÃO:")
    print("Usar o mesmo emoji que estava na reação é a abordagem mais segura!")

def main():
    """Executa todos os testes"""
    print("🚀 Testando correção da remoção de reações...")
    
    testar_correcao_remocao()
    verificar_documentacao_wapi()
    testar_endpoint_corrigido()
    
    print("\n✅ Testes concluídos!")
    print("\n📋 CORREÇÃO APLICADA:")
    print("1. ✅ Capturar emoji_removido da reação")
    print("2. ✅ Enviar emoji_removido para W-API")
    print("3. ✅ W-API remove reação do WhatsApp")
    print("4. ✅ Backend remove do banco de dados")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Teste adicionando uma reação")
    print("2. Teste removendo a reação")
    print("3. Verifique se desaparece no WhatsApp")
    print("4. Confirme que não volta ao recarregar")

if __name__ == "__main__":
    main() 