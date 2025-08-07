"""
URLs da API do sistema MultiChat.

Define as rotas para todos os endpoints da API REST, incluindo:
- Gestão de clientes e instâncias WhatsApp
- Departamentos e usuários
- Chats e mensagens
- Eventos de webhook
- Dashboard e estatísticas
- Relatórios

Autor: Sistema MultiChat
Data: 2025-07-11
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    UsuarioViewSet, recuperar_status_whatsapp, WebhookMessageViewSet, test_chats_public, serve_audio, serve_audio_by_message, serve_wapi_media,
    serve_whatsapp_media,
    serve_audio_message,
    serve_audio_message_public,
    serve_whatsapp_audio,
    serve_image_message,
    serve_video_message,
    serve_sticker_message,
    serve_document_message,
    test_mensagens_public
)

# Router principal para ViewSets
router = DefaultRouter()
router.register(r'clientes', views.ClienteViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'departamentos', views.DepartamentoViewSet)
router.register(r'whatsapp-instances', views.WhatsappInstanceViewSet)
router.register(r'chats', views.ChatViewSet)
router.register(r'mensagens', views.MensagemViewSet)
router.register(r'webhook-events', views.WebhookEventViewSet)
router.register(r'media-files', views.MediaFileViewSet)
router.register(r'dashboard', views.DashboardViewSet, basename='dashboard')
router.register(r'wapi', views.WApiProxyViewSet, basename='wapi')
router.register(r'webhook-mensagens', WebhookMessageViewSet, basename='webhook-mensagens')

app_name = 'api'

urlpatterns = [
    # Incluir todas as rotas do router
    path('', include(router.urls)),
    
    # Endpoint de relatórios
    path('relatorios/', views.RelatorioView.as_view(), name='relatorios'),
    
    # Endpoint público para teste
    path('test-chats/', test_chats_public, name='test_chats_public'),
    
    # Endpoints de mídia (públicos)
    path('wapi-media/<str:media_type>/<str:filename>/', serve_wapi_media, name='serve_wapi_media'),
    path('whatsapp-media/<int:cliente_id>/<str:instance_id>/<str:chat_id>/<str:media_type>/<str:filename>/', serve_whatsapp_media, name='serve_whatsapp_media'),
    
    # Endpoints de áudio (públicos)
    path('audio/<path:audio_path>/', serve_audio, name='serve_audio'),
    path('audio/message/<int:message_id>/', serve_audio_by_message, name='serve_audio_by_message'),
    path('audio/message/<int:message_id>/public/', serve_audio_message_public, name='serve_audio_message_public'),
    path('whatsapp-audio/<int:cliente_id>/<str:instance_id>/<str:chat_id>/<str:filename>/', serve_whatsapp_audio, name='serve_whatsapp_audio'),
    
    # Endpoints de mídia (com autenticação)
    path('audio/message/<int:message_id>/', serve_audio_message, name='serve_audio_message'),
    path('image/message/<int:message_id>/', serve_image_message, name='serve_image_message'),
    path('video/message/<int:message_id>/', serve_video_message, name='serve_video_message'),
    path('sticker/message/<int:message_id>/', serve_sticker_message, name='serve_sticker_message'),
    path('document/message/<int:message_id>/', serve_document_message, name='serve_document_message'),
    
    # Endpoint público temporário para teste
    path('test/mensagens/public/', test_mensagens_public, name='test_mensagens_public'),
]

urlpatterns += [
    path('clientes/recuperar-status-whatsapp/', recuperar_status_whatsapp, name='recuperar_status_whatsapp'),
]


