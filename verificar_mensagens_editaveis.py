#!/usr/bin/env python
"""
Script para verificar mensagens editáveis no banco de dados
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from api.models import Mensagem, Chat, Cliente
from django.db.models import Q

def verificar_mensagens_editaveis():
    """Verifica mensagens que podem ser editadas"""
    print("🔍 Verificando mensagens editáveis no banco de dados...")
    
    # Buscar mensagens que atendem aos critérios de edição
    mensagens_editaveis = Mensagem.objects.filter(
        Q(tipo='texto') | Q(tipo='text'),
        from_me=True,
        message_id__isnull=False
    ).exclude(message_id='')
    
    print(f"\n📊 Total de mensagens editáveis encontradas: {mensagens_editaveis.count()}")
    
    if mensagens_editaveis.count() == 0:
        print("\n❌ Nenhuma mensagem editável encontrada!")
        print("💡 Para testar a edição, você precisa de mensagens que:")
        print("   - Sejam do tipo 'texto' ou 'text'")
        print("   - Tenham from_me=True (enviadas por você)")
        print("   - Tenham message_id preenchido")
        return
    
    print("\n📝 Mensagens editáveis encontradas:")
    for i, msg in enumerate(mensagens_editaveis[:5], 1):  # Mostrar apenas as primeiras 5
        print(f"\n{i}. ID: {msg.id}")
        print(f"   Chat: {msg.chat.chat_id}")
        print(f"   Cliente: {msg.chat.cliente.nome}")
        print(f"   Message ID: {msg.message_id}")
        print(f"   From Me: {msg.from_me}")
        print(f"   Tipo: {msg.tipo}")
        print(f"   Conteúdo: {msg.conteudo[:50]}...")
        print(f"   Data: {msg.data_envio}")
    
    if mensagens_editaveis.count() > 5:
        print(f"\n... e mais {mensagens_editaveis.count() - 5} mensagens")

def verificar_todas_mensagens():
    """Verifica todas as mensagens para debug"""
    print("\n🔍 Verificando todas as mensagens...")
    
    total_mensagens = Mensagem.objects.count()
    print(f"📊 Total de mensagens no banco: {total_mensagens}")
    
    if total_mensagens == 0:
        print("❌ Nenhuma mensagem encontrada no banco!")
        return
    
    # Estatísticas por tipo
    tipos = Mensagem.objects.values_list('tipo', flat=True).distinct()
    print(f"\n📋 Tipos de mensagem encontrados: {list(tipos)}")
    
    for tipo in tipos:
        count = Mensagem.objects.filter(tipo=tipo).count()
        print(f"   - {tipo}: {count} mensagens")
    
    # Estatísticas por from_me
    from_me_count = Mensagem.objects.filter(from_me=True).count()
    from_others_count = Mensagem.objects.filter(from_me=False).count()
    print(f"\n👤 Mensagens por remetente:")
    print(f"   - Enviadas por você (from_me=True): {from_me_count}")
    print(f"   - Recebidas de outros (from_me=False): {from_others_count}")
    
    # Estatísticas por message_id
    with_message_id = Mensagem.objects.filter(message_id__isnull=False).exclude(message_id='').count()
    without_message_id = Mensagem.objects.filter(Q(message_id__isnull=True) | Q(message_id='')).count()
    print(f"\n🆔 Mensagens por message_id:")
    print(f"   - Com message_id: {with_message_id}")
    print(f"   - Sem message_id: {without_message_id}")

def verificar_mensagem_especifica(mensagem_id):
    """Verifica uma mensagem específica"""
    try:
        msg = Mensagem.objects.get(id=mensagem_id)
        print(f"\n🔍 Detalhes da mensagem {mensagem_id}:")
        print(f"   ID: {msg.id}")
        print(f"   Chat: {msg.chat.chat_id}")
        print(f"   Cliente: {msg.chat.cliente.nome}")
        print(f"   Message ID: {msg.message_id}")
        print(f"   From Me: {msg.from_me}")
        print(f"   Tipo: {msg.tipo}")
        print(f"   Conteúdo: {msg.conteudo}")
        print(f"   Data: {msg.data_envio}")
        
        # Verificar se pode ser editada
        pode_editar = (
            msg.tipo in ['texto', 'text'] and
            msg.from_me and
            msg.message_id and
            msg.message_id.strip() != ''
        )
        
        print(f"\n✅ Pode ser editada: {'SIM' if pode_editar else 'NÃO'}")
        
        if not pode_editar:
            print("❌ Motivos pelos quais não pode ser editada:")
            if msg.tipo not in ['texto', 'text']:
                print(f"   - Tipo '{msg.tipo}' não é texto")
            if not msg.from_me:
                print("   - Não foi enviada por você (from_me=False)")
            if not msg.message_id or msg.message_id.strip() == '':
                print("   - Não tem message_id")
        
    except Mensagem.DoesNotExist:
        print(f"❌ Mensagem com ID {mensagem_id} não encontrada!")

if __name__ == "__main__":
    print("🧪 Script de verificação de mensagens editáveis")
    print("=" * 50)
    
    verificar_todas_mensagens()
    verificar_mensagens_editaveis()
    
    # Se foi passado um ID específico como argumento
    if len(sys.argv) > 1:
        try:
            mensagem_id = int(sys.argv[1])
            verificar_mensagem_especifica(mensagem_id)
        except ValueError:
            print(f"❌ ID inválido: {sys.argv[1]}")
    
    print("\n✅ Verificação concluída!") 