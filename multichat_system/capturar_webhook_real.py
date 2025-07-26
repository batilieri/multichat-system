#!/usr/bin/env python3
"""
Capturador de Webhooks Reais do WhatsApp
Captura e salva webhooks reais para análise posterior
"""

import os
import sys
import json
import django
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.webhook_media_analyzer import analisar_webhook_whatsapp


def salvar_webhook_para_analise(webhook_data: Dict[str, Any], prefixo: str = "webhook") -> str:
    """
    Salva webhook em arquivo JSON para análise posterior
    """
    # Criar pasta para webhooks se não existir
    pasta_webhooks = Path(__file__).parent / "webhooks_capturados"
    pasta_webhooks.mkdir(exist_ok=True)
    
    # Gerar nome do arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    message_id = webhook_data.get('messageId', 'sem_id')
    instance_id = webhook_data.get('instanceId', 'sem_instance')
    
    # Limpar caracteres especiais do nome do arquivo
    message_id_limpo = "".join(c for c in message_id if c.isalnum() or c in ('-', '_'))
    instance_id_limpo = "".join(c for c in instance_id if c.isalnum() or c in ('-', '_'))
    
    nome_arquivo = f"{prefixo}_{timestamp}_{instance_id_limpo}_{message_id_limpo}.json"
    caminho_arquivo = pasta_webhooks / nome_arquivo
    
    # Salvar webhook
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        json.dump(webhook_data, f, indent=2, ensure_ascii=False)
    
    return str(caminho_arquivo)


def analisar_webhook_capturado(caminho_arquivo: str) -> None:
    """
    Analisa um webhook capturado
    """
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            webhook_data = json.load(f)
        
        print(f"\n📁 Analisando webhook capturado: {caminho_arquivo}")
        print("="*80)
        
        # Análise básica
        analise = analisar_webhook_whatsapp(webhook_data)
        
        print(f"📊 Total de mídias: {analise.get('total_midias', 0)}")
        print(f"🔍 Tem mídias: {analise.get('tem_midias', False)}")
        
        # Informações do cliente
        cliente_info = analise.get('cliente_info', {})
        if cliente_info.get('encontrado'):
            print(f"👤 Cliente: {cliente_info.get('cliente_nome')}")
            print(f"📱 Instância: {cliente_info.get('instance_id')}")
        else:
            print(f"❌ Cliente não encontrado: {cliente_info.get('erro')}")
        
        # Detalhes das mídias
        midias = analise.get('midias', [])
        for i, midia in enumerate(midias, 1):
            print(f"\n📎 Mídia {i}:")
            print(f"   Tipo: {midia['type']}")
            print(f"   Mimetype: {midia.get('mimetype')}")
            print(f"   Tamanho: {midia.get('fileLength', 'N/A')} bytes")
            print(f"   Válido: {midia.get('valido_para_download')}")
            
            # Mostrar campos obrigatórios
            campos_obrigatorios = ['mediaKey', 'directPath', 'fileSha256', 'fileEncSha256']
            print(f"   🔐 Campos obrigatórios:")
            for campo in campos_obrigatorios:
                valor = midia.get(campo)
                if valor:
                    print(f"      ✅ {campo}: {str(valor)[:30]}...")
                else:
                    print(f"      ❌ {campo}: AUSENTE")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao analisar webhook: {e}")
        return False


