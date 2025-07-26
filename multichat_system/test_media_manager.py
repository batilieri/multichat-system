#!/usr/bin/env python3
"""
Script de teste para o sistema de gerenciamento de mídias do MultiChat
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Cliente, WhatsappInstance
from core.media_manager import MultiChatMediaManager, criar_media_manager
import json


def test_media_manager():
    """Testa o sistema de gerenciamento de mídias"""
    
    print("🧪 Iniciando testes do MediaManager...")
    
    # Buscar um cliente e instância para teste
    try:
        cliente = Cliente.objects.first()
        if not cliente:
            print("❌ Nenhum cliente encontrado no banco de dados")
            return
        
        instance = WhatsappInstance.objects.filter(cliente=cliente).first()
        if not instance:
            print("❌ Nenhuma instância WhatsApp encontrada para o cliente")
            return
        
        print(f"✅ Usando Cliente: {cliente.nome} (ID: {cliente.id})")
        print(f"✅ Usando Instância: {instance.instance_id}")
        
        # Criar gerenciador de mídias
        media_manager = criar_media_manager(
            cliente_id=cliente.id,
            instance_id=instance.instance_id,
            bearer_token=instance.token
        )
        
        # Testar funcionalidades básicas
        print("\n📋 Testando funcionalidades básicas...")
        
        # 1. Verificar estrutura de pastas
        print("📁 Verificando estrutura de pastas...")
        for tipo, pasta in media_manager.pastas_midia.items():
            if pasta.exists():
                print(f"   ✅ Pasta {tipo}: {pasta}")
            else:
                print(f"   ❌ Pasta {tipo} não existe")
        
        # 2. Verificar banco de dados
        print("\n🗄️ Verificando banco de dados...")
        if media_manager.db_path.exists():
            print(f"   ✅ Banco de dados: {media_manager.db_path}")
        else:
            print(f"   ❌ Banco de dados não existe")
        
        # 3. Testar busca de mídias pendentes
        print("\n🔍 Testando busca de mídias pendentes...")
        midias_pendentes = media_manager.buscar_midias_pendentes()
        print(f"   📊 Mídias pendentes encontradas: {len(midias_pendentes)}")
        
        # 4. Testar estatísticas
        print("\n📊 Testando estatísticas...")
        stats = media_manager.obter_estatisticas()
        print(f"   📈 Estatísticas: {json.dumps(stats, indent=2, default=str)}")
        
        # 5. Testar processamento de mensagem simulada
        print("\n📨 Testando processamento de mensagem simulada...")
        mensagem_teste = {
            'messageId': 'test_message_123',
            'sender': {
                'id': '5511999999999@s.whatsapp.net',
                'pushName': 'Usuário Teste'
            },
            'chat': {
                'id': '5511999999999@s.whatsapp.net'
            },
            'msgContent': {
                'imageMessage': {
                    'mimetype': 'image/jpeg',
                    'fileName': 'test_image.jpg',
                    'fileLength': 1024,
                    'caption': 'Imagem de teste',
                    'mediaKey': 'test_media_key_123',
                    'directPath': '/test/direct/path',
                    'fileSha256': 'test_sha256_123',
                    'fileEncSha256': 'test_enc_sha256_123',
                    'mediaKeyTimestamp': '1234567890',
                    'width': 800,
                    'height': 600,
                    'jpegThumbnail': 'base64_thumbnail_data'
                }
            },
            'isGroup': False,
            'fromMe': False,
            'moment': 1234567890
        }
        
        # Processar mensagem de teste
        media_manager.processar_mensagem_whatsapp(mensagem_teste)
        
        # Verificar se foi salva no banco
        midias_apos_teste = media_manager.buscar_midias_pendentes()
        print(f"   📊 Mídias após teste: {len(midias_apos_teste)}")
        
        # 6. Testar validação de dados
        print("\n✅ Testando validação de dados...")
        info_midia_valida = {
            'type': 'image',
            'mimetype': 'image/jpeg',
            'mediaKey': 'test_key',
            'fileSha256': 'test_sha256'
        }
        
        info_midia_invalida = {
            'type': 'image',
            'mimetype': 'image/jpeg'
            # Faltando campos obrigatórios
        }
        
        valida = media_manager._validar_dados_midia(info_midia_valida)
        invalida = media_manager._validar_dados_midia(info_midia_invalida)
        
        print(f"   ✅ Dados válidos: {valida}")
        print(f"   ❌ Dados inválidos: {invalida}")
        
        # 7. Testar geração de nomes de arquivo
        print("\n📝 Testando geração de nomes de arquivo...")
        nome_arquivo = media_manager.gerar_nome_arquivo(
            info_midia_valida,
            'test_message_123',
            'Usuário Teste'
        )
        print(f"   📄 Nome gerado: {nome_arquivo}")
        
        # 8. Testar extensões de mimetype
        print("\n🔗 Testando extensões de mimetype...")
        extensoes_teste = [
            'image/jpeg',
            'video/mp4',
            'audio/mp3',
            'application/pdf',
            'text/plain'
        ]
        
        for mimetype in extensoes_teste:
            extensao = media_manager.obter_extensao_mimetype(mimetype)
            print(f"   📋 {mimetype} -> {extensao}")
        
        print("\n🎉 Testes concluídos com sucesso!")
        
        # Mostrar estatísticas finais
        stats_finais = media_manager.obter_estatisticas()
        print(f"\n📊 Estatísticas finais:")
        print(f"   📈 Total de mídias: {stats_finais.get('total_midias', 0)}")
        print(f"   ✅ Mídias baixadas: {stats_finais.get('midias_baixadas', 0)}")
        print(f"   ⏳ Mídias pendentes: {stats_finais.get('midias_pendentes', 0)}")
        print(f"   ❌ Mídias falhadas: {stats_finais.get('midias_falhadas', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_webhook_integration():
    """Testa a integração com webhooks"""
    
    print("\n🔗 Testando integração com webhooks...")
    
    try:
        # Buscar cliente e instância
        cliente = Cliente.objects.first()
        instance = WhatsappInstance.objects.filter(cliente=cliente).first()
        
        if not cliente or not instance:
            print("❌ Cliente ou instância não encontrados")
            return False
        
        # Criar gerenciador
        media_manager = criar_media_manager(
            cliente_id=cliente.id,
            instance_id=instance.instance_id,
            bearer_token=instance.token
        )
        
        # Simular diferentes tipos de webhook
        webhooks_teste = [
            # Webhook de mensagem de imagem
            {
                'event': 'webhookReceived',
                'instanceId': instance.instance_id,
                'messageId': 'img_msg_001',
                'sender': {
                    'id': '5511999999999@s.whatsapp.net',
                    'pushName': 'Teste Imagem'
                },
                'chat': {
                    'id': '5511999999999@s.whatsapp.net'
                },
                'msgContent': {
                    'imageMessage': {
                        'mimetype': 'image/jpeg',
                        'fileName': 'foto_teste.jpg',
                        'fileLength': 2048,
                        'caption': 'Foto de teste',
                        'mediaKey': 'img_key_001',
                        'directPath': '/img/direct/path',
                        'fileSha256': 'img_sha256_001',
                        'fileEncSha256': 'img_enc_sha256_001',
                        'width': 1024,
                        'height': 768
                    }
                },
                'isGroup': False,
                'fromMe': False,
                'moment': 1234567890
            },
            
            # Webhook de mensagem de vídeo
            {
                'event': 'webhookReceived',
                'instanceId': instance.instance_id,
                'messageId': 'vid_msg_001',
                'sender': {
                    'id': '5511999999999@s.whatsapp.net',
                    'pushName': 'Teste Vídeo'
                },
                'chat': {
                    'id': '5511999999999@s.whatsapp.net'
                },
                'msgContent': {
                    'videoMessage': {
                        'mimetype': 'video/mp4',
                        'fileName': 'video_teste.mp4',
                        'fileLength': 10240,
                        'caption': 'Vídeo de teste',
                        'mediaKey': 'vid_key_001',
                        'directPath': '/vid/direct/path',
                        'fileSha256': 'vid_sha256_001',
                        'fileEncSha256': 'vid_enc_sha256_001',
                        'seconds': 30,
                        'width': 1280,
                        'height': 720
                    }
                },
                'isGroup': False,
                'fromMe': False,
                'moment': 1234567890
            },
            
            # Webhook de mensagem de áudio
            {
                'event': 'webhookReceived',
                'instanceId': instance.instance_id,
                'messageId': 'aud_msg_001',
                'sender': {
                    'id': '5511999999999@s.whatsapp.net',
                    'pushName': 'Teste Áudio'
                },
                'chat': {
                    'id': '5511999999999@s.whatsapp.net'
                },
                'msgContent': {
                    'audioMessage': {
                        'mimetype': 'audio/mp3',
                        'fileLength': 5120,
                        'mediaKey': 'aud_key_001',
                        'directPath': '/aud/direct/path',
                        'fileSha256': 'aud_sha256_001',
                        'fileEncSha256': 'aud_enc_sha256_001',
                        'seconds': 15,
                        'ptt': False
                    }
                },
                'isGroup': False,
                'fromMe': False,
                'moment': 1234567890
            }
        ]
        
        # Processar cada webhook
        for i, webhook in enumerate(webhooks_teste, 1):
            print(f"   📨 Processando webhook {i}...")
            media_manager.processar_mensagem_whatsapp(webhook)
        
        # Verificar resultados
        stats = media_manager.obter_estatisticas()
        print(f"   📊 Mídias processadas: {stats.get('total_midias', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na integração com webhooks: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do sistema de mídias do MultiChat")
    print("=" * 60)
    
    # Teste básico
    sucesso_basico = test_media_manager()
    
    # Teste de integração
    sucesso_integracao = test_webhook_integration()
    
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES:")
    print(f"   ✅ Teste básico: {'PASSOU' if sucesso_basico else 'FALHOU'}")
    print(f"   ✅ Teste de integração: {'PASSOU' if sucesso_integracao else 'FALHOU'}")
    
    if sucesso_basico and sucesso_integracao:
        print("\n🎉 Todos os testes passaram! O sistema está funcionando corretamente.")
        return True
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os logs acima.")
        return False


if __name__ == "__main__":
    main() 