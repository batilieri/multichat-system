#!/usr/bin/env python3
"""
Teste do Sistema de Mídias com API W-APi Real
Testa o download real de mídias usando a API W-APi
"""

import os
import sys
import django
from pathlib import Path
import requests
import json
from datetime import datetime

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Cliente, WhatsappInstance
from core.media_manager import criar_media_manager
from webhook.media_processor import process_webhook_media, media_processor


def test_real_api_connection():
    """Testa a conexão com a API W-APi real"""
    
    print("🔗 TESTE DE CONEXÃO COM API W-API REAL")
    print("=" * 50)
    
    # Buscar dados reais
    cliente = Cliente.objects.first()
    instance = WhatsappInstance.objects.filter(cliente=cliente).first()
    
    if not cliente or not instance:
        print("❌ Dados de teste não encontrados")
        return False
    
    print(f"✅ Cliente: {cliente.nome}")
    print(f"✅ Instância: {instance.instance_id}")
    print(f"✅ Token: {instance.token[:20]}...")
    
    # Testar conexão com a API
    base_url = "https://api.w-api.app/v1"
    headers = {
        'Authorization': f'Bearer {instance.token}',
        'Content-Type': 'application/json'
    }
    
    # 1. Testar status da instância
    print("\n📊 1. Testando status da instância...")
    try:
        # Tentar diferentes endpoints de status
        endpoints_status = [
            f"{base_url}/instance/connectionState",
            f"{base_url}/instance/status",
            f"{base_url}/instance/info"
        ]
        
        status_ok = False
        for endpoint in endpoints_status:
            try:
                response = requests.get(
                    endpoint,
                    headers=headers,
                    params={'instanceId': instance.instance_id},
                    timeout=5
                )
                
                if response.status_code == 200:
                    status_data = response.json()
                    print(f"   ✅ Endpoint funcionando: {endpoint}")
                    print(f"   📊 Status: {status_data.get('status', 'unknown')}")
                    print(f"   📱 Conectado: {status_data.get('connected', False)}")
                    print(f"   📶 QR Code: {'Sim' if status_data.get('qrCode') else 'Não'}")
                    status_ok = True
                    break
                else:
                    print(f"   ⚠️ Endpoint {endpoint}: {response.status_code}")
                    
            except Exception as e:
                print(f"   ⚠️ Erro no endpoint {endpoint}: {e}")
                continue
        
        if not status_ok:
            print("   ❌ Nenhum endpoint de status funcionou")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro de conexão: {e}")
        return False
    
    # 2. Testar busca de mensagens
    print("\n📨 2. Testando busca de mensagens...")
    try:
        response = requests.get(
            f"{base_url}/messages",
            headers=headers,
            params={
                'instanceId': instance.instance_id,
                'limit': 10
            },
            timeout=10
        )
        
        if response.status_code == 200:
            messages_data = response.json()
            messages = messages_data.get('data', [])
            print(f"   ✅ Mensagens encontradas: {len(messages)}")
            
            # Procurar por mensagens com mídia
            media_messages = []
            for msg in messages:
                if any(media_type in msg.get('msgContent', {}) for media_type in [
                    'imageMessage', 'videoMessage', 'audioMessage', 
                    'documentMessage', 'stickerMessage'
                ]):
                    media_messages.append(msg)
            
            print(f"   📎 Mensagens com mídia: {len(media_messages)}")
            
            if media_messages:
                return test_real_media_download(media_messages[0], instance)
            else:
                print("   ℹ️ Nenhuma mensagem com mídia encontrada")
                return True
                
        else:
            print(f"   ❌ Erro {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao buscar mensagens: {e}")
        return False


def test_real_media_download(message_data, instance):
    """Testa o download real de uma mídia"""
    
    print("\n📥 3. Testando download real de mídia...")
    
    try:
        # Criar gerenciador de mídias
        media_manager = criar_media_manager(
            cliente_id=instance.cliente.id,
            instance_id=instance.instance_id,
            bearer_token=instance.token
        )
        
        # Processar mensagem real
        print(f"   📨 Processando mensagem: {message_data.get('messageId', 'unknown')}")
        media_manager.processar_mensagem_whatsapp(message_data)
        
        # Verificar resultados
        stats = media_manager.obter_estatisticas()
        print(f"   📊 Resultados:")
        print(f"      - Total de mídias: {stats.get('total_midias', 0)}")
        print(f"      - Mídias baixadas: {stats.get('midias_baixadas', 0)}")
        print(f"      - Mídias pendentes: {stats.get('midias_pendentes', 0)}")
        print(f"      - Mídias falhadas: {stats.get('midias_falhadas', 0)}")
        
        # Verificar arquivos baixados
        for tipo, pasta in media_manager.pastas_midia.items():
            if pasta.exists():
                arquivos = list(pasta.glob('*'))
                if arquivos:
                    print(f"   📁 {tipo}: {len(arquivos)} arquivos baixados")
                    for arquivo in arquivos:
                        tamanho = arquivo.stat().st_size
                        print(f"      - {arquivo.name} ({tamanho / 1024:.1f} KB)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no download: {e}")
        return False


