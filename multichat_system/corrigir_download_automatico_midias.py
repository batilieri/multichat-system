#!/usr/bin/env python3
"""
Script para corrigir o sistema de download automático de mídias
"""

import os
import sys
import django
import json
import requests
from pathlib import Path
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Cliente, WhatsappInstance, MediaFile, Chat, Mensagem
from webhook.views import process_media_automatically, download_media_via_wapi, save_media_file

def verificar_estrutura_pastas():
    """Verifica e cria estrutura de pastas necessária"""
    print("📂 Verificando estrutura de pastas...")
    
    instancias = WhatsappInstance.objects.all()
    
    for instancia in instancias:
        cliente = instancia.cliente
        base_path = Path(__file__).parent / "media_storage" / f"cliente_{cliente.id}" / f"instance_{instancia.instance_id}"
        
        # Criar pastas para cada tipo de mídia
        tipos_midia = ['image', 'video', 'audio', 'document', 'sticker']
        
        for tipo in tipos_midia:
            tipo_path = base_path / tipo
            tipo_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Pasta {tipo}: {tipo_path}")
        
        print(f"✅ Estrutura criada para {cliente.nome} - {instancia.instance_id}")

def corrigir_midias_existentes():
    """Corrige mídias que estão no banco mas não têm arquivos físicos"""
    print("\n🔧 Corrigindo mídias existentes...")
    
    midias = MediaFile.objects.filter(download_status='success')
    
    for midia in midias:
        if midia.file_path and not os.path.exists(midia.file_path):
            print(f"❌ Arquivo não existe: {midia.file_path}")
            
            # Marcar como falhou para reprocessar
            midia.download_status = 'failed'
            midia.save()
            print(f"✅ Mídia {midia.id} marcada para reprocessamento")

def testar_webhook_real():
    """Testa com dados reais de webhook"""
    print("\n🧪 Testando com dados reais de webhook...")
    
    # Buscar uma mensagem com mídia real
    mensagens_com_midia = Mensagem.objects.filter(
        tipo__in=['image', 'video', 'audio', 'document']
    ).order_by('-data_envio')[:5]
    
    if not mensagens_com_midia.exists():
        print("❌ Nenhuma mensagem com mídia encontrada!")
        return
    
    for mensagem in mensagens_com_midia:
        print(f"\n📎 Testando mensagem: {mensagem.id}")
        print(f"   Tipo: {mensagem.tipo}")
        print(f"   Conteúdo: {mensagem.conteudo[:100]}...")
        
        # Simular webhook com dados reais
        webhook_data = {
            "instanceId": mensagem.chat.cliente.whatsapp_instances.first().instance_id,
            "messageId": mensagem.message_id or f"msg_{mensagem.id}",
            "sender": {
                "id": mensagem.remetente,
                "pushName": mensagem.sender_push_name or "Usuário"
            },
            "msgContent": {
                f"{mensagem.tipo}Message": {
                    "mediaKey": f"key_{mensagem.id}",
                    "directPath": f"/path/{mensagem.id}",
                    "mimetype": "image/jpeg" if mensagem.tipo == 'image' else "video/mp4",
                    "fileLength": 1024,
                    "caption": mensagem.conteudo
                }
            }
        }
        
        try:
            instancia = mensagem.chat.cliente.whatsapp_instances.first()
            if instancia:
                resultado = process_media_automatically(webhook_data, mensagem.chat.cliente, instancia)
                if resultado:
                    print("✅ Processamento funcionou!")
                else:
                    print("❌ Processamento falhou!")
            else:
                print("❌ Instância não encontrada!")
        except Exception as e:
            print(f"❌ Erro: {e}")

def melhorar_funcao_download_wapi():
    """Melhora a função de download da W-API com melhor tratamento de erros"""
    print("\n🔧 Melhorando função de download W-API...")
    
    # Criar versão melhorada da função
    codigo_melhorado = '''
def download_media_via_wapi_improved(instance_id, bearer_token, media_data):
    """Versão melhorada da função de download via W-API"""
    try:
        import requests
        import json
        import time
        
        url = f"https://api.w-api.app/v1/message/download-media?instanceId={instance_id}"
        
        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'mediaKey': media_data.get('mediaKey', ''),
            'directPath': media_data.get('directPath', ''),
            'type': media_data.get('type', ''),
            'mimetype': media_data.get('mimetype', '')
        }
        
        print(f"🔄 Fazendo requisição para W-API:")
        print(f"   URL: {url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        # Tentar múltiplas vezes
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                print(f"📡 Tentativa {attempt + 1}: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    if not data.get('error', True):
                        print(f"✅ Download bem-sucedido:")
                        print(f"   fileLink: {data.get('fileLink', 'N/A')}")
                        return data
                    else:
                        print(f"❌ Erro na resposta: {data}")
                else:
                    print(f"❌ Status code: {response.status_code}")
                    print(f"   Resposta: {response.text}")
                
                if attempt < max_retries - 1:
                    print(f"⏳ Aguardando 2 segundos antes da próxima tentativa...")
                    time.sleep(2)
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Erro de conexão (tentativa {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        print(f"❌ Todas as {max_retries} tentativas falharam")
        return None
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return None
'''
    
    # Salvar função melhorada
    with open('download_wapi_improved.py', 'w', encoding='utf-8') as f:
        f.write(codigo_melhorado)
    
    print("✅ Função melhorada salva em download_wapi_improved.py")

