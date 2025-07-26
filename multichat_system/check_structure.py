import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Departamento, Cliente
from authentication.models import Usuario

print("=== ESTRUTURA ATUAL DO BANCO ===")

print(DEPARTAMENTOS:)
departamentos = Departamento.objects.all()
for dept in departamentos:
    print(f- {dept.nome} (Cliente: {dept.cliente.nome})")

print(f"Total de departamentos: {departamentos.count()}")

print(nUSUARIOS:")
usuarios = Usuario.objects.all()
for user in usuarios:
    cliente_nome = user.cliente.nome if user.cliente else Nenhum"
    print(f"- {user.nome} ({user.tipo_usuario}) - Cliente: {cliente_nome}")

print(f"\nTotal de usuarios: {usuarios.count()}")

print("\nCLIENTES:")
clientes = Cliente.objects.all()
for cliente in clientes:
    print(f"-[object Object]cliente.nome} ({cliente.email})")

print(fundefinednTotal de clientes: {clientes.count()}")

print("\n=== ANALISE ===)print("PROBLEMA IDENTIFICADO: Nao ha relacionamento direto entre Usuarios e Departamentos")
print("SOLUCAO NECESSARIA: Adicionar campodepartamento' no modelo Usuario") 