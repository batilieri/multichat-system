#!/usr/bin/env python3
"""
Script para testar o endpoint de mídias
"""

import requests
import json

def test_media_endpoints():
    """Testa os endpoints de mídias"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testando endpoints de mídias...")
    
    # Testar endpoint de mídias WAPI (sem autenticação)
    print("\n1. Testando endpoint /api/wapi-media/ (sem autenticação)")
    
    # Testar áudio
    audio_url = f"{base_url}/api/wapi-media/audios/migrado_20250806_150850_ColdPlay - The Scientist.mp3"
    print(f"   Áudio: {audio_url}")
    
    try:
        response = requests.get(audio_url)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        print(f"   Tamanho: {len(response.content)} bytes")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Testar imagem
    image_url = f"{base_url}/api/wapi-media/imagens/migrado_20250806_150850_d327976b-1152-43e2-8ae9-fee503914ee9_image.jpeg"
    print(f"   Imagem: {image_url}")
    
    try:
        response = requests.get(image_url)
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        print(f"   Tamanho: {len(response.content)} bytes")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Testar endpoint de mídias do Django (com autenticação)
    print("\n2. Testando endpoint /api/media-files/ (com autenticação)")
    
    # Primeiro fazer login para obter token
    login_data = {
        'email': 'admin@multichat.com',
        'password': 'admin123'
    }
    
    try:
        login_response = requests.post(f"{base_url}/api/auth/login/", json=login_data)
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access')
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Testar endpoint de mídias
            response = requests.get(f"{base_url}/api/media-files/", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Total de mídias: {data.get('count', 0)}")
                if 'results' in data:
                    for media in data['results'][:3]:  # Mostrar apenas 3
                        print(f"     - {media.get('media_type')}: {media.get('file_name')}")
                        print(f"       URL: {media.get('file_url')}")
            else:
                print(f"   Resposta: {response.text}")
        else:
            print(f"   ❌ Erro no login: {login_response.status_code}")
            print(f"   Resposta: {login_response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Testar endpoint de estatísticas
    print("\n3. Testando endpoint /api/media-files/stats/")
    
    try:
        if 'headers' in locals():
            response = requests.get(f"{base_url}/api/media-files/stats/", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Total: {data.get('total', 0)}")
                print(f"   Por tipo: {data.get('por_tipo', [])}")
                print(f"   Por status: {data.get('por_status', [])}")
            else:
                print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    test_media_endpoints() 