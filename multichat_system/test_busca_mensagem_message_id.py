#!/usr/bin/env python
"""
Script para testar a busca de mensagem por message_id.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Mensagem, Chat, Cliente, WhatsappInstance

def test_busca_mensagem_message_id():
    """Testa a busca de mensagem por message_id"""
    
    print("🧪 Testando busca de mensagem por message_id...")
    
    # Buscar uma mensagem com message_id
    mensagem = Mensagem.objects.filter(
        message_id__isnull=False
    ).exclude(message_id='').first()
    
    if not mensagem:
        print("❌ Nenhuma mensagem com message_id encontrada")
        return
    
    print(f"📋 Mensagem encontrada:")
    print(f"   - ID interno: {mensagem.id}")
    print(f"   - message_id: {mensagem.message_id}")
    print(f"   - from_me: {mensagem.from_me}")
    print(f"   - chat_id: {mensagem.chat.chat_id}")
    print(f"   - cliente: {mensagem.chat.cliente.nome}")
    
    # Verificar se a instância WhatsApp existe
    try:
        instancia = WhatsappInstance.objects.get(cliente=mensagem.chat.cliente)
        print(f"✅ Instância WhatsApp encontrada:")
        print(f"   - instance_id: {instancia.instance_id}")
        print(f"   - token: {instancia.token[:20]}...")
        
        # Testar o import e criação do deletador
        import sys
        import os
        
        wapi_path = os.path.join(os.path.dirname(__file__), '..', 'wapi')
        if wapi_path not in sys.path:
            sys.path.append(wapi_path)
        
        try:
            from mensagem.deletar.deletarMensagens import DeletaMensagem
            
            deletador = DeletaMensagem(instancia.instance_id, instancia.token)
            print("✅ Deletador criado com sucesso!")
            
            # Testar a chamada do método deletar (sem executar)
            print(f"🧪 Testando chamada do método deletar...")
            print(f"   - phone_number: {mensagem.chat.chat_id}")
            print(f"   - message_ids: {mensagem.message_id}")
            
            # Verificar se o método existe
            if hasattr(deletador, 'deletar'):
                print("✅ Método deletar existe!")
            else:
                print("❌ Método deletar não existe!")
                
        except Exception as e:
            print(f"❌ Erro ao criar deletador: {e}")
            
    except WhatsappInstance.DoesNotExist:
        print("❌ Instância WhatsApp não encontrada para este cliente")

if __name__ == "__main__":
    test_busca_mensagem_message_id() 