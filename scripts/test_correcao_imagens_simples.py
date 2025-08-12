#!/usr/bin/env python3
"""
Teste simples da correção das imagens de perfil
"""

def extract_profile_picture_robust(webhook_data):
    """Extrai foto de perfil de forma mais robusta do webhook"""
    # Verificar se é uma mensagem enviada pelo usuário (fromMe: true)
    from_me = webhook_data.get('fromMe', False)
    
    # Lista de possíveis locais onde a foto pode estar
    extraction_paths = []
    
    if from_me:
        # Se é mensagem enviada pelo usuário, PRIORIZAR a foto do CHAT (contato/grupo)
        # e evitar usar a foto do SENDER (usuário)
        extraction_paths = [
            # PRIORIDADE 1: Foto do chat (contato/grupo)
            ('chat.profilePicture', lambda data: data.get('chat', {}).get('profilePicture')),
            ('chat.profile_picture', lambda data: data.get('chat', {}).get('profile_picture')),
            
            # PRIORIDADE 2: Nível raiz (pode ser do chat)
            ('root.profilePicture', lambda data: data.get('profilePicture')),
            ('root.profile_picture', lambda data: data.get('profile_picture')),
            
            # PRIORIDADE 3: Dentro de msgContent
            ('msgContent.profilePicture', lambda data: data.get('msgContent', {}).get('profilePicture')),
            
            # PRIORIDADE 4: Dentro de data (estrutura aninhada)
            ('data.chat.profilePicture', lambda data: data.get('data', {}).get('chat', {}).get('profilePicture')),
            
            # ÚLTIMA OPÇÃO: Sender (apenas se não houver outras opções)
            ('sender.profilePicture', lambda data: data.get('sender', {}).get('profilePicture')),
            ('sender.profile_picture', lambda data: data.get('sender', {}).get('profile_picture')),
            ('data.sender.profilePicture', lambda data: data.get('data', {}).get('sender', {}).get('profilePicture')),
        ]
        print("🔄 Mensagem enviada pelo usuário - priorizando foto do chat/contato")
    else:
        # Se é mensagem recebida, usar a lógica normal
        extraction_paths = [
            # Dados do sender
            ('sender.profilePicture', lambda data: data.get('sender', {}).get('profilePicture')),
            ('sender.profile_picture', lambda data: data.get('sender', {}).get('profile_picture')),
            
            # Dados do chat
            ('chat.profilePicture', lambda data: data.get('chat', {}).get('profilePicture')),
            ('chat.profile_picture', lambda data: data.get('chat', {}).get('profile_picture')),
            
            # Nível raiz
            ('root.profilePicture', lambda data: data.get('profilePicture')),
            ('root.profile_picture', lambda data: data.get('profile_picture')),
            
            # Dentro de msgContent (algumas APIs colocam aqui)
            ('msgContent.profilePicture', lambda data: data.get('msgContent', {}).get('profilePicture')),
            
            # Dentro de data (estrutura aninhada)
            ('data.sender.profilePicture', lambda data: data.get('data', {}).get('sender', {}).get('profilePicture')),
            ('data.chat.profilePicture', lambda data: data.get('data', {}).get('chat', {}).get('profilePicture')),
        ]
        print("📥 Mensagem recebida - usando lógica normal")
    
    for path_name, extractor in extraction_paths:
        try:
            result = extractor(webhook_data)
            if result and isinstance(result, str) and result.strip():
                profile_url = result.strip()
                
                # Validar se parece uma URL válida
                if profile_url.startswith(('http://', 'https://', 'data:image/')):
                    print(f"🖼️ Foto de perfil extraída de {path_name}: {profile_url[:50]}...")
                    return profile_url
                else:
                    print(f"⚠️ URL inválida em {path_name}: {profile_url[:50]}...")
        except Exception as e:
            print(f"❌ Erro ao extrair de {path_name}: {e}")
    
    print("🖼️ Nenhuma foto de perfil encontrada no webhook")
    return None

def test_extract_profile_picture():
    """Testa a extração de imagens de perfil"""
    print("🧪 TESTANDO EXTRAÇÃO DE IMAGENS DE PERFIL")
    print("=" * 60)
    
    # Dados de teste - mensagem enviada pelo usuário
    webhook_data_from_me = {
        "fromMe": True,
        "chat": {
            "id": "556999267344",
            "profilePicture": "https://pps.whatsapp.net/v/t61.24694-24/462429652_2229319410767469_7773187573644695635_n.jpg?ccb=11-4&oh=01_Q5Aa2AE5OOQugwo4m88csmkTQpNDwDyEXPePZcqA4oELniMqig&oe=689B38AF&_nc_sid=5e03e0&_nc_cat=100"
        },
        "sender": {
            "id": "556993291093",
            "profilePicture": "https://pps.whatsapp.net/v/t61.24694-24/462189315_448942584891093_7781840178101974754_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoXklUo9Xh-ciywvfPd3oicMRVv0tIzOHHtY6V0iG9kw&oe=689B5B12&_nc_sid=5e03e0&_nc_cat=103",
            "pushName": "Elizeu",
            "verifiedBizName": ""
        }
    }
    
    # Dados de teste - mensagem recebida
    webhook_data_received = {
        "fromMe": False,
        "chat": {
            "id": "556999267344",
            "profilePicture": "https://pps.whatsapp.net/v/t61.24694-24/462429652_2229319410767469_7773187573644695635_n.jpg?ccb=11-4&oh=01_Q5Aa2AE5OOQugwo4m88csmkTQpNDwDyEXPePZcqA4oELniMqig&oe=689B38AF&_nc_sid=5e03e0&_nc_cat=100"
        },
        "sender": {
            "id": "556993291093",
            "profilePicture": "https://pps.whatsapp.net/v/t61.24694-24/462189315_448942584891093_7781840178101974754_n.jpg?ccb=11-4&oh=01_Q5Aa2AFoXklUo9Xh-ciywvfPd3oicMRVv0tIzOHHtY6V0iG9kw&oe=689B5B12&_nc_sid=5e03e0&_nc_cat=103",
            "pushName": "João Silva",
            "verifiedBizName": ""
        }
    }
    
    print("📤 Testando mensagem enviada pelo usuário (fromMe: true)...")
    profile_picture_from_me = extract_profile_picture_robust(webhook_data_from_me)
    print(f"✅ Foto extraída: {profile_picture_from_me}")
    
    print("\n📥 Testando mensagem recebida (fromMe: false)...")
    profile_picture_received = extract_profile_picture_robust(webhook_data_received)
    print(f"✅ Foto extraída: {profile_picture_received}")
    
    # Verificar se as fotos são diferentes
    if profile_picture_from_me != profile_picture_received:
        print("✅ CORREÇÃO FUNCIONANDO: Fotos diferentes extraídas corretamente!")
        print(f"📤 Mensagem enviada: {profile_picture_from_me}")
        print(f"📥 Mensagem recebida: {profile_picture_received}")
    else:
        print("❌ PROBLEMA: Fotos iguais - correção não funcionou")

def main():
    """Função principal"""
    print("🔧 TESTE DA CORREÇÃO DE IMAGENS DE PERFIL")
    print("=" * 60)
    
    try:
        # Testar extração de imagens
        test_extract_profile_picture()
        
        print("\n✅ Testes concluídos!")
        
    except Exception as e:
        print(f"❌ Erro nos testes: {e}")

if __name__ == "__main__":
    main() 