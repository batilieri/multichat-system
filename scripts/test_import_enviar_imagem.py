#!/usr/bin/env python3
"""
Teste de importação do módulo EnviarImagem
"""

import sys
import os

# Adicionar o caminho para o módulo wapi
current_dir = os.path.dirname(os.path.abspath(__file__))
wapi_path = os.path.join(current_dir, '..', 'wapi')
sys.path.insert(0, wapi_path)

print(f"🔍 Testando importação do módulo EnviarImagem...")
print(f"📁 Caminho adicionado: {wapi_path}")

try:
    from mensagem.enviosMensagensDocs.enviarImagem import EnviarImagem
    print("✅ Importação do EnviarImagem funcionou!")
    
    # Testar criação da classe
    try:
        instance = EnviarImagem("test_instance", "test_token")
        print("✅ Criação da classe EnviarImagem funcionou!")
        
        # Testar métodos da classe
        methods = [attr for attr in dir(instance) if not attr.startswith('_')]
        print(f"📋 Métodos disponíveis: {methods}")
        
    except Exception as e:
        print(f"❌ Erro ao criar instância: {e}")
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    
    # Verificar se o arquivo existe
    file_path = os.path.join(wapi_path, 'mensagem', 'enviosMensagensDocs', 'enviarImagem.py')
    if os.path.exists(file_path):
        print(f"✅ Arquivo existe: {file_path}")
    else:
        print(f"❌ Arquivo não existe: {file_path}")
        
    # Listar arquivos no diretório
    mensagem_path = os.path.join(wapi_path, 'mensagem')
    if os.path.exists(mensagem_path):
        print(f"📁 Conteúdo de {mensagem_path}:")
        for root, dirs, files in os.walk(mensagem_path):
            level = root.replace(mensagem_path, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
    else:
        print(f"❌ Diretório não existe: {mensagem_path}")
        
except Exception as e:
    print(f"❌ Erro inesperado: {e}")

print("\n✅ Teste de importação concluído!") 