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
from .views import UsuarioViewSet, recuperar_status_whatsapp, WebhookMessageViewSet, test_chats_public

# Router principal para ViewSets
router = DefaultRouter()
router.register(r'clientes', views.ClienteViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'departamentos', views.DepartamentoViewSet)
router.register(r'whatsapp-instances', views.WhatsappInstanceViewSet)
router.register(r'chats', views.ChatViewSet)
router.register(r'mensagens', views.MensagemViewSet)
router.register(r'webhook-events', views.WebhookEventViewSet)
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
    
    # Endpoints adicionais podem ser adicionados aqui
    # path('custom-endpoint/', views.CustomView.as_view(), name='custom-endpoint'),
]

urlpatterns += [
    path('clientes/recuperar-status-whatsapp/', recuperar_status_whatsapp, name='recuperar_status_whatsapp'),
]


