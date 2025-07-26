from django.db import migrations

def processar_midias_antigas(apps, schema_editor):
    WebhookEvent = apps.get_model('webhook', 'WebhookEvent')
    from webhook.media_downloader import processar_midias_automaticamente
    total = 0
    for evento in WebhookEvent.objects.all():
        try:
            processar_midias_automaticamente(evento)
            total += 1
        except Exception as e:
            print(f'Erro ao processar evento {evento.event_id}: {e}')
    print(f'Processamento de mídias antigas concluído para {total} eventos.')

class Migration(migrations.Migration):
    dependencies = [
        ('webhook', '0004_messagemedia_caption_messagemedia_direct_path_and_more'),
    ]

    operations = [
        migrations.RunPython(processar_midias_antigas),
    ] 