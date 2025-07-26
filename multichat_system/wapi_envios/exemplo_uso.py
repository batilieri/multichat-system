#!/usr/bin/env python3
"""
Exemplo de uso dos módulos de envio WAPI atualizados.

Este arquivo demonstra como usar os módulos de envio de mensagens
via WhatsApp usando a API W-API com as funcionalidades mais recentes.

Autor: Sistema MultiChat
Data: 2025-07-11
"""

import os
import sys
from typing import Dict, Any

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wapi_envios.enviarTexto import EnviaTexto
from wapi_envios.enviarImagem import EnviaImagem
from wapi_envios.enviarDocumento import EnviaDocumento
from wapi_envios.enviarAudio import EnviaAudio
# from wapi_envios.enviarVideo import EnviaVideo  # Módulo básico, pode precisar de atualização
# from wapi_envios.enviarListaOpcoes import EnviaListaOpcoes  # Módulo básico, pode precisar de atualização
# from wapi_envios.enviarLocalizacao import EnviaLocalizacao  # Módulo básico, pode precisar de atualização
# from wapi_envios.enviarContato import EnviaContato  # Módulo básico, pode precisar de atualização


def exemplo_envio_texto():
    """Exemplo de envio de mensagem de texto"""
    print("📝 Exemplo: Envio de Texto")
    print("-" * 40)
    
    # Configurações
    instance_id = "SEU_INSTANCE_ID"
    api_token = "SEU_API_TOKEN"
    phone_number = "5511999999999"
    
    # Criar instância
    sender = EnviaTexto(instance_id, api_token)
    
    # Verificar status da conexão
    status = sender.check_connection_status()
    print(f"Status da conexão: {status}")
    
    if status == "connected":
        # Enviar mensagem simples
        result = sender.envia_mensagem_texto(phone_number, "Olá! Esta é uma mensagem de teste.")
        print(f"Resultado: {result}")
        
        # Enviar mensagem formatada
        result_bold = sender.envia_mensagem_formatada(phone_number, "Texto em negrito", "bold")
        print(f"Resultado negrito: {result_bold}")
        
        # Enviar mensagem com link
        result_link = sender.envia_mensagem_com_link(
            phone_number, 
            "Confira nosso site", 
            "https://exemplo.com"
        )
        print(f"Resultado com link: {result_link}")
        
        # Enviar mensagem urgente
        result_urgent = sender.envia_mensagem_urgente(phone_number, "Mensagem importante!")
        print(f"Resultado urgente: {result_urgent}")
    else:
        print("❌ Instância não conectada")


def exemplo_envio_imagem():
    """Exemplo de envio de imagem"""
    print("\n🖼️ Exemplo: Envio de Imagem")
    print("-" * 40)
    
    # Configurações
    instance_id = "SEU_INSTANCE_ID"
    api_token = "SEU_API_TOKEN"
    phone_number = "5511999999999"
    image_path = "/caminho/para/imagem.jpg"
    
    # Criar instância
    sender = EnviaImagem(instance_id, api_token)
    
    # Verificar formatos suportados
    formats = sender.get_supported_formats()
    print(f"Formatos suportados: {formats}")
    
    # Verificar tamanho máximo
    max_size = sender.get_max_file_size()
    print(f"Tamanho máximo: {max_size // (1024*1024)}MB")
    
    if os.path.exists(image_path):
        # Enviar imagem normal
        result = sender.enviar(phone_number, image_path, "Confira esta imagem!")
        print(f"Resultado: {result}")
        
        # Enviar com compressão
        result_compressed = sender.enviar_com_compressao(
            phone_number, image_path, "Imagem comprimida", quality=80
        )
        print(f"Resultado comprimido: {result_compressed}")
        
        # Enviar thumbnail
        result_thumb = sender.enviar_thumbnail(
            phone_number, image_path, "Thumbnail", (150, 150)
        )
        print(f"Resultado thumbnail: {result_thumb}")
    else:
        print(f"❌ Arquivo não encontrado: {image_path}")


def exemplo_envio_documento():
    """Exemplo de envio de documento"""
    print("\n📄 Exemplo: Envio de Documento")
    print("-" * 40)
    
    # Configurações
    instance_id = "SEU_INSTANCE_ID"
    api_token = "SEU_API_TOKEN"
    phone_number = "5511999999999"
    doc_path = "/caminho/para/documento.pdf"
    
    # Criar instância
    sender = EnviaDocumento(instance_id, api_token)
    
    # Verificar formatos suportados
    formats = sender.get_supported_formats()
    print(f"Formatos suportados: {formats}")
    
    # Verificar tamanho máximo
    max_size = sender.get_max_file_size()
    print(f"Tamanho máximo: {max_size // (1024*1024)}MB")
    
    if os.path.exists(doc_path):
        # Obter informações do arquivo
        file_info = sender.get_file_info(doc_path)
        print(f"Informações do arquivo: {file_info}")
        
        # Enviar documento normal
        result = sender.enviar(phone_number, doc_path, "Documento importante")
        print(f"Resultado: {result}")
        
        # Enviar PDF específico
        if doc_path.lower().endswith('.pdf'):
            result_pdf = sender.enviar_pdf(phone_number, doc_path, "PDF específico")
            print(f"Resultado PDF: {result_pdf}")
    else:
        print(f"❌ Arquivo não encontrado: {doc_path}")


