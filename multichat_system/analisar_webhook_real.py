#!/usr/bin/env python3
"""
Analisador de Webhook Real do WhatsApp
Extrai e analisa dados reais de webhooks recebidos
"""

import os
import sys
import json
import django
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat.settings')
django.setup()

from core.webhook_media_analyzer import analisar_webhook_whatsapp, gerar_relatorio_webhook


def analisar_estrutura_webhook(webhook_data: Dict[str, Any], nivel: int = 0, max_nivel: int = 5) -> None:
    """
    Analisa recursivamente a estrutura do webhook
    """
    if nivel > max_nivel:
        return
    
    indent = "  " * nivel
    
    for key, value in webhook_data.items():
        if isinstance(value, dict):
            print(f"{indent}📁 {key}: {{")
            analisar_estrutura_webhook(value, nivel + 1, max_nivel)
            print(f"{indent}}}")
        elif isinstance(value, list):
            print(f"{indent}📋 {key}: [")
            for i, item in enumerate(value[:3]):  # Mostrar apenas os 3 primeiros
                print(f"{indent}  [{i}]:")
                if isinstance(item, dict):
                    analisar_estrutura_webhook(item, nivel + 2, max_nivel)
                else:
                    print(f"{indent}    {item}")
            if len(value) > 3:
                print(f"{indent}  ... ({len(value) - 3} mais)")
            print(f"{indent}]")
        else:
            # Truncar valores muito longos
            str_value = str(value)
            if len(str_value) > 100:
                str_value = str_value[:100] + "..."
            print(f"{indent}📄 {key}: {str_value}")


