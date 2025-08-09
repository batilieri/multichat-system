#!/usr/bin/env python3
"""
🧪 TESTE DOWNLOAD WEBHOOK CORRIGIDO
Simula o webhook real que você enviou para testar se as correções funcionaram
"""

import os
import sys
import django
import json
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

from webhook.views import process_webhook_message

def simular_webhook_real():
    """Simula exatamente o webhook que você enviou"""
    print("🧪 SIMULANDO WEBHOOK REAL - ÁUDIO")
    print("=" * 60)
    
    # Dados exatos do webhook que você enviou
    webhook_data = {
        "event": "webhookDelivery",
        "instanceId": "3B6XIW-ZTS923-GEAY6V",
        "connectedPhone": "556993291093",
        "connectedLid": "176488829694091@lid",
        "isGroup": False,
        "messageId": "E93A86D6119804FE8714DF3CAED360B6",
        "fromMe": True,
        "chat": {
            "id": "556999267344",
            "profilePicture": "https://pps.whatsapp.net/v/t61.24694-24/462429652_2229319410767469_7773187573644695635_n.jpg?ccb=11-4&oh=01_Q5Aa2QF5cPihflgr_oRaYQ_iIuVHGYIxOFqoc8RSQBIhoOJlPg&oe=68A4AB6F&_nc_sid=5e03e0&_nc_cat=100"
        },
        "sender": {
            "id": "556993291093",
            "profilePicture": "https://pps.whatsapp.net/v/t61.24694-24/462189315_448942584891093_7781840178101974754_n.jpg?ccb=11-4&oh=01_Q5Aa2QE_Jb9o7FTPD60chVFK5FGYT5CVIBUsa1HMFpoB8ugu5g&oe=68A49592&_nc_sid=5e03e0&_nc_cat=103",
            "pushName": "Elizeu",
            "verifiedBizName": ""
        },
        "moment": 1754764919,
        "fromApi": False,
        "msgContent": {
            "audioMessage": {
                "url": "https://mmg.whatsapp.net/v/t62.7117-24/530121278_763400350189604_2525529204231189072_n.enc?ccb=11-4&oh=01_Q5Aa2QGGVq0dHKQ6Y09ZtySxlDjFIXvcEG1EWD_Js8avMyPoNg&oe=68BEF50F&_nc_sid=5e03e0&mms3=true",
                "mimetype": "audio/ogg; codecs=opus",
                "fileSha256": "0+XYjwWLjrIypHbFEhgD4f9OqH58Rrqg/9wnVwdXAaY=",
                "fileLength": "5691",
                "seconds": 2,
                "ptt": True,
                "mediaKey": "cMVqM8QbTKnLurfZBhJVKYy5UkA+9u/kID1py3kVA6Y=",
                "fileEncSha256": "3X/rpn27b+QZfkONpTSc/6njVhTuwEq2C3HwkRZB3Hk=",
                "directPath": "/v/t62.7117-24/530121278_763400350189604_2525529204231189072_n.enc?ccb=11-4&oh=01_Q5Aa2QGGVq0dHKQ6Y09ZtySxlDjFIXvcEG1EWD_Js8avMyPoNg&oe=68BEF50F&_nc_sid=5e03e0",
                "mediaKeyTimestamp": "1754764917",
                "waveform": "AAAAAAABAQAAAAAAAAABBQ8YL0hZVj81Wl1cWFJCJh9NVFNRVVJQTUg6OjsyNTk5NjAvLikRBQooJRIEEB8pLQ=="
            }
        }
    }
    
    print("📱 Dados do webhook:")
    print(f"   Tipo: {webhook_data['event']}")
    print(f"   Instance: {webhook_data['instanceId']}")
    print(f"   Message ID: {webhook_data['messageId']}")
    print(f"   From Me: {webhook_data['fromMe']}")
    print(f"   Chat ID: {webhook_data['chat']['id']}")
    print(f"   Sender: {webhook_data['sender']['pushName']}")
    print(f"   Mídia: audioMessage")
    
    return webhook_data

def verificar_estrutura_antes():
    """Verifica estrutura antes do teste"""
    print(f"\n📂 VERIFICANDO ESTRUTURA ANTES DO TESTE")
    print("=" * 60)
    
    base_path = Path("multichat_system/media_storage")
    
    if base_path.exists():
        print(f"✅ Pasta base existe: {base_path}")
        
        # Listar estrutura atual
        for item in base_path.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(base_path)
                print(f"   📄 {rel_path}")
        
        # Verificar nova estrutura por nome do cliente
        elizeu_path = base_path / "Elizeu_Batiliere_Dos_Santos"
        if elizeu_path.exists():
            print(f"✅ Pasta do cliente existe: {elizeu_path.name}")
        else:
            print(f"❌ Pasta do cliente não existe ainda")
    else:
        print(f"❌ Pasta base não existe")