# def exemplo_envio_lista_opcoes():
#     """Exemplo de envio de lista de opções"""
#     print("\n📋 Exemplo: Lista de Opções")
#     print("-" * 40)
#     
#     # Configurações
#     instance_id = "SEU_INSTANCE_ID"
#     api_token = "SEU_API_TOKEN"
#     phone_number = "5511999999999"
#     
#     # Criar instância
#     sender = EnviaListaOpcoes(instance_id, api_token)
#     
#     # Lista de opções
#     opcoes = [
#         {"title": "Opção 1", "description": "Descrição da opção 1"},
#         {"title": "Opção 2", "description": "Descrição da opção 2"},
#         {"title": "Opção 3", "description": "Descrição da opção 3"}
#     ]
#     
#     # Enviar lista
#     result = sender.enviar_lista_opcoes(
#         phone_number, 
#         "Escolha uma opção:", 
#         "Título da lista", 
#         opcoes
#     )
#     print(f"Resultado: {result}")


# def exemplo_envio_localizacao():
#     """Exemplo de envio de localização"""
#     print("\n📍 Exemplo: Localização")
#     print("-" * 40)
#     
#     # Configurações
#     instance_id = "SEU_INSTANCE_ID"
#     api_token = "SEU_API_TOKEN"
#     phone_number = "5511999999999"
#     
#     # Criar instância
#     sender = EnviaLocalizacao(instance_id, api_token)
#     
#     # Coordenadas (exemplo: São Paulo)
#     latitude = -23.5505
#     longitude = -46.6333
#     nome = "São Paulo, SP"
#     endereco = "São Paulo, São Paulo, Brasil"
#     
#     # Enviar localização
#     result = sender.enviar_localizacao(
#         phone_number, latitude, longitude, nome, endereco
#     )
#     print(f"Resultado: {result}")


# def exemplo_envio_contato():
#     """Exemplo de envio de contato"""
#     print("\n👤 Exemplo: Contato")
#     print("-" * 40)
#     
#     # Configurações
#     instance_id = "SEU_INSTANCE_ID"
#     api_token = "SEU_API_TOKEN"
#     phone_number = "5511999999999"
#     
#     # Criar instância
#     sender = EnviaContato(instance_id, api_token)
#     
#     # Dados do contato
#     nome = "João Silva"
#     telefone = "5511888888888"
#     
#     # Enviar contato
#     result = sender.enviar_contato(phone_number, nome, telefone)
#     print(f"Resultado: {result}")


def exemplo_envio_audio():
    """Exemplo de envio de áudio"""
    print("\n🎵 Exemplo: Áudio")
    print("-" * 40)
    
    # Configurações
    instance_id = "SEU_INSTANCE_ID"
    api_token = "SEU_API_TOKEN"
    phone_number = "5511999999999"
    audio_path = "/caminho/para/audio.mp3"
    
    # Criar instância
    sender = EnviaAudio(instance_id, api_token)
    
    if os.path.exists(audio_path):
        # Enviar áudio
        result = sender.enviar(phone_number, audio_path)
        print(f"Resultado: {result}")
    else:
        print(f"❌ Arquivo não encontrado: {audio_path}")


# def exemplo_envio_video():
#     """Exemplo de envio de vídeo"""
#     print("\n🎬 Exemplo: Vídeo")
#     print("-" * 40)
#     
#     # Configurações
#     instance_id = "SEU_INSTANCE_ID"
#     api_token = "SEU_API_TOKEN"
#     phone_number = "5511999999999"
#     video_path = "/caminho/para/video.mp4"
#     
#     # Criar instância
#     sender = EnviaVideo(instance_id, api_token)
#     
#     if os.path.exists(video_path):
#         # Enviar vídeo
#         result = sender.enviar(phone_number, video_path, "Confira este vídeo!")
#         print(f"Resultado: {result}")
#     else:
#         print(f"❌ Arquivo não encontrado: {video_path}")


def main():
    """Função principal com todos os exemplos"""
    print("🚀 Exemplos de Uso dos Módulos WAPI Atualizados")
    print("=" * 60)
    
    # Configurar credenciais (substitua pelos seus valores)
    os.environ['WAPI_INSTANCE_ID'] = "SEU_INSTANCE_ID"
    os.environ['WAPI_API_TOKEN'] = "SEU_API_TOKEN"
    
    # Executar exemplos
    try:
        exemplo_envio_texto()
        exemplo_envio_imagem()
        exemplo_envio_documento()
        # exemplo_envio_lista_opcoes()  # Módulo básico, comentado
        # exemplo_envio_localizacao()   # Módulo básico, comentado
        # exemplo_envio_contato()       # Módulo básico, comentado
        exemplo_envio_audio()
        # exemplo_envio_video()         # Módulo básico, comentado
        
        print("\n✅ Todos os exemplos executados!")
        
    except Exception as e:
        print(f"\n❌ Erro ao executar exemplos: {e}")
        print("💡 Certifique-se de configurar as credenciais corretas")


if __name__ == "__main__":
    main() 