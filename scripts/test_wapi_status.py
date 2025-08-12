#!/usr/bin/env python3
"""
Script de teste para verificar o status da WAPI usando dados do banco de dados
"""
import os
import sys
import django
import requests
import json
from datetime import datetime

# Configurar Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'multichat_system'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import WhatsappInstance, Cliente
from api.wapi_integration import WApiIntegration

def test_wapi_status_from_database():
    """Testa o status da WAPI usando instâncias do banco de dados"""
    print("🔍 TESTE DE STATUS WAPI - DADOS DO BANCO")
    print("=" * 60)
    
    try:
        # Buscar todas as instâncias cadastradas
        instancias = WhatsappInstance.objects.all()
        
        if not instancias.exists():
            print("❌ Nenhuma instância encontrada no banco de dados")
            print("\n💡 Para criar uma instância de teste, use:")
            print("   python manage.py shell")
            print("   from core.models import Cliente, WhatsappInstance")
            print("   cliente = Cliente.objects.first()")
            print("   instancia = WhatsappInstance.objects.create(")
            print("       instance_id='test_instance',")
            print("       token='test_token',")
            print("       cliente=cliente,")
            print("       status='pendente'")
            print("   )")
            return
        
        print(f"📊 Total de instâncias encontradas: {instancias.count()}")
        print()
        
        for i, instancia in enumerate(instancias, 1):
            print(f"🔸 INSTÂNCIA {i}: {instancia.instance_id}")
            print(f"   Cliente: {instancia.cliente.nome if instancia.cliente else 'N/A'}")
            print(f"   Status atual: {instancia.status}")
            print(f"   Token: {instancia.token[:10]}..." if instancia.token else "Token não definido")
            print(f"   Criada em: {instancia.created_at}")
            print(f"   Última atualização: {instancia.updated_at}")
            
            # Testar conexão com WAPI
            print("   🔄 Testando conexão com WAPI...")
            
            try:
                # Usar a classe de integração
                wapi = WApiIntegration(instancia.instance_id, instancia.token)
                status_result = wapi.verificar_status_conexao()
                
                print(f"   ✅ Status da WAPI: {status_result.get('status', 'N/A')}")
                print(f"   📱 Conectado: {status_result.get('connected', 'N/A')}")
                print(f"   📊 Mensagens: {status_result.get('messages', 'N/A')}")
                
                if status_result.get('qr_code'):
                    print(f"   📱 QR Code disponível: Sim")
                
                # Atualizar status no banco
                instancia.status = status_result.get('status', 'erro')
                if status_result.get('qr_code'):
                    instancia.qr_code = status_result['qr_code']
                instancia.save()
                
                print(f"   💾 Status atualizado no banco: {instancia.status}")
                
            except Exception as e:
                print(f"   ❌ Erro ao verificar status: {str(e)}")
                instancia.status = 'erro'
                instancia.save()
            
            print()
        
        # Teste adicional: verificar se o servidor WAPI está rodando
        print("🌐 TESTE DE CONECTIVIDADE DO SERVIDOR WAPI")
        print("-" * 40)
        
        try:
            response = requests.get('http://localhost:5000/', timeout=5)
            print(f"✅ Servidor WAPI está rodando (Status: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print("❌ Servidor WAPI não está rodando na porta 5000")
            print("💡 Para iniciar o servidor WAPI:")
            print("   cd wapi/")
            print("   python src/main.py")
        except requests.exceptions.Timeout:
            print("⏰ Timeout ao conectar com o servidor WAPI")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
        
        print()
        
        # Resumo final
        print("📋 RESUMO DO TESTE")
        print("=" * 30)
        
        total_instancias = instancias.count()
        instancias_conectadas = instancias.filter(status='conectado').count()
        instancias_erro = instancias.filter(status='erro').count()
        instancias_pendentes = instancias.filter(status='pendente').count()
        
        print(f"Total de instâncias: {total_instancias}")
        print(f"Conectadas: {instancias_conectadas}")
        print(f"Com erro: {instancias_erro}")
        print(f"Pendentes: {instancias_pendentes}")
        
        if instancias_erro > 0:
            print("\n⚠️  Instâncias com erro:")
            for instancia in instancias.filter(status='erro'):
                print(f"   - {instancia.instance_id} (Cliente: {instancia.cliente.nome if instancia.cliente else 'N/A'})")
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()

def test_specific_instance(instance_id):
    """Testa uma instância específica"""
    print(f"🎯 TESTE DE INSTÂNCIA ESPECÍFICA: {instance_id}")
    print("=" * 50)
    
    try:
        instancia = WhatsappInstance.objects.get(instance_id=instance_id)
        
        print(f"Cliente: {instancia.cliente.nome if instancia.cliente else 'N/A'}")
        print(f"Token: {instancia.token[:10]}..." if instancia.token else "Token não definido")
        print(f"Status atual: {instancia.status}")
        
        # Testar WAPI
        wapi = WApiIntegration(instancia.instance_id, instancia.token)
        
        # Teste 1: Status da conexão
        print("\n1️⃣ Testando status da conexão...")
        status_result = wapi.verificar_status_conexao()
        print(f"Resultado: {json.dumps(status_result, indent=2)}")
        
        # Teste 2: QR Code (se necessário)
        if status_result.get('status') == 'qrcode_gerado':
            print("\n2️⃣ Testando geração de QR Code...")
            qr_result = wapi.gerar_qr_code()
            print(f"Resultado: {json.dumps(qr_result, indent=2)}")
        
        # Teste 3: Envio de mensagem de teste (opcional)
        print("\n3️⃣ Testando envio de mensagem...")
        test_result = wapi.enviar_mensagem_texto("5511999999999", "Teste de mensagem - " + datetime.now().strftime("%H:%M:%S"))
        print(f"Resultado: {json.dumps(test_result, indent=2)}")
        
    except WhatsappInstance.DoesNotExist:
        print(f"❌ Instância {instance_id} não encontrada no banco de dados")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Testar instância específica
        instance_id = sys.argv[1]
        test_specific_instance(instance_id)
    else:
        # Testar todas as instâncias
        test_wapi_status_from_database() 