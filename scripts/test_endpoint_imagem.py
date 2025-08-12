#!/usr/bin/env python3
"""
Teste do endpoint de envio de imagem
"""

import requests
import json
import base64
import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'multichat_system'))

def test_endpoint_imagem():
    """Testa o endpoint de envio de imagem"""
    
    # Configurações
    API_BASE_URL = "http://localhost:8000"
    
    # Token de teste (substitua por um token válido)
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM1NzI4MDAwLCJpYXQiOjE3MzU3MjQ0MDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoxfQ.example"
    
    # Chat ID de teste (substitua por um chat válido)
    chat_id = 21
    
    print(f"🧪 Testando endpoint de envio de imagem...")
    print(f"🌐 API URL: {API_BASE_URL}")
    print(f"📱 Chat ID: {chat_id}")
    print(f"🔑 Token: {token[:20]}...")
    
    # Teste 1: Verificar se o servidor está rodando
    try:
        response = requests.get(f"{API_BASE_URL}/api/", timeout=5)
        print(f"✅ Servidor respondendo: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando na porta 8000")
        return False
    except Exception as e:
        print(f"❌ Erro ao conectar com servidor: {e}")
        return False
    
    # Teste 2: Verificar se o chat existe
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{API_BASE_URL}/api/chats/{chat_id}/", headers=headers)
        print(f"📱 Chat {chat_id} status: {response.status_code}")
        
        if response.status_code == 200:
            chat_data = response.json()
            print(f"✅ Chat encontrado: {chat_data.get('chat_id', 'N/A')}")
        elif response.status_code == 404:
            print("❌ Chat não encontrado")
            return False
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            print(f"Resposta: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Erro ao verificar chat: {e}")
        return False
    
    # Teste 3: Verificar se o endpoint de imagem existe
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chats/{chat_id}/enviar-imagem/",
            headers=headers,
            json={
                'image_data': 'teste',
                'image_type': 'base64',
                'caption': 'Teste'
            }
        )
        print(f"📸 Endpoint imagem status: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Endpoint existe (erro esperado - dados inválidos)")
            print(f"Resposta: {response.text[:200]}")
        elif response.status_code == 404:
            print("❌ Endpoint não encontrado")
            return False
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            print(f"Resposta: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Erro ao testar endpoint: {e}")
        return False
    
    # Teste 4: Criar uma imagem de teste
    try:
        # Criar uma imagem simples em base64
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Criar imagem de teste
        img = Image.new('RGB', (100, 100), color='red')
        draw = ImageDraw.Draw(img)
        draw.text((10, 40), "TESTE", fill='white')
        
        # Converter para base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        print(f"📄 Imagem de teste criada: {len(img_base64)} caracteres")
        
        # Teste 5: Enviar imagem real
        response = requests.post(
            f"{API_BASE_URL}/api/chats/{chat_id}/enviar-imagem/",
            headers=headers,
            json={
                'image_data': img_base64,
                'image_type': 'base64',
                'caption': 'Imagem de teste'
            }
        )
        
        print(f"📤 Envio imagem status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Imagem enviada com sucesso: {result}")
        else:
            print(f"❌ Erro ao enviar imagem: {response.status_code}")
            print(f"Resposta: {response.text[:500]}")
            
    except ImportError:
        print("⚠️ PIL não disponível, pulando teste de imagem real")
    except Exception as e:
        print(f"❌ Erro no teste de imagem: {e}")
    
    return True

def listar_chats_disponiveis():
    """Lista chats disponíveis para teste"""
    
    API_BASE_URL = "http://localhost:8000"
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM1NzI4MDAwLCJpYXQiOjE3MzU3MjQ0MDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoxfQ.example"
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{API_BASE_URL}/api/chats/", headers=headers)
        
        if response.status_code == 200:
            chats = response.json()
            print(f"📱 Chats disponíveis ({len(chats)}):")
            for chat in chats[:5]:  # Mostrar apenas os primeiros 5
                print(f"  - ID: {chat.get('id')}, Chat ID: {chat.get('chat_id')}, Cliente: {chat.get('cliente')}")
        else:
            print(f"❌ Erro ao listar chats: {response.status_code}")
            print(f"Resposta: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Erro ao listar chats: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes do endpoint de imagem...")
    
    # Listar chats disponíveis
    print("\n📋 Listando chats disponíveis:")
    listar_chats_disponiveis()
    
    # Testar endpoint
    print("\n🧪 Testando endpoint:")
    success = test_endpoint_imagem()
    
    if success:
        print("\n✅ Testes concluídos com sucesso!")
    else:
        print("\n❌ Testes falharam!") 