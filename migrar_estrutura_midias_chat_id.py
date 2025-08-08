#!/usr/bin/env python3
"""
Script para migrar estrutura de mídias para organização por chat_id
Migra de: cliente_X/instance_Y/tipo/arquivo
Para: cliente_X/instance_Y/chats/chat_id/tipo/arquivo
"""

import os
import shutil
import sqlite3
import re
from pathlib import Path
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MigradorEstruturaMidias:
    """Migrador para nova estrutura organizacional por chat_id"""
    
    def __init__(self, base_path: str = None):
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Usar caminho padrão do projeto
            self.base_path = Path(__file__).parent / "multichat_system" / "media_storage"
        
        self.backup_path = self.base_path.parent / "media_storage_backup"
        self.stats = {
            'arquivos_migrados': 0,
            'arquivos_erro': 0,
            'chats_criados': 0,
            'clientes_processados': 0
        }
        
    def criar_backup(self) -> bool:
        """Cria backup completo da estrutura atual"""
        try:
            logger.info("📦 Criando backup da estrutura atual...")
            
            if self.backup_path.exists():
                shutil.rmtree(self.backup_path)
                
            shutil.copytree(self.base_path, self.backup_path)
            logger.info(f"✅ Backup criado em: {self.backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar backup: {e}")
            return False
            
    def extrair_info_arquivo(self, caminho_arquivo: Path) -> dict:
        """Extrai informações do nome do arquivo"""
        nome = caminho_arquivo.stem
        extensao = caminho_arquivo.suffix
        
        # Padrões para extrair message_id dos nomes existentes
        patterns = [
            r'wapi_([A-F0-9]{32})_',  # wapi_HASH_timestamp
            r'(\d{8}_\d{6})_',        # timestamp_sender_message
            r'.*_([A-Z0-9]{8,})$'     # qualquer hash no final
        ]
        
        message_id = None
        for pattern in patterns:
            match = re.search(pattern, nome)
            if match:
                message_id = match.group(1)
                break
                
        if not message_id:
            # Gerar ID baseado no timestamp do arquivo
            timestamp = datetime.fromtimestamp(caminho_arquivo.stat().st_mtime)
            message_id = f"migrated_{timestamp.strftime('%Y%m%d_%H%M%S')}"
            
        return {
            'message_id': message_id,
            'extensao': extensao,
            'nome_original': nome,
            'tamanho': caminho_arquivo.stat().st_size
        }
        
    def buscar_chat_id_no_banco(self, cliente_id: str, instance_id: str, message_id: str) -> str:
        """Busca chat_id no banco de dados local da instância"""
        try:
            db_path = self.base_path / f"cliente_{cliente_id}" / f"instance_{instance_id}" / "media_database.db"
            
            if not db_path.exists():
                return None
                
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT chat_id FROM midias WHERE message_id LIKE ? OR message_id = ? LIMIT 1",
                    (f"%{message_id}%", message_id)
                )
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logger.debug(f"Erro ao buscar no banco: {e}")
            return None
            
    def normalizar_chat_id(self, chat_id: str) -> str:
        """Normaliza chat_id removendo sufixos do WhatsApp"""
        if not chat_id:
            return "unknown"
            
        # Remover sufixos do WhatsApp
        chat_id = re.sub(r'@[^.]+\.us$', '', chat_id)
        chat_id = re.sub(r'@[^.]+$', '', chat_id)
        
        # Extrair apenas números
        numbers_only = re.sub(r'[^\d]', '', chat_id)
        
        # Se é um grupo (padrão 120363), usar identificador especial
        if len(numbers_only) > 15 and numbers_only.startswith('120363'):
            return f"group_{numbers_only[-12:]}"  # Últimos 12 dígitos
            
        # Se é número válido, usar como está
        if len(numbers_only) >= 10:
            return numbers_only
            
        # Fallback para chat_id original limpo
        clean_id = re.sub(r'[^\w\-]', '_', str(chat_id))
        return clean_id or "unknown"
        
    def migrar_arquivo(self, arquivo_origem: Path, cliente_id: str, instance_id: str) -> bool:
        """Migra um arquivo individual para a nova estrutura"""
        try:
            # Extrair informações do arquivo
            info = self.extrair_info_arquivo(arquivo_origem)
            tipo_midia = arquivo_origem.parent.name
            
            # Buscar chat_id no banco de dados
            chat_id = self.buscar_chat_id_no_banco(cliente_id, instance_id, info['message_id'])
            
            if not chat_id:
                # Se não encontrar no banco, usar chat_id padrão baseado no nome do arquivo
                if 'wapi_' in info['nome_original']:
                    # Para arquivos do WAPI, tentar extrair do hash
                    chat_id = "unknown_wapi"
                else:
                    chat_id = "unknown"
                    
            # Normalizar chat_id
            chat_id_normalizado = self.normalizar_chat_id(chat_id)
            
            # Criar estrutura de destino
            destino_base = self.base_path / f"cliente_{cliente_id}" / f"instance_{instance_id}"
            destino_chat = destino_base / "chats" / chat_id_normalizado / tipo_midia
            destino_chat.mkdir(parents=True, exist_ok=True)
            
            # Gerar nome do novo arquivo (incluindo message_id e timestamp original)
            timestamp_original = datetime.fromtimestamp(arquivo_origem.stat().st_mtime).strftime("%Y%m%d_%H%M%S")
            nome_novo = f"msg_{info['message_id']}_{timestamp_original}{info['extensao']}"
            arquivo_destino = destino_chat / nome_novo
            
            # Verificar se já existe (adicionar contador se necessário)
            contador = 1
            while arquivo_destino.exists():
                nome_novo = f"msg_{info['message_id']}_{timestamp_original}_{contador:02d}{info['extensao']}"
                arquivo_destino = destino_chat / nome_novo
                contador += 1
                
            # Mover arquivo
            shutil.move(str(arquivo_origem), str(arquivo_destino))
            
            logger.info(f"📁 {arquivo_origem.name} -> chats/{chat_id_normalizado}/{tipo_midia}/{nome_novo}")
            
            self.stats['arquivos_migrados'] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao migrar {arquivo_origem}: {e}")
            self.stats['arquivos_erro'] += 1
            return False
            
    def migrar_instancia(self, instancia_path: Path) -> bool:
        """Migra todos os arquivos de uma instância"""
        try:
            logger.info(f"🔄 Migrando instância: {instancia_path.name}")
            
            # Extrair IDs
            cliente_id = instancia_path.parent.name.replace('cliente_', '')
            instance_id = instancia_path.name.replace('instance_', '')
            
            # Tipos de mídia existentes
            tipos_midia = ['audio', 'video', 'image', 'document', 'sticker']
            
            arquivos_encontrados = 0
            
            for tipo in tipos_midia:
                pasta_tipo = instancia_path / tipo
                if not pasta_tipo.exists():
                    continue
                    
                # Processar todos os arquivos da pasta
                for arquivo in pasta_tipo.iterdir():
                    if arquivo.is_file():
                        arquivos_encontrados += 1
                        self.migrar_arquivo(arquivo, cliente_id, instance_id)
                        
            # Remover pastas antigas vazias
            for tipo in tipos_midia:
                pasta_tipo = instancia_path / tipo
                if pasta_tipo.exists() and not list(pasta_tipo.iterdir()):
                    pasta_tipo.rmdir()
                    logger.info(f"🗑️ Removida pasta vazia: {tipo}")
                    
            logger.info(f"✅ Instância migrada: {arquivos_encontrados} arquivos processados")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao migrar instância {instancia_path}: {e}")
            return False
            
    def migrar_cliente(self, cliente_path: Path) -> bool:
        """Migra todos os arquivos de um cliente"""
        try:
            logger.info(f"👤 Migrando cliente: {cliente_path.name}")
            
            instancias_migradas = 0
            
            for item in cliente_path.iterdir():
                if item.is_dir() and item.name.startswith('instance_'):
                    if self.migrar_instancia(item):
                        instancias_migradas += 1
                        
            logger.info(f"✅ Cliente migrado: {instancias_migradas} instâncias")
            self.stats['clientes_processados'] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao migrar cliente {cliente_path}: {e}")
            return False
            
    def executar_migracao(self, criar_backup: bool = True) -> bool:
        """Executa a migração completa"""
        try:
            logger.info("🚀 Iniciando migração da estrutura de mídias...")
            
            if not self.base_path.exists():
                logger.error(f"❌ Pasta base não encontrada: {self.base_path}")
                return False
                
            # Criar backup se solicitado
            if criar_backup and not self.criar_backup():
                logger.error("❌ Falha ao criar backup. Abortando migração.")
                return False
                
            # Processar cada cliente
            for item in self.base_path.iterdir():
                if item.is_dir() and item.name.startswith('cliente_'):
                    self.migrar_cliente(item)
                    
            # Relatório final
            self.gerar_relatorio()
            
            logger.info("🎉 Migração concluída!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na migração: {e}")
            return False
            
    def gerar_relatorio(self):
        """Gera relatório da migração"""
        logger.info("📊 Relatório de Migração:")
        logger.info(f"   📁 Clientes processados: {self.stats['clientes_processados']}")
        logger.info(f"   📄 Arquivos migrados: {self.stats['arquivos_migrados']}")
        logger.info(f"   ❌ Arquivos com erro: {self.stats['arquivos_erro']}")
        logger.info(f"   💾 Backup criado em: {self.backup_path}")
        
        # Salvar relatório em arquivo
        relatorio_path = self.base_path.parent / f"relatorio_migracao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            f.write("Relatório de Migração - Estrutura de Mídias por Chat ID\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("Estatísticas:\n")
            f.write(f"- Clientes processados: {self.stats['clientes_processados']}\n")
            f.write(f"- Arquivos migrados: {self.stats['arquivos_migrados']}\n")
            f.write(f"- Arquivos com erro: {self.stats['arquivos_erro']}\n")
            f.write(f"- Backup criado em: {self.backup_path}\n\n")
            
            if self.stats['arquivos_erro'] > 0:
                f.write("⚠️ Alguns arquivos tiveram erro na migração.\n")
                f.write("Verifique os logs para mais detalhes.\n\n")
                
            f.write("Nova estrutura:\n")
            f.write("cliente_X/\n")
            f.write("└── instance_Y/\n")
            f.write("    └── chats/\n")
            f.write("        ├── chat_id_1/\n")
            f.write("        │   ├── audio/\n")
            f.write("        │   ├── document/\n")
            f.write("        │   ├── image/\n")
            f.write("        │   └── video/\n")
            f.write("        └── chat_id_2/\n")
            f.write("            ├── audio/\n")
            f.write("            └── ...\n")
            
        logger.info(f"📝 Relatório salvo em: {relatorio_path}")


def main():
    """Função principal"""
    print("Migracao de Estrutura de Midias por Chat ID")
    print("=" * 50)
    
    # Executar migração automaticamente (modo não-interativo)
    print("Executando migracao automaticamente...")
        
    # Criar migrador
    migrador = MigradorEstruturaMidias()
    
    # Executar migração
    sucesso = migrador.executar_migracao(criar_backup=True)
    
    if sucesso:
        print("OK Migracao concluida com sucesso!")
        print(f"Arquivos migrados: {migrador.stats['arquivos_migrados']}")
        print(f"Backup disponivel em: {migrador.backup_path}")
    else:
        print("ERRO Migracao falhou. Verifique os logs.")
        
        
if __name__ == "__main__":
    main()