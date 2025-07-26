import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem

# Analisar mensagens existentes
print("=== ANÁLISE DAS MENSAGENS EXISTENTES ===")
mensagens = Mensagem.objects.all()
total = mensagens.count()
from_me_true = mensagens.filter(from_me=True).count()
from_me_false = mensagens.filter(from_me=False).count()

print(f"Total de mensagens: {total}")
print(f"from_me=True: {from_me_true}")
print(f"from_me=False: {from_me_false}")

# Mostrar algumas mensagens
print("\n=== EXEMPLOS DE MENSAGENS ===")
for msg in mensagens[:10]:
    print(f"ID: {msg.id}, Remetente: '{msg.remetente}', from_me: {msg.from_me}, Conteúdo: {msg.conteudo[:50]}...")

# Corrigir mensagens com remetente "Elizeu Batiliere"
print("\n=== CORRIGINDO MENSAGENS ===")
mensagens_elizeu = mensagens.filter(remetente="Elizeu Batiliere", from_me=False)
print(f"Mensagens de 'Elizeu Batiliere' com from_me=False: {mensagens_elizeu.count()}")

for msg in mensagens_elizeu:
    msg.from_me = True
    msg.save()
    print(f"Corrigida mensagem ID {msg.id}")

# Verificar resultado
print("\n=== RESULTADO APÓS CORREÇÃO ===")
from_me_true_final = Mensagem.objects.filter(from_me=True).count()
from_me_false_final = Mensagem.objects.filter(from_me=False).count()

print(f"from_me=True: {from_me_true_final}")
print(f"from_me=False: {from_me_false_final}")
print(f"Corrigidas: {from_me_true_final - from_me_true}") 