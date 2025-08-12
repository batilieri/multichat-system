#!/usr/bin/env python3
"""
🔧 TESTE REORGANIZAÇÃO FINAL
Testa se a reorganização de arquivos está funcionando com a correção aplicada
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

def test_reorganizacao_completa():
    """Testa todo o fluxo de download e reorganização"""
    print("🔧 TESTE REORGANIZAÇÃO COMPLETA")
    print("=" * 80)
    
    from webhook.models import WebhookEvent
    from core.models import WhatsappInstance
    from webhook.views import process_media_automatically
    
    # Buscar último webhook com áudio
    ultimo_webhook = None
    
    for webhook in WebhookEvent.objects.all().order_by('-timestamp')[:10]:
        try:
            data = webhook.raw_data
            msg_content = data.get('msgContent', {})
            
            if 'audioMessage' in msg_content and data.get('chat', {}).get('id'):
                ultimo_webhook = webhook
                break
        except:
            continue
    
    if not ultimo_webhook:
        print("❌ Nenhum webhook com áudio e chat_id encontrado")
        return
    
    data = ultimo_webhook.raw_data
    instance_id = data.get('instanceId')
    chat_id = data.get('chat', {}).get('id')
    
    print(f"✅ Webhook encontrado:")
    print(f"   📧 messageId: {data.get('messageId')}")
    print(f"   📞 chat_id: {chat_id}")
    print(f"   📱 instanceId: {instance_id}")
    
    # Buscar instância
    try:
        instance = WhatsappInstance.objects.get(instance_id=instance_id)
        cliente = instance.cliente
        
        print(f"✅ Instância encontrada: {cliente.nome}")
        
        # Testar process_media_automatically diretamente
        print(f"\n🔄 Testando process_media_automatically...")
        
        resultado = process_media_automatically(data, cliente, instance)
        
        print(f"📋 Resultado: {resultado}")
        
        if resultado:
            # Verificar se arquivo foi criado na estrutura correta
            cliente_nome = "".join(c for c in cliente.nome if c.isalnum() or c in (' ', '-', '_')).strip()
            cliente_nome = cliente_nome.replace(' ', '_')
            
            expected_path = Path(__file__).parent / "multichat_system" / "media_storage" / cliente_nome / f"instance_{instance.instance_id}" / "chats" / str(chat_id) / "audio"
            
            print(f"\n📂 Verificando estrutura esperada:")
            print(f"   {expected_path}")
            
            if expected_path.exists():
                arquivos = list(expected_path.glob("*.mp3"))
                print(f"✅ Pasta existe com {len(arquivos)} arquivos:")
                for arquivo in arquivos[-3:]:  # Últimos 3
                    print(f"   📁 {arquivo.name}")
            else:
                print(f"❌ Pasta não existe")
                
                # Verificar estrutura antiga
                old_path = Path(__file__).parent / "multichat_system" / "media_storage" / f"cliente_{cliente.id}" / f"instance_{instance.instance_id}" / "audio"
                if old_path.exists():
                    arquivos = list(old_path.glob("*.mp3"))
                    print(f"⚠️ Arquivos na estrutura antiga: {len(arquivos)}")
        else:
            print(f"❌ process_media_automatically falhou")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    print("🔧 TESTE REORGANIZAÇÃO FINAL")
    print("=" * 100)
    print("OBJETIVO: Verificar se a reorganização está funcionando")
    print("=" * 100)
    
    test_reorganizacao_completa()
    
    print("\n" + "=" * 100)
    print("🎯 PRÓXIMOS PASSOS SE AINDA NÃO FUNCIONAR:")
    print("1. 🔄 Enviar um novo áudio pelo WhatsApp")
    print("2. 🔍 Verificar logs no terminal do Django")  
    print("3. 📂 Verificar se arquivo aparece na nova estrutura")
    print("4. 🎯 Se ainda vai para cliente_X, há outro problema")

if __name__ == "__main__":
    main() 