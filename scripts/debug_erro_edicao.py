#!/usr/bin/env python
"""
Script para debugar o erro "Mensagem não encontrada" na edição
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from api.models import Mensagem
from django.db.models import Q

def debug_erro_edicao():
    """Debuga o erro de mensagem não encontrada"""
    print("🔍 Debugando erro 'Mensagem não encontrada'...")
    
    # Verificar se há mensagens no banco
    total_mensagens = Mensagem.objects.count()
    print(f"📊 Total de mensagens no banco: {total_mensagens}")
    
    if total_mensagens == 0:
        print("❌ Nenhuma mensagem encontrada no banco!")
        print("💡 O erro 'Mensagem não encontrada' pode ocorrer porque:")
        print("   1. Não há mensagens no banco de dados")
        print("   2. O ID da mensagem enviado pelo frontend não existe")
        print("   3. Há um problema na sincronização entre frontend e backend")
        return
    
    # Verificar mensagens com IDs específicos (comuns no frontend)
    print("\n🔍 Verificando mensagens com IDs específicos...")
    
    # IDs comuns que podem estar sendo usados no frontend
    ids_para_verificar = [1, 2, 3, 4, 5, 10, 20, 50, 100, 200, 500, 1000]
    
    for msg_id in ids_para_verificar:
        try:
            msg = Mensagem.objects.get(id=msg_id)
            print(f"✅ Mensagem {msg_id} existe:")
            print(f"   - Tipo: {msg.tipo}")
            print(f"   - From Me: {msg.from_me}")
            print(f"   - Message ID: {msg.message_id}")
            print(f"   - Conteúdo: {msg.conteudo[:50]}...")
        except Mensagem.DoesNotExist:
            print(f"❌ Mensagem {msg_id} NÃO existe")
    
    # Verificar mensagens editáveis
    print("\n🔍 Verificando mensagens editáveis...")
    mensagens_editaveis = Mensagem.objects.filter(
        Q(tipo='texto') | Q(tipo='text'),
        from_me=True,
        message_id__isnull=False
    ).exclude(message_id='')
    
    print(f"📝 Mensagens editáveis encontradas: {mensagens_editaveis.count()}")
    
    if mensagens_editaveis.count() > 0:
        print("\n📋 Primeiras 5 mensagens editáveis:")
        for i, msg in enumerate(mensagens_editaveis[:5], 1):
            print(f"\n{i}. ID: {msg.id}")
            print(f"   - Tipo: {msg.tipo}")
            print(f"   - From Me: {msg.from_me}")
            print(f"   - Message ID: {msg.message_id}")
            print(f"   - Conteúdo: {msg.conteudo[:50]}...")
    
    # Verificar problemas comuns
    print("\n🔍 Verificando problemas comuns...")
    
    # Mensagens sem message_id
    sem_message_id = Mensagem.objects.filter(
        Q(message_id__isnull=True) | Q(message_id='')
    ).count()
    print(f"   - Mensagens sem message_id: {sem_message_id}")
    
    # Mensagens não próprias
    nao_proprias = Mensagem.objects.filter(from_me=False).count()
    print(f"   - Mensagens não próprias (from_me=False): {nao_proprias}")
    
    # Mensagens não-texto
    nao_texto = Mensagem.objects.exclude(
        Q(tipo='texto') | Q(tipo='text')
    ).count()
    print(f"   - Mensagens não-texto: {nao_texto}")
    
    # Verificar se há problemas de sincronização
    print("\n🔍 Verificando sincronização frontend-backend...")
    
    # Simular o que o frontend pode estar enviando
    print("💡 Possíveis causas do erro 'Mensagem não encontrada':")
    print("   1. Frontend está enviando um ID que não existe no banco")
    print("   2. Problema de cache no frontend (ID desatualizado)")
    print("   3. Problema de autenticação (usuário não tem acesso à mensagem)")
    print("   4. Problema de permissões (mensagem de outro cliente)")
    
    # Verificar mensagens por cliente
    print("\n🔍 Verificando mensagens por cliente...")
    from api.models import Cliente
    
    clientes = Cliente.objects.all()
    for cliente in clientes:
        mensagens_cliente = Mensagem.objects.filter(chat__cliente=cliente).count()
        print(f"   - Cliente '{cliente.nome}': {mensagens_cliente} mensagens")

def simular_erro_frontend():
    """Simula o erro que pode estar acontecendo no frontend"""
    print("\n🧪 Simulando erro do frontend...")
    
    # Simular dados que o frontend pode estar enviando
    dados_frontend = [
        {'id': 999, 'content': 'Mensagem inexistente'},
        {'id': 0, 'content': 'ID zero'},
        {'id': -1, 'content': 'ID negativo'},
        {'id': None, 'content': 'ID nulo'},
    ]
    
    for dados in dados_frontend:
        msg_id = dados['id']
        print(f"\n🎯 Testando ID: {msg_id}")
        
        try:
            if msg_id is None:
                print("❌ ID nulo - não pode ser processado")
                continue
                
            msg = Mensagem.objects.get(id=msg_id)
            print(f"✅ Mensagem {msg_id} existe!")
        except Mensagem.DoesNotExist:
            print(f"❌ Mensagem {msg_id} não encontrada!")
        except (ValueError, TypeError):
            print(f"❌ ID inválido: {msg_id}")

if __name__ == "__main__":
    print("🔍 Debug do erro 'Mensagem não encontrada'")
    print("=" * 50)
    
    debug_erro_edicao()
    simular_erro_frontend()
    
    print("\n✅ Debug concluído!")
    print("\n💡 Próximos passos:")
    print("   1. Verifique se o backend está rodando")
    print("   2. Verifique se há mensagens editáveis no banco")
    print("   3. Verifique os logs do frontend no console do navegador")
    print("   4. Teste com uma mensagem específica que você sabe que existe") 