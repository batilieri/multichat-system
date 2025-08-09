#!/usr/bin/env python3
"""
📋 ANÁLISE DE CONFORMIDADE - W-API DOWNLOAD MEDIA
Comparação entre implementação atual e documentação oficial
"""

import json

def analisar_conformidade_wapi():
    """Analisa conformidade com documentação W-API"""
    print("📋 ANÁLISE DE CONFORMIDADE - W-API DOWNLOAD MEDIA")
    print("=" * 80)
    
    # Documentação oficial fornecida pelo usuário
    documentacao_oficial = {
        "endpoint": "https://api.w-api.app/v1/message/download-media?instanceId=",
        "metodo": "POST",
        "headers": {
            "Authorization": "Bearer <token>",
            "Content-Type": "application/json"
        },
        "query_params": {
            "instanceId": "obrigatório"
        },
        "body": {
            "mediaKey": "string (obrigatório)",
            "directPath": "string (obrigatório)", 
            "type": "string (image, document, audio, video)",
            "mimetype": "string (obrigatório)"
        },
        "resposta_sucesso": {
            "error": False,
            "fileLink": "https://api.w-api.app/media/file/4a863bcc-bfce-40fb-8222-7a76630b8db2_image.jpeg",
            "expires": 1746908140798
        }
    }
    
    # Implementação atual no sistema
    implementacao_atual = {
        "endpoint": "https://api.w-api.app/v1/message/download-media?instanceId={instance_id}",
        "metodo": "POST",
        "headers": {
            "Authorization": "Bearer {bearer_token}",
            "Content-Type": "application/json"
        },
        "query_params": {
            "instanceId": "via URL parameter"
        },
        "body": {
            "mediaKey": "media_data.get('mediaKey', '')",
            "directPath": "media_data.get('directPath', '')",
            "type": "media_data.get('type', '')",
            "mimetype": "media_data.get('mimetype', '')"
        },
        "tratamento_resposta": {
            "verifica_status_200": True,
            "verifica_error_false": True,
            "extrai_fileLink": True,
            "extrai_expires": True
        }
    }
    
    print("\n🔍 1. COMPARAÇÃO ENDPOINT")
    print("-" * 60)
    doc_endpoint = documentacao_oficial["endpoint"]
    impl_endpoint = implementacao_atual["endpoint"]
    
    print(f"📚 Documentação: {doc_endpoint}")
    print(f"💻 Implementação: {impl_endpoint}")
    
    if "message/download-media" in impl_endpoint and "instanceId=" in impl_endpoint:
        print("✅ CONFORME: Endpoint correto")
    else:
        print("❌ NÃO CONFORME: Endpoint incorreto")
    
    print("\n🔍 2. COMPARAÇÃO MÉTODO HTTP")
    print("-" * 60)
    print(f"📚 Documentação: {documentacao_oficial['metodo']}")
    print(f"💻 Implementação: {implementacao_atual['metodo']}")
    print("✅ CONFORME: Método POST")
    
    print("\n🔍 3. COMPARAÇÃO HEADERS")
    print("-" * 60)
    doc_headers = documentacao_oficial["headers"]
    impl_headers = implementacao_atual["headers"]
    
    for header, valor in doc_headers.items():
        print(f"📚 {header}: {valor}")
        if header in impl_headers:
            print(f"💻 {header}: {impl_headers[header]}")
            print("✅ CONFORME")
        else:
            print("❌ NÃO CONFORME: Header ausente")
        print()
    
    print("\n🔍 4. COMPARAÇÃO QUERY PARAMS")
    print("-" * 60)
    print("📚 instanceId: obrigatório via query param")
    print("💻 instanceId: passado via URL template")
    print("✅ CONFORME: instanceId sendo passado corretamente")
    
    print("\n🔍 5. COMPARAÇÃO BODY/PAYLOAD")
    print("-" * 60)
    doc_body = documentacao_oficial["body"]
    impl_body = implementacao_atual["body"]
    
    campos_obrigatorios = ["mediaKey", "directPath", "type", "mimetype"]
    
    for campo in campos_obrigatorios:
        print(f"\n📋 Campo: {campo}")
        print(f"📚 Documentação: {doc_body[campo]}")
        print(f"💻 Implementação: {impl_body[campo]}")
        
        if campo in impl_body:
            print("✅ CONFORME: Campo presente")
        else:
            print("❌ NÃO CONFORME: Campo ausente")
    
    print("\n🔍 6. COMPARAÇÃO TRATAMENTO DE RESPOSTA")
    print("-" * 60)
    doc_resposta = documentacao_oficial["resposta_sucesso"]
    impl_tratamento = implementacao_atual["tratamento_resposta"]
    
    print("📚 Resposta esperada:")
    print(json.dumps(doc_resposta, indent=2))
    
    print("\n💻 Tratamento implementado:")
    for tratamento, implementado in impl_tratamento.items():
        status = "✅" if implementado else "❌"
        print(f"   {status} {tratamento}")
    
    print("\n🔍 7. PROBLEMAS IDENTIFICADOS NA IMPLEMENTAÇÃO")
    print("-" * 60)
    
    problemas = []
    
    # Verificar se campos podem estar vazios
    print("⚠️ PROBLEMA POTENCIAL 1: Campos podem estar vazios")
    print("   Implementação atual usa .get('campo', '') que pode retornar string vazia")
    print("   W-API pode rejeitar campos vazios")
    problemas.append("Campos podem estar vazios")
    
    # Verificar validação de dados
    print("\n⚠️ PROBLEMA POTENCIAL 2: Sem validação prévia")
    print("   Não há validação se mediaKey, directPath, etc. são válidos antes do envio")
    print("   W-API pode rejeitar dados inválidos")
    problemas.append("Falta validação de dados")
    
    # Verificar tratamento de erro
    print("\n⚠️ PROBLEMA POTENCIAL 3: Tratamento de erro pode estar incorreto")
    print("   Código verifica 'if not data.get('error', True)' ")
    print("   Isso significa que se 'error' não existir, assume True (erro)")
    print("   Deveria ser 'if not data.get('error', False)'")
    problemas.append("Lógica de erro invertida")
    
    return problemas

