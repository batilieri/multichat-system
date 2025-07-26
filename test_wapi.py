#!/usr/bin/env python3
"""
Script de teste para verificar se o W-API está funcionando
"""
import requests
import json

def test_wapi():
    """Testa se o W-API está respondendo"""
    try:
        # Teste 1: Verificar se o servidor está rodando
        print("Testando se o W-API está rodando...")
        response = requests.get('http://localhost:5000/', timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text[:200]}...")
        
        # Teste 2: Verificar rota de status
        print("\nTestando rota de status...")
        response = requests.get(
            'http://localhost:5000/api/auth/status',
            params={'instanceId': 'test'},
            headers={'Authorization': 'Bearer test_token'},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        # Teste 3: Verificar rota de QR Code
        print("\nTestando rota de QR Code...")
        response = requests.get(
            'http://localhost:5000/api/auth/qrcode',
            params={'instanceId': 'test'},
            headers={'Authorization': 'Bearer test_token'},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao W-API (porta 5000)")
    except requests.exceptions.Timeout:
        print("❌ Erro: Timeout ao conectar ao W-API")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_wapi() 