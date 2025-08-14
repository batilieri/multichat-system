#!/usr/bin/env python3
"""
Comando para recriar completamente o playlist de áudio
Conecta arquivos existentes com mensagens do banco e cria estrutura correta
"""

from django.core.management.base import BaseCommand
from core.models import Mensagem, Chat, Cliente
from django.utils import timezone
import json
import os
import glob
from pathlib import Path

class Command(BaseCommand):
    help = 'Recria completamente o playlist de áudio conectando arquivos existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cliente-id',
            type=int,
            default=2,
            help='ID do cliente para processar (padrão: 2)'
        )
        parser.add_argument(
            '--instance-id',
            type=str,
            default='3B6XIW-ZTS923-GEAY6V',
            help='ID da instância WhatsApp'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forçar recriação mesmo se já existir'
        )

    def handle(self, *args, **options):
        cliente_id = options['cliente_id']
        instance_id = options['instance_id']
        force = options['force']
        
        self.stdout.write("🎵 RECRIANDO PLAYLIST DE ÁUDIO COMPLETO")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Cliente ID: {cliente_id}")
        self.stdout.write(f"Instance ID: {instance_id}")
        self.stdout.write(f"Forçar: {force}")
        
        # Verificar se o cliente existe
        try:
            cliente = Cliente.objects.get(id=cliente_id)
            self.stdout.write(f"✅ Cliente encontrado: {cliente.nome}")
        except Cliente.DoesNotExist:
            self.stdout.write(f"❌ Cliente {cliente_id} não encontrado")
            return
        
        # Processar áudios
        self.processar_audios_existentes(cliente, instance_id, force)
        self.verificar_estrutura_final(cliente)

    def processar_audios_existentes(self, cliente, instance_id, force):
        """Processa todos os áudios existentes na estrutura de pastas"""
        self.stdout.write(f"\n📁 PROCESSANDO ÁUDIOS EXISTENTES")
        self.stdout.write("=" * 60)
        
        # Caminho base para os áudios
        base_path = Path(f"media_storage/{cliente.nome.replace(' ', '_')}/instance_{instance_id}/chats")
        
        if not base_path.exists():
            self.stdout.write(f"❌ Caminho não encontrado: {base_path}")
            return
        
        # Encontrar todos os chats com áudios
        chat_dirs = [d for d in base_path.iterdir() if d.is_dir()]
        self.stdout.write(f"📱 Chats encontrados: {len(chat_dirs)}")
        
        total_audios = 0
        audios_processados = 0
        
        for chat_dir in chat_dirs:
            chat_id = chat_dir.name
            audio_dir = chat_dir / "audio"
            
            if not audio_dir.exists():
                continue
                
            # Encontrar arquivos de áudio
            audio_files = list(audio_dir.glob("*.ogg")) + list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.m4a"))
            
            if not audio_files:
                continue
                
            self.stdout.write(f"\n🎵 Chat {chat_id}: {len(audio_files)} áudios")
            total_audios += len(audio_files)
            
            # Processar cada arquivo de áudio
            for audio_file in audio_files:
                if self.processar_arquivo_audio(audio_file, chat_id, cliente, force):
                    audios_processados += 1
        
        self.stdout.write(f"\n✅ Processamento concluído!")
        self.stdout.write(f"📊 Total de áudios: {total_audios}")
        self.stdout.write(f"📊 Áudios processados: {audios_processados}")

    def processar_arquivo_audio(self, audio_file, chat_id, cliente, force):
        """Processa um arquivo de áudio individual"""
        try:
            # Extrair informações do nome do arquivo
            filename = audio_file.name
            file_path = str(audio_file.relative_to(Path("media_storage")))
            
            # Tentar extrair message_id do nome do arquivo
            message_id = self.extrair_message_id(filename)
            
            if not message_id:
                self.stdout.write(f"  ⚠️ Não foi possível extrair message_id de: {filename}")
                return False
            
            # Verificar se já existe mensagem para este áudio
            existing_message = Mensagem.objects.filter(
                message_id=message_id,
                tipo='audio'
            ).first()
            
            if existing_message and not force:
                self.stdout.write(f"  ✅ Já existe mensagem para: {filename}")
                return True
            
            # Buscar ou criar chat
            chat, created = Chat.objects.get_or_create(
                chat_id=chat_id,
                cliente=cliente,
                defaults={
                    'chat_name': f"Chat {chat_id}",
                    'status': 'active'
                }
            )
            
            if created:
                self.stdout.write(f"  📱 Chat criado: {chat_id}")
            
            # Criar estrutura de dados do áudio
            audio_data = {
                "audioMessage": {
                    "url": f"/{file_path}",
                    "localPath": str(audio_file.absolute()),
                    "fileName": filename,
                    "mimetype": self.get_mimetype(audio_file),
                    "seconds": self.estimate_duration(audio_file),
                    "ptt": True,
                    "mediaKey": message_id,
                    "fileLength": str(audio_file.stat().st_size),
                    "directPath": file_path
                }
            }
            
            # Criar ou atualizar mensagem
            if existing_message:
                existing_message.conteudo = json.dumps(audio_data, ensure_ascii=False)
                existing_message.tipo = 'audio'
                existing_message.save()
                self.stdout.write(f"  🔄 Mensagem atualizada: {existing_message.id}")
            else:
                new_message = Mensagem.objects.create(
                    chat=chat,
                    remetente=chat_id,  # Usar chat_id como remetente temporário
                    conteudo=json.dumps(audio_data, ensure_ascii=False),
                    tipo='audio',
                    from_me=False,
                    message_id=message_id,
                    data_envio=timezone.now()
                )
                self.stdout.write(f"  ✅ Nova mensagem criada: {new_message.id}")
            
            return True
            
        except Exception as e:
            self.stdout.write(f"  ❌ Erro ao processar {audio_file.name}: {e}")
            return False

    def extrair_message_id(self, filename):
        """Extrai o message_id do nome do arquivo"""
        # Formato esperado: msg_XXXXXXXX_YYYYMMDD_HHMMSS.ext
        if filename.startswith('msg_'):
            parts = filename.split('_')
            if len(parts) >= 2:
                # Usar os primeiros 8 caracteres como message_id
                message_id = parts[1]
                if len(message_id) >= 8:
                    return message_id[:8]
                return message_id
        return None

    def get_mimetype(self, audio_file):
        """Determina o mimetype baseado na extensão"""
        ext = audio_file.suffix.lower()
        mimetypes = {
            '.ogg': 'audio/ogg; codecs=opus',
            '.mp3': 'audio/mpeg',
            '.m4a': 'audio/mp4',
            '.wav': 'audio/wav'
        }
        return mimetypes.get(ext, 'audio/ogg')

    def estimate_duration(self, audio_file):
        """Estima a duração baseada no tamanho do arquivo (aproximado)"""
        size_mb = audio_file.stat().st_size / (1024 * 1024)
        # Estimativa aproximada: 1MB ≈ 1 minuto para áudio comprimido
        estimated_seconds = int(size_mb * 60)
        return max(1, min(estimated_seconds, 300))  # Entre 1 e 300 segundos

    def verificar_estrutura_final(self, cliente):
        """Verifica a estrutura final criada"""
        self.stdout.write(f"\n🔍 VERIFICANDO ESTRUTURA FINAL")
        self.stdout.write("=" * 60)
        
        # Verificar mensagens de áudio
        audio_messages = Mensagem.objects.filter(tipo='audio')
        self.stdout.write(f"📊 Total de mensagens de áudio: {audio_messages.count()}")
        
        # Agrupar por chat
        chats_com_audio = {}
        for msg in audio_messages:
            chat_id = msg.chat.chat_id
            if chat_id not in chats_com_audio:
                chats_com_audio[chat_id] = []
            chats_com_audio[chat_id].append(msg)
        
        self.stdout.write(f"📱 Chats com áudio: {len(chats_com_audio)}")
        
        for chat_id, messages in list(chats_com_audio.items())[:5]:  # Mostrar só os primeiros 5
            self.stdout.write(f"\n🎵 Chat {chat_id}: {len(messages)} áudios")
            
            # Mostrar alguns áudios como exemplo
            for msg in messages[:3]:
                try:
                    audio_data = json.loads(msg.conteudo)
                    if 'audioMessage' in audio_data:
                        audio_info = audio_data['audioMessage']
                        filename = audio_info.get('fileName', 'N/A')
                        duration = audio_info.get('seconds', 'N/A')
                        self.stdout.write(f"  - {filename} ({duration}s)")
                except:
                    self.stdout.write(f"  - Erro ao processar dados")
        
        self.stdout.write(f"\n✅ Verificação concluída!")
        self.stdout.write(f"\n💡 Para testar no frontend:")
        self.stdout.write(f"   1. Inicie o backend: python manage.py runserver")
        self.stdout.write(f"   2. Inicie o frontend: npm start")
        self.stdout.write(f"   3. Acesse um chat com mensagens de áudio")
        self.stdout.write(f"   4. Os áudios devem aparecer com player interativo") 