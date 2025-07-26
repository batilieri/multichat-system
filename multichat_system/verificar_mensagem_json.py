#!/usr/bin/env python
"""
Script para verificar uma mensagem específica com JSON inválido
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem, Cliente

def verificar_mensagem_json():
    """Verifica uma mensagem específica com JSON inválido"""
    print("🔍 Verificando mensagem com JSON inválido...")
    print("=" * 50)
    
    # Buscar uma mensagem com JSON inválido
    msg = Mensagem.objects.get(id=425)
    
    print(f"📄 Mensagem ID: {msg.id}")
    print(f"📄 Message ID: {msg.message_id}")
    print(f"📄 Tipo: {msg.tipo}")
    print(f"📄 Remetente: {msg.remetente}")
    print(f"📄 Data: {msg.data_envio}")
    print(f"📄 From Me: {msg.from_me}")
    print(f"📄 Conteúdo completo:")
    print(f"{msg.conteudo}")
    
    # Tentar encontrar onde está o problema no JSON
    conteudo = msg.conteudo
    if conteudo:
        # Verificar se há caracteres especiais que podem estar causando problemas
        print(f"\n🔍 Análise do conteúdo:")
        print(f"   Tamanho: {len(conteudo)}")
        print(f"   Primeiros 100 chars: {repr(conteudo[:100])}")
        print(f"   Últimos 100 chars: {repr(conteudo[-100:])}")
        
        # Tentar encontrar onde está o problema
        try:
            # Tentar parsear até encontrar o erro
            for i in range(1, len(conteudo)):
                try:
                    json.loads(conteudo[:i])
                except json.JSONDecodeError as e:
                    print(f"   ❌ Erro no caractere {i}: {e}")
                    print(f"   Contexto: {repr(conteudo[max(0, i-20):i+20])}")
                    break
        except Exception as e:
            print(f"   ❌ Erro na análise: {e}")

if __name__ == "__main__":
    verificar_mensagem_json() 