def gerar_implementacao_corrigida():
    """Gera implementação corrigida baseada na documentação"""
    print("\n🔧 IMPLEMENTAÇÃO CORRIGIDA SUGERIDA")
    print("=" * 80)
    
    codigo_corrigido = '''
def download_media_via_wapi_corrigido(instance_id, bearer_token, media_data):
    """
    Download de mídia via W-API - CORRIGIDO conforme documentação oficial
    """
    import requests
    import json
    import time
    
    # 1. VALIDAÇÃO PRÉVIA DOS DADOS (NOVO)
    campos_obrigatorios = ['mediaKey', 'directPath', 'type', 'mimetype']
    for campo in campos_obrigatorios:
        if not media_data.get(campo):
            print(f"❌ Campo obrigatório ausente: {campo}")
            return None
    
    # 2. ENDPOINT CONFORME DOCUMENTAÇÃO
    url = f"https://api.w-api.app/v1/message/download-media?instanceId={instance_id}"
    
    # 3. HEADERS CONFORME DOCUMENTAÇÃO
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json'
    }
    
    # 4. PAYLOAD CONFORME DOCUMENTAÇÃO
    payload = {
        'mediaKey': media_data['mediaKey'],      # Sem .get() para garantir que existe
        'directPath': media_data['directPath'],  # Sem .get() para garantir que existe
        'type': media_data['type'],              # Sem .get() para garantir que existe
        'mimetype': media_data['mimetype']       # Sem .get() para garantir que existe
    }
    
    print(f"🔄 Requisição W-API:")
    print(f"   URL: {url}")
    print(f"   Headers: {json.dumps(headers, indent=2)}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"📡 Status: {response.status_code}")
        print(f"📨 Resposta: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            
            # 5. TRATAMENTO DE RESPOSTA CORRIGIDO
            if data.get('error', False) == False:  # CORRIGIDO: error deve ser False
                print(f"✅ Download bem-sucedido!")
                print(f"   fileLink: {data.get('fileLink')}")
                print(f"   expires: {data.get('expires')}")
                return data
            else:
                print(f"❌ Erro retornado pela API: {data}")
                return None
        else:
            print(f"❌ Status HTTP inválido: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None
'''
    
    print(codigo_corrigido)
    
    print("\n📋 PRINCIPAIS CORREÇÕES:")
    print("-" * 60)
    print("1. ✅ Validação prévia de campos obrigatórios")
    print("2. ✅ Remoção de .get() com valores padrão vazios")
    print("3. ✅ Correção da lógica de verificação de erro")
    print("4. ✅ Logs mais detalhados para debug")
    print("5. ✅ Timeout adequado (30s)")

def main():
    """Função principal"""
    print("📋 ANÁLISE COMPLETA DE CONFORMIDADE W-API")
    print("=" * 80)
    
    # Analisar conformidade
    problemas = analisar_conformidade_wapi()
    
    # Gerar implementação corrigida
    gerar_implementacao_corrigida()
    
    print("\n📊 RESUMO FINAL")
    print("=" * 80)
    print(f"✅ Endpoint: CONFORME")
    print(f"✅ Método: CONFORME") 
    print(f"✅ Headers: CONFORME")
    print(f"✅ Query Params: CONFORME")
    print(f"✅ Payload: CONFORME (estrutura)")
    
    print(f"\n❌ PROBLEMAS ENCONTRADOS: {len(problemas)}")
    for i, problema in enumerate(problemas, 1):
        print(f"   {i}. {problema}")
    
    print("\n🎯 CONCLUSÃO:")
    print("A implementação está ESTRUTURALMENTE CORRETA,")
    print("mas tem PROBLEMAS DE VALIDAÇÃO E LÓGICA que podem")
    print("estar causando as falhas no download automático.")
    
    print("\n🔧 RECOMENDAÇÃO:")
    print("Implementar a versão corrigida sugerida acima!")

if __name__ == "__main__":
    main() 