def extrair_dados_midia_detalhado(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrai dados detalhados de mídia do webhook
    """
    resultado = {
        'info_basica': {},
        'midias_encontradas': [],
        'campos_obrigatorios': {},
        'campos_opcionais': {},
        'estrutura_completa': {}
    }
    
    # Informações básicas
    resultado['info_basica'] = {
        'event': webhook_data.get('event'),
        'instanceId': webhook_data.get('instanceId'),
        'messageId': webhook_data.get('messageId'),
        'timestamp': webhook_data.get('moment'),
        'isGroup': webhook_data.get('isGroup'),
        'fromMe': webhook_data.get('fromMe')
    }
    
    # Analisar msgContent
    msg_content = webhook_data.get('msgContent', {})
    
    tipos_midia = {
        'imageMessage': 'image',
        'videoMessage': 'video', 
        'audioMessage': 'audio',
        'documentMessage': 'document',
        'stickerMessage': 'sticker'
    }
    
    for tipo_msg, tipo_midia in tipos_midia.items():
        if tipo_msg in msg_content:
            midia_data = msg_content[tipo_msg]
            
            # Campos obrigatórios para descriptografia
            campos_obrigatorios = ['mediaKey', 'directPath', 'fileEncSha256', 'fileSha256']
            campos_presentes = {}
            campos_faltando = []
            
            for campo in campos_obrigatorios:
                if campo in midia_data:
                    valor = midia_data[campo]
                    # Truncar valores longos para exibição
                    if isinstance(valor, str) and len(valor) > 50:
                        valor_exibicao = valor[:50] + "..."
                    else:
                        valor_exibicao = valor
                    campos_presentes[campo] = {
                        'valor': valor,
                        'valor_exibicao': valor_exibicao,
                        'tipo': type(valor).__name__,
                        'tamanho': len(str(valor)) if valor else 0
                    }
                else:
                    campos_faltando.append(campo)
            
            # Campos opcionais
            campos_opcionais = {}
            for campo, valor in midia_data.items():
                if campo not in campos_obrigatorios:
                    if isinstance(valor, str) and len(valor) > 100:
                        valor_exibicao = valor[:100] + "..."
                    else:
                        valor_exibicao = valor
                    campos_opcionais[campo] = {
                        'valor': valor,
                        'valor_exibicao': valor_exibicao,
                        'tipo': type(valor).__name__,
                        'tamanho': len(str(valor)) if valor else 0
                    }
            
            midia_info = {
                'tipo': tipo_midia,
                'tipo_original': tipo_msg,
                'campos_obrigatorios': {
                    'presentes': campos_presentes,
                    'faltando': campos_faltando,
                    'valido_para_download': len(campos_faltando) == 0
                },
                'campos_opcionais': campos_opcionais,
                'dados_completos': midia_data
            }
            
            resultado['midias_encontradas'].append(midia_info)
    
    # Estrutura completa do webhook
    resultado['estrutura_completa'] = webhook_data
    
    return resultado


def mostrar_analise_detalhada(analise: Dict[str, Any]) -> None:
    """
    Mostra análise detalhada dos dados extraídos
    """
    print("\n" + "="*80)
    print("🔍 ANÁLISE DETALHADA DO WEBHOOK")
    print("="*80)
    
    # Informações básicas
    info_basica = analise['info_basica']
    print(f"\n📋 INFORMAÇÕES BÁSICAS:")
    print(f"   📨 Evento: {info_basica.get('event')}")
    print(f"   📱 Instance ID: {info_basica.get('instanceId')}")
    print(f"   🆔 Message ID: {info_basica.get('messageId')}")
    print(f"   ⏰ Timestamp: {info_basica.get('timestamp')}")
    print(f"   👥 É Grupo: {info_basica.get('isGroup')}")
    print(f"   📤 De Mim: {info_basica.get('fromMe')}")
    
    # Mídias encontradas
    midias = analise['midias_encontradas']
    print(f"\n📎 MÍDIAS ENCONTRADAS: {len(midias)}")
    
    for i, midia in enumerate(midias, 1):
        print(f"\n   {i}. {midia['tipo'].upper()} ({midia['tipo_original']}):")
        
        # Campos obrigatórios
        obrigatorios = midia['campos_obrigatorios']
        print(f"      🔐 CAMPOS OBRIGATÓRIOS:")
        print(f"         ✅ Válido para download: {obrigatorios['valido_para_download']}")
        
        for campo, info in obrigatorios['presentes'].items():
            print(f"         ✅ {campo}:")
            print(f"            Valor: {info['valor_exibicao']}")
            print(f"            Tipo: {info['tipo']}")
            print(f"            Tamanho: {info['tamanho']} caracteres")
        
        if obrigatorios['faltando']:
            print(f"         ❌ CAMPOS FALTANDO:")
            for campo in obrigatorios['faltando']:
                print(f"            - {campo}")
        
        # Campos opcionais
        opcionais = midia['campos_opcionais']
        if opcionais:
            print(f"      📄 CAMPOS OPCIONAIS ({len(opcionais)}):")
            for campo, info in opcionais.items():
                print(f"         📄 {campo}:")
                print(f"            Valor: {info['valor_exibicao']}")
                print(f"            Tipo: {info['tipo']}")
                print(f"            Tamanho: {info['tamanho']} caracteres")


def analisar_webhook_arquivo(caminho_arquivo: str) -> None:
    """
    Analisa webhook de um arquivo JSON
    """
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            webhook_data = json.load(f)
        
        print(f"📁 Analisando arquivo: {caminho_arquivo}")
        analisar_webhook_completo(webhook_data)
        
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {e}")
    except Exception as e:
        print(f"❌ Erro ao analisar arquivo: {e}")


def analisar_webhook_completo(webhook_data: Dict[str, Any]) -> None:
    """
    Análise completa de um webhook
    """
    print("\n" + "="*80)
    print("🚀 ANÁLISE COMPLETA DE WEBHOOK WHATSAPP")
    print("="*80)
    
    # 1. Estrutura do webhook
    print(f"\n📊 ESTRUTURA DO WEBHOOK:")
    analisar_estrutura_webhook(webhook_data)
    
    # 2. Extração detalhada de dados
    print(f"\n🔍 EXTRAÇÃO DETALHADA DE DADOS:")
    analise_detalhada = extrair_dados_midia_detalhado(webhook_data)
    mostrar_analise_detalhada(analise_detalhada)
    
    # 3. Análise usando o sistema Django
    print(f"\n🎯 ANÁLISE COM SISTEMA DJANGO:")
    try:
        analise_django = analisar_webhook_whatsapp(webhook_data)
        
        if analise_django.get('cliente_info', {}).get('encontrado'):
            cliente_info = analise_django['cliente_info']
            print(f"   ✅ Cliente encontrado: {cliente_info['cliente_nome']}")
            print(f"   📱 Instância: {cliente_info['instance_id']}")
            print(f"   🔑 Token: {cliente_info['instance_token'][:20]}...")
        else:
            print(f"   ❌ Cliente não encontrado: {analise_django.get('cliente_info', {}).get('erro')}")
        
        print(f"   📎 Total de mídias: {analise_django.get('total_midias', 0)}")
        
        for midia in analise_django.get('midias', []):
            print(f"   📄 {midia['type']}: {midia.get('mimetype')} - {midia.get('valido_para_download')}")
            
    except Exception as e:
        print(f"   ❌ Erro na análise Django: {e}")
    
    # 4. Relatório completo
    print(f"\n📋 RELATÓRIO COMPLETO:")
    try:
        relatorio = gerar_relatorio_webhook(webhook_data)
        print(relatorio)
    except Exception as e:
        print(f"   ❌ Erro ao gerar relatório: {e}")


def criar_webhook_exemplo() -> Dict[str, Any]:
    """
    Cria um webhook de exemplo para teste
    """
    return {
        'event': 'webhookReceived',
        'instanceId': '3B6XIW-ZTS923-GEAY6V',
        'messageId': f'exemplo_{int(datetime.now().timestamp())}',
        'sender': {
            'id': '5511999999999@s.whatsapp.net',
            'pushName': 'Usuário Teste'
        },
        'chat': {
            'id': '5511999999999@s.whatsapp.net'
        },
        'msgContent': {
            'imageMessage': {
                'mimetype': 'image/jpeg',
                'fileName': 'foto_exemplo.jpg',
                'fileLength': 8192,
                'caption': 'Foto de exemplo para análise',
                'mediaKey': 'exemplo_media_key_1234567890123456789012345678901234567890',
                'directPath': '/exemplo/path/to/image',
                'fileSha256': 'exemplo_sha256_1234567890123456789012345678901234567890',
                'fileEncSha256': 'exemplo_enc_sha256_1234567890123456789012345678901234567890',
                'width': 1200,
                'height': 800,
                'jpegThumbnail': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxAAPwCdABmX/9k=',
                'mediaKeyTimestamp': '1234567890'
            }
        },
        'isGroup': False,
        'fromMe': False,
        'moment': int(datetime.now().timestamp())
    }


def main():
    """
    Função principal
    """
    print("🔍 ANALISADOR DE WEBHOOK REAL DO WHATSAPP")
    print("="*60)
    
    # Verificar se foi passado um arquivo como argumento
    if len(sys.argv) > 1:
        arquivo_webhook = sys.argv[1]
        analisar_webhook_arquivo(arquivo_webhook)
    else:
        print("📝 Nenhum arquivo especificado. Criando webhook de exemplo...")
        
        # Criar webhook de exemplo
        webhook_exemplo = criar_webhook_exemplo()
        
        print("✅ Webhook de exemplo criado!")
        print("💡 Para analisar um webhook real, execute:")
        print("   python analisar_webhook_real.py caminho/para/webhook.json")
        
        # Analisar webhook de exemplo
        analisar_webhook_completo(webhook_exemplo)


if __name__ == "__main__":
    main() 