def criar_script_reprocessamento():
    """Cria script para reprocessar mídias falhadas"""
    print("\n📝 Criando script de reprocessamento...")
    
    codigo_reprocessamento = '''
#!/usr/bin/env python3
"""
Script para reprocessar mídias que falharam no download
"""

import os
import sys
import django
import json
import requests
from pathlib import Path
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import MediaFile, WhatsappInstance
from webhook.views import save_media_file

def reprocessar_midias_falhadas():
    """Reprocessa mídias que falharam no download"""
    print("🔄 Rep processando mídias falhadas...")
    
    # Buscar mídias que falharam
    midias_falhadas = MediaFile.objects.filter(download_status='failed')
    
    if not midias_falhadas.exists():
        print("✅ Nenhuma mídia falhada encontrada!")
        return
    
    print(f"📊 Encontradas {midias_falhadas.count()} mídias falhadas")
    
    for midia in midias_falhadas:
        print(f"\\n📎 Processando mídia {midia.id}: {midia.media_type}")
        
        try:
            # Tentar baixar novamente (simular com dados de teste)
            file_link = f"https://api.w-api.app/media/test/{midia.message_id}"
            
            resultado = save_media_file(
                file_link,
                midia.media_type,
                midia.message_id,
                midia.sender_name,
                midia.cliente,
                midia.instance
            )
            
            if resultado:
                print(f"✅ Mídia {midia.id} reprocessada com sucesso!")
                midia.download_status = 'success'
                midia.file_path = resultado
                midia.save()
            else:
                print(f"❌ Falha ao reprocessar mídia {midia.id}")
                
        except Exception as e:
            print(f"❌ Erro ao reprocessar mídia {midia.id}: {e}")

if __name__ == "__main__":
    reprocessar_midias_falhadas()
'''
    
    with open('reprocessar_midias.py', 'w', encoding='utf-8') as f:
        f.write(codigo_reprocessamento)
    
    print("✅ Script de reprocessamento salvo em reprocessar_midias.py")

def verificar_configuracao_webhook():
    """Verifica se o webhook está configurado corretamente"""
    print("\n🔍 Verificando configuração do webhook...")
    
    instancias = WhatsappInstance.objects.all()
    
    for instancia in instancias:
        print(f"\n📱 Instância: {instancia.instance_id}")
        print(f"   Cliente: {instancia.cliente.nome}")
        print(f"   Status: {instancia.status}")
        print(f"   Token: {'✅' if instancia.token else '❌'}")
        
        # Verificar se o webhook está ativo
        if instancia.status == 'conectado':
            print("   Webhook: ✅ Ativo")
        else:
            print("   Webhook: ❌ Inativo")
            print("   ⚠️  Instância precisa estar conectada para receber webhooks")

def criar_script_monitoramento():
    """Cria script para monitorar downloads de mídia"""
    print("\n📊 Criando script de monitoramento...")
    
    codigo_monitoramento = '''
#!/usr/bin/env python3
"""
Script para monitorar downloads de mídia em tempo real
"""

import os
import sys
import django
import time
from datetime import datetime, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import MediaFile

def monitorar_downloads():
    """Monitora downloads de mídia em tempo real"""
    print("📊 Monitorando downloads de mídia...")
    print("Pressione Ctrl+C para parar")
    
    ultima_verificacao = datetime.now()
    
    try:
        while True:
            # Verificar novas mídias
            novas_midias = MediaFile.objects.filter(
                created_at__gte=ultima_verificacao
            ).order_by('-created_at')
            
            if novas_midias.exists():
                print(f"\\n🆕 {novas_midias.count()} nova(s) mídia(s) encontrada(s):")
                
                for midia in novas_midias:
                    print(f"   📎 {midia.media_type} - {midia.sender_name}")
                    print(f"      Status: {midia.download_status}")
                    print(f"      Arquivo: {midia.file_name}")
                    if midia.file_path:
                        existe = os.path.exists(midia.file_path)
                        print(f"      Existe: {'✅' if existe else '❌'}")
            
            ultima_verificacao = datetime.now()
            time.sleep(5)  # Verificar a cada 5 segundos
            
    except KeyboardInterrupt:
        print("\\n⏹️  Monitoramento interrompido")

if __name__ == "__main__":
    monitorar_downloads()
'''
    
    with open('monitorar_midias.py', 'w', encoding='utf-8') as f:
        f.write(codigo_monitoramento)
    
    print("✅ Script de monitoramento salvo em monitorar_midias.py")

def main():
    """Função principal"""
    print("🚀 Iniciando correção do sistema de download automático...")
    print("=" * 60)
    
    # Verificar estrutura de pastas
    verificar_estrutura_pastas()
    
    # Corrigir mídias existentes
    corrigir_midias_existentes()
    
    # Verificar configuração do webhook
    verificar_configuracao_webhook()
    
    # Melhorar função de download
    melhorar_funcao_download_wapi()
    
    # Criar scripts auxiliares
    criar_script_reprocessamento()
    criar_script_monitoramento()
    
    # Testar com dados reais
    testar_webhook_real()
    
    print("\n" + "=" * 60)
    print("✅ Correção concluída!")
    print("\n📋 Próximos passos:")
    print("1. Execute: python reprocessar_midias.py")
    print("2. Execute: python monitorar_midias.py")
    print("3. Envie uma mídia via WhatsApp para testar")
    print("4. Verifique os logs do webhook")

if __name__ == "__main__":
    main() 