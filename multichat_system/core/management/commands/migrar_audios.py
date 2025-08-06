from django.core.management.base import BaseCommand
from core.models import Mensagem, Chat
from django.utils import timezone
import json

class Command(BaseCommand):
    help = 'Migra mensagens de áudio para aparecerem no frontend'

    def handle(self, *args, **options):
        self.stdout.write("🔄 MIGRANDO ÁUDIOS PARA O FRONTEND")
        self.stdout.write("=" * 60)
        
        # Buscar todas as mensagens
        mensagens = Mensagem.objects.all()
        self.stdout.write(f"📊 Total de mensagens: {mensagens.count()}")
        
        migradas = 0
        
        for msg in mensagens:
            # Verificar se é um áudio
            if msg.conteudo and 'audioMessage' in msg.conteudo:
                self.stdout.write(f"\n🎵 Encontrada mensagem de áudio ID: {msg.id}")
                
                # Definir tipo como áudio se não estiver
                if msg.tipo != 'audio':
                    msg.tipo = 'audio'
                    msg.save()
                    self.stdout.write(f"  ✅ Tipo alterado para 'audio'")
                    migradas += 1
                else:
                    self.stdout.write(f"  ✅ Já é do tipo 'audio'")
                
                # Extrair dados do áudio
                try:
                    json_data = json.loads(msg.conteudo)
                    if 'audioMessage' in json_data:
                        audio_data = json_data['audioMessage']
                        url = audio_data.get('url', 'N/A')
                        duration = audio_data.get('seconds', 0)
                        self.stdout.write(f"  📁 URL: {url}")
                        self.stdout.write(f"  ⏱️ Duração: {duration} segundos")
                except:
                    self.stdout.write(f"  ⚠️ Erro ao extrair dados JSON")
        
        self.stdout.write(f"\n✅ Migração concluída!")
        self.stdout.write(f"📊 Mensagens migradas: {migradas}")
        
        # Criar mensagem de teste
        self.criar_audio_teste()
        
        # Verificar áudios
        self.verificar_audios()

    def criar_audio_teste(self):
        """Cria uma mensagem de áudio de teste"""
        self.stdout.write("\n🧪 CRIANDO MENSAGEM DE ÁUDIO DE TESTE")
        self.stdout.write("=" * 60)
        
        # Buscar primeiro chat
        chat = Chat.objects.first()
        
        if not chat:
            self.stdout.write("❌ Nenhum chat encontrado")
            return
        
        # Dados de teste
        test_audio = {
            "audioMessage": {
                "url": "https://mmg.whatsapp.net/v/t62.7117-24/11418572_639123605874985_2074276734782391920_n.enc?ccb=11-4&oh=01_Q5Aa2AH90VmSBOTtBIXsGxf0r5vMtkmkC4BsJLVg9s4HdByRdQ&oe=68B5B693&_nc_sid=5e03e0&mms3=true",
                "mimetype": "audio/ogg; codecs=opus",
                "fileSha256": "+ylX/pg8Tsa+zRJ8fgO0rpPycxdXtmLUZvZeZybjRAE=",
                "fileLength": "20718",
                "seconds": 8,
                "ptt": True,
                "mediaKey": "FnIfz9Ka/QzEPkAzlOQ9x0m3WBwUQaG265dvhLjnFl0="
            }
        }
        
        # Criar mensagem
        test_message = Mensagem.objects.create(
            chat=chat,
            remetente="556993291093",
            conteudo=json.dumps(test_audio),
            tipo='audio',
            from_me=False,
            data_envio=timezone.now()
        )
        
        self.stdout.write(f"✅ Mensagem de teste criada: {test_message.id}")
        self.stdout.write(f"  Tipo: {test_message.tipo}")
        self.stdout.write(f"  Chat: {chat.chat_name}")

    def verificar_audios(self):
        """Verifica áudios existentes"""
        self.stdout.write("\n🔍 VERIFICANDO ÁUDIOS EXISTENTES")
        self.stdout.write("=" * 60)
        
        # Buscar mensagens de áudio
        audio_messages = Mensagem.objects.filter(tipo='audio')
        self.stdout.write(f"📊 Mensagens de áudio: {audio_messages.count()}")
        
        for msg in audio_messages[:3]:
            self.stdout.write(f"\n🎵 Mensagem ID: {msg.id}")
            self.stdout.write(f"  Tipo: {msg.tipo}")
            self.stdout.write(f"  From Me: {msg.from_me}")
            self.stdout.write(f"  Data: {msg.data_envio}")
            
            # Verificar dados JSON
            try:
                json_data = json.loads(msg.conteudo)
                if 'audioMessage' in json_data:
                    audio_data = json_data['audioMessage']
                    self.stdout.write(f"  ✅ Dados de áudio encontrados")
                    self.stdout.write(f"  📁 URL: {audio_data.get('url', 'N/A')}")
                    self.stdout.write(f"  ⏱️ Duração: {audio_data.get('seconds', 0)} segundos")
                    self.stdout.write(f"  🎤 PTT: {audio_data.get('ptt', False)}")
            except:
                self.stdout.write(f"  ⚠️ Erro ao processar JSON")
        
        self.stdout.write("\n✅ Verificação concluída!")
        self.stdout.write("\n💡 Para testar no frontend:")
        self.stdout.write("   1. Inicie o backend: python manage.py runserver")
        self.stdout.write("   2. Inicie o frontend: npm start")
        self.stdout.write("   3. Acesse um chat com mensagens de áudio") 