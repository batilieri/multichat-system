#!/usr/bin/env python3
"""
🚨 CORREÇÃO LÓGICA WEBHOOK
Corrige a lógica para processar TODOS os áudios, independente de fromMe
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

def corrigir_webhook_send_message():
    """Corrige o webhook_send_message para processar TODOS os áudios"""
    print("🚨 CORREÇÃO URGENTE: LÓGICA WEBHOOK")
    print("=" * 60)
    
    views_file = Path("multichat_system/webhook/views.py")
    content = views_file.read_text(encoding='utf-8')
    
    # Encontrar função webhook_send_message
    old_logic = '''        # Processar apenas mensagens enviadas (fromMe: true)
        if webhook_data.get('fromMe') or webhook_data.get('data', {}).get('fromMe'):
            return process_webhook_message(webhook_data, 'send_message')
        else:
            return JsonResponse({'status': 'ignored', 'message': 'Não é mensagem enviada'})'''
    
    new_logic = '''        # CORREÇÃO URGENTE: Processar TODOS os áudios independente de fromMe
        # Verificar se tem mídia (áudio, imagem, vídeo, etc.)
        msg_content = webhook_data.get('msgContent', {})
        tem_midia = any(key in msg_content for key in ['audioMessage', 'imageMessage', 'videoMessage', 'documentMessage', 'stickerMessage'])
        
        logger.info(f"🔍 DEBUG CRÍTICO:")
        logger.info(f"   fromMe: {webhook_data.get('fromMe')}")
        logger.info(f"   messageId: {webhook_data.get('messageId', 'N/A')}")
        logger.info(f"   tem_midia: {tem_midia}")
        logger.info(f"   msgContent keys: {list(msg_content.keys())}")
        
        # Se tem mídia, SEMPRE processar (independente de fromMe)
        if tem_midia:
            logger.info(f"✅ PROCESSANDO MÍDIA (fromMe={webhook_data.get('fromMe')})")
            return process_webhook_message(webhook_data, 'send_message')
        # Se não tem mídia mas é fromMe=True, processar normalmente
        elif webhook_data.get('fromMe') or webhook_data.get('data', {}).get('fromMe'):
            return process_webhook_message(webhook_data, 'send_message')
        else:
            logger.info(f"⚠️ IGNORANDO (sem mídia e fromMe=False)")
            return JsonResponse({'status': 'ignored', 'message': 'Sem mídia e não é mensagem enviada'})'''
    
    if old_logic in content:
        content = content.replace(old_logic, new_logic)
        print("✅ Lógica webhook_send_message corrigida")
    else:
        print("⚠️ Lógica não encontrada - pode já ter sido modificada")
        return False
    
    # Salvar arquivo
    try:
        views_file.write_text(content, encoding='utf-8')
        print("✅ Arquivo salvo com correção")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        return False

def corrigir_webhook_receive_message():
    """Corrige também o webhook_receive_message para ter lógica similar"""
    print("\n🔧 CORRIGINDO WEBHOOK_RECEIVE_MESSAGE")
    print("=" * 60)
    
    views_file = Path("multichat_system/webhook/views.py")
    content = views_file.read_text(encoding='utf-8')
    
    old_logic_receive = '''        # Processar apenas mensagens recebidas (fromMe: false)
        if not webhook_data.get('fromMe') and not webhook_data.get('data', {}).get('fromMe'):
            return process_webhook_message(webhook_data, 'receive_message')
        else:
            return JsonResponse({'status': 'ignored', 'message': 'Não é mensagem recebida'})'''
    
    new_logic_receive = '''        # CORREÇÃO: Processar TODOS os áudios recebidos independente de fromMe
        msg_content = webhook_data.get('msgContent', {})
        tem_midia = any(key in msg_content for key in ['audioMessage', 'imageMessage', 'videoMessage', 'documentMessage', 'stickerMessage'])
        
        logger.info(f"🔍 RECEIVE DEBUG:")
        logger.info(f"   fromMe: {webhook_data.get('fromMe')}")
        logger.info(f"   tem_midia: {tem_midia}")
        
        # Se tem mídia, SEMPRE processar
        if tem_midia:
            logger.info(f"✅ PROCESSANDO MÍDIA RECEBIDA (fromMe={webhook_data.get('fromMe')})")
            return process_webhook_message(webhook_data, 'receive_message')
        # Se não tem mídia mas é fromMe=False, processar texto
        elif not webhook_data.get('fromMe') and not webhook_data.get('data', {}).get('fromMe'):
            return process_webhook_message(webhook_data, 'receive_message')
        else:
            logger.info(f"⚠️ IGNORANDO RECEIVE (sem mídia e fromMe=True)")
            return JsonResponse({'status': 'ignored', 'message': 'Sem mídia e não é mensagem recebida'})'''
    
    if old_logic_receive in content:
        content = content.replace(old_logic_receive, new_logic_receive)
        print("✅ Lógica webhook_receive_message corrigida")
    else:
        print("⚠️ Lógica receive não encontrada")
    
    # Salvar arquivo
    try:
        views_file.write_text(content, encoding='utf-8')
        print("✅ Arquivo salvo com correção receive")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar receive: {e}")
        return False

def testar_webhook_atual():
    """Testa o estado atual dos webhooks"""
    print("\n🔧 TESTANDO WEBHOOKS ATUAIS")
    print("=" * 60)
    
    from webhook.models import WebhookEvent
    
    # Buscar últimos 5 webhooks com áudio
    webhooks_audio = []
    
    for webhook in WebhookEvent.objects.all().order_by('-timestamp')[:20]:
        try:
            data = webhook.raw_data
            msg_content = data.get('msgContent', {})
            
            if 'audioMessage' in msg_content:
                webhooks_audio.append({
                    'webhook': webhook,
                    'fromMe': data.get('fromMe'),
                    'messageId': data.get('messageId'),
                    'processed': webhook.processed
                })
                
                if len(webhooks_audio) >= 5:
                    break
        except:
            continue
    
    print(f"📊 Últimos 5 webhooks com áudio:")
    for i, item in enumerate(webhooks_audio, 1):
        webhook = item['webhook']
        print(f"   {i}. {webhook.timestamp}")
        print(f"      fromMe: {item['fromMe']}")
        print(f"      messageId: {item['messageId']}")
        print(f"      processed: {item['processed']}")
        print()

def main():
    """Função principal"""
    print("🚨 CORREÇÃO CRÍTICA WEBHOOK - LÓGICA fromMe")
    print("=" * 80)
    print("PROBLEMA: Webhooks sendo ignorados porque fromMe=False")
    print("SOLUÇÃO: Processar TODOS os áudios independente de fromMe")
    print("=" * 80)
    
    # 1. Corrigir webhook_send_message
    sucesso_send = corrigir_webhook_send_message()
    
    # 2. Corrigir webhook_receive_message  
    sucesso_receive = corrigir_webhook_receive_message()
    
    # 3. Testar estado atual
    testar_webhook_atual()
    
    print("\n" + "=" * 80)
    print("📋 RESULTADO DA CORREÇÃO:")
    print("=" * 80)
    
    if sucesso_send:
        print("✅ webhook_send_message: CORRIGIDO")
        print("   → Agora processa TODOS os áudios (fromMe=True/False)")
    else:
        print("❌ webhook_send_message: FALHA")
    
    if sucesso_receive:
        print("✅ webhook_receive_message: CORRIGIDO")
        print("   → Agora processa TODOS os áudios recebidos")
    else:
        print("❌ webhook_receive_message: FALHA")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("=" * 80)
    print("1. 🔄 REINICIAR servidor Django imediatamente")
    print("2. 📱 ENVIAR áudio pelo WhatsApp")
    print("3. 🔍 VERIFICAR se arquivo aparece na pasta")
    print("4. 📋 MONITORAR logs com: python monitor_logs_webhook.py")
    
    print("\n💡 O QUE FOI CORRIGIDO:")
    print("   - Webhook agora processa TODOS os áudios")
    print("   - Não importa se fromMe=True ou False") 
    print("   - Se tem áudio = sempre baixa")
    print("   - Logs detalhados adicionados")

if __name__ == "__main__":
    main() 