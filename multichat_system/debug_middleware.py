"""
Middleware de debug para monitorar quais rotas estão sendo chamadas
"""
import logging

logger = logging.getLogger(__name__)

class DebugRouteMiddleware:
    """
    Middleware simples para debug de rotas
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log da rota sendo acessada
        logger.info(f"[DEBUG] 🛣️ Rota recebida: {request.method} {request.path}")
        print(f"[DEBUG] 🛣️ Rota recebida: {request.method} {request.path}")
        
        # Se for um webhook, log adicional
        if 'webhook' in request.path:
            logger.info(f"[DEBUG] 🎣 WEBHOOK detectado: {request.path}")
            print(f"[DEBUG] 🎣 WEBHOOK detectado: {request.path}")
        
        response = self.get_response(request)
        return response 