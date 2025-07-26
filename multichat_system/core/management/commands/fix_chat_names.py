from django.core.management.base import BaseCommand
from core.models import Chat
from webhook.models import Sender
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Corrige os nomes dos chats para usar o número de telefone como chat_name'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem fazer alterações no banco',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostra informações detalhadas',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS('🔄 Iniciando correção dos nomes dos chats...')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️ Modo DRY-RUN ativado - nenhuma alteração será feita')
            )
        
        # Buscar todos os chats
        chats = Chat.objects.all()
        total_chats = chats.count()
        updated_count = 0
        
        self.stdout.write(f"📊 Total de chats encontrados: {total_chats}")
        
        for chat in chats:
            try:
                # Verificar se o chat_name é diferente do chat_id
                if chat.chat_name != chat.chat_id:
                    if verbose:
                        self.stdout.write(
                            f"🔄 Chat {chat.id}: '{chat.chat_name}' -> '{chat.chat_id}'"
                        )
                    
                    if not dry_run:
                        # Salvar o nome antigo em um campo temporário se necessário
                        old_chat_name = chat.chat_name
                        
                        # Atualizar chat_name para ser o número de telefone
                        chat.chat_name = chat.chat_id
                        chat.save(update_fields=['chat_name'])
                        
                        # Buscar ou criar sender com o nome antigo
                        sender, created = Sender.objects.get_or_create(
                            sender_id=chat.chat_id,
                            cliente=chat.cliente,
                            defaults={
                                'push_name': old_chat_name,
                                'verified_name': old_chat_name,
                            }
                        )
                        
                        if not created and not sender.push_name:
                            # Atualizar sender existente se não tiver push_name
                            sender.push_name = old_chat_name
                            sender.save(update_fields=['push_name'])
                        
                        if verbose:
                            self.stdout.write(
                                f"✅ Chat {chat.id} atualizado: chat_name='{chat.chat_id}', sender.push_name='{old_chat_name}'"
                            )
                    
                    updated_count += 1
                else:
                    if verbose:
                        self.stdout.write(f"✅ Chat {chat.id} já está correto: '{chat.chat_name}'")
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Erro ao processar chat {chat.id}: {e}")
                )
        
        # Resumo final
        self.stdout.write(
            self.style.SUCCESS(f"🎉 Correção concluída!")
        )
        self.stdout.write(f"📊 Total de chats: {total_chats}")
        self.stdout.write(f"🔄 Chats atualizados: {updated_count}")
        self.stdout.write(f"✅ Chats já corretos: {total_chats - updated_count}")
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️ Modo DRY-RUN - nenhuma alteração foi feita no banco')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ Alterações aplicadas com sucesso!')
            ) 