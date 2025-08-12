#!/usr/bin/env python3
"""
Script para testar os endpoints de mídias com as mídias migradas
"""

import requests
import json

def test_endpoints_midias():
    """Testa os endpoints de mídias com as mídias migradas"""
    base_url = "http://localhost:8000"
    
    print("🧪 TESTANDO ENDPOINTS DE MÍDIAS MIGRADAS")
    print("=" * 50)
    
    # Lista de mídias migradas
    midias_teste = [
        {
            "tipo": "audio",
            "arquivo": "ColdPlay - The Scientist.mp3",
            "endpoint": "/api/wapi-media/audios/ColdPlay - The Scientist.mp3"
        },
        {
            "tipo": "image", 
            "arquivo": "d327976b-1152-43e2-8ae9-fee503914ee9_image.jpeg",
            "endpoint": "/api/wapi-media/imagens/d327976b-1152-43e2-8ae9-fee503914ee9_image.jpeg"
        },
        {
            "tipo": "video",
            "arquivo": "9wle8b.mp4", 
            "endpoint": "/api/wapi-media/videos/9wle8b.mp4"
        }
    ]
    
    print("1️⃣ TESTANDO ENDPOINTS DE MÍDIAS")
    
    for midia in midias_teste:
        url = f"{base_url}{midia['endpoint']}"
        print(f"\n   📄 Testando: {midia['arquivo']}")
        print(f"   🔗 URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"   📡 Status: {response.status_code}")
            print(f"   📋 Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"   📏 Tamanho: {len(response.content)} bytes")
            
            if response.status_code == 200:
                print(f"   ✅ SUCESSO!")
            else:
                print(f"   ❌ ERRO: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ ERRO: {e}")
    
    print("\n2️⃣ TESTANDO ENDPOINT DE LISTAGEM DE MÍDIAS")
    
    # Testar endpoint de listagem (requer autenticação)
    try:
        url = f"{base_url}/api/media-files/"
        print(f"   🔗 URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"   📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Total de mídias: {data.get('count', 'N/A')}")
            print(f"   ✅ SUCESSO!")
        elif response.status_code == 401:
            print(f"   🔐 Requer autenticação (esperado)")
        else:
            print(f"   ❌ ERRO: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
    
    print("\n3️⃣ TESTANDO ENDPOINT DE MÍDIAS WAPI (sem auth)")
    
    # Testar endpoint que não requer autenticação
    try:
        url = f"{base_url}/api/wapi-media/audios/"
        print(f"   🔗 URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"   📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ SUCESSO!")
        else:
            print(f"   ❌ ERRO: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ ERRO: {e}")

if __name__ == "__main__":
    test_endpoints_midias() 