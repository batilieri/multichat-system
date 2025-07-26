from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Chat
from webhook.models import WebhookEvent
import logging

class Command(BaseCommand):
    help = 'Corrige fotos de perfil dos chats existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem fazer alterações no banco',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostra logs detalhados',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        if verbose:
            logging.basicConfig(level=logging.INFO)
        
        logger = logging.getLogger(__name__)
        
        self.stdout.write("🔍 Iniciando correção de fotos de perfil...")
        
        # Buscar chats sem foto de perfil
        chats_without_photo = Chat.objects.filter(
            foto_perfil__isnull=True
        ) | Chat.objects.filter(foto_perfil='')
        
        total_chats = chats_without_photo.count()
        self.stdout.write(f"📊 Encontrados {total_chats} chats sem foto de perfil")
        
        chats_updated = 0
        
        for i, chat in enumerate(chats_without_photo, 1):
            if verbose:
                self.stdout.write(f"🔍 Processando chat {i}/{total_chats}: {chat.chat_id}")
            
            # Buscar último evento de webhook para este chat
            last_event = WebhookEvent.objects.filter(
                chat_id=chat.chat_id,
                cliente=chat.cliente
            ).order_by('-timestamp').first()
            
            if last_event and last_event.raw_data:
                profile_picture = self.extract_profile_picture(last_event.raw_data)
                
                if profile_picture:
                    if not dry_run:
                        try:
                            with transaction.atomic():
                                chat.foto_perfil = profile_picture
                                chat.save(update_fields=['foto_perfil'])
                                chats_updated += 1
                                
                            if verbose:
                                self.stdout.write(f"✅ Chat {chat.chat_id} atualizado: {profile_picture[:50]}...")
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f"❌ Erro ao atualizar chat {chat.chat_id}: {e}")
                            )
                    else:
                        chats_updated += 1
                        self.stdout.write(f"✅ [DRY-RUN] Chat {chat.chat_id} seria atualizado: {profile_picture[:50]}...")
            
            # Progresso a cada 50 chats
            if i % 50 == 0:
                self.stdout.write(f"📊 Progresso: {i}/{total_chats} ({(i/total_chats)*100:.1f}%)")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"🧪 [DRY-RUN] {chats_updated} chats seriam atualizados")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"✅ {chats_updated} chats atualizados com sucesso!")
            )
    
    def extract_profile_picture(self, webhook_data):
        """Extrai foto de perfil do webhook"""
        sources = [
            webhook_data.get('sender', {}).get('profilePicture'),
            webhook_data.get('sender', {}).get('profile_picture'),
            webhook_data.get('chat', {}).get('profilePicture'),
            webhook_data.get('chat', {}).get('profile_picture'),
            webhook_data.get('profilePicture'),
            webhook_data.get('profile_picture'),
            webhook_data.get('data', {}).get('sender', {}).get('profilePicture'),
            webhook_data.get('data', {}).get('chat', {}).get('profilePicture'),
        ]
        
        for source in sources:
            if source and isinstance(source, str) and source.strip():
                url = source.strip()
                if url.startswith(('http://', 'https://', 'data:image/')):
                    return url
        
        return None 