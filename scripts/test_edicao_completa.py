#!/usr/bin/env python
"""
Script para testar a edição completa de mensagens
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from api.models import Mensagem, WhatsappInstance
from django.db.models import Q

def test_edicao_completa():
    """Testa a edição completa de mensagens"""
    print("🧪 Testando edição completa de mensagens...")
    
    # Buscar instâncias WhatsApp
    instancias = WhatsappInstance.objects.all()
    if not instancias.exists():
        print("❌ Nenhuma instância WhatsApp encontrada")
        return
    
    instancia = instancias.first()
    print(f"✅ Instância encontrada: {instancia.instance_id}")
    
    # Buscar mensagens editáveis
    mensagens_editaveis = Mensagem.objects.filter(
        Q(tipo='texto') | Q(tipo='text'),
        from_me=True,
        message_id__isnull=False
    ).exclude(message_id='')
    
    if not mensagens_editaveis.exists():
        print("❌ Nenhuma mensagem editável encontrada")
        print("💡 Para testar, você precisa de mensagens que:")
        print("   - Sejam do tipo 'texto' ou 'text'")
        print("   - Tenham from_me=True (enviadas por você)")
        print("   - Tenham message_id preenchido")
        return
    
    mensagem = mensagens_editaveis.first()
    print(f"\n🎯 Mensagem editável encontrada:")
    print(f"   - ID: {mensagem.id}")
    print(f"   - Message ID: {mensagem.message_id}")
    print(f"   - Chat ID: {mensagem.chat.chat_id}")
    print(f"   - Cliente: {mensagem.chat.cliente.nome}")
    print(f"   - Tipo: {mensagem.tipo}")
    print(f"   - From Me: {mensagem.from_me}")
    print(f"   - Conteúdo atual: {mensagem.conteudo}")
    
    # Testar importação da classe EditarMensagem
    print("\n🔧 Testando importação da classe EditarMensagem...")
    try:
        # Adicionar o diretório wapi ao path
        wapi_path = os.path.join(os.path.dirname(__file__), 'wapi')
        if wapi_path not in sys.path:
            sys.path.append(wapi_path)
        
        from mensagem.editar.editarMensagens import EditarMensagem
        print("✅ Classe EditarMensagem importada com sucesso")
        
        # Criar instância do editor
        editor = EditarMensagem(instancia.instance_id, instancia.token)
        print("✅ Instância do editor criada com sucesso")
        
        # Testar validações
        print("\n🔍 Testando validações...")
        
        # Teste 1: Parâmetros válidos
        novo_texto = f"{mensagem.conteudo} [TESTE_EDITADO]"
        print(f"   - Novo texto: {novo_texto}")
        print(f"   - Phone: {mensagem.chat.chat_id}")
        print(f"   - Message ID: {mensagem.message_id}")
        
        # Testar método de validação
        resultado_teste = editor.editar_mensagem(
            phone=mensagem.chat.chat_id,
            message_id=mensagem.message_id,
            new_text=novo_texto
        )
        
        print(f"\n📡 Resultado do teste:")
        print(f"   - Sucesso: {'erro' not in resultado_teste}")
        print(f"   - Resposta: {resultado_teste}")
        
        if "erro" not in resultado_teste:
            print("✅ Teste de edição bem-sucedido!")
        else:
            print("❌ Teste de edição falhou!")
            print(f"   - Erro: {resultado_teste.get('erro', 'Erro desconhecido')}")
        
    except ImportError as e:
        print(f"❌ Erro ao importar EditarMensagem: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def verificar_dados_necessarios():
    """Verifica se todos os dados necessários estão presentes"""
    print("\n🔍 Verificando dados necessários...")
    
    # Verificar instâncias
    instancias = WhatsappInstance.objects.all()
    print(f"   - Instâncias WhatsApp: {instancias.count()}")
    
    if instancias.exists():
        instancia = instancias.first()
        print(f"   - Instância: {instancia.instance_id}")
        print(f"   - Token: {'✅ Presente' if instancia.token else '❌ Ausente'}")
    
    # Verificar mensagens editáveis
    mensagens_editaveis = Mensagem.objects.filter(
        Q(tipo='texto') | Q(tipo='text'),
        from_me=True,
        message_id__isnull=False
    ).exclude(message_id='')
    
    print(f"   - Mensagens editáveis: {mensagens_editaveis.count()}")
    
    if mensagens_editaveis.exists():
        msg = mensagens_editaveis.first()
        print(f"   - Exemplo de mensagem:")
        print(f"     * ID: {msg.id}")
        print(f"     * Message ID: {msg.message_id}")
        print(f"     * Chat ID: {msg.chat.chat_id}")
        print(f"     * Tipo: {msg.tipo}")
        print(f"     * From Me: {msg.from_me}")
        print(f"     * Cliente: {msg.chat.cliente.nome}")

if __name__ == "__main__":
    print("🧪 Teste completo de edição de mensagens")
    print("=" * 50)
    
    verificar_dados_necessarios()
    test_edicao_completa()
    
    print("\n✅ Teste concluído!")
    print("\n💡 Para testar no frontend:")
    print("   1. Certifique-se de que o backend está rodando")
    print("   2. Certifique-se de que o frontend está rodando")
    print("   3. Abra o console do navegador (F12)")
    print("   4. Tente editar uma mensagem própria de texto")
    print("   5. Verifique os logs no console") 