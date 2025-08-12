#!/usr/bin/env python
"""
Script para verificar se o backend está rodando
"""
import requests
import time

def verificar_backend():
    """Verifica se o backend está rodando"""
    print("🔍 Verificando se o backend está rodando...")
    
    urls_para_testar = [
        "http://localhost:8000/api/",
        "http://localhost:8000/admin/",
        "http://localhost:8000/api/mensagens/",
    ]
    
    for url in urls_para_testar:
        try:
            print(f"\n📡 Testando: {url}")
            response = requests.get(url, timeout=5)
            print(f"   ✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Backend está rodando!")
                return True
            elif response.status_code == 401:
                print("   ⚠️ Backend está rodando (autenticação necessária)")
                return True
            else:
                print(f"   ⚠️ Status inesperado: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Erro de conexão - Backend não está rodando")
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout - Backend pode estar lento")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
    
    return False

def verificar_mensagem_especifica(mensagem_id):
    """Verifica se uma mensagem específica existe"""
    print(f"\n🔍 Verificando mensagem ID: {mensagem_id}")
    
    try:
        url = f"http://localhost:8000/api/mensagens/{mensagem_id}/"
        response = requests.get(url, timeout=5)
        
        print(f"   📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Mensagem encontrada:")
            print(f"      - ID: {data.get('id')}")
            print(f"      - Message ID: {data.get('message_id')}")
            print(f"      - Tipo: {data.get('tipo')}")
            print(f"      - From Me: {data.get('from_me')}")
            print(f"      - Conteúdo: {data.get('conteudo', 'N/A')}")
            return True
        elif response.status_code == 404:
            print(f"   ❌ Mensagem não encontrada")
            return False
        else:
            print(f"   ⚠️ Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Verificação do backend")
    print("=" * 40)
    
    backend_ok = verificar_backend()
    
    if backend_ok:
        print("\n✅ Backend está rodando!")
        
        # Verificar mensagem específica mencionada no erro
        verificar_mensagem_especifica(834)
        
        print("\n💡 Para iniciar o backend:")
        print("   cd multichat_system")
        print("   python manage.py runserver")
        
    else:
        print("\n❌ Backend não está rodando!")
        print("\n🚀 Para iniciar o backend:")
        print("   1. cd multichat_system")
        print("   2. python manage.py runserver")
        print("   3. Aguarde a mensagem 'Starting development server at http://127.0.0.1:8000/'") 