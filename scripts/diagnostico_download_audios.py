#!/usr/bin/env python3
"""
Diagnóstico do Sistema de Download Automático de Áudios
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
django.setup()

from core.models import Cliente, Chat, Mensagem
from webhook.models import WebhookEvent
import json
from pathlib import Path

def verificar_configuracao_cliente():
    """Verifica a configuração do cliente"""
    print("🔧 VERIFICANDO CONFIGURAÇÃO DO CLIENTE")
    print("=" * 60)
    
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado!")
        return False
    
    print(f"✅ Cliente encontrado: {cliente.nome}")
    print(f"   ID: {cliente.id}")
    print(f"   Status: {cliente.status}")
    print(f"   WAPI Instance ID: {cliente.wapi_instance_id}")
    print(f"   WAPI Token: {cliente.wapi_token[:20] if cliente.wapi_token else 'Nenhum'}...")
    
    # Verificar se tem configuração completa
    if not cliente.wapi_token or not cliente.wapi_instance_id:
        print("❌ Configuração W-API incompleta!")
        return False
    
    print("✅ Configuração W-API completa")
    return True

def verificar_mensagens_audio():
    """Verifica mensagens de áudio no banco"""
    print("\n🎵 VERIFICANDO MENSAGENS DE ÁUDIO")
    print("=" * 60)
    
    # Buscar mensagens de áudio
    audio_messages = Mensagem.objects.filter(tipo='audio')
    print(f"📊 Total de mensagens de áudio: {audio_messages.count()}")
    
    if audio_messages.count() == 0:
        print("⚠️ Nenhuma mensagem de áudio encontrada")
        return
    
    # Analisar algumas mensagens
    for msg in audio_messages[:3]:
        print(f"\n🎵 Mensagem ID: {msg.id}")
        print(f"   Chat: {msg.chat.chat_id}")
        print(f"   Remetente: {msg.remetente}")
        print(f"   Data: {msg.data_envio}")
        print(f"   Conteúdo: {msg.conteudo[:100]}...")
        
        # Verificar dados do áudio
        try:
            json_data = json.loads(msg.conteudo)
            if 'audioMessage' in json_data:
                audio_data = json_data['audioMessage']
                print(f"   ✅ Dados do áudio:")
                print(f"      URL: {audio_data.get('url', 'N/A')}")
                print(f"      MediaKey: {audio_data.get('mediaKey', 'N/A')}")
                print(f"      DirectPath: {audio_data.get('directPath', 'N/A')}")
                print(f"      Mimetype: {audio_data.get('mimetype', 'N/A')}")
            else:
                print(f"   ⚠️ Não contém audioMessage")
        except:
            print(f"   ❌ Erro ao processar JSON")

def verificar_webhooks_recentes():
    """Verifica webhooks recentes"""
    print("\n📡 VERIFICANDO WEBHOOKS RECENTES")
    print("=" * 60)
    
    # Buscar webhooks recentes
    webhooks = WebhookEvent.objects.all().order_by('-timestamp')[:5]
    print(f"📊 Webhooks recentes: {webhooks.count()}")
    
    for webhook in webhooks:
        print(f"\n📡 Webhook ID: {webhook.id}")
        print(f"   Tipo: {webhook.event_type}")
        print(f"   Data: {webhook.timestamp}")
        print(f"   Dados: {webhook.raw_data[:100]}...")
        
        # Verificar se contém áudio
        try:
            data = json.loads(webhook.raw_data)
            if 'msgContent' in data:
                msg_content = data['msgContent']
                if 'audioMessage' in msg_content:
                    print(f"   🎵 CONTÉM ÁUDIO!")
                    audio_data = msg_content['audioMessage']
                    print(f"      URL: {audio_data.get('url', 'N/A')}")
                    print(f"      MediaKey: {audio_data.get('mediaKey', 'N/A')}")
                else:
                    print(f"   ⚠️ Não contém áudio")
        except:
            print(f"   ❌ Erro ao processar dados")

def verificar_estrutura_pastas():
    """Verifica a estrutura de pastas de mídia"""
    print("\n📁 VERIFICANDO ESTRUTURA DE PASTAS")
    print("=" * 60)
    
    # Verificar pasta de mídia
    media_path = Path("multichat_system/media_storage")
    if not media_path.exists():
        print("❌ Pasta media_storage não encontrada!")
        return
    
    print(f"✅ Pasta media_storage encontrada")
    
    # Verificar estrutura de clientes
    for cliente_dir in media_path.glob("cliente_*"):
        print(f"\n👤 Cliente: {cliente_dir.name}")
        
        # Verificar instâncias
        for instance_dir in cliente_dir.glob("instance_*"):
            print(f"   📱 Instância: {instance_dir.name}")
            
            # Verificar tipos de mídia
            for media_type in ['audio', 'imagens', 'videos', 'documentos']:
                media_dir = instance_dir / media_type
                if media_dir.exists():
                    files = list(media_dir.glob("*"))
                    print(f"      {media_type}: {len(files)} arquivos")
                else:
                    print(f"      {media_type}: pasta não existe")

def testar_download_automatico():
    """Testa o download automático"""
    print("\n🧪 TESTANDO DOWNLOAD AUTOMÁTICO")
    print("=" * 60)
    
    # Buscar uma mensagem de áudio para teste
    audio_message = Mensagem.objects.filter(tipo='audio').first()
    if not audio_message:
        print("❌ Nenhuma mensagem de áudio para testar")
        return
    
    print(f"🎵 Testando com mensagem ID: {audio_message.id}")
    
    try:
        # Extrair dados do áudio
        json_data = json.loads(audio_message.conteudo)
        if 'audioMessage' in json_data:
            audio_data = json_data['audioMessage']
            
            # Verificar campos necessários
            campos_necessarios = ['mediaKey', 'directPath', 'mimetype']
            campos_presentes = []
            
            for campo in campos_necessarios:
                if audio_data.get(campo):
                    campos_presentes.append(campo)
                    print(f"   ✅ {campo}: {audio_data[campo][:20]}...")
                else:
                    print(f"   ❌ {campo}: ausente")
            
            if len(campos_presentes) == len(campos_necessarios):
                print("✅ Todos os campos necessários estão presentes!")
                print("💡 O download automático deve funcionar")
            else:
                print("❌ Campos necessários ausentes!")
                print("💡 Isso pode estar impedindo o download automático")
        else:
            print("❌ Não contém dados de áudio válidos")
            
    except Exception as e:
        print(f"❌ Erro ao testar: {e}")

def main():
    """Função principal"""
    print("🔍 DIAGNÓSTICO DO SISTEMA DE DOWNLOAD AUTOMÁTICO DE ÁUDIOS")
    print("=" * 80)
    
    try:
        # Verificar configuração
        config_ok = verificar_configuracao_cliente()
        
        # Verificar mensagens
        verificar_mensagens_audio()
        
        # Verificar webhooks
        verificar_webhooks_recentes()
        
        # Verificar estrutura
        verificar_estrutura_pastas()
        
        # Testar download
        testar_download_automatico()
        
        print("\n" + "=" * 80)
        print("✅ DIAGNÓSTICO CONCLUÍDO!")
        
        if config_ok:
            print("💡 SUGESTÕES:")
            print("   1. Verifique se os webhooks estão chegando")
            print("   2. Confirme se as credenciais W-API estão corretas")
            print("   3. Teste enviando um áudio real no WhatsApp")
            print("   4. Verifique os logs do Django para erros")
        else:
            print("❌ PROBLEMAS ENCONTRADOS:")
            print("   1. Configure o cliente com W-API Token e Instance ID")
            print("   2. Verifique se a instância está conectada")
            print("   3. Teste a conexão com a API W-API")
        
    except Exception as e:
        print(f"❌ Erro no diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 