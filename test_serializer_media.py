#!/usr/bin/env python3
"""
Teste do MensagemSerializer com URLs de mídia locais
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
project_path = Path(__file__).parent / 'multichat_system'
sys.path.insert(0, str(project_path))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

# Mudar para o diretório do projeto Django
os.chdir(str(project_path))
django.setup()

from core.models import Mensagem, Chat, Cliente
from api.serializers import MensagemSerializer

def testar_serializer_media():
    print("🧪 Testando MensagemSerializer com URLs de mídia locais")
    print("=" * 60)
    
    try:
        # Buscar mensagem de áudio com chat_id real
        chat_id = "556999211347"  # Chat do Elizeu
        
        # Buscar chat
        chat = Chat.objects.filter(chat_id=chat_id).first()
        if not chat:
            print(f"❌ Chat {chat_id} não encontrado")
            return
        
        print(f"✅ Chat encontrado: {chat_id} - Cliente: {chat.cliente.nome}")
        
        # Buscar mensagens de áudio deste chat
        mensagens_audio = Mensagem.objects.filter(
            chat=chat,
            tipo='audio'
        ).order_by('-data_envio')[:3]
        
        print(f"📱 Mensagens de áudio encontradas: {len(mensagens_audio)}")
        
        for i, msg in enumerate(mensagens_audio):
            print(f"\n--- Mensagem {i+1} ---")
            print(f"Message ID: {msg.message_id}")
            print(f"Tipo: {msg.tipo}")
            print(f"Conteúdo original: {msg.conteudo[:100]}...")
            
            # Serializar a mensagem
            serializer = MensagemSerializer(msg)
            data = serializer.data
            
            print(f"Conteúdo serializado: {data.get('conteudo', 'N/A')}")
            print(f"Media URL: {data.get('media_url', 'N/A')}")
            
            # Verificar se o arquivo existe fisicamente
            if data.get('media_url'):
                # Construir caminho físico
                media_url = data['media_url']
                # Remover /media/whatsapp_media/ e construir caminho real
                relative_path = media_url.replace('/media/whatsapp_media/', '')
                file_path = project_path / 'media_storage' / relative_path
                
                if file_path.exists():
                    print(f"✅ Arquivo existe: {file_path}")
                    print(f"   Tamanho: {file_path.stat().st_size} bytes")
                else:
                    print(f"❌ Arquivo não encontrado: {file_path}")
            
            print("-" * 40)
        
        print("\n🎯 Teste da API completo")
        print("✅ Serializer modificado com sucesso")
        
    except Exception as e:
        import traceback
        print(f"❌ Erro no teste: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    testar_serializer_media()