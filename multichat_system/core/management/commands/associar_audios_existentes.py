from django.core.management.base import BaseCommand
from core.models import Mensagem, Chat
from django.utils import timezone
import json
import os
import glob
from pathlib import Path

class Command(BaseCommand):
    help = 'Associa arquivos de áudio existentes na pasta media_storage às mensagens no banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cliente-id',
            type=int,
            default=2,  # Cliente Elizeu por padrão
            help='ID do cliente para processar'
        )
        parser.add_argument(
            '--instance-id',
            type=str,
            default='DTBDM1-YC2NM5-79C0T4',  # Instância específica
            help='ID da instância WhatsApp'
        )
        parser.add_argument(
            '--chat-id',
            type=str,
            default='556999267344',  # Chat específico
            help='ID do chat para processar'
        )

    def handle(self, *args, **options):
        cliente_id = options['cliente_id']
        instance_id = options['instance_id']
        chat_id = options['chat_id']
        
        self.stdout.write("🔄 ASSOCIANDO ÁUDIOS EXISTENTES ÀS MENSAGENS")
        self.stdout.write("=" * 60)
        self.stdout.write(f"Cliente ID: {cliente_id}")
        self.stdout.write(f"Instância: {instance_id}")
        self.stdout.write(f"Chat ID: {chat_id}")
        
        # Caminho para a pasta de áudios
        project_root = Path(__file__).parent.parent.parent.parent
        audio_dir = project_root / 'media_storage' / 'Elizeu_Batiliere_Dos_Santos' / instance_id / 'chats' / chat_id / 'audio'
        
        if not audio_dir.exists():
            self.stdout.write(f"❌ Diretório de áudio não encontrado: {audio_dir}")
            return
        
        self.stdout.write(f"📁 Diretório de áudio: {audio_dir}")
        
        # Listar arquivos de áudio
        audio_files = list(audio_dir.glob('*.ogg')) + list(audio_dir.glob('*.mp3')) + list(audio_dir.glob('*.m4a'))
        self.stdout.write(f"🎵 Arquivos de áudio encontrados: {len(audio_files)}")
        
        for audio_file in audio_files:
            self.stdout.write(f"\n📁 Processando: {audio_file.name}")
            
            # Extrair message_id do nome do arquivo
            # Formato esperado: msg_7400F35B_20250814_100212.ogg
            filename_parts = audio_file.stem.split('_')
            if len(filename_parts) >= 2:
                message_id = filename_parts[1]  # 7400F35B
                self.stdout.write(f"  🆔 Message ID extraído: {message_id}")
                
                # Verificar se já existe uma mensagem com este message_id
                existing_message = Mensagem.objects.filter(message_id=message_id).first()
                
                if existing_message:
                    self.stdout.write(f"  ✅ Mensagem já existe: ID {existing_message.id}")
                    
                    # Verificar se é do tipo áudio
                    if existing_message.tipo != 'audio':
                        existing_message.tipo = 'audio'
                        existing_message.save()
                        self.stdout.write(f"  🔄 Tipo alterado para 'audio'")
                    
                    # Verificar se tem chat_id correto
                    if not existing_message.chat.chat_id == chat_id:
                        self.stdout.write(f"  ⚠️ Chat ID diferente: {existing_message.chat.chat_id} vs {chat_id}")
                    
                else:
                    self.stdout.write(f"  ❌ Mensagem não encontrada no banco")
                    
                    # Buscar chat
                    chat = Chat.objects.filter(chat_id=chat_id).first()
                    if not chat:
                        self.stdout.write(f"  ❌ Chat não encontrado: {chat_id}")
                        continue
                    
                    # Criar mensagem de áudio
                    audio_data = {
                        "audioMessage": {
                            "url": f"/media/whatsapp_media/{cliente_id}/{instance_id}/chats/{chat_id}/audio/{audio_file.name}",
                            "mimetype": "audio/ogg",
                            "fileName": audio_file.name,
                            "directPath": f"{cliente_id}/{instance_id}/chats/{chat_id}/audio/{audio_file.name}",
                            "seconds": 0,  # Será detectado automaticamente
                            "ptt": False
                        }
                    }
                    
                    # Criar mensagem
                    new_message = Mensagem.objects.create(
                        chat=chat,
                        remetente=chat_id,  # Usar chat_id como remetente por enquanto
                        conteudo=json.dumps(audio_data),
                        tipo='audio',
                        message_id=message_id,
                        from_me=False,
                        data_envio=timezone.now()
                    )
                    
                    self.stdout.write(f"  ✅ Nova mensagem criada: ID {new_message.id}")
            else:
                self.stdout.write(f"  ⚠️ Formato de nome inválido: {audio_file.name}")
        
        self.stdout.write(f"\n✅ Processamento concluído!")
        self.stdout.write(f"📊 Total de arquivos processados: {len(audio_files)}")
        
        # Verificar mensagens de áudio no banco
        self.verificar_mensagens_audio(chat_id)

    def verificar_mensagens_audio(self, chat_id):
        """Verifica mensagens de áudio no banco de dados"""
        self.stdout.write(f"\n🔍 VERIFICANDO MENSAGENS DE ÁUDIO NO BANCO")
        self.stdout.write("=" * 60)
        
        # Buscar mensagens de áudio do chat
        chat = Chat.objects.filter(chat_id=chat_id).first()
        if not chat:
            self.stdout.write(f"❌ Chat não encontrado: {chat_id}")
            return
        
        audio_messages = Mensagem.objects.filter(chat=chat, tipo='audio')
        self.stdout.write(f"📊 Mensagens de áudio no chat: {audio_messages.count()}")
        
        for msg in audio_messages:
            self.stdout.write(f"\n🎵 Mensagem ID: {msg.id}")
            self.stdout.write(f"  Message ID: {msg.message_id}")
            self.stdout.write(f"  Tipo: {msg.tipo}")
            self.stdout.write(f"  Data: {msg.data_envio}")
            
            # Verificar dados JSON
            try:
                json_data = json.loads(msg.conteudo)
                if 'audioMessage' in json_data:
                    audio_data = json_data['audioMessage']
                    self.stdout.write(f"  ✅ Dados de áudio encontrados")
                    self.stdout.write(f"  📁 URL: {audio_data.get('url', 'N/A')}")
                    self.stdout.write(f"  📁 FileName: {audio_data.get('fileName', 'N/A')}")
                    self.stdout.write(f"  📁 DirectPath: {audio_data.get('directPath', 'N/A')}")
            except:
                self.stdout.write(f"  ⚠️ Erro ao processar JSON")
        
        self.stdout.write("\n✅ Verificação concluída!") 