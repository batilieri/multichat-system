#!/usr/bin/env python3
"""
Script para testar webhook com mídia
"""

import requests
import json

def test_webhook_with_media():
    """Testa webhook com dados de mídia"""
    
    # Dados do webhook com imagem (baseado no exemplo fornecido)
    webhook_data = {
        "event": "webhookReceived",
        "instanceId": "3B6XIW-ZTS923-GEAY6V",  # Usar instância real
        "connectedPhone": "559992249708",
        "isGroup": False,
        "messageId": "3EB00CD0857BA22EAEDCD9",
        "fromMe": False,  # Mensagem recebida
        "data": {
            "messages": [
                {
                    "key": {
                        "id": "3EB00CD0857BA22EAEDCD9"
                    },
                    "message": {
                        "imageMessage": {
                            "url": "https://mmg.whatsapp.net/v/t61.24694-24/123456789_abcdef_123456789_n.jpg",
                            "mimetype": "image/jpeg",
                            "caption": "Teste de imagem",
                            "fileLength": "59583",
                            "height": 445,
                            "width": 959,
                            "mediaKey": "test_media_key_123",
                            "fileEncSha256": "test_enc_sha256",
                            "directPath": "/v/t61.24694-24/123456789_abcdef_123456789_n.jpg",
                            "mediaKeyTimestamp": "1749131966",
                            "jpegThumbnail": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
                            "contextInfo": {
                                "ephemeralSettingTimestamp": "1748612109",
                                "disappearingMode": {
                                    "initiator": "CHANGED_IN_CHAT"
                                }
                            },
                            "viewOnce": False
                        }
                    }
                }
            ]
        },
        "chat": {
            "id": "556999267344",  # Usar chat_id real
            "profilePicture": "https://pps.whatsapp.net/v/t61.24694-24/462429652_2229319410767469_7773187573644695635_n.jpg?ccb=11-4&oh=01_Q5Aa2AHWG8-poaLNKMAK_eAEr60ghjR2hvM39zZJZqOL_vblvw&oe=68A0B6EF&_nc_sid=5e03e0&_nc_cat=100"
        },
        "sender": {
            "id": "556999267344",
            "profilePicture": "https://pps.whatsapp.net/v/t61.24694-24/462429652_2229319410767469_7773187573644695635_n.jpg?ccb=11-4&oh=01_Q5Aa2AHWG8-poaLNKMAK_eAEr60ghjR2hvM39zZJZqOL_vblvw&oe=68A0B6EF&_nc_sid=5e03e0&_nc_cat=100",
            "pushName": "Teste Mídia",
            "verifiedBizName": ""
        },
        "moment": 1749131970,
        "msgContent": {
            "imageMessage": {
                "url": "https://mmg.whatsapp.net/v/t61.24694-24/123456789_abcdef_123456789_n.jpg",
                "mimetype": "image/jpeg",
                "caption": "Teste de imagem",
                "fileLength": "59583",
                "height": 445,
                "width": 959,
                "mediaKey": "test_media_key_123",
                "fileEncSha256": "test_enc_sha256",
                "directPath": "/v/t61.24694-24/123456789_abcdef_123456789_n.jpg",
                "mediaKeyTimestamp": "1749131966",
                "jpegThumbnail": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
                "contextInfo": {
                    "ephemeralSettingTimestamp": "1748612109",
                    "disappearingMode": {
                        "initiator": "CHANGED_IN_CHAT"
                    }
                },
                "viewOnce": False
            },
            "messageContextInfo": {
                "deviceListMetadata": {
                    "senderKeyHash": "2slISnt5DU1cWQ==",
                    "senderTimestamp": "1749126475",
                    "senderAccountType": "E2EE",
                    "receiverAccountType": "E2EE",
                    "recipientKeyHash": "g21uUc3ydJ5lFA==",
                    "recipientTimestamp": "1749131190"
                },
                "deviceListMetadataVersion": 2,
                "messageSecret": "1BmKF7KT9e2TNyxnbFzo2EoZhShI7zHbk0S67a6eSHE="
            }
        }
    }
    
    print("🧪 Testando webhook com mídia...")
    print(f"📋 Dados do webhook:")
    print(f"   Instance ID: {webhook_data['instanceId']}")
    print(f"   Message ID: {webhook_data['messageId']}")
    print(f"   fromMe: {webhook_data['fromMe']}")
    print(f"   Tipo de mídia: imageMessage")
    print(f"   Mimetype: {webhook_data['msgContent']['imageMessage']['mimetype']}")
    print(f"   Tamanho: {webhook_data['msgContent']['imageMessage']['fileLength']} bytes")
    
    # Enviar webhook para o backend
    try:
        response = requests.post(
            'http://localhost:8000/webhook/receive-message/',  # Endpoint correto para mensagens recebidas
            json=webhook_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\n📡 Resposta do webhook:")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Resposta: {json.dumps(data, indent=2)}")
            except:
                print(f"   Resposta: {response.text}")
        else:
            print(f"   Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {e}")

if __name__ == "__main__":
    test_webhook_with_media() 