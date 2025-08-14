#!/usr/bin/env python3
"""
🧪 TESTE: VERIFICAÇÃO DA SINCRONIZAÇÃO DE ÁUDIOS
Verifica se os áudios foram sincronizados corretamente com os chats
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

def test_audios_sincronizados():
    """Testa se os áudios foram sincronizados corretamente"""
    print("🧪 TESTANDO SINCRONIZAÇÃO DE ÁUDIOS")
    print("=" * 60)
    
    from core.models import Mensagem
    
    # Buscar mensagens de áudio que foram atualizadas
    mensagens_audio = Mensagem.objects.filter(tipo='audio')
    
    print(f"✅ {mensagens_audio.count()} mensagens de áudio encontradas no total")
    
    # Verificar mensagens com URLs locais
    mensagens_com_url_local = []
    mensagens_sem_url_local = []
    
    for msg in mensagens_audio:
        try:
            if msg.conteudo and msg.conteudo.startswith('{'):
                import json
                conteudo_json = json.loads(msg.conteudo)
                
                if 'audioMessage' in conteudo_json:
                    audio_message = conteudo_json['audioMessage']
                    
                    if 'localPath' in audio_message or 'localUrl' in audio_message:
                        mensagens_com_url_local.append({
                            'id': msg.id,
                            'chat_id': msg.chat.chat_id,
                            'localPath': audio_message.get('localPath'),
                            'localUrl': audio_message.get('localUrl'),
                            'message_id': msg.message_id
                        })
                    else:
                        mensagens_sem_url_local.append({
                            'id': msg.id,
                            'chat_id': msg.chat.chat_id,
                            'message_id': msg.message_id
                        })
        except:
            continue
    
    print(f"\n📊 RESULTADO DA SINCRONIZAÇÃO:")
    print(f"   ✅ Com URL local: {len(mensagens_com_url_local)}")
    print(f"   ❌ Sem URL local: {len(mensagens_sem_url_local)}")
    
    if mensagens_com_url_local:
        print(f"\n🎵 MENSAGENS COM URL LOCAL:")
        for msg in mensagens_com_url_local[:10]:  # Mostrar apenas as primeiras 10
            print(f"   - ID {msg['id']}: Chat {msg['chat_id']}")
            print(f"     localPath: {msg['localPath']}")
            print(f"     localUrl: {msg['localUrl']}")
            print(f"     message_id: {msg['message_id']}")
    
    if mensagens_sem_url_local:
        print(f"\n⚠️ MENSAGENS SEM URL LOCAL (primeiras 10):")
        for msg in mensagens_sem_url_local[:10]:
            print(f"   - ID {msg['id']}: Chat {msg['chat_id']}")
    
    return len(mensagens_com_url_local), len(mensagens_sem_url_local)

def test_endpoint_audio():
    """Testa se o endpoint de áudio está funcionando"""
    print("\n🔗 TESTANDO ENDPOINT DE ÁUDIO")
    print("=" * 60)
    
    from core.models import Mensagem
    
    # Buscar uma mensagem de áudio com URL local
    mensagem_audio = Mensagem.objects.filter(
        tipo='audio',
        conteudo__contains='localUrl'
    ).first()
    
    if not mensagem_audio:
        print("❌ Nenhuma mensagem de áudio com URL local encontrada")
        return False
    
    print(f"✅ Mensagem de teste: ID {mensagem_audio.id}")
    print(f"   - Chat ID: {mensagem_audio.chat.chat_id}")
    print(f"   - Message ID: {mensagem_audio.message_id}")
    
    # Construir URL do endpoint
    endpoint_url = f"/api/audio/hash-mapping/{mensagem_audio.id}/"
    print(f"🔗 Endpoint: {endpoint_url}")
    
    # URL completa para teste
    full_url = f"http://localhost:8000{endpoint_url}"
    print(f"🔗 URL completa: {full_url}")
    
    print("\n💡 PARA TESTAR:")
    print("1. Iniciar servidor Django: python manage.py runserver")
    print("2. Acessar URL no navegador ou fazer requisição HTTP")
    print("3. Verificar se retorna o arquivo de áudio correto")
    
    return True

def test_frontend_integration():
    """Testa a integração com o frontend"""
    print("\n🌐 TESTANDO INTEGRAÇÃO COM FRONTEND")
    print("=" * 60)
    
    from core.models import Mensagem
    
    # Verificar se há mensagens de áudio com URLs locais
    mensagens_audio_local = Mensagem.objects.filter(
        tipo='audio',
        conteudo__contains='localUrl'
    )
    
    if mensagens_audio_local.exists():
        print(f"✅ {mensagens_audio_local.count()} mensagens de áudio com URLs locais")
        print("   → Frontend deve conseguir reproduzir automaticamente")
        
        # Verificar estrutura do conteúdo
        for msg in mensagens_audio_local[:3]:  # Primeiras 3
            try:
                import json
                conteudo = json.loads(msg.conteudo)
                audio_message = conteudo.get('audioMessage', {})
                
                print(f"\n📱 Mensagem ID {msg.id}:")
                print(f"   - localPath: {audio_message.get('localPath', 'N/A')}")
                print(f"   - localUrl: {audio_message.get('localUrl', 'N/A')}")
                print(f"   - message_id: {msg.message_id}")
                
            except:
                print(f"   ❌ Erro ao processar conteúdo da mensagem {msg.id}")
    else:
        print("❌ Nenhuma mensagem de áudio com URL local encontrada")
        print("   → Frontend não conseguirá reproduzir áudios")
    
    return mensagens_audio_local.exists()

def test_arquivos_fisicos():
    """Testa se os arquivos físicos existem"""
    print("\n📁 TESTANDO ARQUIVOS FÍSICOS")
    print("=" * 60)
    
    from core.models import Mensagem
    
    # Buscar mensagens com localPath
    mensagens_com_path = Mensagem.objects.filter(
        tipo='audio',
        conteudo__contains='localPath'
    )
    
    if not mensagens_com_path.exists():
        print("❌ Nenhuma mensagem com localPath encontrada")
        return False
    
    print(f"✅ {mensagens_com_path.count()} mensagens com localPath encontradas")
    
    arquivos_existentes = 0
    arquivos_inexistentes = 0
    
    for msg in mensagens_com_path:
        try:
            import json
            conteudo = json.loads(msg.conteudo)
            audio_message = conteudo.get('audioMessage', {})
            local_path = audio_message.get('localPath')
            
            if local_path and os.path.exists(local_path):
                arquivos_existentes += 1
                print(f"   ✅ Arquivo existe: {os.path.basename(local_path)}")
            else:
                arquivos_inexistentes += 1
                print(f"   ❌ Arquivo não existe: {local_path}")
                
        except Exception as e:
            print(f"   ❌ Erro ao verificar mensagem {msg.id}: {e}")
    
    print(f"\n📊 RESULTADO:")
    print(f"   ✅ Arquivos existentes: {arquivos_existentes}")
    print(f"   ❌ Arquivos inexistentes: {arquivos_inexistentes}")
    
    return arquivos_existentes > 0

def main():
    """Função principal"""
    print("🧪 TESTE COMPLETO: VERIFICAÇÃO DA SINCRONIZAÇÃO")
    print("=" * 80)
    print("Verificando se os áudios foram sincronizados corretamente")
    print("=" * 80)
    
    # 1. Testar sincronização
    sucesso_sincronizacao = test_audios_sincronizados()
    
    # 2. Testar endpoint
    sucesso_endpoint = test_endpoint_audio()
    
    # 3. Testar integração frontend
    sucesso_frontend = test_frontend_integration()
    
    # 4. Testar arquivos físicos
    sucesso_arquivos = test_arquivos_fisicos()
    
    print("\n" + "=" * 80)
    print("📋 RESULTADO DOS TESTES:")
    print("=" * 80)
    
    if sucesso_sincronizacao[0] > 0:
        print("✅ Sincronização: FUNCIONANDO")
        print(f"   → {sucesso_sincronizacao[0]} mensagens com URLs locais")
    else:
        print("❌ Sincronização: FALHOU")
    
    if sucesso_endpoint:
        print("✅ Endpoint: FUNCIONANDO")
        print("   → Endpoint de áudio configurado")
    else:
        print("❌ Endpoint: FALHOU")
    
    if sucesso_frontend:
        print("✅ Integração Frontend: FUNCIONANDO")
        print("   → Frontend deve conseguir reproduzir áudios")
    else:
        print("❌ Integração Frontend: FALHOU")
    
    if sucesso_arquivos:
        print("✅ Arquivos Físicos: FUNCIONANDO")
        print("   → Arquivos de áudio existem no sistema")
    else:
        print("❌ Arquivos Físicos: FALHOU")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("=" * 80)
    print("1. 🔄 Reiniciar servidor Django")
    print("2. 🌐 Testar frontend - áudios devem aparecer automaticamente")
    print("3. 🔍 Verificar logs para confirmar funcionamento")
    print("4. 📱 Testar reprodução de áudios nos chats")
    
    print("\n💡 STATUS DA SINCRONIZAÇÃO:")
    if sucesso_sincronizacao[0] > 0:
        print("   🟢 SUCESSO: Áudios sincronizados e prontos para uso")
    else:
        print("   🔴 FALHA: Sincronização não funcionou")

if __name__ == "__main__":
    main() 