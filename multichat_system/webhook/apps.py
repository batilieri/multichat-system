from django.apps import AppConfig


class WebhookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webhook'
    verbose_name = 'Webhook System'
    
    def ready(self):
        """Executado quando o app é carregado"""
        try:
            # Importar signals para garantir que sejam registrados
            from . import signals
            print("✅ Signals do webhook carregados com sucesso")
        except ImportError as e:
            print(f"⚠️ Erro ao carregar signals do webhook: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado ao carregar signals: {e}")
