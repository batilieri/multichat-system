#!/usr/bin/env python
"""
Script para testar se as correções dos remetentes estão funcionando
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Cliente, Chat
from api.utils import determine_from_me_saas

def testar_correcao_remetentes():
    """Testa se as correções dos remetentes estão funcionando de forma genérica"""
    print("🧪 TESTANDO CORREÇÃO DOS REMETENTES")
    print("=" * 60)
    
    # 1. Verificar se ainda existem mensagens incorretas (qualquer cliente)
    clientes = Cliente.objects.all()
    mensagens_incorretas = []
    
    for cliente in clientes:
        # Verificar mensagens recebidas que tenham qualquer parte do nome do cliente
        nome_partes = cliente.nome.split()
        for parte in nome_partes:
            if len(parte) > 2:  # Ignorar palavras muito pequenas
                msgs_incorretas = Mensagem.objects.filter(
                    from_me=False, 
                    remetente__icontains=parte
                )
                mensagens_incorretas.extend(msgs_incorretas)
    
    # Remover duplicatas
    mensagens_incorretas = list(set(mensagens_incorretas))
    
    print(f"📊 Mensagens ainda incorretas: {len(mensagens_incorretas)}")
    
    if len(mensagens_incorretas) > 0:
        print("❌ Ainda existem mensagens incorretas!")
        for msg in mensagens_incorretas:
            print(f"   ID: {msg.id}, Remetente: {msg.remetente}, FromMe: {msg.from_me}, Chat: {msg.chat.chat_id}")
    else:
        print("✅ Nenhuma mensagem incorreta encontrada!")
    
    print()
    
    # 2. Verificar mensagens de todos os chats ativos
    chats_ativos = Chat.objects.filter(status='active').values_list('chat_id', flat=True).distinct()[:5]
    
    for chat_id in chats_ativos:
        chat_obj = Chat.objects.filter(chat_id=chat_id).first()
        if chat_obj:
            mensagens_chat = Mensagem.objects.filter(
                chat=chat_obj
            ).order_by('-data_envio')[:5]
            
            if mensagens_chat.exists():
                print(f"💬 Chat {chat_id} (Cliente: {chat_obj.cliente.nome}):")
                
                for msg in mensagens_chat:
                    # Verificar se o remetente está correto baseado no from_me
                    cliente_nome = chat_obj.cliente.nome
                    # Mensagem enviada (from_me=True) deve ter nome do cliente
                    # Mensagem recebida (from_me=False) NÃO deve ter nome do cliente
                    if msg.from_me:
                        # Para mensagens enviadas, verificar se contém parte do nome do cliente
                        is_correct = any(part in msg.remetente for part in cliente_nome.split())
                    else:
                        # Para mensagens recebidas, verificar se NÃO contém parte do nome do cliente
                        is_correct = not any(part in msg.remetente for part in cliente_nome.split())
                    
                    status = "✅" if is_correct else "❌"
                    print(f"   {status} ID: {msg.id}, Remetente: {msg.remetente}, FromMe: {msg.from_me}, Conteúdo: {msg.conteudo[:30]}...")
                print()
    
    print()
    
    # 3. Testar a função determine_from_me_saas
    print("🔍 TESTANDO FUNÇÃO determine_from_me_saas")
    print("=" * 40)
    
    # Simular payloads de teste
    test_payloads = [
        {
            "key": {"fromMe": True},
            "sender": {"id": "556999267344@s.whatsapp.net"},
            "chat": {"id": "556999267344@s.whatsapp.net"},
            "instanceId": "556999267344"
        },
        {
            "key": {"fromMe": False},
            "sender": {"id": "556999267344@s.whatsapp.net"},
            "chat": {"id": "556999267344@s.whatsapp.net"},
            "instanceId": "556999267344"
        },
        {
            "fromMe": True,
            "sender": {"id": "556999267344@s.whatsapp.net"},
            "chat": {"id": "556999267344@s.whatsapp.net"},
            "instanceId": "556999267344"
        },
        {
            "sender": {"id": "123456789@s.whatsapp.net"},
            "chat": {"id": "556999267344@s.whatsapp.net"},
            "instanceId": "556999267344"
        }
    ]
    
    for i, payload in enumerate(test_payloads, 1):
        from_me = determine_from_me_saas(payload, "556999267344")
        print(f"   Teste {i}: from_me = {from_me}")
    
    print()
    
    # 4. Verificar estatísticas gerais
    total_mensagens = Mensagem.objects.count()
    mensagens_enviadas = Mensagem.objects.filter(from_me=True).count()
    mensagens_recebidas = Mensagem.objects.filter(from_me=False).count()
    
    print("📊 ESTATÍSTICAS GERAIS")
    print("=" * 40)
    print(f"   Total de mensagens: {total_mensagens}")
    print(f"   Mensagens enviadas: {mensagens_enviadas}")
    print(f"   Mensagens recebidas: {mensagens_recebidas}")
    
    # 5. Verificar se há mensagens duplicadas
    print()
    print("🔍 VERIFICANDO DUPLICATAS")
    print("=" * 40)
    
    # Verificar mensagens com mesmo conteúdo e timestamp
    from django.db.models import Count
    duplicatas = Mensagem.objects.values('conteudo', 'data_envio', 'chat').annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    print(f"   Possíveis duplicatas encontradas: {duplicatas.count()}")
    
    if duplicatas.count() > 0:
        print("   ⚠️ Verificar mensagens duplicadas:")
        for dup in duplicatas[:5]:
            print(f"      Conteúdo: {dup['conteudo'][:30]}..., Chat: {dup['chat']}, Count: {dup['count']}")

if __name__ == "__main__":
    testar_correcao_remetentes() 