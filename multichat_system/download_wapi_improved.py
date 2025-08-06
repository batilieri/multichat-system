
def download_media_via_wapi_improved(instance_id, bearer_token, media_data):
    """Versão melhorada da função de download via W-API"""
    try:
        import requests
        import json
        import time
        
        url = f"https://api.w-api.app/v1/message/download-media?instanceId={instance_id}"
        
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'mediaKey': media_data.get('mediaKey', ''),
            'directPath': media_data.get('directPath', ''),
            'type': media_data.get('type', ''),
            'mimetype': media_data.get('mimetype', '')
        }
        
        print(f"🔄 Fazendo requisição para W-API:")
        print(f"   URL: {url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        # Tentar múltiplas vezes
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                print(f"📡 Tentativa {attempt + 1}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if not data.get('error', True):
                        print(f"✅ Download bem-sucedido:")
                        print(f"   fileLink: {data.get('fileLink', 'N/A')}")
                        return data
                    else:
                        print(f"❌ Erro na resposta: {data}")
                else:
                    print(f"❌ Status code: {response.status_code}")
                    print(f"   Resposta: {response.text}")
                
                if attempt < max_retries - 1:
                    print(f"⏳ Aguardando 2 segundos antes da próxima tentativa...")
                    time.sleep(2)
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Erro de conexão (tentativa {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        print(f"❌ Todas as {max_retries} tentativas falharam")
        return None
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return None
