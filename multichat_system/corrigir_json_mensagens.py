#!/usr/bin/env python
"""
Script para corrigir mensagens com JSON inválido
"""

import os
import sys
import django
import json
import ast

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Mensagem, Cliente

def corrigir_json_mensagens():
    """Corrige mensagens com JSON inválido"""
    print("🔧 Corrigindo mensagens com JSON inválido...")
    print("=" * 50)
    
    # Buscar mensagens que podem ter JSON inválido
    mensagens = Mensagem.objects.filter(conteudo__startswith='{')
    print(f"Total de mensagens com possível JSON: {mensagens.count()}")
    
    corrigidas = 0
    
    for msg in mensagens:
        if not msg.conteudo:
            continue
            
        conteudo = msg.conteudo.strip()
        
        # Tentar parsear como JSON
        try:
            json.loads(conteudo)
            # Se chegou aqui, o JSON é válido
            continue
        except json.JSONDecodeError:
            # JSON inválido, tentar corrigir
            print(f"🔧 Corrigindo mensagem {msg.id}...")
            
            try:
                # Tentar usar ast.literal_eval para converter string Python para dict
                if conteudo.startswith('{') and conteudo.endswith('}'):
                    # Substituir aspas simples por aspas duplas
                    conteudo_corrigido = conteudo.replace("'", '"')
                    
                    # Tentar parsear novamente
                    try:
                        json.loads(conteudo_corrigido)
                        # Se chegou aqui, a correção funcionou
                        msg.conteudo = conteudo_corrigido
                        msg.save(update_fields=['conteudo'])
                        print(f"   ✅ JSON corrigido para mensagem {msg.id}")
                        corrigidas += 1
                    except json.JSONDecodeError:
                        print(f"   ❌ Não foi possível corrigir JSON da mensagem {msg.id}")
                        
                        # Verificar se é uma mensagem de mídia
                        if 'imageMessage' in conteudo and msg.tipo != 'image':
                            msg.tipo = 'image'
                            msg.save(update_fields=['tipo'])
                            print(f"   ✅ Tipo corrigido para 'image'")
                        elif 'videoMessage' in conteudo and msg.tipo != 'video':
                            msg.tipo = 'video'
                            msg.save(update_fields=['tipo'])
                            print(f"   ✅ Tipo corrigido para 'video'")
                        elif 'audioMessage' in conteudo and msg.tipo != 'audio':
                            msg.tipo = 'audio'
                            msg.save(update_fields=['tipo'])
                            print(f"   ✅ Tipo corrigido para 'audio'")
                        elif 'documentMessage' in conteudo and msg.tipo != 'document':
                            msg.tipo = 'document'
                            msg.save(update_fields=['tipo'])
                            print(f"   ✅ Tipo corrigido para 'document'")
                        elif 'stickerMessage' in conteudo and msg.tipo != 'sticker':
                            msg.tipo = 'sticker'
                            msg.save(update_fields=['tipo'])
                            print(f"   ✅ Tipo corrigido para 'sticker'")
                        
            except Exception as e:
                print(f"   ❌ Erro ao corrigir mensagem {msg.id}: {e}")
    
    print(f"\n✅ Total de mensagens corrigidas: {corrigidas}")
    
    # Verificar mensagens de imagem especificamente
    print(f"\n🔍 Verificando mensagens de imagem...")
    mensagens_imagem = Mensagem.objects.filter(tipo='image')
    print(f"Total de mensagens de imagem: {mensagens_imagem.count()}")
    
    for msg in mensagens_imagem[:3]:  # Mostrar apenas as primeiras 3
        print(f"   📸 ID: {msg.id}, Conteúdo: {msg.conteudo[:100]}...")
        
        # Verificar se tem URL de imagem
        if msg.conteudo and 'imageMessage' in msg.conteudo:
            try:
                if msg.conteudo.startswith('{'):
                    json_content = json.loads(msg.conteudo)
                    if 'imageMessage' in json_content:
                        image_url = json_content['imageMessage'].get('url', 'N/A')
                        print(f"      📷 URL: {image_url[:50]}...")
            except:
                print(f"      ❌ Erro ao processar JSON")

if __name__ == "__main__":
    corrigir_json_mensagens() 