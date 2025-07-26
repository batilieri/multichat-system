#!/usr/bin/env python3
"""
Script para configurar e testar o sistema de webhook MultiChat
Baseado na estrutura do betZap
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def install_requirements():
    """Instala as dependências do webhook"""
    print("📦 INSTALANDO DEPENDÊNCIAS DO WEBHOOK")
    print("=" * 50)
    
    try:
        # Instalar dependências do webhook
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements_webhook.txt"
        ], check=True)
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("🔍 VERIFICANDO DEPENDÊNCIAS")
    print("=" * 50)
    
    dependencies = [
        'flask',
        'pyngrok', 
        'requests',
        'python-dateutil'
    ]
    
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - Faltando")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️ Dependências faltando: {', '.join(missing)}")
        return False
    
    print("✅ Todas as dependências estão instaladas!")
    return True

def run_migrations():
    """Executa as migrações do webhook"""
    print("\n🗄️ EXECUTANDO MIGRAÇÕES")
    print("=" * 50)
    
    try:
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
        import django
        django.setup()
        
        # Executar migrações
        subprocess.run([
            sys.executable, "manage.py", "makemigrations", "webhook"
        ], check=True)
        
        subprocess.run([
            sys.executable, "manage.py", "migrate", "webhook"
        ], check=True)
        
        print("✅ Migrações executadas com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro nas migrações: {e}")
        return False

def test_webhook_system():
    """Testa o sistema de webhook"""
    print("\n🧪 TESTANDO SISTEMA DE WEBHOOK")
    print("=" * 50)
    
    try:
        # Importar e testar componentes
        from webhook.models import WebhookEvent, Chat, Sender, Message
        from webhook.processors import WhatsAppWebhookProcessor, WebhookValidator
        from core.models import Cliente
        
        print("✅ Modelos importados com sucesso!")
        print("✅ Processors importados com sucesso!")
        
        # Verificar se há clientes
        clientes = Cliente.objects.filter(ativo=True)
        print(f"👥 Clientes ativos: {clientes.count()}")
        
        if clientes.exists():
            cliente = clientes.first()
            print(f"✅ Usando cliente: {cliente.nome}")
            
            # Testar processor
            processor = WhatsAppWebhookProcessor(cliente)
            print("✅ Processor criado com sucesso!")
            
            # Testar validador
            test_data = {
                "instanceId": "test",
                "key": {"remoteJid": "test"},
                "message": {"conversation": "test"}
            }
            
            is_valid = WebhookValidator.validate_webhook_data(test_data)
            print(f"✅ Validador funcionando: {is_valid}")
            
        else:
            print("⚠️ Nenhum cliente ativo encontrado")
            print("💡 Execute: python create_test_data.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def create_sample_data():
    """Cria dados de exemplo"""
    print("\n🔧 CRIANDO DADOS DE EXEMPLO")
    print("=" * 50)
    
    try:
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
        import django
        django.setup()
        
        from core.models import Cliente
        from webhook.processors import WhatsAppWebhookProcessor
        
        # Verificar se há clientes
        if not Cliente.objects.filter(ativo=True).exists():
            print("❌ Nenhum cliente ativo encontrado")
            print("💡 Execute primeiro: python create_test_data.py")
            return False
        
        cliente = Cliente.objects.filter(ativo=True).first()
        
        # Dados de exemplo baseados no betZap
        sample_data = {
            "instanceId": "sample_instance_123",
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "fromMe": False,
                "id": f"sample_message_{int(time.time())}"
            },
            "message": {
                "conversationMessage": {
                    "conversation": "Olá! Esta é uma mensagem de exemplo do sistema MultiChat."
                }
            },
            "messageTimestamp": str(int(time.time())),
            "pushName": "Usuário Exemplo",
            "msgContent": {
                "conversation": "Olá! Esta é uma mensagem de exemplo do sistema MultiChat."
            }
        }
        
        # Processar dados
        processor = WhatsAppWebhookProcessor(cliente)
        webhook_event = processor.process_webhook_data(sample_data)
        
        print(f"✅ Evento criado: {webhook_event.event_id}")
        print(f"   Tipo: {webhook_event.event_type}")
        print(f"   Processado: {webhook_event.processed}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar dados de exemplo: {e}")
        return False

def show_usage_instructions():
    """Mostra instruções de uso"""
    print("\n📖 INSTRUÇÕES DE USO")
    print("=" * 50)
    print("🚀 Para iniciar o servidor webhook local:")
    print("   python webhook/servidor_webhook_local.py")
    print()
    print("🌐 Para iniciar o servidor Django:")
    print("   python manage.py runserver")
    print()
    print("🧪 Para testar o sistema:")
    print("   python test_webhook.py")
    print()
    print("📊 Para acessar o admin:")
    print("   http://localhost:8000/admin/")
    print()
    print("🔗 URLs do webhook:")
    print("   Local: http://localhost:5000/webhook")
    print("   Django: http://localhost:8000/webhook/")
    print("   Status: http://localhost:8000/webhook/status/")
    print("   Teste: http://localhost:8000/webhook/test/")
    print()
    print("💡 Para receber webhooks do WhatsApp:")
    print("   1. Inicie o servidor webhook local")
    print("   2. Use a URL pública do ngrok no WhatsApp Business API")
    print("   3. Os dados serão salvos automaticamente no banco")

def main():
    """Função principal"""
    print("🚀 CONFIGURAÇÃO DO SISTEMA DE WEBHOOK MULTICHAT")
    print("=" * 60)
    print("✅ Baseado na estrutura do betZap")
    print("✅ Integração com Django")
    print("✅ Processamento automático de WhatsApp")
    print("=" * 60)
    
    # Verificar se estamos no diretório correto
    if not Path("manage.py").exists():
        print("❌ Execute este script no diretório multichat_system/")
        return 1
    
    # Instalar dependências
    if not install_requirements():
        return 1
    
    # Verificar dependências
    if not check_dependencies():
        return 1
    
    # Executar migrações
    if not run_migrations():
        return 1
    
    # Testar sistema
    if not test_webhook_system():
        return 1
    
    # Criar dados de exemplo
    create_sample_data()
    
    # Mostrar instruções
    show_usage_instructions()
    
    print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
    print("✅ Sistema de webhook pronto para uso")
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 