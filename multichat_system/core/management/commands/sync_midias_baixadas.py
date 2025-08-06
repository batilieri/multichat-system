#!/usr/bin/env python3
"""
Comando Django para sincronizar mídias baixadas com o banco de dados
Conecta os áudios da pasta /wapi/midias/ com as mensagens no Django
"""

import os
import json
import hashlib
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Mensagem, Chat, Cliente
from datetime import datetime

class Command(BaseCommand):
    help = 'Sincroniza mídias baixadas da pasta /wapi/midias/ com as mensagens do Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pasta-midias',
            type=str,
            default='../../wapi/midias',
            help='Caminho para a pasta de mídias baixadas'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas simular as operações'
        )

    def handle(self, *args, **options):
        pasta_midias = Path(options['pasta_midias'])
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN ATIVADO - Nenhuma alteração será feita'))
        
        self.stdout.write(f'Sincronizando mídias de: {pasta_midias.absolute()}')
        
        if not pasta_midias.exists():
            self.stdout.write(self.style.ERROR(f'Pasta não encontrada: {pasta_midias}'))
            return
        
        # Processar áudios
        pasta_audios = pasta_midias / 'audios'
        if pasta_audios.exists():
            self.processar_audios(pasta_audios, dry_run)
        
        # Processar imagens
        pasta_imagens = pasta_midias / 'imagens'
        if pasta_imagens.exists():
            self.processar_imagens(pasta_imagens, dry_run)
        
        self.stdout.write(self.style.SUCCESS('Sincronização concluída!'))

    def processar_audios(self, pasta_audios, dry_run=False):
        """Processa arquivos de áudio"""
        self.stdout.write('\n=== PROCESSANDO ÁUDIOS ===')
        
        arquivos_audio = list(pasta_audios.glob('*.mp3')) + list(pasta_audios.glob('*.ogg')) + list(pasta_audios.glob('*.m4a'))
        
        self.stdout.write(f'Encontrados {len(arquivos_audio)} arquivos de áudio')
        
        for arquivo in arquivos_audio:
            self.stdout.write(f'\nProcessando: {arquivo.name}')
            
            try:
                # Obter informações do arquivo
                stats = arquivo.stat()
                tamanho = stats.st_size
                data_modificacao = datetime.fromtimestamp(stats.st_mtime)
                
                self.stdout.write(f'  Tamanho: {tamanho} bytes')
                self.stdout.write(f'  Modificado: {data_modificacao}')
                
                # Calcular hash para identificação única
                hash_arquivo = self.calcular_hash_arquivo(arquivo)
                self.stdout.write(f'  Hash: {hash_arquivo[:16]}...')
                
                # Verificar se já existe mensagem com este áudio
                mensagem_existente = Mensagem.objects.filter(
                    tipo='audio',
                    conteudo__icontains=arquivo.name
                ).first()
                
                if mensagem_existente:
                    self.stdout.write(f'  OK Mensagem existente encontrada: ID {mensagem_existente.id}')
                    
                    # Atualizar URL se necessário
                    caminho_relativo = f'/wapi/midias/audios/{arquivo.name}'
                    conteudo_atual = mensagem_existente.conteudo
                    
                    try:
                        if conteudo_atual.startswith('{'):
                            conteudo_json = json.loads(conteudo_atual)
                        else:
                            conteudo_json = {"audioMessage": {}}
                        
                        # Atualizar com caminho correto
                        conteudo_json["audioMessage"]["url"] = caminho_relativo
                        conteudo_json["audioMessage"]["localPath"] = str(arquivo.absolute())
                        conteudo_json["audioMessage"]["fileSize"] = tamanho
                        conteudo_json["audioMessage"]["hash"] = hash_arquivo
                        
                        if not dry_run:
                            mensagem_existente.conteudo = json.dumps(conteudo_json, ensure_ascii=False)
                            mensagem_existente.save()
                            self.stdout.write(f'  OK Mensagem atualizada com caminho do áudio')
                        
                    except json.JSONDecodeError:
                        # Criar conteúdo JSON válido
                        conteudo_json = {
                            "audioMessage": {
                                "url": caminho_relativo,
                                "localPath": str(arquivo.absolute()),
                                "fileSize": tamanho,
                                "hash": hash_arquivo,
                                "fileName": arquivo.name
                            }
                        }
                        
                        if not dry_run:
                            mensagem_existente.conteudo = json.dumps(conteudo_json, ensure_ascii=False)
                            mensagem_existente.save()
                            self.stdout.write(f'  OK Conteúdo JSON criado para áudio')
                else:
                    self.stdout.write(f'  AVISO Nenhuma mensagem correspondente encontrada')
                    
                    # Criar mensagem de exemplo para qualquer áudio não associado
                    self.stdout.write(f'  INFO - Criando mensagem de exemplo para: {arquivo.name}')
                    self.criar_mensagem_audio_exemplo(arquivo, hash_arquivo, tamanho, dry_run)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ERRO Erro ao processar {arquivo.name}: {e}'))

    def processar_imagens(self, pasta_imagens, dry_run=False):
        """Processa arquivos de imagem"""
        self.stdout.write('\n=== PROCESSANDO IMAGENS ===')
        
        arquivos_imagem = (list(pasta_imagens.glob('*.jpg')) + 
                          list(pasta_imagens.glob('*.jpeg')) + 
                          list(pasta_imagens.glob('*.png')))
        
        self.stdout.write(f'Encontrados {len(arquivos_imagem)} arquivos de imagem')
        
        for arquivo in arquivos_imagem:
            self.stdout.write(f'\nProcessando: {arquivo.name}')
            
            try:
                # Procurar mensagem correspondente
                mensagem = Mensagem.objects.filter(
                    tipo='image',
                    conteudo__icontains=arquivo.stem
                ).first()
                
                if mensagem:
                    caminho_relativo = f'/wapi/midias/imagens/{arquivo.name}'
                    
                    # Atualizar conteúdo com caminho da imagem
                    try:
                        if mensagem.conteudo.startswith('{'):
                            conteudo_json = json.loads(mensagem.conteudo)
                        else:
                            conteudo_json = {"imageMessage": {}}
                        
                        conteudo_json["imageMessage"]["url"] = caminho_relativo
                        conteudo_json["imageMessage"]["localPath"] = str(arquivo.absolute())
                        
                        if not dry_run:
                            mensagem.conteudo = json.dumps(conteudo_json, ensure_ascii=False)
                            mensagem.save()
                            self.stdout.write(f'  OK Imagem atualizada: ID {mensagem.id}')
                        
                    except json.JSONDecodeError:
                        self.stdout.write(f'  AVISO Erro ao processar JSON da mensagem {mensagem.id}')
                else:
                    self.stdout.write(f'  AVISO Nenhuma mensagem correspondente encontrada')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ERRO Erro: {e}'))

    def criar_mensagem_audio_exemplo(self, arquivo, hash_arquivo, tamanho, dry_run=False):
        """Cria mensagem de áudio de exemplo para testes"""
        try:
            # Buscar ou criar cliente de teste
            cliente_teste, created = Cliente.objects.get_or_create(
                telefone='+5511999999999',
                defaults={'nome': 'Cliente Teste Áudio'}
            )
            
            # Buscar ou criar chat de teste
            chat_teste, created = Chat.objects.get_or_create(
                cliente=cliente_teste,
                chat_id='5511999999999',
                defaults={'chat_name': 'Chat Teste Áudio'}
            )
            
            # Criar conteúdo JSON para o áudio
            conteudo_json = {
                "audioMessage": {
                    "url": f"/wapi/midias/audios/{arquivo.name}",
                    "localPath": str(arquivo.absolute()),
                    "fileSize": tamanho,
                    "hash": hash_arquivo,
                    "fileName": arquivo.name,
                    "seconds": self.estimar_duracao_audio(arquivo),
                    "mimetype": "audio/mpeg"
                }
            }
            
            if not dry_run:
                # Criar mensagem
                mensagem = Mensagem.objects.create(
                    chat=chat_teste,
                    remetente="Sistema Teste",
                    conteudo=json.dumps(conteudo_json, ensure_ascii=False),
                    tipo='audio',
                    from_me=False,
                    data_envio=datetime.now()
                )
                
                self.stdout.write(f'  OK Mensagem de teste criada: ID {mensagem.id}')
            else:
                self.stdout.write(f'  INFO Mensagem de teste seria criada para {arquivo.name}')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ERRO Erro ao criar mensagem de teste: {e}'))

    def calcular_hash_arquivo(self, arquivo):
        """Calcula hash SHA256 do arquivo"""
        hash_sha256 = hashlib.sha256()
        with open(arquivo, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def estimar_duracao_audio(self, arquivo):
        """Estima duração do áudio baseado no tamanho (aproximação)"""
        try:
            tamanho_mb = arquivo.stat().st_size / (1024 * 1024)
            # Estimativa: 1MB ≈ 60s para MP3 128kbps
            duracao_estimada = int(tamanho_mb * 60)
            return max(1, duracao_estimada)  # Mínimo 1 segundo
        except:
            return 30  # Fallback para 30 segundos