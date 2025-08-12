#!/usr/bin/env python3
"""
Script para migrar áudios e garantir que apareçam no frontend
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
django.setup()

from core.models import Mensagem, Cliente, Chat
from webhook.models import Message
from django.utils import timezone
import json

def migrar_mensagens_audio_existentes():
    """Migra mensagens existentes para garantir que áudios apareçam no frontend"""
    print("🔄 MIGRANDO MENSAGENS DE ÁUDIO EXISTENTES")
    print("=" * 60)
    
    # Buscar mensagens que podem ser áudios
    mensagens = Mensagem.objects.all()
    print(f"📊 Total de mensagens: {mensagens.count()}")
    
    migradas = 0
    
    for msg in mensagens:
        # Verificar se é um áudio baseado no conteúdo
        if msg.conteudo and ('audioMessage' in msg.conteudo or 'audio' in msg.conteudo.lower()):
            print(f"\n🎵 Encontrada possível mensagem de áudio ID: {msg.id}")
            
            # Se não tem tipo definido, definir como áudio
            if msg.tipo != 'audio':
                msg.tipo = 'audio'
                msg.save()
                print(f"  ✅ Tipo alterado para 'audio'")
                migradas += 1
            
            # Verificar se tem dados JSON válidos
            try:
                if msg.conteudo.startswith('{'):
                    json_data = json.loads(msg.conteudo)
                    if 'audioMessage' in json_data:
                        print(f"  ✅ Dados de áudio encontrados no JSON")
                        
                        # Extrair informações do áudio
                        audio_data = json_data['audioMessage']
                        url = audio_data.get('url')
                        duration = audio_data.get('seconds', 0)
                        
                        print(f"  📁 URL: {url}")
                        print(f"  ⏱️ Duração: {duration} segundos")
                        
            except json.JSONDecodeError:
                print(f"  ⚠️ Conteúdo não é JSON válido")
            except Exception as e:
                print(f"  ❌ Erro ao processar: {e}")
    
    print(f"\n✅ Migração concluída!")
    print(f"📊 Mensagens migradas: {migradas}")

def criar_mensagens_audio_teste():
    """Cria mensagens de áudio de teste para verificar o frontend"""
    print("\n🧪 CRIANDO MENSAGENS DE ÁUDIO DE TESTE")
    print("=" * 60)
    
    # Obter cliente e chat
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado")
        return
    
    chat = Chat.objects.filter(cliente=cliente).first()
    if not chat:
        print("❌ Nenhum chat encontrado")
        return
    
    # Dados de teste de áudio
    test_audios = [
        {
            "audioMessage": {
                "url": "https://mmg.whatsapp.net/v/t62.7117-24/11418572_639123605874985_2074276734782391920_n.enc?ccb=11-4&oh=01_Q5Aa2AH90VmSBOTtBIXsGxf0r5vMtkmkC4BsJLVg9s4HdByRdQ&oe=68B5B693&_nc_sid=5e03e0&mms3=true",
                "mimetype": "audio/ogg; codecs=opus",
                "fileSha256": "+ylX/pg8Tsa+zRJ8fgO0rpPycxdXtmLUZvZeZybjRAE=",
                "fileLength": "20718",
                "seconds": 8,
                "ptt": True,
                "mediaKey": "FnIfz9Ka/QzEPkAzlOQ9x0m3WBwUQaG265dvhLjnFl0="
            }
        },
        {
            "audioMessage": {
                "url": "https://mmg.whatsapp.net/v/t62.7117-24/11418572_639123605874985_2074276734782391920_n.enc?ccb=11-4&oh=01_Q5Aa2AH90VmSBOTtBIXsGxf0r5vMtkmkC4BsJLVg9s4HdByRdQ&oe=68B5B693&_nc_sid=5e03e0&mms3=true",
                "mimetype": "audio/ogg; codecs=opus",
                "fileSha256": "+ylX/pg8Tsa+zRJ8fgO0rpPycxdXtmLUZvZeZybjRAE=",
                "fileLength": "20718",
                "seconds": 15,
                "ptt": False,
                "mediaKey": "FnIfz9Ka/QzEPkAzlOQ9x0m3WBwUQaG265dvhLjnFl0="
            }
        }
    ]
    
    criadas = 0
    
    for i, audio_data in enumerate(test_audios):
        # Criar mensagem de teste
        test_message = Mensagem.objects.create(
            chat=chat,
            remetente="556993291093",
            conteudo=json.dumps(audio_data),
            tipo='audio',
            from_me=False,
            data_envio=timezone.now()
        )
        
        print(f"✅ Mensagem de teste {i+1} criada: {test_message.id}")
        print(f"  Tipo: {test_message.tipo}")
        print(f"  Duração: {audio_data['audioMessage']['seconds']} segundos")
        print(f"  PTT: {audio_data['audioMessage']['ptt']}")
        
        criadas += 1
    
    print(f"\n✅ {criadas} mensagens de teste criadas!")

def verificar_frontend_data():
    """Verifica como os dados apareceriam no frontend"""
    print("\n🖥️ VERIFICANDO DADOS PARA O FRONTEND")
    print("=" * 60)
    
    # Buscar mensagens de áudio
    audio_messages = Mensagem.objects.filter(tipo='audio')
    print(f"📊 Mensagens de áudio encontradas: {audio_messages.count()}")
    
    for msg in audio_messages[:5]:
        print(f"\n🎵 Mensagem ID: {msg.id}")
        
        # Dados que o frontend deve receber
        frontend_data = {
            'id': msg.id,
            'tipo': msg.tipo,
            'type': msg.tipo,
            'content': msg.conteudo,
            'fromMe': msg.from_me,
            'from_me': msg.from_me,
            'timestamp': msg.data_envio.isoformat(),
            'mediaUrl': None,
            'mediaType': 'audio',
            'duration': None
        }
        
        # Extrair dados do JSON
        try:
            json_data = json.loads(msg.conteudo)
            if 'audioMessage' in json_data:
                audio_data = json_data['audioMessage']
                frontend_data['mediaUrl'] = audio_data.get('url')
                frontend_data['duration'] = audio_data.get('seconds')
                print(f"  ✅ Dados extraídos do JSON")
                print(f"  📁 URL: {frontend_data['mediaUrl']}")
                print(f"  ⏱️ Duração: {frontend_data['duration']} segundos")
        except:
            print(f"  ⚠️ Erro ao extrair dados JSON")
        
        # Verificar se seria renderizado
        if frontend_data['tipo'] == 'audio':
            print(f"  ✅ Seria renderizado como áudio no frontend")
        else:
            print(f"  ❌ NÃO seria renderizado como áudio")

def limpar_mensagens_teste():
    """Remove mensagens de teste antigas"""
    print("\n🧹 LIMPANDO MENSAGENS DE TESTE ANTIGAS")
    print("=" * 60)
    
    # Buscar mensagens de teste (baseado no conteúdo)
    from django.db.models import Q
    test_messages = Mensagem.objects.filter(
        Q(conteudo__contains='audioMessage') & Q(conteudo__contains='mmg.whatsapp.net')
    )
    
    print(f"📊 Mensagens de teste encontradas: {test_messages.count()}")
    
    if test_messages.count() > 0:
        # Confirmar exclusão
        response = input("Deseja excluir mensagens de teste? (s/N): ")
        if response.lower() == 's':
            test_messages.delete()
            print("✅ Mensagens de teste removidas!")
        else:
            print("⚠️ Mensagens de teste mantidas")
    else:
        print("✅ Nenhuma mensagem de teste encontrada")

def main():
    """Função principal"""
    print("🎵 MIGRAÇÃO DE ÁUDIOS PARA O FRONTEND")
    print("=" * 60)
    
    try:
        # Migrar mensagens existentes
        migrar_mensagens_audio_existentes()
        
        # Criar mensagens de teste
        criar_mensagens_audio_teste()
        
        # Verificar dados para frontend
        verificar_frontend_data()
        
        # Opção de limpeza
        limpar_mensagens_teste()
        
        print("\n✅ Migração concluída!")
        print("\n💡 Para testar no frontend:")
        print("   1. Inicie o backend: python manage.py runserver")
        print("   2. Inicie o frontend: npm start")
        print("   3. Acesse um chat com mensagens de áudio")
        print("   4. Verifique se os áudios aparecem com player")
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 