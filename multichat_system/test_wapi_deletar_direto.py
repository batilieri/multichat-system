#!/usr/bin/env python
"""
Script para testar diretamente o método deletar da W-API.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente, WhatsappInstance

def test_wapi_deletar_direto():
    """Testa diretamente o método deletar da W-API"""
    
    print("🧪 Testando método deletar da W-API diretamente...")
    print("=" * 60)
    
    # Buscar uma mensagem para testar
    mensagem = Mensagem.objects.filter(
        from_me=True,
        message_id__isnull=False
    ).exclude(message_id='').first()
    
    if not mensagem:
        print("❌ Nenhuma mensagem encontrada para teste")
        return
    
    print(f"📋 Mensagem para teste:")
    print(f"   - ID interno: {mensagem.id}")
    print(f"   - message_id: {mensagem.message_id}")
    print(f"   - chat_id: {mensagem.chat.chat_id}")
    print(f"   - from_me: {mensagem.from_me}")
    
    # Buscar instância WhatsApp
    try:
        instancia = WhatsappInstance.objects.get(cliente=mensagem.chat.cliente)
        print(f"✅ Instância encontrada:")
        print(f"   - instance_id: {instancia.instance_id}")
        print(f"   - token: {instancia.token[:20]}...")
    except WhatsappInstance.DoesNotExist:
        print("❌ Instância WhatsApp não encontrada")
        return
    
    # Importar e testar DeletaMensagem
    import sys
    import os
    
    wapi_path = os.path.join(os.path.dirname(__file__), '..', 'wapi')
    if wapi_path not in sys.path:
        sys.path.append(wapi_path)
    
    try:
        from mensagem.deletar.deletarMensagens import DeletaMensagem
        
        # Criar instância do deletador
        deletador = DeletaMensagem(instancia.instance_id, instancia.token)
        print("✅ Deletador criado com sucesso")
        
        # Testar método deletar
        print(f"\n🔄 Testando exclusão...")
        print(f"   - phone_number: {mensagem.chat.chat_id}")
        print(f"   - message_ids: {mensagem.message_id}")
        
        resultado = deletador.deletar(
            phone_number=mensagem.chat.chat_id,
            message_ids=mensagem.message_id
        )
        
        print(f"📡 Resultado: {resultado}")
        
        if resultado.get('success'):
            print("✅ Exclusão bem-sucedida na W-API!")
        else:
            print("❌ Falha na exclusão da W-API")
            print(f"   - Erro: {resultado.get('error', 'Erro desconhecido')}")
            
    except Exception as e:
        print(f"❌ Erro ao testar W-API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_wapi_deletar_direto() 