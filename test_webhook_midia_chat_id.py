#!/usr/bin/env python3
"""
Script para testar o processamento de mídias com chat_id correto
"""

import os
import sys
import django
import json
from datetime import datetime

# Configurar Django
sys.path.append(os.path.join(os.path.dirname(__file__), 'multichat_system'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')

try:
    django.setup()
except:
    pass

from core.models import Cliente
from webhook.models import WebhookEvent  
from webhook.media_downloader import processar_midias_automaticamente
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def criar_webhook_evento_teste(chat_id="556992962392"):
    """Cria um evento de webhook de teste com áudio"""
    
    # Buscar cliente existente
    try:
        cliente = Cliente.objects.get(id=2)  # Cliente 2 como visto na estrutura
        logger.info(f"Cliente encontrado: {cliente.nome} (ID: {cliente.id})")
        logger.info(f"WAPI Instance ID: {cliente.wapi_instance_id}")
        logger.info(f"WAPI Token: {'Configurado' if cliente.wapi_token else 'NÃO CONFIGURADO'}")
    except Cliente.DoesNotExist:
        logger.error("Cliente ID 2 não encontrado")
        return False
        
    # Dados de webhook simulado com áudio (estrutura correta do W-API)
    webhook_data = {
        "event": "message",
        "instanceId": cliente.wapi_instance_id or "3B6XIW-ZTS923-GEAY6V",
        "messageId": f"TEST_MSG_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "chat": {
            "id": f"{chat_id}@c.us",
            "name": f"Contato {chat_id}"
        },
        "sender": {
            "id": f"{chat_id}@c.us", 
            "pushName": f"Usuário Teste {chat_id}"
        },
        "msgContent": {
            "audioMessage": {
                "mimetype": "audio/ogg; codecs=opus",
                "seconds": 5,
                "ptt": True,
                "mediaKey": "TEST_MEDIA_KEY_AUDIO_123456789_32CHARS",
                "directPath": "/v/t62.7114-24/audio_test.enc",
                "fileSha256": "TEST_SHA256_HASH_AUDIO",
                "fileEncSha256": "TEST_ENC_SHA256_HASH_AUDIO",
                "mediaKeyTimestamp": int(datetime.now().timestamp())
            }
        },
        "messageTimestamp": int(datetime.now().timestamp()),
        "fromMe": False
    }
    
    # Criar WebhookEvent
    try:
        import uuid
        
        webhook_event = WebhookEvent.objects.create(
            event_id=str(uuid.uuid4()),  # Usar UUID válido
            cliente=cliente,
            instance_id=cliente.wapi_instance_id or "3B6XIW-ZTS923-GEAY6V",
            event_type="message",
            raw_data=webhook_data,
            chat_id=chat_id,  # Definir chat_id normalizado
            message_id=webhook_data["messageId"],
            sender_id=f"{chat_id}@c.us",
            sender_name=f"Usuário Teste {chat_id}",
            message_type="audio"
        )
        
        logger.info(f"WebhookEvent criado com sucesso: {webhook_event.event_id}")
        logger.info(f"Chat ID: {webhook_event.chat_id}")
        
        return webhook_event
        
    except Exception as e:
        logger.error(f"Erro ao criar WebhookEvent: {e}")
        return None


def testar_processamento_midia():
    """Testa o processamento automático de mídias"""
    
    print("Teste de Processamento Automatico de Midias")
    print("=" * 50)
    
    # Testar com diferentes chat_ids
    chat_ids_teste = [
        "556992962392",  # Chat ID real da API
        "5511999999999", # Chat ID de teste
    ]
    
    for chat_id in chat_ids_teste:
        print(f"\nTestando chat_id: {chat_id}")
        print("-" * 30)
        
        # Criar evento de teste
        webhook_event = criar_webhook_evento_teste(chat_id)
        
        if not webhook_event:
            print(f"ERRO Falha ao criar evento para {chat_id}")
            continue
            
        try:
            # Processar mídia automaticamente
            print(f"Processando midia automaticamente...")
            processar_midias_automaticamente(webhook_event)
            
            # Verificar se pasta foi criada
            from pathlib import Path
            
            # Caminho esperado na nova estrutura
            base_path = Path(__file__).parent / "multichat_system" / "media_storage"
            pasta_esperada = base_path / "cliente_2" / f"instance_{webhook_event.instance_id}" / "chats" / chat_id / "audio"
            
            if pasta_esperada.exists():
                arquivos = list(pasta_esperada.glob("*.ogg"))
                if arquivos:
                    print(f"OK Midia processada! Arquivo criado: {arquivos[0].name}")
                    print(f"   Pasta: {pasta_esperada}")
                else:
                    print(f"AVISO Pasta criada mas nenhum arquivo encontrado")
                    print(f"   Pasta: {pasta_esperada}")
            else:
                print(f"ERRO Pasta nao foi criada: {pasta_esperada}")
                
        except Exception as e:
            print(f"ERRO no processamento: {e}")
            import traceback
            traceback.print_exc()


def verificar_estrutura_existente():
    """Verifica a estrutura de mídias existente"""
    
    print("\nVerificando Estrutura Existente:")
    print("=" * 40)
    
    from pathlib import Path
    
    base_path = Path(__file__).parent / "multichat_system" / "media_storage"
    
    if base_path.exists():
        for cliente_dir in base_path.iterdir():
            if cliente_dir.is_dir() and cliente_dir.name.startswith('cliente_'):
                print(f"Cliente: {cliente_dir.name}")
                
                for instance_dir in cliente_dir.iterdir():
                    if instance_dir.is_dir():
                        print(f"   Instance: {instance_dir.name}")
                        
                        chats_dir = instance_dir / "chats"
                        if chats_dir.exists():
                            print(f"      chats/")
                            for chat_dir in chats_dir.iterdir():
                                if chat_dir.is_dir():
                                    print(f"         {chat_dir.name}/")
                                    for media_dir in chat_dir.iterdir():
                                        if media_dir.is_dir():
                                            arquivos = list(media_dir.glob("*"))
                                            print(f"            {media_dir.name}/ ({len(arquivos)} arquivos)")
    else:
        print("ERRO Pasta base de midias nao encontrada")


def main():
    """Função principal"""
    verificar_estrutura_existente()
    testar_processamento_midia()
    
    print("\n" + "="*50)
    print("OK Teste concluido!")
    print("Verifique os logs acima para detalhes do processamento")


if __name__ == "__main__":
    main()