#!/usr/bin/env python3
"""
🚨 CORREÇÃO URGENTE WEBHOOK
Implementa logging e debug para identificar problema do download automático
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

def adicionar_logging_webhook():
    """Adiciona logging detalhado ao webhook views.py"""
    print("🔧 IMPLEMENTANDO LOGGING URGENTE")
    print("=" * 60)
    
    views_file = Path("multichat_system/webhook/views.py")
    
    if not views_file.exists():
        print("❌ Arquivo views.py não encontrado")
        return False
    
    # Ler conteúdo atual
    content = views_file.read_text(encoding='utf-8')
    
    # Verificar se logging já foi adicionado
    if "logger = logging.getLogger(__name__)" in content:
        print("✅ Logging já está configurado")
        return True
    
    # Adicionar imports de logging
    import_section = """import json
import os
import logging
from pathlib import Path"""
    
    if "import logging" not in content:
        content = content.replace("import json", import_section)
        print("✅ Import logging adicionado")
    
    # Adicionar logger
    logger_setup = "logger = logging.getLogger(__name__)\n\n"
    
    # Encontrar onde adicionar logger (após imports)
    lines = content.split('\n')
    insert_pos = 0
    
    for i, line in enumerate(lines):
        if line.startswith("from ") or line.startswith("import "):
            insert_pos = i + 1
        elif line.strip() == "" and insert_pos > 0:
            break
    
    # Inserir logger
    lines.insert(insert_pos + 1, logger_setup.strip())
    content = '\n'.join(lines)
    
    print("✅ Logger configurado")
    
    # Substituir prints críticos por logs
    replacements = [
        ('print(f"📤 WEBHOOK ENVIAR MENSAGEM: {webhook_data}")', 
         'logger.info(f"📤 WEBHOOK ENVIAR MENSAGEM: {webhook_data.get(\'messageId\', \'N/A\')} - fromMe: {webhook_data.get(\'fromMe\', \'N/A\')}")'),
        
        ('print(f"🔄 INICIANDO DOWNLOAD AUTOMÁTICO - Cliente: {cliente.nome}")',
         'logger.info(f"🔄 INICIANDO DOWNLOAD AUTOMÁTICO - Cliente: {cliente.nome}")'),
         
        ('print(f"📎 Mídia detectada: {media_type}")',
         'logger.info(f"📎 Mídia detectada: {media_type}")'),
         
        ('print(f"✅ Mídia processada automaticamente: {message_id}")',
         'logger.info(f"✅ Mídia processada automaticamente: {message_id}")'),
         
        ('print(f"❌ Falha no download via W-API: {file_path}")',
         'logger.error(f"❌ Falha no download via W-API: {file_path}")'),
    ]
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            print(f"✅ Substituído: {old[:50]}...")
    
    # Adicionar debug específico para fromMe
    debug_frommme = '''
        # DEBUG URGENTE: Verificar fromMe
        logger.info(f"🔍 DEBUG fromMe: {webhook_data.get('fromMe')} | event: {webhook_data.get('event', 'N/A')}")
        logger.info(f"🔍 DEBUG messageId: {webhook_data.get('messageId', 'N/A')}")
        logger.info(f"🔍 DEBUG msgContent keys: {list(webhook_data.get('msgContent', {}).keys())}")
        '''
    
    # Encontrar função webhook_send_message e adicionar debug
    if "def webhook_send_message(request):" in content:
        content = content.replace(
            'webhook_data = json.loads(request.body)',
            f'webhook_data = json.loads(request.body){debug_frommme}'
        )
        print("✅ Debug fromMe adicionado")
    
    # Salvar arquivo modificado
    try:
        views_file.write_text(content, encoding='utf-8')
        print("✅ Arquivo views.py atualizado com logging")
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")
        return False

def configurar_django_logging():
    """Configura logging no settings.py do Django"""
    print("\n🔧 CONFIGURANDO DJANGO LOGGING")
    print("=" * 60)
    
    settings_file = Path("multichat_system/multichat/settings.py")
    
    if not settings_file.exists():
        print("❌ Arquivo settings.py não encontrado")
        return False
    
    content = settings_file.read_text(encoding='utf-8')
    
    # Verificar se logging já está configurado
    if "LOGGING = {" in content:
        print("✅ Logging já está configurado no Django")
        return True
    
    # Configuração de logging
    logging_config = '''

# Configuração de Logging para Debug Webhook
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'webhook_debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'webhook.views': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
'''
    
    # Adicionar no final do arquivo
    content += logging_config
    
    try:
        settings_file.write_text(content, encoding='utf-8')
        print("✅ Logging configurado no Django")
        return True
    except Exception as e:
        print(f"❌ Erro ao configurar logging: {e}")
        return False

def criar_script_monitor_logs():
    """Cria script para monitorar logs em tempo real"""
    print("\n🔧 CRIANDO MONITOR DE LOGS")
    print("=" * 60)
    
    monitor_script = '''#!/usr/bin/env python3
"""
🔍 MONITOR LOGS WEBHOOK
Monitora logs do webhook em tempo real
"""

import time
import os
from pathlib import Path
from datetime import datetime

def monitor_webhook_logs():
    """Monitora logs do webhook"""
    log_file = Path("webhook_debug.log")
    
    print("🔍 MONITOR LOGS WEBHOOK INICIADO")
    print("=" * 60)
    print("💡 Envie um áudio pelo WhatsApp agora!")
    print("🔍 Monitorando arquivo: webhook_debug.log")
    print("=" * 60)
    
    # Posição inicial do arquivo
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            f.seek(0, 2)  # Ir para o final
            last_position = f.tell()
    else:
        last_position = 0
        print("⚠️ Arquivo de log não existe ainda")
    
    try:
        while True:
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    f.seek(last_position)
                    new_lines = f.readlines()
                    last_position = f.tell()
                    
                    for line in new_lines:
                        line = line.strip()
                        if any(keyword in line for keyword in ['🔄', '📎', '✅', '❌', '🔍']):
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            print(f"[{timestamp}] {line}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\\n⏹️ Monitor interrompido")

if __name__ == "__main__":
    monitor_webhook_logs()
'''
    
    monitor_file = Path("monitor_logs_webhook.py")
    monitor_file.write_text(monitor_script, encoding='utf-8')
    print("✅ Script monitor_logs_webhook.py criado")

def testar_endpoint_webhook():
    """Testa qual endpoint está sendo usado"""
    print("\n🔧 TESTANDO ENDPOINT WEBHOOK")
    print("=" * 60)
    
    from webhook.models import WebhookEvent
    
    # Buscar webhook mais recente
    ultimo_webhook = WebhookEvent.objects.all().order_by('-timestamp').first()
    
    if ultimo_webhook:
        print(f"📧 Último webhook:")
        print(f"   Timestamp: {ultimo_webhook.timestamp}")
        print(f"   Event Type: {ultimo_webhook.event_type}")
        print(f"   Processed: {ultimo_webhook.processed}")
        print(f"   Message ID: {ultimo_webhook.raw_data.get('messageId', 'N/A')}")
        print(f"   From Me: {ultimo_webhook.raw_data.get('fromMe', 'N/A')}")
        
        # Verificar se tem áudio
        msg_content = ultimo_webhook.raw_data.get('msgContent', {})
        if 'audioMessage' in msg_content:
            print(f"   🎵 Tem áudio: SIM")
        else:
            print(f"   🎵 Tem áudio: NÃO")
            
    else:
        print("❌ Nenhum webhook encontrado")

def main():
    """Função principal"""
    print("🚨 CORREÇÃO URGENTE WEBHOOK - IMPLEMENTAÇÃO")
    print("=" * 80)
    
    # 1. Adicionar logging ao views.py
    sucesso_views = adicionar_logging_webhook()
    
    # 2. Configurar logging no Django
    sucesso_django = configurar_django_logging()
    
    # 3. Criar monitor de logs
    criar_script_monitor_logs()
    
    # 4. Testar estado atual
    testar_endpoint_webhook()
    
    print("\n" + "=" * 80)
    print("📋 PRÓXIMOS PASSOS:")
    print("=" * 80)
    
    if sucesso_views and sucesso_django:
        print("✅ 1. Logging configurado com sucesso")
        print("🔄 2. Reiniciar servidor Django:")
        print("   cd multichat_system")
        print("   python manage.py runserver")
        print()
        print("🔍 3. Em outro terminal, monitorar logs:")
        print("   python monitor_logs_webhook.py")
        print()
        print("📱 4. Enviar áudio pelo WhatsApp")
        print("🔍 5. Observar logs detalhados aparecendo")
    else:
        print("❌ Falha na configuração - verificar erros acima")
        
    print("\n💡 ARQUIVOS CRIADOS/MODIFICADOS:")
    print("   - multichat_system/webhook/views.py (logging adicionado)")
    print("   - multichat_system/multichat/settings.py (logging configurado)")
    print("   - monitor_logs_webhook.py (monitor criado)")
    print("   - webhook_debug.log (será criado pelo Django)")

if __name__ == "__main__":
    main() 