def listar_webhooks_capturados() -> None:
    """
    Lista todos os webhooks capturados
    """
    pasta_webhooks = Path(__file__).parent / "webhooks_capturados"
    
    if not pasta_webhooks.exists():
        print("📁 Nenhum webhook capturado ainda.")
        return
    
    arquivos = list(pasta_webhooks.glob("*.json"))
    
    if not arquivos:
        print("📁 Nenhum webhook capturado ainda.")
        return
    
    print(f"📁 Webhooks capturados ({len(arquivos)}):")
    print("="*60)
    
    for arquivo in sorted(arquivos, key=lambda x: x.stat().st_mtime, reverse=True):
        # Ler informações básicas do arquivo
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                webhook_data = json.load(f)
            
            # Extrair informações básicas
            event = webhook_data.get('event', 'N/A')
            instance_id = webhook_data.get('instanceId', 'N/A')
            message_id = webhook_data.get('messageId', 'N/A')
            moment = webhook_data.get('moment', 0)
            
            # Verificar se tem mídia
            msg_content = webhook_data.get('msgContent', {})
            tem_midia = any(tipo in msg_content for tipo in [
                'imageMessage', 'videoMessage', 'audioMessage', 
                'documentMessage', 'stickerMessage'
            ])
            
            # Data do arquivo
            data_arquivo = datetime.fromtimestamp(arquivo.stat().st_mtime)
            
            print(f"📄 {arquivo.name}")
            print(f"   📅 Data: {data_arquivo.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"   📨 Evento: {event}")
            print(f"   📱 Instance: {instance_id}")
            print(f"   🆔 Message: {message_id[:20]}...")
            print(f"   📎 Tem mídia: {'✅' if tem_midia else '❌'}")
            print()
            
        except Exception as e:
            print(f"❌ Erro ao ler {arquivo.name}: {e}")


def simular_webhook_real() -> Dict[str, Any]:
    """
    Simula um webhook real baseado em dados reais do WhatsApp
    """
    return {
        'event': 'webhookReceived',
        'instanceId': '3B6XIW-ZTS923-GEAY6V',
        'messageId': f'real_{int(datetime.now().timestamp())}',
        'sender': {
            'id': '5511999999999@s.whatsapp.net',
            'pushName': 'Usuário Real'
        },
        'chat': {
            'id': '5511999999999@s.whatsapp.net'
        },
        'msgContent': {
            'imageMessage': {
                'mimetype': 'image/jpeg',
                'fileName': 'IMG_20240718_143022.jpg',
                'fileLength': 245760,
                'caption': 'Foto tirada agora',
                'mediaKey': 'AQAiS8nF8X9Y2Z3W4V5U6T7S8R9Q0P1O2N3M4L5K6J7I8H9G0F1E2D3C4B5A6',
                'directPath': '/v/t62.7118-24/12345678_98765432_1234567890123456789012345678901234567890/n/ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/',
                'fileSha256': 'A1B2C3D4E5F6789012345678901234567890ABCDEF1234567890ABCDEF123456',
                'fileEncSha256': 'F1E2D3C4B5A6789012345678901234567890ABCDEF1234567890ABCDEF123456',
                'width': 1920,
                'height': 1080,
                'jpegThumbnail': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=',
                'mediaKeyTimestamp': '1752894203'
            }
        },
        'isGroup': False,
        'fromMe': False,
        'moment': int(datetime.now().timestamp())
    }


def main():
    """
    Função principal
    """
    print("📡 CAPTURADOR DE WEBHOOKS REAIS DO WHATSAPP")
    print("="*60)
    
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        if comando == "listar" or comando == "ls":
            listar_webhooks_capturados()
            
        elif comando == "analisar" and len(sys.argv) > 2:
            arquivo = sys.argv[2]
            analisar_webhook_capturado(arquivo)
            
        elif comando == "simular":
            print("🎭 Simulando webhook real...")
            webhook_simulado = simular_webhook_real()
            
            # Salvar webhook simulado
            caminho_salvo = salvar_webhook_para_analise(webhook_simulado, "simulado")
            print(f"✅ Webhook simulado salvo em: {caminho_salvo}")
            
            # Analisar webhook simulado
            analisar_webhook_capturado(caminho_salvo)
            
        else:
            print("❌ Comando inválido!")
            print("\n💡 Comandos disponíveis:")
            print("   python capturar_webhook_real.py listar")
            print("   python capturar_webhook_real.py analisar arquivo.json")
            print("   python capturar_webhook_real.py simular")
    else:
        print("📝 Nenhum comando especificado.")
        print("\n💡 Comandos disponíveis:")
        print("   python capturar_webhook_real.py listar")
        print("   python capturar_webhook_real.py analisar arquivo.json")
        print("   python capturar_webhook_real.py simular")
        print("\n🎭 Para testar, execute:")
        print("   python capturar_webhook_real.py simular")


if __name__ == "__main__":
    main() 