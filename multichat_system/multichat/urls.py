"""
URL Configuration for MultiChat System
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_root(request):
    """Root endpoint da API"""
    return JsonResponse({
        'message': 'MultiChat System API',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'auth': '/api/auth/',
            'webhook': '/webhook/',
            'docs': '/api/docs/',
        }
    })

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Root
    path('', api_root, name='api-root'),
    
    # API endpoints
    path('api/', include('api.urls')),
    
    # Authentication
    path('api/auth/', include('authentication.urls')),
    
    # Webhook endpoints
    path('webhook/', include('webhook.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin
admin.site.site_header = "MultiChat System"
admin.site.site_title = "MultiChat Admin"
admin.site.index_title = "Painel de Administração"

