#!/usr/bin/env python3
"""
Script de teste para verificar se o servidor webhook pode ser iniciado
"""

import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')

try:
    import django
    django.setup()
    print("✅ Django configurado com sucesso")
except Exception as e:
    print(f"❌ Erro ao configurar Django: {e}")
    sys.exit(1)

try:
    import webhook.models
    print("✅ Models do webhook importados com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar models: {e}")
    sys.exit(1)

try:
    import webhook.processors
    print("✅ Processors do webhook importados com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar processors: {e}")
    sys.exit(1)

try:
    import webhook.servidor_webhook_local
    print("✅ Servidor webhook importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar servidor webhook: {e}")
    sys.exit(1)

print("\n🎉 Todos os módulos foram importados com sucesso!")
print("✅ O servidor webhook está pronto para ser executado")
print("\nPara iniciar o servidor, execute:")
print("   python webhook/servidor_webhook_local.py")
print("   ou")
print("   start_webhook.bat") 