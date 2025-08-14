#!/usr/bin/env python3
"""
Script para corrigir o chat problemático
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente
from django.db import connection

def corrigir_chat_problematico():
    """Corrige o chat problemático"""
    print("🔧 CORRIGINDO CHAT PROBLEMÁTICO")
    print("=" * 50)
    
    chat_id_problematico = "556992962029-1415646286@g.us"
    
    try:
        # 1. Verificar clientes disponíveis
        print(f"\n🔍 Verificando clientes disponíveis:")
        clientes = Cliente.objects.all()
        print(f"Total de clientes: {clientes.count()}")
        
        for cliente in clientes:
            print(f"  ID: {cliente.id}, Nome: {cliente.nome}, Email: {cliente.email}")
            
        # 2. Verificar se há conflitos
        print(f"\n🔍 Verificando conflitos:")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT chat_id, cliente_id, COUNT(*) as total
                FROM core_chat 
                WHERE chat_id = %s 
                GROUP BY chat_id, cliente_id
            """, [chat_id_problematico])
            
            conflitos = cursor.fetchall()
            if conflitos:
                print(f"⚠️ CONFLITOS ENCONTRADOS:")
                for conflito in conflitos:
                    print(f"  Chat ID: {conflito[0]}, Cliente ID: {conflito[1]}, Total: {conflito[2]}")
            else:
                print(f"✅ Nenhum conflito encontrado")
                
        # 3. Verificar se o chat existe em outros clientes
        print(f"\n🔍 Verificando chat em outros clientes:")
        chats_similares = Chat.objects.filter(chat_id__contains="556992962029")
        print(f"Chats similares encontrados: {chats_similares.count()}")
        
        for chat in chats_similares:
            print(f"  ID: {chat.id}, Chat ID: {chat.chat_id}, Cliente: {chat.cliente_id}")
            
        # 4. Tentar criar o chat corretamente
        print(f"\n🔧 TENTANDO CRIAR CHAT CORRETAMENTE:")
        
        # Usar o primeiro cliente disponível
        cliente_padrao = Cliente.objects.first()
        if not cliente_padrao:
            print(f"❌ Nenhum cliente encontrado")
            return
            
        print(f"Usando cliente: {cliente_padrao.nome} (ID: {cliente_padrao.id})")
        
        # Verificar se já existe
        chat_existente = Chat.objects.filter(
            chat_id=chat_id_problematico,
            cliente=cliente_padrao
        ).first()
        
        if chat_existente:
            print(f"✅ Chat já existe:")
            print(f"  ID: {chat_existente.id}")
            print(f"  Chat ID: {chat_existente.chat_id}")
            print(f"  Cliente: {chat_existente.cliente.nome}")
        else:
            print(f"📝 Criando novo chat...")
            try:
                novo_chat = Chat.objects.create(
                    chat_id=chat_id_problematico,
                    cliente=cliente_padrao,
                    chat_name="Grupo Victor Guedes",
                    is_group=True,
                    status="ativo",
                    canal="whatsapp"
                )
                print(f"✅ Chat criado com sucesso:")
                print(f"  ID: {novo_chat.id}")
                print(f"  Chat ID: {novo_chat.chat_id}")
                print(f"  Cliente: {novo_chat.cliente.nome}")
                
            except Exception as e:
                print(f"❌ Erro ao criar chat: {e}")
                
                # Tentar identificar o problema específico
                if "UNIQUE constraint failed" in str(e):
                    print(f"🔍 Problema de constraint UNIQUE detectado")
                    
                    # Verificar se há algum chat com este ID em qualquer cliente
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT id, chat_id, cliente_id 
                            FROM core_chat 
                            WHERE chat_id = %s
                        """, [chat_id_problematico])
                        
                        chats_existentes = cursor.fetchall()
                        if chats_existentes:
                            print(f"⚠️ Chat já existe em outros clientes:")
                            for chat_exist in chats_existentes:
                                print(f"  ID: {chat_exist[0]}, Chat ID: {chat_exist[1]}, Cliente ID: {chat_exist[2]}")
                                
                            # Tentar usar o cliente existente
                            cliente_existente = Cliente.objects.filter(id=chats_existentes[0][2]).first()
                            if cliente_existente:
                                print(f"🔄 Usando cliente existente: {cliente_existente.nome}")
                                chat_existente = Chat.objects.filter(
                                    chat_id=chat_id_problematico,
                                    cliente=cliente_existente
                                ).first()
                                
                                if chat_existente:
                                    print(f"✅ Chat encontrado e válido:")
                                    print(f"  ID: {chat_existente.id}")
                                    print(f"  Chat ID: {chat_existente.chat_id}")
                                    print(f"  Cliente: {chat_existente.cliente.nome}")
                                    
        # 5. Verificar se agora conseguimos criar mensagens
        print(f"\n🔍 VERIFICANDO SE AGORA FUNCIONA:")
        
        if 'chat_existente' in locals() and chat_existente:
            print(f"✅ Chat disponível para mensagens")
            
            # Verificar mensagens existentes
            mensagens = Mensagem.objects.filter(chat=chat_existente)
            print(f"Total de mensagens neste chat: {mensagens.count()}")
            
            # Verificar mensagens de áudio
            audio_messages = mensagens.filter(tipo='audio')
            print(f"Mensagens de áudio: {audio_messages.count()}")
            
            if audio_messages.exists():
                print(f"🎵 Mensagens de áudio encontradas!")
                for audio in audio_messages[:3]:
                    print(f"  ID: {audio.id}, Tipo: {audio.tipo}, Conteúdo: {audio.conteudo[:50]}...")
                    
        print("\n" + "=" * 50)
        print("🎵 CORREÇÃO CONCLUÍDA!")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    corrigir_chat_problematico() 