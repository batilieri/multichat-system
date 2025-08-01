#!/usr/bin/env python3
"""
Script para testar a validação automática de chat_id
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.models import Chat, Cliente

def testar_validacao_chat_id():
    """
    Testa a validação automática de chat_id
    """
    print("🧪 TESTANDO VALIDAÇÃO AUTOMÁTICA DE CHAT_ID")
    print("=" * 60)
    
    # Buscar um cliente para teste
    cliente = Cliente.objects.first()
    if not cliente:
        print("❌ Nenhum cliente encontrado para teste")
        return
    
    print(f"👤 Cliente de teste: {cliente.nome}")
    
    # Testes com diferentes formatos de chat_id (usando sufixos únicos)
    testes = [
        ("111141053288574@lid_TESTE", "111141053288574"),
        ("556992962029-1415646286@g.us_TESTE", "5569929620291415646286"),
        ("556999171919-1524353875@g.us_TESTE", "5569991719191524353875"),
        ("120363373541551792@g.us_TESTE", "120363373541551792"),
        ("5511999999999_TESTE", "5511999999999"),  # Já correto
        ("5511888888888@c.us_TESTE", "5511888888888"),
    ]
    
    resultados = []
    
    for chat_id_incorreto, chat_id_esperado in testes:
        try:
            # Criar chat com ID incorreto
            chat = Chat.objects.create(
                chat_id=chat_id_incorreto,
                cliente=cliente,
                status='active',
                canal='whatsapp'
            )
            
            # Verificar se foi normalizado
            chat_salvo = Chat.objects.get(id=chat.id)
            chat_id_real = chat_salvo.chat_id
            
            # Comparar com o esperado
            sucesso = chat_id_real == chat_id_esperado
            
            print(f"📱 Teste: {chat_id_incorreto}")
            print(f"   Esperado: {chat_id_esperado}")
            print(f"   Real: {chat_id_real}")
            print(f"   ✅ {'PASSOU' if sucesso else '❌ FALHOU'}")
            print()
            
            resultados.append({
                'teste': chat_id_incorreto,
                'esperado': chat_id_esperado,
                'real': chat_id_real,
                'sucesso': sucesso
            })
            
            # Limpar chat de teste
            chat.delete()
            
        except Exception as e:
            print(f"❌ Erro no teste {chat_id_incorreto}: {e}")
            resultados.append({
                'teste': chat_id_incorreto,
                'esperado': chat_id_esperado,
                'real': 'ERRO',
                'sucesso': False
            })
    
    # Resumo dos resultados
    print("📊 RESUMO DOS TESTES:")
    print("=" * 60)
    
    sucessos = sum(1 for r in resultados if r['sucesso'])
    total = len(resultados)
    
    print(f"✅ Testes que passaram: {sucessos}/{total}")
    print(f"❌ Testes que falharam: {total - sucessos}/{total}")
    
    if sucessos == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ A validação automática está funcionando corretamente")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM!")
        print("❌ Verifique a implementação da validação")
    
    return sucessos == total

def testar_chats_existentes():
    """
    Verifica se os chats existentes estão com IDs válidos
    """
    print("\n🔍 VERIFICANDO CHATS EXISTENTES...")
    print("=" * 60)
    
    # Buscar chats com IDs inválidos
    chats_invalidos = Chat.objects.filter(chat_id__contains='@')
    chats_validos = Chat.objects.filter(chat_id__regex=r'^\d+$')
    
    print(f"✅ Chats com IDs válidos: {chats_validos.count()}")
    print(f"❌ Chats com IDs inválidos: {chats_invalidos.count()}")
    
    if chats_invalidos.exists():
        print("\n⚠️ Chats com IDs inválidos encontrados:")
        for chat in chats_invalidos[:5]:
            print(f"   - {chat.chat_id} (Cliente: {chat.cliente.nome})")
    else:
        print("\n✅ Todos os chats existentes têm IDs válidos!")
    
    return chats_invalidos.count() == 0

def testar_funcao_normalize():
    """
    Testa a função normalize_chat_id diretamente
    """
    print("\n🔧 TESTANDO FUNÇÃO NORMALIZE_CHAT_ID...")
    print("=" * 60)
    
    testes = [
        ("111141053288574@lid", "111141053288574"),
        ("556992962029-1415646286@g.us", "5569929620291415646286"),
        ("556999171919-1524353875@g.us", "5569991719191524353875"),
        ("120363373541551792@g.us", "120363373541551792"),
        ("5511999999999", "5511999999999"),
        ("5511888888888@c.us", "5511888888888"),
    ]
    
    sucessos = 0
    for chat_id_incorreto, chat_id_esperado in testes:
        resultado = Chat.normalize_chat_id(chat_id_incorreto)
        sucesso = resultado == chat_id_esperado
        
        print(f"📱 {chat_id_incorreto} -> {resultado}")
        print(f"   Esperado: {chat_id_esperado}")
        print(f"   ✅ {'PASSOU' if sucesso else '❌ FALHOU'}")
        print()
        
        if sucesso:
            sucessos += 1
    
    print(f"📊 Função normalize_chat_id: {sucessos}/{len(testes)} testes passaram")
    return sucessos == len(testes)

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DE VALIDAÇÃO DE CHAT_ID...")
    print("=" * 60)
    
    # Testar função normalize diretamente
    normalize_ok = testar_funcao_normalize()
    
    # Testar validação automática
    validacao_ok = testar_validacao_chat_id()
    
    # Verificar chats existentes
    chats_ok = testar_chats_existentes()
    
    print("\n🎯 RESULTADO FINAL:")
    print("=" * 60)
    
    if normalize_ok and validacao_ok and chats_ok:
        print("✅ SISTEMA TOTALMENTE FUNCIONAL!")
        print("🎉 Todos os testes passaram e todos os chats estão corretos")
    elif normalize_ok and chats_ok:
        print("✅ FUNÇÃO NORMALIZE OK E CHATS CORRETOS")
        print("⚠️ Validação automática pode ter problemas")
    else:
        print("❌ PROBLEMAS DETECTADOS")
        print("🔧 Verifique a implementação")
    
    print("\n✅ Testes concluídos!") 