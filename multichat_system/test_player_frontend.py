#!/usr/bin/env python3
"""
Script para testar o player de áudio e modal de imagem no frontend
"""

import os
import sys
import django
import requests
import json

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat
from authentication.models import Usuario as User

def testar_player_audio():
    """Testa o player de áudio no frontend"""
    print("🎵 Testando player de áudio no frontend...")
    
    # Buscar mensagens de áudio
    mensagens_audio = Mensagem.objects.filter(tipo='audio')[:3]
    
    if not mensagens_audio.exists():
        print("❌ Nenhuma mensagem de áudio encontrada!")
        return
    
    print(f"📊 Encontradas {mensagens_audio.count()} mensagens de áudio")
    
    for mensagem in mensagens_audio:
        print(f"\n🎵 Mensagem ID: {mensagem.id}")
        print(f"   Chat: {mensagem.chat.chat_id}")
        print(f"   Remetente: {mensagem.remetente}")
        print(f"   Tipo: {mensagem.tipo}")
        print(f"   Conteúdo: {mensagem.conteudo[:100]}...")
        
        # Verificar se tem media_url
        from api.serializers import MensagemSerializer
        serializer = MensagemSerializer(mensagem)
        data = serializer.data
        
        if data.get('media_url'):
            print(f"   ✅ Media URL: {data['media_url']}")
            
            # Testar se o arquivo existe
            import requests
            try:
                response = requests.head(f"http://localhost:8000{data['media_url']}")
                if response.status_code == 200:
                    print(f"   ✅ Arquivo acessível via API")
                else:
                    print(f"   ❌ Arquivo não acessível: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Erro ao acessar arquivo: {e}")
        else:
            print(f"   ❌ Sem media_url")

def testar_imagens_frontend():
    """Testa as imagens no frontend"""
    print("\n🖼️ Testando imagens no frontend...")
    
    # Buscar mensagens de imagem
    mensagens_imagem = Mensagem.objects.filter(tipo='image')[:3]
    
    if not mensagens_imagem.exists():
        print("❌ Nenhuma mensagem de imagem encontrada!")
        return
    
    print(f"📊 Encontradas {mensagens_imagem.count()} mensagens de imagem")
    
    for mensagem in mensagens_imagem:
        print(f"\n🖼️ Mensagem ID: {mensagem.id}")
        print(f"   Chat: {mensagem.chat.chat_id}")
        print(f"   Remetente: {mensagem.remetente}")
        print(f"   Tipo: {mensagem.tipo}")
        print(f"   Conteúdo: {mensagem.conteudo[:100]}...")
        
        # Verificar se tem media_url
        from api.serializers import MensagemSerializer
        serializer = MensagemSerializer(mensagem)
        data = serializer.data
        
        if data.get('media_url'):
            print(f"   ✅ Media URL: {data['media_url']}")
            
            # Testar se o arquivo existe
            try:
                response = requests.head(f"http://localhost:8000{data['media_url']}")
                if response.status_code == 200:
                    print(f"   ✅ Arquivo acessível via API")
                else:
                    print(f"   ❌ Arquivo não acessível: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Erro ao acessar arquivo: {e}")
        else:
            print(f"   ❌ Sem media_url")

def testar_api_frontend():
    """Testa a API do frontend"""
    print("\n🌐 Testando API do frontend...")
    
    # Testar endpoint de mensagens
    try:
        response = requests.get("http://localhost:8000/api/mensagens/")
        if response.status_code == 200:
            print("✅ API de mensagens funcionando")
            data = response.json()
            print(f"   Total de mensagens: {len(data)}")
        else:
            print(f"❌ API de mensagens falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar API: {e}")
    
    # Testar endpoint de chats
    try:
        response = requests.get("http://localhost:8000/api/chats/")
        if response.status_code == 200:
            print("✅ API de chats funcionando")
            data = response.json()
            print(f"   Total de chats: {len(data)}")
        else:
            print(f"❌ API de chats falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar API: {e}")

def verificar_frontend():
    """Verifica se o frontend está rodando"""
    print("\n🔍 Verificando frontend...")
    
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("✅ Frontend está rodando em http://localhost:3000")
        else:
            print(f"⚠️ Frontend retornou status: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend não está acessível: {e}")
        print("💡 Execute: cd ../multichat-frontend && npm start")

def criar_dados_teste():
    """Cria dados de teste para o frontend"""
    print("\n🧪 Criando dados de teste...")
    
    # Verificar se existe usuário admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("❌ Nenhum usuário admin encontrado!")
        return
    
    print(f"✅ Usuário admin: {admin_user.username}")
    
    # Verificar chats com mídia
    chats_com_midia = Chat.objects.filter(
        mensagens__tipo__in=['audio', 'image', 'video']
    ).distinct()
    
    print(f"📊 Chats com mídia: {chats_com_midia.count()}")
    
    for chat in chats_com_midia:
        print(f"\n📱 Chat: {chat.chat_id}")
        print(f"   Cliente: {chat.cliente.nome}")
        
        # Contar tipos de mídia
        for tipo in ['audio', 'image', 'video']:
            count = chat.mensagens.filter(tipo=tipo).count()
            if count > 0:
                print(f"   {tipo}: {count} mensagens")

def main():
    """Função principal"""
    print("🚀 Testando player de áudio e modal de imagem...")
    print("=" * 60)
    
    # Verificar frontend
    verificar_frontend()
    
    # Testar API
    testar_api_frontend()
    
    # Criar dados de teste
    criar_dados_teste()
    
    # Testar player de áudio
    testar_player_audio()
    
    # Testar imagens
    testar_imagens_frontend()
    
    print("\n" + "=" * 60)
    print("✅ Teste concluído!")
    print("\n📋 INSTRUÇÕES PARA TESTAR:")
    print("1. Acesse: http://localhost:3000")
    print("2. Faça login com usuário admin")
    print("3. Abra um chat com mensagens de áudio/imagem")
    print("4. Teste o player de áudio (play/pause/volume)")
    print("5. Clique nas imagens para abrir o modal")
    print("6. Teste zoom, rotação e download no modal")

if __name__ == "__main__":
    main() 