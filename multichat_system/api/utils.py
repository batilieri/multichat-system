def determine_from_me_saas(payload, instance_id):
    """
    Determina se a mensagem foi enviada pelo próprio usuário (from_me).
    - Método 1: Campo fromMe do WhatsApp (mais confiável)
    - Método 2: Campo fromMe no payload raiz
    - Método 3: Comparar sender com instance_id
    """
    # Método 1: Verificar campo fromMe no key (mais confiável)
    message_key = payload.get('key', {})
    if 'fromMe' in message_key:
        return message_key['fromMe']
    
    # Método 2: Verificar campo fromMe no payload raiz
    if 'fromMe' in payload:
        return payload['fromMe']
    
    # Método 3: Comparar sender com instance_id
    sender_id = payload.get('sender', {}).get('id', '')
    if sender_id and instance_id:
        sender_phone = sender_id.split('@')[0] if '@' in sender_id else sender_id
        
        # Se o instance_id contém o número do sender, é do proprietário
        if sender_phone in instance_id:
            return True
        
        # Se o sender_id é o mesmo do chat_id (para chats individuais), pode ser do usuário
        chat_id = payload.get('chat', {}).get('id', '')
        if sender_id == chat_id:
            return True
    
    return False 