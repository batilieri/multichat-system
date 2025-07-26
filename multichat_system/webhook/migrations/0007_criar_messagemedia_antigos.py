from django.db import migrations
import json

def criar_messagemedia_antigos(apps, schema_editor):
    WebhookEvent = apps.get_model('webhook', 'WebhookEvent')
    MessageMedia = apps.get_model('webhook', 'MessageMedia')
    campos_essenciais = ['mediaKey', 'directPath', 'fileEncSha256', 'fileSha256', 'mimetype', 'type']
    tipos_midia = ['imageMessage', 'videoMessage', 'audioMessage', 'documentMessage', 'stickerMessage']
    total_criados = 0
    for evento in WebhookEvent.objects.all():
        raw_data = evento.raw_data
        msg_content = raw_data.get('msgContent')
        if not msg_content:
            continue
        for tipo_msg in tipos_midia:
            if tipo_msg in msg_content:
                midia_data = msg_content[tipo_msg]
                info_midia = {
                    'type': tipo_msg.replace('Message', '').replace('document', 'document').replace('sticker', 'sticker').replace('audio', 'audio').replace('video', 'video').replace('image', 'image'),
                    'mediaKey': midia_data.get('mediaKey'),
                    'directPath': midia_data.get('directPath'),
                    'mimetype': midia_data.get('mimetype'),
                    'url': midia_data.get('url'),
                    'fileLength': midia_data.get('fileLength'),
                    'fileName': midia_data.get('fileName'),
                    'caption': midia_data.get('caption', ''),
                    'fileSha256': midia_data.get('fileSha256'),
                    'fileEncSha256': midia_data.get('fileEncSha256'),
                    'jpegThumbnail': midia_data.get('jpegThumbnail'),
                    'mediaKeyTimestamp': midia_data.get('mediaKeyTimestamp')
                }
                faltando = [campo for campo in campos_essenciais if not info_midia.get(campo)]
                if not faltando:
                    # Verifica se já existe MessageMedia para este evento e tipo
                    if not MessageMedia.objects.filter(event=evento, media_type=info_midia['type']).exists():
                        MessageMedia.objects.create(
                            event=evento,
                            media_path='',
                            media_type=info_midia['type'],
                            mimetype=info_midia['mimetype'],
                            file_size=info_midia.get('fileLength'),
                            download_status='pending',
                            media_key=info_midia['mediaKey'],
                            direct_path=info_midia['directPath'],
                            file_sha256=info_midia['fileSha256'],
                            file_enc_sha256=info_midia['fileEncSha256'],
                            media_key_timestamp=info_midia.get('mediaKeyTimestamp'),
                            caption=info_midia.get('caption'),
                            width=midia_data.get('width'),
                            height=midia_data.get('height'),
                            duration_seconds=midia_data.get('seconds'),
                            is_ptt=midia_data.get('ptt', False),
                            document_filename=midia_data.get('fileName'),
                            jpeg_thumbnail=midia_data.get('jpegThumbnail'),
                        )
                        total_criados += 1
    print(f'Foram criados {total_criados} registros MessageMedia para eventos antigos.')

class Migration(migrations.Migration):
    dependencies = [
        ('webhook', '0006_teste_extracao_midias_webhooks'),
    ]

    operations = [
        migrations.RunPython(criar_messagemedia_antigos),
    ] 