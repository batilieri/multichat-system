#!/usr/bin/env python3
"""
🔍 INVESTIGAÇÃO WEBHOOK REAL VS TESTE
Por que o teste funciona mas o webhook real não salva os arquivos na pasta?
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

from webhook.models import WebhookEvent
import json

def investigar_webhooks_recentes():
    """Investiga os webhooks mais recentes para encontrar diferenças"""
    print("🔍 INVESTIGAÇÃO: WEBHOOKS RECENTES COM ÁUDIO")
    print("=" * 80)
    
    # Buscar webhooks recentes com audioMessage
    webhooks_audio = []
    
    for webhook in WebhookEvent.objects.all().order_by('-timestamp')[:50]:
        try:
            if isinstance(webhook.raw_data, dict):
                data = webhook.raw_data
            else:
                data = json.loads(webhook.raw_data)
            
            msg_content = data.get('msgContent', {})
            
            if 'audioMessage' in msg_content:
                webhooks_audio.append({
                    'webhook': webhook,
                    'data': data,
                    'audio_data': msg_content['audioMessage']
                })
        
        except Exception as e:
            continue
    
    print(f"📊 Webhooks com áudio encontrados: {len(webhooks_audio)}")
    
    # Analisar diferenças entre webhooks de teste e reais
    for i, item in enumerate(webhooks_audio[:5]):
        webhook = item['webhook']
        data = item['data']
        audio_data = item['audio_data']
        
        print(f"\n--- WEBHOOK {i+1} ---")
        print(f"🕒 Timestamp: {webhook.timestamp}")
        print(f"📧 Event ID: {webhook.event_id}")
        print(f"👤 Cliente: {webhook.cliente.nome}")
        print(f"📱 Instance: {webhook.instance_id}")
        print(f"🆔 Message ID: {data.get('messageId', 'N/A')}")
        print(f"📤 From Me: {data.get('fromMe', False)}")
        print(f"🏠 Event Type: {webhook.event_type}")
        
        # Dados do áudio
        print(f"🎵 Dados do áudio:")
        print(f"   MediaKey: {audio_data.get('mediaKey', 'N/A')[:20]}...")
        print(f"   DirectPath: {audio_data.get('directPath', 'N/A')[:50]}...")
        print(f"   Mimetype: {audio_data.get('mimetype', 'N/A')}")
        print(f"   FileLength: {audio_data.get('fileLength', 'N/A')}")
        
        # Verificar se arquivo foi baixado
        verificar_arquivo_baixado(data, webhook.cliente)

def verificar_arquivo_baixado(data, cliente):
    """Verifica se o arquivo foi realmente baixado"""
    
    # Verificar estrutura antiga (cliente_2)
    path_antigo = Path(f"multichat_system/media_storage/cliente_{cliente.id}")
    
    # Verificar estrutura nova (nome do cliente)
    cliente_nome = "".join(c for c in cliente.nome if c.isalnum() or c in (' ', '-', '_')).strip()
    cliente_nome = cliente_nome.replace(' ', '_')
    path_novo = Path(f"multichat_system/media_storage/{cliente_nome}")
    
    message_id = data.get('messageId', '')
    chat_id = data.get('chat', {}).get('id', 'unknown')
    
    print(f"🔍 Verificando arquivos:")
    
    arquivos_encontrados = []
    
    # Buscar na estrutura antiga
    if path_antigo.exists():
        for arquivo in path_antigo.rglob("*"):
            if arquivo.is_file() and message_id[:8] in arquivo.name:
                arquivos_encontrados.append(str(arquivo))
                print(f"   📄 Antigo: {arquivo}")
    
    # Buscar na estrutura nova
    if path_novo.exists():
        for arquivo in path_novo.rglob("*"):
            if arquivo.is_file():
                arquivos_encontrados.append(str(arquivo))
                print(f"   📄 Novo: {arquivo}")
    
    # Buscar por timestamp aproximado (últimos arquivos)
    from datetime import datetime, timedelta
    agora = datetime.now()
    
    for base_path in [path_antigo, path_novo]:
        if base_path.exists():
            for arquivo in base_path.rglob("*.mp3"):
                if arquivo.is_file():
                    # Verificar se foi criado nas últimas 2 horas
                    mod_time = datetime.fromtimestamp(arquivo.stat().st_mtime)
                    if agora - mod_time < timedelta(hours=2):
                        print(f"   🕒 Recente: {arquivo} (criado em {mod_time})")
    
    if not arquivos_encontrados:
        print(f"   ❌ Nenhum arquivo encontrado para message_id: {message_id}")
    
    return arquivos_encontrados

def comparar_teste_vs_real():
    """Compara dados de teste que funcionaram vs webhook real"""
    print(f"\n🔄 COMPARAÇÃO: TESTE VS WEBHOOK REAL")
    print("=" * 80)
    
    # Dados do teste que funcionou
    teste_dados = {
        "event": "webhookDelivery",
        "instanceId": "3B6XIW-ZTS923-GEAY6V",
        "messageId": "E93A86D6119804FE8714DF3CAED360B6",
        "fromMe": True,
        "msgContent": {
            "audioMessage": {
                "mediaKey": "cMVqM8QbTKnLurfZBhJVKYy5UkA+9u/kID1py3kVA6Y=",
                "directPath": "/v/t62.7117-24/530121278_763400350189604_2525529204231189072_n.enc",
                "mimetype": "audio/ogg; codecs=opus"
            }
        }
    }
    
    print("✅ DADOS DO TESTE QUE FUNCIONOU:")
    print(f"   Event: {teste_dados['event']}")
    print(f"   From Me: {teste_dados['fromMe']}")
    print(f"   Instance: {teste_dados['instanceId']}")
    print(f"   Message ID: {teste_dados['messageId']}")
    
    # Buscar webhook real mais recente
    webhook_real = WebhookEvent.objects.filter(
        raw_data__contains="audioMessage"
    ).order_by('-timestamp').first()
    
    if webhook_real:
        data_real = webhook_real.raw_data
        print(f"\n❓ DADOS DO WEBHOOK REAL:")
        print(f"   Event: {data_real.get('event', 'N/A')}")
        print(f"   From Me: {data_real.get('fromMe', 'N/A')}")
        print(f"   Instance: {data_real.get('instanceId', 'N/A')}")
        print(f"   Message ID: {data_real.get('messageId', 'N/A')}")
        print(f"   Event Type: {webhook_real.event_type}")
        print(f"   Processed: {webhook_real.processed}")
        
        # Comparar estruturas
        audio_teste = teste_dados['msgContent']['audioMessage']
        audio_real = data_real.get('msgContent', {}).get('audioMessage', {})
        
        print(f"\n📊 COMPARAÇÃO DOS DADOS DE ÁUDIO:")
        print(f"   Teste - MediaKey: {audio_teste.get('mediaKey', 'N/A')[:20]}...")
        print(f"   Real  - MediaKey: {audio_real.get('mediaKey', 'N/A')[:20]}...")
        print(f"   Teste - DirectPath: {audio_teste.get('directPath', 'N/A')[:50]}...")
        print(f"   Real  - DirectPath: {audio_real.get('directPath', 'N/A')[:50]}...")
        
        # Verificar se arquivo foi baixado
        print(f"\n🔍 VERIFICAÇÃO DE ARQUIVO BAIXADO (WEBHOOK REAL):")
        arquivos = verificar_arquivo_baixado(data_real, webhook_real.cliente)
        
        if arquivos:
            print(f"✅ Arquivos encontrados: {len(arquivos)}")
        else:
            print(f"❌ Nenhum arquivo encontrado - problema identificado!")

def diagnosticar_function_call():
    """Diagnostica se a função process_media_automatically está sendo chamada"""
    print(f"\n🔧 DIAGNÓSTICO: CHAMADA DA FUNÇÃO")
    print("=" * 80)
    
    print("📋 Fluxo esperado:")
    print("1. webhook_send_message() recebe POST")
    print("2. process_webhook_message() é chamada")
    print("3. process_media_automatically() é chamada")
    print("4. download_media_via_wapi() baixa o arquivo")
    print("5. reorganizar_arquivo_por_cliente() move para pasta correta")
    
    print(f"\n🎯 Possíveis problemas:")
    print("❓ A função process_media_automatically não está sendo chamada?")
    print("❓ A função está falhando silenciosamente?")
    print("❓ O download funciona mas reorganização falha?")
    print("❓ O webhook real tem estrutura diferente do teste?")
    
    # Verificar logs recentes
    print(f"\n📋 PARA VERIFICAR NO PRÓXIMO ÁUDIO:")
    print("1. Verificar se aparece: '🔄 INICIANDO DOWNLOAD AUTOMÁTICO'")
    print("2. Verificar se aparece: '📎 Mídia detectada: audio'")
    print("3. Verificar se aparece: '✅ Mídia processada automaticamente'")
    print("4. Verificar se arquivo aparece em cliente_2/ ou Elizeu_Batiliere_Dos_Santos/")

def main():
    """Função principal"""
    print("🔍 INVESTIGAÇÃO COMPLETA - WEBHOOK REAL VS TESTE")
    print("=" * 80)
    
    # 1. Investigar webhooks recentes
    investigar_webhooks_recentes()
    
    # 2. Comparar teste vs real
    comparar_teste_vs_real()
    
    # 3. Diagnosticar chamadas de função
    diagnosticar_function_call()
    
    print(f"\n" + "=" * 80)
    print("💡 PRÓXIMO PASSO: ENVIE UM ÁUDIO E OBSERVE OS LOGS")
    print("=" * 80)
    print("📋 O que observar:")
    print("✅ Se aparecer: '🔄 INICIANDO DOWNLOAD AUTOMÁTICO' - função sendo chamada")
    print("❌ Se NÃO aparecer: '📎 Mídia detectada' - função não está sendo chamada")
    print("🔍 Se aparecer tudo mas arquivo não for salvo - problema na reorganização")

if __name__ == "__main__":
    main() 