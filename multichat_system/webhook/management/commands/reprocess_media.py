from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from webhook.media_downloader import reprocessar_midias_cliente
from core.models import Cliente


class Command(BaseCommand):
    help = 'Reprocessa mídias pendentes de um cliente específico'

    def add_arguments(self, parser):
        parser.add_argument(
            'cliente_id',
            type=int,
            help='ID do cliente para reprocessar mídias'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Reprocessar mídias de todos os clientes'
        )

    def handle(self, *args, **options):
        try:
            if options['all']:
                # Reprocessar todos os clientes
                clientes = Cliente.objects.all()
                self.stdout.write(f"🔄 Reprocessando mídias para {clientes.count()} clientes...")
                
                total_sucessos = 0
                for cliente in clientes:
                    self.stdout.write(f"📱 Processando cliente: {cliente.nome} (ID: {cliente.id})")
                    sucessos = reprocessar_midias_cliente(cliente.id)
                    total_sucessos += sucessos
                    self.stdout.write(f"   ✅ {sucessos} mídias reprocessadas")
                    
                self.stdout.write(
                    self.style.SUCCESS(f"🎉 Reprocessamento concluído! Total: {total_sucessos} mídias")
                )
            else:
                # Reprocessar cliente específico
                cliente_id = options['cliente_id']
                
                try:
                    cliente = Cliente.objects.get(id=cliente_id)
                except Cliente.DoesNotExist:
                    raise CommandError(f'Cliente com ID {cliente_id} não encontrado')
                
                self.stdout.write(f"🔄 Reprocessando mídias para cliente: {cliente.nome}")
                
                with transaction.atomic():
                    sucessos = reprocessar_midias_cliente(cliente_id)
                
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Reprocessamento concluído! {sucessos} mídias reprocessadas")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erro no reprocessamento: {e}")
            )
            raise CommandError(f'Erro no reprocessamento: {e}') 