def executar_teste_webhook():
    """Executa o teste do webhook corrigido"""
    print(f"\n🔄 EXECUTANDO TESTE WEBHOOK CORRIGIDO")
    print("=" * 60)
    
    # Simular webhook
    webhook_data = simular_webhook_real()
    
    # Verificar estrutura antes
    verificar_estrutura_antes()
    
    print(f"\n🚀 PROCESSANDO WEBHOOK...")
    
    try:
        # Chamar a função corrigida
        resultado = process_webhook_message(webhook_data, 'send_message')
        
        print(f"\n📊 RESULTADO DO PROCESSAMENTO:")
        print(f"   Retorno: {type(resultado)} - {resultado}")
        
        if resultado:
            print(f"✅ Webhook processado com sucesso!")
        else:
            print(f"❌ Webhook falhou no processamento")
        
        return resultado
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_estrutura_depois():
    """Verifica estrutura depois do teste"""
    print(f"\n📂 VERIFICANDO ESTRUTURA DEPOIS DO TESTE")
    print("=" * 60)
    
    base_path = Path("multichat_system/media_storage")
    
    # Verificar nova estrutura por nome
    elizeu_path = base_path / "Elizeu_Batiliere_Dos_Santos"
    
    if elizeu_path.exists():
        print(f"✅ Pasta do cliente criada: {elizeu_path.name}")
        
        # Verificar estrutura completa
        instance_path = elizeu_path / "instance_3B6XIW-ZTS923-GEAY6V"
        if instance_path.exists():
            print(f"✅ Pasta da instância: {instance_path.name}")
            
            chats_path = instance_path / "chats"
            if chats_path.exists():
                print(f"✅ Pasta de chats: chats/")
                
                chat_path = chats_path / "556999267344"
                if chat_path.exists():
                    print(f"✅ Pasta do chat: 556999267344/")
                    
                    audio_path = chat_path / "audio"
                    if audio_path.exists():
                        print(f"✅ Pasta de áudio: audio/")
                        
                        # Listar arquivos de áudio
                        audio_files = list(audio_path.glob("*"))
                        if audio_files:
                            print(f"🎵 Arquivos de áudio encontrados:")
                            for arquivo in audio_files:
                                print(f"   📄 {arquivo.name} ({arquivo.stat().st_size} bytes)")
                            return True
                        else:
                            print(f"❌ Nenhum arquivo de áudio encontrado")
                    else:
                        print(f"❌ Pasta de áudio não criada")
                else:
                    print(f"❌ Pasta do chat não criada")
            else:
                print(f"❌ Pasta de chats não criada")
        else:
            print(f"❌ Pasta da instância não criada")
    else:
        print(f"❌ Pasta do cliente não foi criada")
    
    return False

def gerar_relatorio_teste():
    """Gera relatório final do teste"""
    print(f"\n" + "=" * 80)
    print("📊 RELATÓRIO FINAL - TESTE WEBHOOK CORRIGIDO")
    print("=" * 80)
    
    print(f"🧪 TESTE REALIZADO:")
    print(f"   Webhook: audioMessage de Elizeu")
    print(f"   Message ID: E93A86D6119804FE8714DF3CAED360B6")
    print(f"   Chat ID: 556999267344")
    print(f"   Tipo: audio/ogg; codecs=opus")
    
    print(f"\n📂 ESTRUTURA ESPERADA:")
    print(f"   media_storage/")
    print(f"   └── Elizeu_Batiliere_Dos_Santos/")
    print(f"       └── instance_3B6XIW-ZTS923-GEAY6V/")
    print(f"           └── chats/")
    print(f"               └── 556999267344/")
    print(f"                   └── audio/")
    print(f"                       └── arquivo_baixado.mp3")
    
    # Verificar se funcionou
    base_path = Path("multichat_system/media_storage/Elizeu_Batiliere_Dos_Santos/instance_3B6XIW-ZTS923-GEAY6V/chats/556999267344/audio")
    
    if base_path.exists() and list(base_path.glob("*")):
        print(f"\n🎉 SUCESSO TOTAL!")
        print(f"   ✅ Download automático funcionando")
        print(f"   ✅ Estrutura por nome do cliente criada")
        print(f"   ✅ Organização por chat ID")
        print(f"   ✅ Separação por tipo de mídia")
        return True
    else:
        print(f"\n⚠️ VERIFICAÇÃO NECESSÁRIA:")
        print(f"   Arquivo pode ter sido baixado em outro local")
        print(f"   Verificar logs acima para detalhes")
        return False

def main():
    """Função principal"""
    print("🧪 TESTE COMPLETO - DOWNLOAD AUTOMÁTICO WEBHOOK CORRIGIDO")
    print("=" * 80)
    
    # Executar teste
    resultado = executar_teste_webhook()
    
    # Verificar resultado
    arquivos_criados = verificar_estrutura_depois()
    
    # Gerar relatório
    sucesso = gerar_relatorio_teste()
    
    if sucesso and arquivos_criados:
        print(f"\n🏆 TESTE PASSOU! Download automático funcionando perfeitamente!")
    else:
        print(f"\n🔍 Verificar logs acima para identificar problemas restantes")

if __name__ == "__main__":
    main() 