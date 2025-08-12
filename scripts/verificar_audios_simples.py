#!/usr/bin/env python3
"""
Verificação simples do problema de download automático de áudios
"""

import os
import sys
import json
from pathlib import Path

def verificar_estrutura_pastas():
    """Verifica a estrutura de pastas de mídia"""
    print("📁 VERIFICANDO ESTRUTURA DE PASTAS")
    print("=" * 60)
    
    # Verificar pasta de mídia
    media_path = Path("multichat_system/media_storage")
    if not media_path.exists():
        print("❌ Pasta media_storage não encontrada!")
        return False
    
    print(f"✅ Pasta media_storage encontrada: {media_path}")
    
    # Verificar estrutura de clientes
    for cliente_dir in media_path.glob("cliente_*"):
        print(f"\n👤 Cliente: {cliente_dir.name}")
        
        # Verificar instâncias
        for instance_dir in cliente_dir.glob("instance_*"):
            print(f"   📱 Instância: {instance_dir.name}")
            
            # Verificar tipos de mídia
            for media_type in ['audio', 'imagens', 'videos', 'documentos']:
                media_dir = instance_dir / media_type
                if media_dir.exists():
                    files = list(media_dir.glob("*"))
                    print(f"      {media_type}: {len(files)} arquivos")
                    if len(files) > 0:
                        for file in files[:3]:  # Mostrar primeiros 3 arquivos
                            print(f"         - {file.name}")
                else:
                    print(f"      {media_type}: pasta não existe")
    
    return True

def verificar_webhook_views():
    """Verifica o código do webhook para processamento de áudios"""
    print("\n🔍 VERIFICANDO CÓDIGO DO WEBHOOK")
    print("=" * 60)
    
    webhook_file = Path("multichat_system/webhook/views.py")
    if not webhook_file.exists():
        print("❌ Arquivo webhook/views.py não encontrado!")
        return False
    
    print(f"✅ Arquivo webhook/views.py encontrado")
    
    # Verificar se contém processamento de áudio
    with open(webhook_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
        if 'audioMessage' in content:
            print("✅ Contém processamento de audioMessage")
        else:
            print("❌ NÃO contém processamento de audioMessage")
            
        if 'process_media_automatically' in content:
            print("✅ Contém função process_media_automatically")
        else:
            print("❌ NÃO contém função process_media_automatically")
            
        if 'download_media_via_wapi' in content:
            print("✅ Contém função download_media_via_wapi")
        else:
            print("❌ NÃO contém função download_media_via_wapi")
    
    return True

def verificar_documentacao():
    """Verifica a documentação sobre áudios"""
    print("\n📋 VERIFICANDO DOCUMENTAÇÃO")
    print("=" * 60)
    
    docs_files = [
        "SOLUCAO_FINAL_AUDIOS.md",
        "RELATORIO_TESTE_DOWNLOAD_REAL_MIDIAS.md",
        "SISTEMA_DOWNLOAD_ATIVO.md"
    ]
    
    for doc_file in docs_files:
        doc_path = Path(doc_file)
        if doc_path.exists():
            print(f"✅ {doc_file} encontrado")
            
            # Verificar se menciona problemas com áudio
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'audio' in content.lower():
                    print(f"   📝 Menciona áudio")
                if 'download' in content.lower():
                    print(f"   📥 Menciona download")
                if 'problema' in content.lower() or 'erro' in content.lower():
                    print(f"   ⚠️ Menciona problemas/erros")
        else:
            print(f"❌ {doc_file} não encontrado")

def verificar_logs():
    """Verifica logs do sistema"""
    print("\n📊 VERIFICANDO LOGS")
    print("=" * 60)
    
    log_file = Path("multichat_system/logs/django.log")
    if log_file.exists():
        print(f"✅ Log encontrado: {log_file}")
        
        # Verificar tamanho do log
        size_mb = log_file.stat().st_size / (1024 * 1024)
        print(f"   Tamanho: {size_mb:.2f} MB")
        
        # Verificar últimas linhas
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                last_lines = lines[-10:] if len(lines) > 10 else lines
                
                print(f"   Últimas {len(last_lines)} linhas:")
                for line in last_lines:
                    if 'audio' in line.lower() or 'media' in line.lower():
                        print(f"      🎵 {line.strip()}")
                    elif 'error' in line.lower() or 'erro' in line.lower():
                        print(f"      ❌ {line.strip()}")
        except Exception as e:
            print(f"   ❌ Erro ao ler log: {e}")
    else:
        print("❌ Log não encontrado")

def main():
    """Função principal"""
    print("🔍 ANÁLISE DO PROBLEMA - DOWNLOAD AUTOMÁTICO DE ÁUDIOS")
    print("=" * 80)
    
    try:
        # Verificar estrutura
        estrutura_ok = verificar_estrutura_pastas()
        
        # Verificar código
        codigo_ok = verificar_webhook_views()
        
        # Verificar documentação
        verificar_documentacao()
        
        # Verificar logs
        verificar_logs()
        
        print("\n" + "=" * 80)
        print("✅ ANÁLISE CONCLUÍDA!")
        
        print("\n💡 POSSÍVEIS CAUSAS DO PROBLEMA:")
        print("   1. Webhooks não estão chegando com dados de áudio")
        print("   2. Configuração W-API incorreta (token/instance_id)")
        print("   3. Função process_media_automatically não sendo chamada")
        print("   4. Campos obrigatórios ausentes (mediaKey, directPath)")
        print("   5. Problemas de permissão nas pastas")
        print("   6. Instância WhatsApp desconectada")
        
        print("\n🔧 PRÓXIMOS PASSOS:")
        print("   1. Verificar se webhooks estão chegando")
        print("   2. Testar configuração W-API")
        print("   3. Enviar áudio real no WhatsApp")
        print("   4. Verificar logs em tempo real")
        print("   5. Testar conexão com API W-API")
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 