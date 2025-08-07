#!/usr/bin/env python3
"""
Script para debugar mensagens de áudio no banco de dados
"""

import os
import sys
import django
import json
from pathlib import Path

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente

def verificar_mensagens_audio():
    """Verifica mensagens de áudio no banco de dados"""
    print("🎵 Verificando mensagens de áudio no banco de dados...")
    
    # Buscar todas as mensagens
    mensagens = Mensagem.objects.all().order_by('-data_envio')[:10]
    
    if not mensagens.exists():
        print("❌ Nenhuma mensagem encontrada no banco!")
        return
    
    print(f"📊 Total de mensagens encontradas: {mensagens.count()}")
    
    for mensagem in mensagens:
        print(f"\n📋 Mensagem ID: {mensagem.id}")
        print(f"   Chat: {mensagem.chat.chat_id}")
        print(f"   Remetente: {mensagem.remetente}")
        print(f"   Tipo: {mensagem.tipo}")
        print(f"   From Me: {mensagem.from_me}")
        print(f"   Data: {mensagem.data_envio}")
        print(f"   Conteúdo: {mensagem.conteudo[:100]}...")
        
        # Verificar se é áudio
        if mensagem.tipo == 'audio':
            print("   🎵 É uma mensagem de áudio!")
            
            # Tentar extrair dados do JSON
            try:
                conteudo_json = json.loads(mensagem.conteudo)
                if 'audioMessage' in conteudo_json:
                    audio_data = conteudo_json['audioMessage']
                    print(f"   🎵 Audio URL: {audio_data.get('url', 'N/A')}")
                    print(f"   🎵 Media Key: {audio_data.get('mediaKey', 'N/A')}")
                    print(f"   🎵 Direct Path: {audio_data.get('directPath', 'N/A')}")
            except:
                print("   ⚠️ Conteúdo não é JSON válido")
        
        # Verificar se tem audioMessage no conteúdo
        elif 'audioMessage' in mensagem.conteudo:
            print("   🎵 Contém audioMessage no conteúdo!")
            try:
                conteudo_json = json.loads(mensagem.conteudo)
                if 'audioMessage' in conteudo_json:
                    audio_data = conteudo_json['audioMessage']
                    print(f"   🎵 Audio URL: {audio_data.get('url', 'N/A')}")
            except:
                print("   ⚠️ Erro ao processar JSON")

def verificar_chats_com_audio():
    """Verifica chats que têm mensagens de áudio"""
    print("\n📱 Verificando chats com mensagens de áudio...")
    
    # Buscar chats que têm mensagens de áudio
    chats_com_audio = Chat.objects.filter(
        mensagens__tipo='audio'
    ).distinct()
    
    if not chats_com_audio.exists():
        print("❌ Nenhum chat com mensagens de áudio encontrado!")
        return
    
    print(f"📊 Total de chats com áudio: {chats_com_audio.count()}")
    
    for chat in chats_com_audio:
        print(f"\n📱 Chat: {chat.chat_id}")
        print(f"   Cliente: {chat.cliente.nome}")
        
        # Contar mensagens de áudio
        mensagens_audio = chat.mensagens.filter(tipo='audio')
        print(f"   Mensagens de áudio: {mensagens_audio.count()}")
        
        # Mostrar última mensagem de áudio
        ultima_audio = mensagens_audio.order_by('-data_envio').first()
        if ultima_audio:
            print(f"   Última áudio: {ultima_audio.data_envio}")
            print(f"   Conteúdo: {ultima_audio.conteudo[:100]}...")

def corrigir_tipos_mensagens():
    """Corrige tipos de mensagens que estão incorretos"""
    print("\n🔧 Corrigindo tipos de mensagens...")
    
    # Buscar mensagens que contêm audioMessage mas não são do tipo audio
    mensagens_para_corrigir = Mensagem.objects.filter(
        conteudo__contains='audioMessage'
    ).exclude(tipo='audio')
    
    if not mensagens_para_corrigir.exists():
        print("✅ Nenhuma mensagem precisa ser corrigida!")
        return
    
    print(f"📊 Mensagens para corrigir: {mensagens_para_corrigir.count()}")
    
    corrigidas = 0
    for mensagem in mensagens_para_corrigir:
        try:
            # Verificar se realmente contém audioMessage
            conteudo_json = json.loads(mensagem.conteudo)
            if 'audioMessage' in conteudo_json:
                # Corrigir o tipo
                mensagem.tipo = 'audio'
                mensagem.save()
                print(f"✅ Corrigida mensagem {mensagem.id}: {mensagem.tipo}")
                corrigidas += 1
        except:
            print(f"⚠️ Erro ao processar mensagem {mensagem.id}")
    
    print(f"✅ Total corrigidas: {corrigidas}")

def criar_mensagem_audio_teste():
    """Cria uma mensagem de áudio de teste"""
    print("\n🧪 Criando mensagem de áudio de teste...")
    
    # Buscar cliente e chat
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado!")
        return
    
    chat = Chat.objects.filter(cliente=cliente).first()
    if not chat:
        print("❌ Nenhum chat encontrado!")
        return
    
    # Dados de áudio de teste
    audio_data = {
        'audioMessage': {
            'url': 'https://mmg.whatsapp.net/v/t62.7117-24/19083661_1303226854859439_3997981883652895124_n.enc?ccb=11-4&oh=01_Q5Aa2AHv1g25E-1H3jqetiO5I0A7GCCp1SbCxNT7hCJBPKZhJw&oe=68BB4268&_nc_sid=5e03e0&mms3=true',
            'mediaKey': 'TEST_MEDIA_KEY',
            'directPath': '/v/t62.7117-24/19083661_1303226854859439_3997981883652895124_n.enc?ccb=11-4&oh=01_Q5Aa2AHv1g25E-1H3jqetiO5I0A7GCCp1SbCxNT7hCJBPKZhJw&oe=68BB4268&_nc_sid=5e03e0',
            'mimetype': 'audio/ogg',
            'fileLength': '4478',
            'isPtt': True
        }
    }
    
    try:
        mensagem = Mensagem.objects.create(
            chat=chat,
            remetente="Teste Áudio",
            conteudo=json.dumps(audio_data, ensure_ascii=False),
            tipo='audio',
            lida=False,
            from_me=False,
            message_id="test_audio_debug"
        )
        print(f"✅ Mensagem de teste criada: ID={mensagem.id}")
        print(f"   Tipo: {mensagem.tipo}")
        print(f"   Conteúdo: {mensagem.conteudo[:100]}...")
        
    except Exception as e:
        print(f"❌ Erro ao criar mensagem de teste: {e}")

def main():
    """Função principal"""
    print("🚀 Debug de mensagens de áudio...")
    print("=" * 60)
    
    # Verificar mensagens existentes
    verificar_mensagens_audio()
    
    # Verificar chats com áudio
    verificar_chats_com_audio()
    
    # Corrigir tipos incorretos
    corrigir_tipos_mensagens()
    
    # Criar mensagem de teste
    criar_mensagem_audio_teste()
    
    print("\n" + "=" * 60)
    print("✅ Debug concluído!")

if __name__ == "__main__":
    main() 