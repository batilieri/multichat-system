from django.db import migrations
import json

def testar_extracao_midias(apps, schema_editor):
    WebhookEvent = apps.get_model('webhook', 'WebhookEvent')
    total = 0
    validos = 0
    erros = 0
    campos_essenciais = ['mediaKey', 'directPath', 'fileEncSha256', 'fileSha256', 'mimetype', 'type']
    print('\n--- INÍCIO DO TESTE DE EXTRAÇÃO DE MÍDIAS DOS WEBHOOKS ---')
    for evento in WebhookEvent.objects.all():
        total += 1
        raw_data = evento.raw_data
        msg_content = raw_data.get('msgContent')
        if not msg_content:
            print(f'❌ Evento {evento.event_id}: msgContent ausente')
            erros += 1
            continue
        # Procurar tipos de mídia
        tipos_midia = ['imageMessage', 'videoMessage', 'audioMessage', 'documentMessage', 'stickerMessage']
        encontrou = False
        for tipo_msg in tipos_midia:
            if tipo_msg in msg_content:
                encontrou = True
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
                if faltando:
                    print(f'❌ Evento {evento.event_id}: Faltando campos {faltando} para {tipo_msg}')
                    erros += 1
                else:
                    print(f'✅ Evento {evento.event_id}: Todos os campos essenciais presentes para {tipo_msg}')
                    validos += 1
        if not encontrou:
            print(f'ℹ️ Evento {evento.event_id}: Nenhuma mídia encontrada')
    print(f'--- FIM DO TESTE ---')
    print(f'Total de eventos: {total}')
    print(f'Com mídia válida: {validos}')
    print(f'Com erro/faltando campos: {erros}')

class Migration(migrations.Migration):
    dependencies = [
        ('webhook', '0005_processar_midias_antigas'),
    ]

    operations = [
        migrations.RunPython(testar_extracao_midias),
    ] 