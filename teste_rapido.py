#!/usr/bin/env python3
import requests

# Testar endpoint de mensagens
r = requests.get('http://localhost:8000/api/test-mensagens/')
data = r.json()

print(f"Total mensagens: {data['count']}")
if data['mensagens']:
    msg = data['mensagens'][0]
    print(f"Primeira mensagem: ID {msg['id']}, Tipo: {msg['tipo']}")
    
    # Testar endpoint de áudio com instância correta
    msg_id = msg['id']
    chat_id = '556999267344'  # Chat padrão
    instance_id = 'DTBDM1-YC2NM5-79C0T4'  # Instância correta
    
    url = f"http://localhost:8000/api/whatsapp-audio-smart/2/{instance_id}/{chat_id}/{msg_id}/"
    print(f"Testando URL: {url}")
    
    try:
        audio_r = requests.get(url)
        print(f"Status do áudio: {audio_r.status_code}")
        if audio_r.status_code == 200:
            print("✅ Áudio funcionando!")
        else:
            print(f"⚠️ Erro: {audio_r.text[:100]}")
    except Exception as e:
        print(f"❌ Erro: {e}")
else:
    print("Nenhuma mensagem encontrada") 