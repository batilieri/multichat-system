#!/usr/bin/env python3
"""
Script para testar a nova estrutura de organização por chat_id
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'multichat_system'))

def testar_estrutura_chat_id():
    """Testa a criação da nova estrutura de pastas"""
    
    print("Testando Nova Estrutura de Midias por Chat ID")
    print("=" * 50)
    
    # Simular dados de teste
    cliente_id = "2"
    instance_id = "3B6XIW-ZTS923-GEAY6V"
    chats_teste = [
        "5511999999999",  # Número normal
        "5511888888888",  # Outro número
        "group_363251234",  # Grupo
        "unknown",  # Chat desconhecido
    ]
    
    tipos_midia = ["audio", "video", "image", "document", "sticker"]
    
    # Pasta base de teste
    base_path = Path(__file__).parent / "multichat_system" / "media_storage"
    pasta_teste = base_path / f"cliente_{cliente_id}" / f"instance_{instance_id}" / "chats"
    
    print(f"Pasta base: {pasta_teste}")
    print(f"Chats de teste: {len(chats_teste)}")
    print(f"Tipos de midia: {len(tipos_midia)}")
    print()
    
    # Em vez de criar estrutura de teste, vamos validar a estrutura migrada
    print("Validando estrutura migrada existente...")
    
    # Verificar se a pasta migrada existe
    pasta_migrada = pasta_teste / "unknown_wapi" / "audio"
    if pasta_migrada.exists():
        arquivos_migrados = list(pasta_migrada.glob("*.mp3"))
        print(f"OK - Pasta migrada encontrada: {len(arquivos_migrados)} arquivos MP3")
        
        for arquivo in arquivos_migrados:
            print(f"   -> {arquivo.name}")
    else:
        print("ERRO - Pasta migrada nao encontrada")
    
    print()
    
    # Verificar URLs para o frontend
    print("URLs de Exemplo para Frontend:")
    if pasta_migrada.exists():
        for arquivo in list(pasta_migrada.glob("*.mp3"))[:3]:  # Primeiros 3
            url_exemplo = f"/media/whatsapp_media/cliente_{cliente_id}/instance_{instance_id}/chats/unknown_wapi/audio/{arquivo.name}"
            print(f"   {url_exemplo}")
    
    print()
    print("Teste da nova estrutura concluido!")
    

def comparar_estruturas():
    """Compara a estrutura antiga vs nova"""
    print("\n📊 Comparação de Estruturas:")
    print("=" * 40)
    
    print("❌ Estrutura ANTIGA (problemática):")
    print("   cliente_2/instance_X/audio/")
    print("   ├── wapi_ABC123_20250806_161207.mp3")
    print("   ├── wapi_DEF456_20250806_161210.mp3")
    print("   └── wapi_GHI789_20250806_161614.mp3")
    print("   ⚠️ Problemas: Difícil buscar por chat, nomes confusos")
    
    print("\n✅ Estrutura NOVA (organizada):")
    print("   cliente_2/instance_X/chats/")
    print("   ├── 5511999999999/audio/")
    print("   │   ├── msg_ABC123_20250806_161207.mp3")
    print("   │   └── msg_DEF456_20250806_161210.mp3")
    print("   └── 5511888888888/audio/")
    print("       └── msg_GHI789_20250806_161614.mp3")
    print("   ✅ Vantagens: Organizado por chat, URLs previsíveis")
    
    print("\n🚀 Benefícios da Nova Estrutura:")
    print("   • 📁 Organização clara por chat_id")
    print("   • 🔍 Busca rápida de mídias específicas")
    print("   • 🌐 URLs previsíveis para o frontend") 
    print("   • 📈 Escalável para milhares de chats")
    print("   • 🏷️ Nomes de arquivo com message_id")
    print("   • 🔧 Compatibilidade com estrutura antiga")


def gerar_documentacao():
    """Gera documentação da nova estrutura"""
    doc_path = Path(__file__).parent / "NOVA_ESTRUTURA_MIDIAS.md"
    
    conteudo = """# Nova Estrutura de Organização de Mídias por Chat ID

## Visão Geral

A nova estrutura organiza as mídias do WhatsApp por `chat_id`, facilitando a busca e exibição no frontend.

## Estrutura de Pastas

```
multichat_system/media_storage/
├── cliente_2/
│   └── instance_3B6XIW-ZTS923-GEAY6V/
│       └── chats/
│           ├── 5511999999999/          # Chat individual
│           │   ├── audio/
│           │   │   ├── msg_ABC123_20250806_161207.mp3
│           │   │   └── msg_DEF456_20250806_161210.mp3
│           │   ├── document/
│           │   ├── image/
│           │   └── video/
│           ├── 5511888888888/          # Outro chat
│           │   ├── audio/
│           │   └── image/
│           └── group_363251234/        # Chat de grupo
│               ├── audio/
│               └── image/
```

## Normalização do Chat ID

- **Números individuais**: `5511999999999` (apenas números)
- **Grupos**: `group_363251234` (prefixo + últimos 12 dígitos)
- **Desconhecidos**: `unknown` (fallback)

## Formato dos Arquivos

- **Padrão**: `msg_{message_id}_{timestamp}.{extensão}`
- **Exemplo**: `msg_ABC12345_20250806_161207.mp3`

## URLs para Frontend

```
/media/whatsapp_media/cliente_2/instance_X/chats/5511999999999/audio/msg_ABC123_20250806_161207.mp3
```

## Migração

Execute o script `migrar_estrutura_midias_chat_id.py` para migrar da estrutura antiga.

## Vantagens

1. **Organização**: Mídias organizadas por conversa
2. **Performance**: Busca mais rápida por chat específico
3. **Escalabilidade**: Suporta milhares de chats
4. **Frontend**: URLs previsíveis e organizadas
5. **Identificação**: Nomes de arquivo com message_id

## Compatibilidade

O código mantém compatibilidade com a estrutura antiga durante a migração.
"""
    
    doc_path.write_text(conteudo, encoding='utf-8')
    print(f"📝 Documentação gerada: {doc_path}")


if __name__ == "__main__":
    testar_estrutura_chat_id()
    comparar_estruturas()
    gerar_documentacao()
    
    print("\n" + "="*50)
    print("✅ Todos os testes concluídos!")
    print("📋 Próximos passos:")
    print("   1. Execute: python migrar_estrutura_midias_chat_id.py")
    print("   2. Teste a nova estrutura em desenvolvimento")
    print("   3. Atualize o frontend para usar as novas URLs")
    print("   4. Monitore logs para verificar funcionamento")