import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Cliente

print("Clientes existentes:")
clients = Cliente.objects.all()
for client in clients:
    print(f"- {client.nome} ({client.email}) - ID: {client.id}")
    print(f"  Telefone: {client.telefone}")
    print(f"  Empresa: {client.empresa}")

print(f"undefinednTotal de clientes: {clients.count()}") 