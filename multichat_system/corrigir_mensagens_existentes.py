#!/usr/bin/env python
"""
Script para corrigir mensagens existentes que têm conteúdo JSON
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem, Cliente

def corrigir_mensagens_existentes():
    """Corrige mensagens existentes que têm conteúdo JSON"""
    print("🔧 Corrigindo mensagens existentes...")
    print("=" * 50)
    
    # Buscar mensagens que podem ter conteúdo JSON
    mensagens = Mensagem.objects.all()
    print(f"Total de mensagens: {mensagens.count()}")
    
    corrigidas = 0
    
    for msg in mensagens:
        if not msg.conteudo:
            continue
            
        # Verificar se o conteúdo parece ser JSON
        conteudo = msg.conteudo.strip()
        if conteudo.startswith('{') and conteudo.endswith('}'):
            try:
                json_content = json.loads(conteudo)
                print(f"📄 Mensagem {msg.id} tem JSON válido")
                
                # Verificar se é uma mensagem de mídia
                if 'imageMessage' in json_content:
                    print(f"   📷 Imagem detectada")
                    # Atualizar o tipo se necessário
                    if msg.tipo != 'image':
                        msg.tipo = 'image'
                        print(f"   ✅ Tipo corrigido para 'image'")
                elif 'videoMessage' in json_content:
                    print(f"   🎥 Vídeo detectado")
                    if msg.tipo != 'video':
                        msg.tipo = 'video'
                        print(f"   ✅ Tipo corrigido para 'video'")
                elif 'audioMessage' in json_content:
                    print(f"   🎵 Áudio detectado")
                    if msg.tipo != 'audio':
                        msg.tipo = 'audio'
                        print(f"   ✅ Tipo corrigido para 'audio'")
                elif 'documentMessage' in json_content:
                    print(f"   📄 Documento detectado")
                    if msg.tipo != 'document':
                        msg.tipo = 'document'
                        print(f"   ✅ Tipo corrigido para 'document'")
                elif 'stickerMessage' in json_content:
                    print(f"   😀 Sticker detectado")
                    if msg.tipo != 'sticker':
                        msg.tipo = 'sticker'
                        print(f"   ✅ Tipo corrigido para 'sticker'")
                
                corrigidas += 1
                
            except json.JSONDecodeError:
                print(f"❌ Mensagem {msg.id} tem JSON inválido")
    
    print(f"\n✅ Total de mensagens corrigidas: {corrigidas}")
    
    # Verificar mensagens que podem ter conteúdo JSON mas não estão sendo detectadas
    print(f"\n🔍 Verificando mensagens com possível conteúdo JSON...")
    
    mensagens_suspeitas = Mensagem.objects.filter(
        conteudo__contains='imageMessage'
    ).exclude(tipo='image')
    
    print(f"Mensagens com 'imageMessage' mas tipo incorreto: {mensagens_suspeitas.count()}")
    
    for msg in mensagens_suspeitas[:5]:  # Mostrar apenas as primeiras 5
        print(f"   📄 ID: {msg.id}, Tipo: {msg.tipo}, Conteúdo: {msg.conteudo[:100]}...")

if __name__ == "__main__":
    corrigir_mensagens_existentes() 