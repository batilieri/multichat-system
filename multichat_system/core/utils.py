#!/usr/bin/env python3
"""
Utilitários para o sistema MultiChat
Funções para buscar instâncias e garantir isolamento entre clientes
"""

from typing import Optional
from .models import WhatsappInstance, Cliente


def get_client_whatsapp_instance(cliente: Cliente, prefer_connected: bool = True) -> Optional[WhatsappInstance]:
    """
    Busca a instância do WhatsApp para um cliente específico.
    
    Args:
        cliente: Cliente para buscar a instância
        prefer_connected: Se True, prioriza instâncias conectadas
        
    Returns:
        WhatsappInstance ou None se não encontrar
    """
    if not cliente:
        return None
    
    if prefer_connected:
        # Primeiro tentar encontrar instância conectada
        instance = WhatsappInstance.objects.filter(
            cliente=cliente,
            status='connected'
        ).first()
        
        if instance:
            return instance
    
    # Se não encontrou conectada ou prefer_connected=False, buscar qualquer instância
    return WhatsappInstance.objects.filter(cliente=cliente).first()


def get_whatsapp_instance_by_chat(chat, prefer_connected: bool = True) -> Optional[WhatsappInstance]:
    """
    Busca a instância do WhatsApp baseada no chat.
    
    Args:
        chat: Chat para buscar a instância
        prefer_connected: Se True, prioriza instâncias conectadas
        
    Returns:
        WhatsappInstance ou None se não encontrar
    """
    if not chat or not hasattr(chat, 'cliente'):
        return None
    
    return get_client_whatsapp_instance(chat.cliente, prefer_connected)


def get_whatsapp_instance_by_message(mensagem, prefer_connected: bool = True) -> Optional[WhatsappInstance]:
    """
    Busca a instância do WhatsApp baseada na mensagem.
    
    Args:
        mensagem: Mensagem para buscar a instância
        prefer_connected: Se True, prioriza instâncias conectadas
        
    Returns:
        WhatsappInstance ou None se não encontrar
    """
    if not mensagem or not hasattr(mensagem, 'chat'):
        return None
    
    return get_whatsapp_instance_by_chat(mensagem.chat, prefer_connected)


def validate_client_isolation(cliente: Cliente, instance_id: str) -> bool:
    """
    Valida se uma instância pertence ao cliente correto.
    
    Args:
        cliente: Cliente para validar
        instance_id: ID da instância para validar
        
    Returns:
        True se a instância pertence ao cliente, False caso contrário
    """
    try:
        instance = WhatsappInstance.objects.get(instance_id=instance_id)
        return instance.cliente == cliente
    except WhatsappInstance.DoesNotExist:
        return False


def get_all_client_instances(cliente: Cliente) -> list:
    """
    Retorna todas as instâncias de um cliente.
    
    Args:
        cliente: Cliente para buscar instâncias
        
    Returns:
        Lista de instâncias do cliente
    """
    if not cliente:
        return []
    
    return list(WhatsappInstance.objects.filter(cliente=cliente).order_by('-created_at'))


def get_primary_client_instance(cliente: Cliente) -> Optional[WhatsappInstance]:
    """
    Retorna a instância principal de um cliente (primeira criada).
    
    Args:
        cliente: Cliente para buscar a instância principal
        
    Returns:
        WhatsappInstance principal ou None se não encontrar
    """
    if not cliente:
        return None
    
    return WhatsappInstance.objects.filter(cliente=cliente).order_by('created_at').first() 