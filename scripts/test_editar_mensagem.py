#!/usr/bin/env python
"""
Script para testar a classe EditarMensagem
"""
import sys
import os

# Adicionar o diretório wapi ao path
wapi_path = os.path.join(os.path.dirname(__file__), 'wapi')
if wapi_path not in sys.path:
    sys.path.append(wapi_path)

def test_editar_mensagem():
    """Testa a classe EditarMensagem"""
    print("🧪 Testando classe EditarMensagem...")
    
    try:
        from mensagem.editar.editarMensagens import EditarMensagem
        print("✅ Classe EditarMensagem importada com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar EditarMensagem: {e}")
        return
    
    # Dados de teste (substitua pelos dados reais)
    instance_id = "test_instance"  # Substitua pelo ID real
    token = "test_token"           # Substitua pelo token real
    
    try:
        # Testar inicialização
        print("\n🔧 Testando inicialização...")
        editor = EditarMensagem(instance_id, token)
        print("✅ Instância criada com sucesso")
        
        # Testar validações
        print("\n🔍 Testando validações...")
        
        # Teste 1: Parâmetros vazios
        resultado1 = editor.editar_mensagem("", "msg123", "Novo texto")
        print(f"   Teste 1 (phone vazio): {'❌' if 'erro' in resultado1 else '✅'} - {resultado1.get('erro', 'OK')}")
        
        # Teste 2: Message ID vazio
        resultado2 = editor.editar_mensagem("5569999267344", "", "Novo texto")
        print(f"   Teste 2 (message_id vazio): {'❌' if 'erro' in resultado2 else '✅'} - {resultado2.get('erro', 'OK')}")
        
        # Teste 3: Texto vazio
        resultado3 = editor.editar_mensagem("5569999267344", "msg123", "")
        print(f"   Teste 3 (texto vazio): {'❌' if 'erro' in resultado3 else '✅'} - {resultado3.get('erro', 'OK')}")
        
        # Teste 4: Telefone inválido
        resultado4 = editor.editar_mensagem("abc123", "msg123", "Novo texto")
        print(f"   Teste 4 (telefone inválido): {'❌' if 'erro' in resultado4 else '✅'} - {resultado4.get('erro', 'OK')}")
        
        # Teste 5: Texto muito longo
        texto_longo = "A" * 5000
        resultado5 = editor.editar_mensagem("5569999267344", "msg123", texto_longo)
        print(f"   Teste 5 (texto muito longo): {'❌' if 'erro' in resultado5 else '✅'} - {resultado5.get('erro', 'OK')}")
        
        # Teste 6: Parâmetros válidos (não executará realmente devido aos dados de teste)
        resultado6 = editor.editar_mensagem("5569999267344", "msg123", "Novo texto válido")
        print(f"   Teste 6 (parâmetros válidos): {'❌' if 'erro' in resultado6 else '✅'} - {resultado6.get('erro', 'OK')}")
        
        # Testar método simples
        print("\n🔧 Testando método simples...")
        resultado_simples = editor.editar_mensagem_simples("5569999267344", "msg123", "Novo texto")
        print(f"   Resultado simples: {'✅ Sucesso' if resultado_simples else '❌ Falha'}")
        
        # Testar conexão
        print("\n🔧 Testando conexão...")
        resultado_conexao = editor.testar_conexao()
        print(f"   Teste de conexão: {resultado_conexao}")
        
    except ValueError as e:
        print(f"❌ Erro de validação: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def testar_com_dados_reais():
    """Testa com dados reais do banco"""
    print("\n🔍 Testando com dados reais...")
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
    
    try:
        import django
        django.setup()
        
        from api.models import Mensagem, WhatsappInstance
        from mensagem.editar.editarMensagens import EditarMensagem
        
        # Buscar uma instância
        instancias = WhatsappInstance.objects.all()
        if not instancias.exists():
            print("❌ Nenhuma instância WhatsApp encontrada")
            return
        
        instancia = instancias.first()
        print(f"✅ Instância encontrada: {instancia.instance_id}")
        
        # Buscar mensagens editáveis
        mensagens_editaveis = Mensagem.objects.filter(
            from_me=True,
            message_id__isnull=False
        ).exclude(message_id='')
        
        if not mensagens_editaveis.exists():
            print("❌ Nenhuma mensagem editável encontrada")
            return
        
        mensagem = mensagens_editaveis.first()
        print(f"✅ Mensagem editável encontrada: ID={mensagem.id}, message_id={mensagem.message_id}")
        
        # Criar editor
        editor = EditarMensagem(instancia.instance_id, instancia.token)
        
        # Testar edição (apenas simulação)
        novo_texto = f"{mensagem.conteudo} [TESTE]"
        print(f"\n🎯 Simulando edição:")
        print(f"   Phone: {mensagem.chat.chat_id}")
        print(f"   Message ID: {mensagem.message_id}")
        print(f"   Novo texto: {novo_texto}")
        
        # Não executar realmente para evitar edições acidentais
        print("⚠️ Edição não executada (modo de teste)")
        
    except Exception as e:
        print(f"❌ Erro ao testar com dados reais: {e}")

if __name__ == "__main__":
    print("🧪 Teste da classe EditarMensagem")
    print("=" * 50)
    
    test_editar_mensagem()
    testar_com_dados_reais()
    
    print("\n✅ Teste concluído!") 