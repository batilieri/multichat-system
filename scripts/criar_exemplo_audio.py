#!/usr/bin/env python3
"""
Script para criar exemplo de mensagem de áudio para teste
"""

import os
import sys
import django
import shutil

# Configurar Django
sys.path.append('multichat_system')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente
from datetime import datetime

def criar_exemplo_audio():
    print("Criando exemplo de mensagem de audio...")
    
    # 1. Copiar áudio de exemplo
    source_audio = os.path.join('backup_atual', 'multichat-frontend', 'public', 'files', 'audio.m4a')
    dest_dir = os.path.join('multichat_system', 'media', 'audios', '1')
    dest_audio = os.path.join(dest_dir, 'audio_exemplo_teste.mp3')
    
    os.makedirs(dest_dir, exist_ok=True)
    
    if os.path.exists(source_audio):
        shutil.copy2(source_audio, dest_audio)
        print(f"Audio copiado: {dest_audio}")
    else:
        print("Audio de exemplo nao encontrado, criando placeholder...")
        # Criar arquivo vazio como placeholder
        with open(dest_audio, 'w') as f:
            f.write("")
    
    # 2. Buscar ou criar cliente
    try:
        cliente = Cliente.objects.first()
        if not cliente:
            cliente = Cliente.objects.create(
                nome="Cliente Teste",
                telefone="+5511999999999"
            )
            print(f"Cliente criado: {cliente.nome}")
    except Exception as e:
        print(f"Erro ao criar cliente: {e}")
        return
    
    # 3. Buscar ou criar chat
    try:
        chat = Chat.objects.filter(cliente=cliente).first()
        if not chat:
            chat = Chat.objects.create(
                cliente=cliente,
                chat_id="5511999999999",
                chat_name="Chat de Teste"
            )
            print(f"Chat criado: {chat.chat_name}")
    except Exception as e:
        print(f"Erro ao criar chat: {e}")
        return
    
    # 4. Criar mensagem de áudio
    try:
        # Deletar mensagem existente se houver
        Mensagem.objects.filter(
            chat=chat,
            tipo='audio'
        ).delete()
        
        mensagem = Mensagem.objects.create(
            chat=chat,
            remetente="Teste",
            conteudo='{"audioMessage": {"url": "/media/audios/1/audio_exemplo_teste.mp3", "seconds": 10}}',
            tipo='audio',
            from_me=False,
            data_envio=datetime.now()
        )
        
        print(f"Mensagem de audio criada:")
        print(f"  ID: {mensagem.id}")
        print(f"  Tipo: {mensagem.tipo}")
        print(f"  Conteudo: {mensagem.conteudo}")
        print(f"  Chat: {mensagem.chat.chat_name}")
        
        # 5. Dados para o frontend
        frontend_data = {
            'id': mensagem.id,
            'tipo': 'audio',
            'type': 'audio',
            'content': '[Audio]',
            'conteudo': mensagem.conteudo,
            'mediaUrl': '/media/audios/1/audio_exemplo_teste.mp3',
            'mediaType': 'audio',
            'fromMe': mensagem.from_me,
            'timestamp': str(mensagem.data_envio)
        }
        
        print("\nDados JSON para frontend:")
        import json
        print(json.dumps(frontend_data, indent=2, ensure_ascii=False))
        
        print("\nURLs de teste:")
        print(f"Direct: http://localhost:8000/media/audios/1/audio_exemplo_teste.mp3")
        print(f"API: http://localhost:8000/api/audio/message/{mensagem.id}/")
        
        return mensagem
        
    except Exception as e:
        print(f"Erro ao criar mensagem: {e}")
        return None

if __name__ == '__main__':
    criar_exemplo_audio()