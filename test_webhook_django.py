import requests
import json

# Substitua pela URL do seu ngrok apontando para o Django
NGROK_URL = 'http://localhost:8000'  # Altere para sua URL pública do ngrok se necessário

ENDPOINT = f'{NGROK_URL}/webhook/receive-message/'

payload = {
    "fromMe": False,
    "data": {
        "fromMe": False,
        "chat": {"id": "5511999999999@c.us"},
        "sender": {"id": "5511999999999@c.us", "pushName": "Teste"},
        "msgContent": {"conversation": "Mensagem de teste via Django webhook"},
        "messageId": "teste-django-123"
    },
    "instanceId": "INSTANCIA_TESTE"
}

headers = {'Content-Type': 'application/json'}

print(f'Enviando para: {ENDPOINT}')
response = requests.post(ENDPOINT, data=json.dumps(payload), headers=headers)
print('Status:', response.status_code)
print('Resposta:', response.text) 