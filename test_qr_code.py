#!/usr/bin/env python3
"""
Script de teste específico para QR Code da WAPI
"""
import os
import sys
import django
import requests
import json

# Configurar Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'multichat_system'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import WhatsappInstance
from api.wapi_integration import WApiIntegration

def test_qr_code():
    """Testa a funcionalidade de QR Code"""
    print("📱 TESTE DE QR CODE - WAPI")
    print("=" * 50)
    
    try:
        # Buscar instância no banco
        instancia = WhatsappInstance.objects.first()
        if not instancia:
            print("❌ Nenhuma instância encontrada no banco de dados")
            return
        
        print(f"🔸 Instância: {instancia.instance_id}")
        print(f"   Cliente: {instancia.cliente.nome if instancia.cliente else 'N/A'}")
        print(f"   Status atual: {instancia.status}")
        print(f"   Token: {instancia.token[:10]}..." if instancia.token else "Token não definido")
        
        # Testar QR Code
        print("\n🔄 Testando geração de QR Code...")
        
        wapi = WApiIntegration(instancia.instance_id, instancia.token)
        qr_result = wapi.gerar_qr_code()
        
        print(f"✅ Resultado: {json.dumps(qr_result, indent=2)}")
        
        if qr_result.get("success"):
            print("🎉 QR Code gerado com sucesso!")
            qr_code = qr_result.get("qr_code")
            if qr_code:
                print(f"📱 QR Code disponível: {qr_code[:50]}..." if len(qr_code) > 50 else qr_code)
            else:
                print("⚠️  QR Code vazio - pode indicar que a instância já está conectada")
        else:
            print(f"❌ Erro ao gerar QR Code: {qr_result.get('message')}")
        
        # Testar status após QR Code
        print("\n🔄 Verificando status após QR Code...")
        status_result = wapi.verificar_status_conexao()
        print(f"✅ Status: {json.dumps(status_result, indent=2)}")
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qr_code() 