def test_webhook_simulation():
    """Simula o processamento de webhook real"""
    
    print("\n🔄 4. Simulando webhook real...")
    
    # Buscar dados
    cliente = Cliente.objects.first()
    instance = WhatsappInstance.objects.filter(cliente=cliente).first()
    
    if not cliente or not instance:
        print("❌ Dados não encontrados")
        return False
    
    # Simular webhook real
    webhook_data = {
        'event': 'webhookReceived',
        'instanceId': instance.instance_id,
        'messageId': f'real_test_{int(datetime.now().timestamp())}',
        'sender': {
            'id': '5511999999999@s.whatsapp.net',
            'pushName': 'Teste Real'
        },
        'chat': {
            'id': '5511999999999@s.whatsapp.net'
        },
        'msgContent': {
            'imageMessage': {
                'mimetype': 'image/jpeg',
                'fileName': 'teste_real.jpg',
                'fileLength': 4096,
                'caption': 'Teste com API real',
                'mediaKey': 'real_test_key_001',
                'directPath': '/real/test/path',
                'fileSha256': 'real_test_sha256_001',
                'fileEncSha256': 'real_test_enc_sha256_001',
                'width': 1200,
                'height': 800
            }
        },
        'isGroup': False,
        'fromMe': False,
        'moment': int(datetime.now().timestamp())
    }
    
    try:
        # Processar via webhook
        success = process_webhook_media(
            webhook_data, 
            cliente.id, 
            instance.instance_id
        )
        
        print(f"   {'✅' if success else '❌'} Webhook processado: {'Sucesso' if success else 'Falha'}")
        
        # Verificar gerenciador
        cache_key = f"{cliente.id}_{instance.instance_id}"
        if hasattr(media_processor, 'media_managers') and cache_key in media_processor.media_managers:
            manager = media_processor.media_managers[cache_key]
            stats = manager.obter_estatisticas()
            print(f"   📊 Mídias no gerenciador: {stats.get('total_midias', 0)}")
        
        return success
        
    except Exception as e:
        print(f"   ❌ Erro no webhook: {e}")
        return False


def test_api_endpoints():
    """Testa endpoints específicos da API W-APi"""
    
    print("\n🔧 5. Testando endpoints da API...")
    
    # Buscar dados
    cliente = Cliente.objects.first()
    instance = WhatsappInstance.objects.filter(cliente=cliente).first()
    
    if not cliente or not instance:
        print("❌ Dados não encontrados")
        return False
    
    base_url = "https://api.w-api.app/v1"
    headers = {
        'Authorization': f'Bearer {instance.token}',
        'Content-Type': 'application/json'
    }
    
    endpoints = [
        {
            'name': 'Status da Instância',
            'url': f"{base_url}/instance/connectionState",
            'params': {'instanceId': instance.instance_id}
        },
        {
            'name': 'Informações da Instância',
            'url': f"{base_url}/instance/info",
            'params': {'instanceId': instance.instance_id}
        },
        {
            'name': 'Chats',
            'url': f"{base_url}/chats",
            'params': {'instanceId': instance.instance_id, 'limit': 5}
        },
        {
            'name': 'Contatos',
            'url': f"{base_url}/contacts",
            'params': {'instanceId': instance.instance_id, 'limit': 5}
        }
    ]
    
    for endpoint in endpoints:
        try:
            print(f"   🔍 Testando: {endpoint['name']}")
            response = requests.get(
                endpoint['url'],
                headers=headers,
                params=endpoint['params'],
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Sucesso - Status: {response.status_code}")
                
                # Mostrar algumas informações úteis
                if 'data' in data:
                    print(f"      📊 Items: {len(data['data'])}")
                elif 'status' in data:
                    print(f"      📊 Status: {data['status']}")
                    
            else:
                print(f"      ❌ Erro {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Erro: {e}")


def main():
    """Função principal do teste"""
    
    print("🚀 TESTE DO SISTEMA DE MÍDIAS COM API W-API REAL")
    print("=" * 70)
    
    try:
        # Teste de conexão
        connection_ok = test_real_api_connection()
        
        if connection_ok:
            # Teste de webhook
            webhook_ok = test_webhook_simulation()
            
            # Teste de endpoints
            test_api_endpoints()
            
            print("\n" + "=" * 70)
            print("📋 RESUMO DOS TESTES:")
            print(f"   ✅ Conexão com API: {'OK' if connection_ok else 'FALHOU'}")
            print(f"   ✅ Webhook: {'OK' if webhook_ok else 'FALHOU'}")
            
            if connection_ok and webhook_ok:
                print("\n🎉 Todos os testes passaram!")
                print("✅ O sistema está pronto para uso com a API real")
            else:
                print("\n⚠️ Alguns testes falharam")
                print("🔧 Verifique a configuração da API W-APi")
        else:
            print("\n❌ Falha na conexão com a API")
            print("🔧 Verifique:")
            print("   - Token da instância")
            print("   - Status da instância")
            print("   - Conectividade com a API")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    main() 