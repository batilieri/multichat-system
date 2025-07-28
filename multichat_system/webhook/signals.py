"""
Signals para o app webhook
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.utils import timezone
from core.models import Mensagem, Chat

# Cache para armazenar atualizações pendentes
REALTIME_CACHE_KEY = "realtime_updates"
REALTIME_CACHE_TIMEOUT = 300

def notify_realtime_update(update_type, chat_id, data):
    """
    Notifica uma atualização em tempo real
    """
    try:
        # Obter atualizações existentes do cache
        updates = cache.get(REALTIME_CACHE_KEY, [])
        
        # Criar nova atualização
        update = {
            'type': update_type,
            'chat_id': chat_id,
            'timestamp': timezone.now().isoformat(),
            'data': data
        }
        
        # Adicionar à lista de atualizações
        updates.append(update)
        
        # Manter apenas as últimas 100 atualizações para evitar overflow
        if len(updates) > 100:
            updates = updates[-100:]
        
        # Salvar no cache
        cache.set(REALTIME_CACHE_KEY, updates, REALTIME_CACHE_TIMEOUT)
        
        print(f"✅ Atualização em tempo real salva no cache: {update_type}")
        print(f"📊 Total de atualizações no cache: {len(updates)}")
        
    except Exception as e:
        print(f"❌ Erro ao notificar atualização em tempo real: {e}")

def notify_all_chats_update(update_type, data):
    """
    Notifica todos os chats sobre uma atualização global
    """
    try:
        # Obter todos os chats ativos
        all_chats = Chat.objects.filter(status='active')
        
        # Obter atualizações existentes do cache
        updates = cache.get(REALTIME_CACHE_KEY, [])
        
        # Criar atualização para cada chat
        for chat in all_chats:
            update = {
                'type': update_type,
                'chat_id': chat.chat_id,
                'timestamp': timezone.now().isoformat(),
                'data': data
            }
            updates.append(update)
        
        # Manter apenas as últimas 100 atualizações para evitar overflow
        if len(updates) > 100:
            updates = updates[-100:]
        
        # Salvar no cache
        cache.set(REALTIME_CACHE_KEY, updates, REALTIME_CACHE_TIMEOUT)
        
        print(f"✅ Atualização global salva no cache: {update_type} para {all_chats.count()} chats")
        print(f"📊 Total de atualizações no cache: {len(updates)}")
        
    except Exception as e:
        print(f"❌ Erro ao notificar atualização global: {e}")

@receiver(post_save, sender=Mensagem)
def mensagem_saved_handler(sender, instance, created, **kwargs):
    """
    Signal handler para quando uma mensagem é salva
    """
    if created:
        print(f"🔔 Signal disparado: Mensagem {instance.id} criada")
        
        # Preparar dados da mensagem para o frontend
        message_data = {
            'id': instance.id,
            'type': instance.tipo,
            'content': instance.conteudo,
            'timestamp': instance.data_envio.isoformat(),
            'sender': instance.remetente,
            'isOwn': instance.from_me,
            'status': 'read' if instance.lida else 'sent',
            'message_id': instance.message_id
        }
        
        # Notificar nova mensagem para o chat específico
        notify_realtime_update('new_message', instance.chat.chat_id, message_data)
        
        # ATUALIZAÇÃO GLOBAL: Notificar todos os chats sobre a nova mensagem
        # Isso fará com que todos os chats sejam atualizados na interface
        global_update_data = {
            'type': 'global_new_message',
            'message': message_data,
            'chat_id': instance.chat.chat_id,
            'chat_name': instance.chat.chat_name or instance.chat.chat_id,
            'sender_name': instance.remetente,
            'timestamp': instance.data_envio.isoformat()
        }
        
        notify_all_chats_update('global_new_message', global_update_data)
        
        print(f"📝 Dados da atualização: {message_data}")
        print(f"🌐 Atualização global enviada para todos os chats")
    else:
        # Mensagem atualizada (não criada)
        print(f"🔄 Signal disparado: Mensagem {instance.id} atualizada")
        
        # Notificar atualização de mensagem
        update_data = {
            'id': instance.id,
            'type': instance.tipo,
            'content': instance.conteudo,
            'timestamp': instance.data_envio.isoformat(),
            'sender': instance.remetente,
            'isOwn': instance.from_me,
            'status': 'read' if instance.lida else 'sent',
            'message_id': instance.message_id
        }
        
        notify_realtime_update('message_updated', instance.chat.chat_id, update_data) 