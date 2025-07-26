#!/usr/bin/env python
"""
Script para testar o import do módulo DeletaMensagem.
"""

import sys
import os

def test_import_deleta_mensagem():
    """Testa o import do módulo DeletaMensagem"""
    
    print("🧪 Testando import do DeletaMensagem...")
    
    # Adicionar o diretório wapi ao path
    wapi_path = os.path.join(os.path.dirname(__file__), '..', 'wapi')
    print(f"📁 WAPI Path: {wapi_path}")
    print(f"📁 WAPI Path existe: {os.path.exists(wapi_path)}")
    
    if wapi_path not in sys.path:
        sys.path.append(wapi_path)
        print(f"✅ WAPI Path adicionado ao sys.path")
    
    try:
        from mensagem.deletar.deletarMensagens import DeletaMensagem
        print("✅ Import do DeletaMensagem bem-sucedido!")
        
        # Testar criação da instância
        try:
            deletador = DeletaMensagem("test_instance", "test_token")
            print("✅ Instância DeletaMensagem criada com sucesso!")
            
            # Verificar métodos disponíveis
            methods = [method for method in dir(deletador) if not method.startswith('_')]
            print(f"📋 Métodos disponíveis: {methods}")
            
        except Exception as e:
            print(f"❌ Erro ao criar instância: {e}")
            
    except ImportError as e:
        print(f"❌ Erro ao importar DeletaMensagem: {e}")
        
        # Verificar estrutura de diretórios
        print("\n📁 Verificando estrutura de diretórios:")
        
        if os.path.exists(wapi_path):
            print(f"   ✅ Diretório wapi existe")
            
            mensagem_path = os.path.join(wapi_path, 'mensagem')
            if os.path.exists(mensagem_path):
                print(f"   ✅ Diretório mensagem existe")
                
                deletar_path = os.path.join(mensagem_path, 'deletar')
                if os.path.exists(deletar_path):
                    print(f"   ✅ Diretório deletar existe")
                    
                    arquivo_path = os.path.join(deletar_path, 'deletarMensagens.py')
                    if os.path.exists(arquivo_path):
                        print(f"   ✅ Arquivo deletarMensagens.py existe")
                    else:
                        print(f"   ❌ Arquivo deletarMensagens.py não existe")
                else:
                    print(f"   ❌ Diretório deletar não existe")
            else:
                print(f"   ❌ Diretório mensagem não existe")
        else:
            print(f"   ❌ Diretório wapi não existe")

if __name__ == "__main__":
    test_import_deleta_mensagem() 