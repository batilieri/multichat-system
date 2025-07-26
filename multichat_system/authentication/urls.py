"""
URLs para autenticação do MultiChat System
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Autenticação JWT
    path('login/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Gestão de usuários (usando ViewSets)
    # path('registro/', views.UsuarioRegistroView.as_view({'post': 'create'}), name='registro_usuario'),
    # path('perfil/', views.UsuarioPerfilView.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}), name='perfil_usuario'),
]

app_name = 'authentication'

