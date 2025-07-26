"""
Views da API do sistema MultiChat com integração W-APi.

Este módulo contém todas as views da API REST para gerenciar:
- Clientes e suas instâncias do WhatsApp
- Departamentos
- Chats e mensagens
- Eventos de webhook
- Instâncias do WhatsApp (W-APi)

Autor: Sistema MultiChat
Data: 2025-07-11
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Q, Count, Sum
from django.utils import timezone
from datetime import timedelta
import json
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ClienteSerializer
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes

from core.models import Cliente, Departamento, Chat, Mensagem, WebhookEvent, WhatsappInstance
from authentication.models import Usuario
from authentication.serializers import UsuarioRegistroSerializer, UsuarioPerfilSerializer
from .serializers import (
    ClienteSerializer, DepartamentoSerializer, ChatSerializer,
    MensagemSerializer, WebhookEventSerializer, WhatsappInstanceSerializer
)
from .permissions import IsAdminOrReadOnly, IsAtendenteOrAdmin, IsClienteOwner, IsClienteOrAdmin, IsColaboradorOnly, IsAdminOrCliente, IsClienteInstanceOwner
from .wapi_integration import WApiIntegration
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from webhook.models import Message, MessageStats, ContactStats
from .serializers import WebhookMessageSerializer
from django.http import StreamingHttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import time

logger = logging.getLogger(__name__)


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar usuários.
    
    Administradores podem criar qualquer tipo de usuário.
    Clientes podem criar apenas colaboradores associados a eles.
    Colaboradores não podem criar usuários.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioPerfilSerializer
    permission_classes = [IsClienteOrAdmin]

    def get_queryset(self):
        """
        Retorna o queryset de usuários baseado no tipo de usuário logado.
        """
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin'):
            return Usuario.objects.all()
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'cliente':
            # Cliente vê apenas colaboradores associados a ele
            if hasattr(user, 'cliente') and user.cliente:
                return Usuario.objects.filter(tipo_usuario='colaborador', cliente=user.cliente)
            else:
                return Usuario.objects.none()
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador':
            # Colaborador vê apenas a si mesmo
            return Usuario.objects.filter(id=user.id)
        return Usuario.objects.none()

    def create(self, request, *args, **kwargs):
        """
        Cria um novo usuário baseado no tipo de usuário logado.
        """
        user = request.user
        
        # Verificar permissões
        if not (user.is_superuser or 
                (hasattr(user, 'tipo_usuario') and 
                 (user.tipo_usuario == 'admin' or user.tipo_usuario == 'cliente'))):
            return Response({
                "error": "Apenas administradores e clientes podem criar usuários"
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Se for cliente, só pode criar colaboradores
        if hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'cliente':
            if request.data.get('tipo_usuario') != 'colaborador':
                return Response({
                    "error": "Clientes podem criar apenas colaboradores"
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Associar o colaborador ao cliente
            request.data['cliente'] = user.cliente.id if hasattr(user, 'cliente') else None
        
        serializer = UsuarioRegistroSerializer(data=request.data)
        if not serializer.is_valid():
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erros de validação ao criar usuário: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        new_user = serializer.save()
        
        return Response(UsuarioPerfilSerializer(new_user).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Atualiza um usuário baseado no tipo de usuário logado.
        """
        user = request.user
        target_user = self.get_object()
        
        # Verificar permissões
        if not (user.is_superuser or 
                (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin')):
            # Cliente só pode atualizar seus próprios colaboradores
            if hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'cliente':
                if target_user.tipo_usuario != 'colaborador' or target_user.cliente != user.cliente:
                    return Response({
                        "error": "Você só pode atualizar seus próprios colaboradores"
                    }, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({
                    "error": "Apenas administradores podem atualizar usuários"
                }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Remove um usuário baseado no tipo de usuário logado.
        """
        user = request.user
        target_user = self.get_object()
        
        # Verificar permissões
        if not (user.is_superuser or 
                (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin')):
            # Cliente só pode remover seus próprios colaboradores
            if hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'cliente':
                if target_user.tipo_usuario != 'colaborador' or target_user.cliente != user.cliente:
                    return Response({
                        "error": "Você só pode remover seus próprios colaboradores"
                    }, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({
                    "error": "Apenas administradores podem remover usuários"
                }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)


class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar clientes.

    Permite operações CRUD em clientes. Apenas administradores podem criar, atualizar ou excluir.
    Colaboradores podem apenas visualizar clientes associados a eles.
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        """
        Retorna o queryset de clientes baseado no tipo de usuário logado.

        Administradores veem todos os clientes. 
        Clientes veem apenas a si mesmos.
        Colaboradores veem apenas o cliente ao qual estão associados.
        """
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin'):
            return Cliente.objects.all()
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'cliente':
            # Cliente vê apenas a si mesmo
            return Cliente.objects.filter(email=user.email)
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador' and hasattr(user, 'cliente') and user.cliente:
            return Cliente.objects.filter(id=user.cliente.id)
        return Cliente.objects.none()

    def create(self, request, *args, **kwargs):
        """
        Cria um novo cliente com logs de debug.
        """
        logger.info(f"Tentativa de criar cliente - Dados recebidos: {request.data}")
        logger.info(f"Usuário logado: {request.user.email} - Tipo: {getattr(request.user, 'tipo_usuario', 'N/A')}")
        
        try:
            serializer = self.get_serializer(data=request.data)
            logger.info(f"Serializer criado - Validando dados...")
            
            if serializer.is_valid():
                logger.info(f"Dados válidos - Salvando cliente")
                cliente = serializer.save()
                logger.info(f"Cliente criado com sucesso: {cliente.nome} (ID: {cliente.id})")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"Dados inválidos: {serializer.errors}")
                logger.error(f"Dados recebidos: {request.data}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Erro ao criar cliente: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrReadOnly])
    def connect_wapi(self, request, pk=None):
        """
        Conecta uma instância do W-APi a um cliente existente.

        Recebe `instance_id` e `token` no corpo da requisição.
        Cria ou atualiza uma `WhatsappInstance` e tenta verificar o status na W-APi.
        """
        cliente = self.get_object()
        instance_id = request.data.get("instance_id")
        token = request.data.get("token")
        webhook_url = request.data.get("webhook_url", "https://167.86.75.207/webhook")

        if not instance_id or not token:
            return Response({
                "error": "instance_id e token são obrigatórios"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Criar instância usando o método estático da integração
            result = WApiIntegration.criar_instancia_para_cliente(cliente.id, instance_id, token)
            
            if result["success"]:
                # Configurar webhook se fornecido
                if webhook_url:
                    wapi = WApiIntegration(instance_id, token)
                    webhook_result = wapi.configurar_webhook(webhook_url)
                    
                    if not webhook_result["success"]:
                        return Response({
                            "warning": "Instância criada mas webhook não configurado",
                            "webhook_error": webhook_result["message"],
                            "data": result
                        }, status=status.HTTP_201_CREATED)

                return Response({
                    "message": "Instância W-APi conectada com sucesso!",
                    "data": result
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "error": result["message"]
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["get"])
    def wapi_status(self, request, pk=None):
        """
        Verifica o status da conexão W-APi de um cliente.
        """
        cliente = self.get_object()
        
        try:
            instancia = WhatsappInstance.objects.get(cliente=cliente)
            wapi = WApiIntegration(instancia.instance_id, instancia.token)
            status_result = wapi.verificar_status_conexao()
            
            # Atualizar status na base de dados
            instancia.status = status_result.get("status", "erro")
            if status_result.get("qr_code"):
                instancia.qr_code = status_result["qr_code"]
            instancia.save()
            
            return Response({
                "instance_id": instancia.instance_id,
                "status": instancia.status,
                "qr_code": instancia.qr_code,
                "last_check": status_result
            })
            
        except WhatsappInstance.DoesNotExist:
            return Response({
                "error": "Cliente não possui instância W-APi configurada"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"])
    def send_message(self, request, pk=None):
        """
        Envia uma mensagem através da instância W-APi do cliente.
        """
        cliente = self.get_object()
        numero_destino = request.data.get("numero_destino")
        mensagem = request.data.get("mensagem")
        tipo = request.data.get("tipo", "texto")  # texto, imagem, etc.
        
        if not numero_destino or not mensagem:
            return Response({
                "error": "numero_destino e mensagem são obrigatórios"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            instancia = WhatsappInstance.objects.get(cliente=cliente)
            wapi = WApiIntegration(instancia.instance_id, instancia.token)
            
            if tipo == "texto":
                result = wapi.enviar_mensagem_texto(numero_destino, mensagem)
            elif tipo == "imagem":
                url_imagem = request.data.get("url_imagem")
                legenda = request.data.get("legenda", "")
                result = wapi.enviar_imagem(numero_destino, url_imagem, legenda)
            else:
                return Response({
                    "error": "Tipo de mensagem não suportado"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if result["success"]:
                return Response({
                    "message": "Mensagem enviada com sucesso",
                    "message_id": result.get("message_id"),
                    "data": result
                })
            else:
                return Response({
                    "error": result["message"]
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except WhatsappInstance.DoesNotExist:
            return Response({
                "error": "Cliente não possui instância W-APi configurada"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WhatsappInstanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar instâncias do WhatsApp.
    
    Permite operações CRUD em instâncias de WhatsApp conectadas via W-APi.
    """
    queryset = WhatsappInstance.objects.all()
    serializer_class = WhatsappInstanceSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        """
        Retorna o queryset de instâncias baseado no tipo de usuário logado.
        """
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin'):
            return WhatsappInstance.objects.all()
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'cliente':
            return WhatsappInstance.objects.filter(cliente__email=user.email)
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador' and hasattr(user, 'cliente') and user.cliente:
            return WhatsappInstance.objects.filter(cliente=user.cliente)
        return WhatsappInstance.objects.none()

    @action(detail=True, methods=["get"])
    def get_for_edit(self, request, pk=None):
        """
        Retorna uma instância específica com o token incluído para edição.
        """
        instance = self.get_object()
        from .serializers import WhatsappInstanceEditSerializer
        serializer = WhatsappInstanceEditSerializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsClienteInstanceOwner])
    def refresh_status(self, request, pk=None):
        """
        Atualiza o status de uma instância específica.
        Clientes podem atualizar apenas suas próprias instâncias.
        Administradores podem atualizar qualquer instância.
        """
        instancia = self.get_object()
        
        try:
            result = WApiIntegration.atualizar_status_instancia(instancia.instance_id)
            
            if result["success"]:
                # Recarregar instância atualizada
                instancia.refresh_from_db()
                serializer = self.get_serializer(instancia)
                return Response({
                    "message": result["message"],
                    "data": serializer.data
                })
            else:
                return Response({
                    "error": result["message"]
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"], permission_classes=[IsClienteInstanceOwner])
    def send_message(self, request, pk=None):
        """
        Envia uma mensagem através da instância do WhatsApp.
        Clientes podem enviar mensagens apenas através de suas próprias instâncias.
        Administradores podem enviar mensagens através de qualquer instância.
        """
        instancia = self.get_object()
        numero_destino = request.data.get("numero_destino")
        mensagem = request.data.get("mensagem")
        
        if not numero_destino or not mensagem:
            return Response({
                "error": "numero_destino e mensagem são obrigatórios"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            wapi = WApiIntegration(instancia.instance_id, instancia.token)
            result = wapi.enviar_mensagem_texto(numero_destino, mensagem)
            
            if result["success"]:
                return Response({
                    "message": "Mensagem enviada com sucesso",
                    "message_id": result.get("message_id"),
                    "data": result
                })
            else:
                return Response({
                    "error": result["message"]
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["get"], permission_classes=[IsClienteInstanceOwner])
    def generate_qr(self, request, pk=None):
        """
        Gera um novo QR Code para a instância.
        Clientes podem gerar QR codes apenas de suas próprias instâncias.
        Administradores podem gerar QR codes de qualquer instância.
        """
        instancia = self.get_object()
        
        try:
            wapi = WApiIntegration(instancia.instance_id, instancia.token)
            result = wapi.gerar_qr_code()
            
            if result["success"]:
                instancia.qr_code = result["qr_code"]
                instancia.status = "qrcode_gerado"
                instancia.save()
                
                return Response({
                    "message": "QR Code gerado com sucesso",
                    "qr_code": result["qr_code"]
                })
            else:
                return Response({
                    "error": result["message"]
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DepartamentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar departamentos.

    Permite operações CRUD em departamentos. Apenas administradores podem criar, atualizar ou excluir.
    Colaboradores podem apenas visualizar departamentos associados ao seu cliente.
    """
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        """
        Retorna o queryset de departamentos baseado no tipo de usuário logado.

        Administradores veem todos os departamentos. Colaboradores veem apenas
        departamentos do cliente ao qual estão associados.
        """
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin'):
            return Departamento.objects.all()
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador' and hasattr(user, 'cliente'):
            return Departamento.objects.filter(cliente=user.cliente)
        return Departamento.objects.none()


class ChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar chats.

    Permite operações CRUD em chats. Administradores veem todos os chats.
    Colaboradores e clientes veem apenas chats do cliente ao qual estão associados.
    """
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAtendenteOrAdmin]

    def get_queryset(self):
        """
        Retorna o queryset de chats com mensagens pré-carregadas
        """
        user = self.request.user
        base_queryset = Chat.objects.select_related('cliente', 'atendente').prefetch_related('mensagens')
        if user.is_superuser or (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin'):
            return base_queryset.all()
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'cliente' and hasattr(user, 'cliente') and user.cliente:
            return base_queryset.filter(cliente=user.cliente)
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador' and hasattr(user, 'cliente') and user.cliente:
            return base_queryset.filter(cliente=user.cliente)
        return Chat.objects.none()

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """
        Retorna estatísticas dos chats.
        """
        queryset = self.get_queryset()
        
        # Estatísticas básicas
        total_chats = queryset.count()
        chats_abertos = queryset.filter(status="aberto").count()
        chats_fechados = queryset.filter(status="fechado").count()
        chats_pendentes = queryset.filter(status="pendente").count()
        
        # Chats por período
        hoje = timezone.now().date()
        chats_hoje = queryset.filter(data_inicio__date=hoje).count()
        chats_semana = queryset.filter(
            data_inicio__date__gte=hoje - timedelta(days=7)
        ).count()
        
        return Response({
            "total_chats": total_chats,
            "chats_abertos": chats_abertos,
            "chats_fechados": chats_fechados,
            "chats_pendentes": chats_pendentes,
            "chats_hoje": chats_hoje,
            "chats_semana": chats_semana
        })

    @action(detail=False, methods=["get"], url_path='realtime-updates')
    def realtime_updates(self, request):
        """
        Endpoint SSE para atualizações em tempo real dos chats
        """
        from django.core.cache import cache
        
        def event_stream():
            """Gera stream de eventos SSE"""
            last_check = timezone.now()
            last_cache_check = timezone.now()
            
            while True:
                try:
                    # Verificar cache de atualizações primeiro
                    updates = cache.get("realtime_updates", [])
                    current_time = timezone.now()
                    
                    # Filtrar atualizações novas
                    new_updates = []
                    for update in updates:
                        update_time = timezone.datetime.fromisoformat(update['timestamp'].replace('Z', '+00:00'))
                        if update_time > last_cache_check:
                            new_updates.append(update)
                    
                    # Enviar atualizações do cache
                    if new_updates:
                        data = {
                            'timestamp': current_time.isoformat(),
                            'updates': new_updates
                        }
                        yield f"data: {json.dumps(data, cls=DjangoJSONEncoder)}\n\n"
                        last_cache_check = current_time
                    
                    # Verificar novas mensagens desde a última verificação (fallback)
                    user = request.user
                    base_queryset = Chat.objects.select_related('cliente', 'atendente')
                    
                    # Filtrar por permissões do usuário
                    if user.is_superuser or (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin'):
                        chats = base_queryset.all()
                    elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'cliente' and hasattr(user, 'cliente') and user.cliente:
                        chats = base_queryset.filter(cliente=user.cliente)
                    elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador' and hasattr(user, 'cliente') and user.cliente:
                        chats = base_queryset.filter(cliente=user.cliente)
                    else:
                        chats = Chat.objects.none()
                    
                    # Verificar mensagens novas (apenas se não houver atualizações no cache)
                    if not new_updates:
                        novas_mensagens = Mensagem.objects.filter(
                            chat__in=chats,
                            data_envio__gt=last_check
                        ).select_related('chat').order_by('data_envio')
                        
                        # Verificar chats atualizados
                        chats_atualizados = chats.filter(
                            last_message_at__gt=last_check
                        )
                        
                        updates = []
                        
                        # Adicionar mensagens novas
                        for msg in novas_mensagens:
                            updates.append({
                                'type': 'new_message',
                                'chat_id': msg.chat.chat_id,
                                'message': {
                                    'id': msg.id,
                                    'type': msg.tipo,
                                    'content': msg.conteudo,
                                    'timestamp': msg.data_envio.isoformat(),
                                    'sender': msg.remetente,
                                    'isOwn': msg.from_me,
                                    'status': 'read' if msg.lida else 'sent'
                                }
                            })
                        
                        # Adicionar chats atualizados
                        for chat in chats_atualizados:
                            updates.append({
                                'type': 'chat_updated',
                                'chat_id': chat.chat_id,
                                'last_message_at': chat.last_message_at.isoformat() if chat.last_message_at else None,
                                'message_count': chat.mensagens.count()
                            })
                        
                        # Enviar atualizações se houver
                        if updates:
                            data = {
                                'timestamp': current_time.isoformat(),
                                'updates': updates
                            }
                            yield f"data: {json.dumps(data, cls=DjangoJSONEncoder)}\n\n"
                    
                    # Atualizar timestamp da última verificação
                    last_check = current_time
                    
                    # Aguardar 2 segundos antes da próxima verificação
                    time.sleep(2)
                    
                except Exception as e:
                    # Em caso de erro, enviar evento de erro
                    error_data = {
                        'timestamp': timezone.now().isoformat(),
                        'error': str(e)
                    }
                    yield f"data: {json.dumps(error_data, cls=DjangoJSONEncoder)}\n\n"
                    time.sleep(5)  # Aguardar mais tempo em caso de erro
        
        # Configurar headers corretos para SSE
        response = StreamingHttpResponse(
            event_stream(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Cache-Control'
        response['Access-Control-Allow-Methods'] = 'GET'
        
        # Adicionar headers específicos para SSE
        response['Connection'] = 'keep-alive'
        response['Transfer-Encoding'] = 'chunked'
        
        return response

    @action(detail=False, methods=["get"], url_path='check-updates')
    def check_updates(self, request):
        """
        Endpoint alternativo para verificar atualizações (polling)
        """
        from django.core.cache import cache
        
        try:
            # Obter timestamp da última verificação
            last_check = request.GET.get('last_check')
            if last_check:
                try:
                    # Tentar diferentes formatos de timestamp
                    if ' ' in last_check and '+00:00' in last_check:
                        # Formato: "2025-07-19T03:53:10.655739 00:00"
                        last_check = last_check.replace(' +00:00', '+00:00')
                    elif ' ' in last_check:
                        # Formato: "2025-07-19T03:53:10.655739 00:00"
                        last_check = last_check.replace(' ', '+')
                    
                    last_check = timezone.datetime.fromisoformat(last_check.replace('Z', '+00:00'))
                except ValueError as e:
                    print(f"Erro ao parsear timestamp: {last_check}, erro: {e}")
                    last_check = timezone.now() - timezone.timedelta(minutes=5)
            else:
                last_check = timezone.now() - timezone.timedelta(minutes=5)
            
            # Verificar cache de atualizações
            updates = cache.get("realtime_updates", [])
            current_time = timezone.now()
            
            # Filtrar atualizações novas
            new_updates = []
            for update in updates:
                try:
                    update_timestamp = update.get('timestamp')
                    if update_timestamp:
                        # Corrigir formato do timestamp se necessário
                        if ' ' in update_timestamp and '+00:00' in update_timestamp:
                            update_timestamp = update_timestamp.replace(' +00:00', '+00:00')
                        elif ' ' in update_timestamp:
                            update_timestamp = update_timestamp.replace(' ', '+')
                        
                        update_time = timezone.datetime.fromisoformat(update_timestamp.replace('Z', '+00:00'))
                        if update_time > last_check:
                            new_updates.append(update)
                except (ValueError, TypeError) as e:
                    print(f"Erro ao processar update timestamp: {update.get('timestamp')}, erro: {e}")
                    continue
            
            # Verificar novas mensagens desde a última verificação (fallback)
            user = request.user
            base_queryset = Chat.objects.select_related('cliente', 'atendente')
            
            # Filtrar por permissões do usuário
            if user.is_superuser or (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin'):
                chats = base_queryset.all()
            elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'cliente' and hasattr(user, 'cliente') and user.cliente:
                chats = base_queryset.filter(cliente=user.cliente)
            elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador' and hasattr(user, 'cliente') and user.cliente:
                chats = base_queryset.filter(cliente=user.cliente)
            else:
                chats = Chat.objects.none()
            
            # Verificar mensagens novas (apenas se não houver atualizações no cache)
            if not new_updates:
                novas_mensagens = Mensagem.objects.filter(
                    chat__in=chats,
                    data_envio__gt=last_check
                ).select_related('chat').order_by('data_envio')
                
                # Verificar chats atualizados
                chats_atualizados = chats.filter(
                    last_message_at__gt=last_check
                )
                
                # Adicionar mensagens novas
                for msg in novas_mensagens:
                    new_updates.append({
                        'type': 'new_message',
                        'chat_id': msg.chat.chat_id,
                        'message': {
                            'id': msg.id,
                            'type': msg.tipo,
                            'content': msg.conteudo,
                            'timestamp': msg.data_envio.isoformat(),
                            'sender': msg.remetente,
                            'isOwn': msg.from_me,
                            'status': 'read' if msg.lida else 'sent'
                        }
                    })
                
                # Adicionar chats atualizados
                for chat in chats_atualizados:
                    new_updates.append({
                        'type': 'chat_updated',
                        'chat_id': chat.chat_id,
                        'last_message_at': chat.last_message_at.isoformat() if chat.last_message_at else None,
                        'message_count': chat.mensagens.count()
                    })
            
            return Response({
                'timestamp': current_time.isoformat(),
                'updates': new_updates,
                'has_updates': len(new_updates) > 0
            })
            
        except Exception as e:
            return Response({
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MensagemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar mensagens.

    Permite operações CRUD em mensagens. Administradores veem todas as mensagens.
    Colaboradores e clientes veem apenas mensagens de chats do cliente ao qual estão associados.
    """
    queryset = Mensagem.objects.all()
    serializer_class = MensagemSerializer
    permission_classes = [IsAtendenteOrAdmin]

    def get_queryset(self):
        """
        Retorna o queryset de mensagens baseado no tipo de usuário logado.
        """
        # Verificar se o request tem usuário autenticado
        if not hasattr(self.request, 'user') or not self.request.user.is_authenticated:
            return Mensagem.objects.none()
        
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin'):
            return Mensagem.objects.all()
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador' and hasattr(user, 'cliente'):
            return Mensagem.objects.filter(chat__cliente=user.cliente)
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'cliente' and hasattr(user, 'cliente'):
            return Mensagem.objects.filter(chat__cliente=user.cliente)
        return Mensagem.objects.none()

    def list(self, request, *args, **kwargs):
        """
        Lista mensagens com filtros opcionais.
        """
        queryset = self.get_queryset()
        
        # Filtros opcionais
        chat_id = request.query_params.get('chat_id')
        tipo = request.query_params.get('tipo')
        lida = request.query_params.get('lida')
        
        if chat_id:
            queryset = queryset.filter(chat__chat_id=chat_id)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if lida is not None:
            queryset = queryset.filter(lida=lida.lower() == 'true')
        
        # EXCLUIR MENSAGENS DE PROTOCOLO DO WHATSAPP
        # Filtrar mensagens que contêm dados de protocolo (não devem aparecer no chat)
        queryset = queryset.exclude(
            conteudo__icontains='protocolMessage'
        ).exclude(
            conteudo__icontains='APP_STATE_SYNC_KEY_REQUEST'
        ).exclude(
            conteudo__icontains='deviceListMetadata'
        ).exclude(
            conteudo__icontains='messageContextInfo'
        ).exclude(
            conteudo__icontains='senderKeyHash'
        ).exclude(
            conteudo__icontains='senderTimestamp'
        ).exclude(
            conteudo__icontains='deviceListMetadataVersion'
        ).exclude(
            conteudo__icontains='keyIds'
        ).exclude(
            conteudo__icontains='keyId'
        ).exclude(
            conteudo__icontains='AAAAACSE'
        )
        
        # Ordenar por data de envio (mais recentes primeiro)
        queryset = queryset.order_by('-data_envio')
        
        # Paginação
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='marcar-lidas')
    def marcar_lidas(self, request):
        """
        Marca todas as mensagens de um chat como lidas.
        """
        try:
            chat_id = request.data.get('chat_id')
            if not chat_id:
                return Response({
                    'error': 'chat_id é obrigatório'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Buscar o chat
            chat = get_object_or_404(Chat, chat_id=chat_id)
            
            # Verificar permissões
            user = request.user
            if not (user.is_superuser or 
                    (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin') or
                    (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'cliente' and chat.cliente == user.cliente) or
                    (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador' and chat.cliente == user.cliente)):
                return Response({
                    'error': 'Você não tem permissão para marcar mensagens deste chat como lidas'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Marcar mensagens não lidas como lidas
            mensagens_nao_lidas = Mensagem.objects.filter(
                chat=chat,
                lida=False,
                from_me=False  # Apenas mensagens recebidas (não enviadas pelo usuário)
            )
            
            count = mensagens_nao_lidas.count()
            mensagens_nao_lidas.update(lida=True)
            
            logger.info(f'✅ {count} mensagens marcadas como lidas para o chat {chat_id}')
            
            return Response({
                'success': True,
                'message': f'{count} mensagens marcadas como lidas',
                'chat_id': chat_id,
                'mensagens_marcadas': count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f'❌ Erro ao marcar mensagens como lidas: {e}')
            return Response({
                'error': 'Erro interno do servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """
        Exclui uma mensagem do banco de dados e da W-API.
        """
        try:
            mensagem = self.get_object()
            
            # Verificar se a mensagem tem message_id (ID do WhatsApp)
            if not mensagem.message_id:
                return Response({
                    'error': 'Esta mensagem não pode ser excluída (sem ID do WhatsApp)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar se é uma mensagem enviada pelo usuário (from_me=True)
            if not mensagem.from_me:
                return Response({
                    'error': 'Apenas mensagens enviadas por você podem ser excluídas'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Buscar a instância WhatsApp do cliente
            try:
                instancia = WhatsappInstance.objects.get(cliente=mensagem.chat.cliente)
            except WhatsappInstance.DoesNotExist:
                return Response({
                    'error': 'Instância WhatsApp não encontrada para este cliente'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Importar e usar a classe DeletaMensagem
            import sys
            import os
            # Adicionar o diretório wapi ao path
            wapi_path = os.path.join(os.path.dirname(__file__), '..', '..', 'wapi')
            if wapi_path not in sys.path:
                sys.path.append(wapi_path)
            
            try:
                from mensagem.deletar.deletarMensagens import DeletaMensagem
            except ImportError as e:
                logger.error(f'❌ Erro ao importar DeletaMensagem: {e}')
                return Response({
                    'error': 'Erro interno: módulo de exclusão não encontrado'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Criar instância do deletador
            deletador = DeletaMensagem(instancia.instance_id, instancia.token)
            
            # Excluir da W-API
            resultado_wapi = deletador.deletar(
                phone_number=mensagem.chat.chat_id,
                message_ids=mensagem.message_id
            )
            
            if resultado_wapi.get('success'):
                # Se excluiu com sucesso na W-API, excluir do banco
                mensagem.delete()
                
                logger.info(f'✅ Mensagem {mensagem.message_id} excluída com sucesso da W-API e do banco')
                
                return Response({
                    'success': True,
                    'message': 'Mensagem excluída com sucesso',
                    'wapi_result': resultado_wapi
                }, status=status.HTTP_200_OK)
            else:
                # Se falhou na W-API, retornar erro
                logger.error(f'❌ Erro ao excluir mensagem na W-API: {resultado_wapi}')
                
                return Response({
                    'error': 'Erro ao excluir mensagem no WhatsApp',
                    'details': resultado_wapi.get('error', 'Erro desconhecido')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f'❌ Erro ao excluir mensagem: {e}')
            return Response({
                'error': 'Erro interno do servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WebhookEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar eventos de webhook.

    Permite visualizar e gerenciar eventos de webhook recebidos do WhatsApp.
    """
    queryset = WebhookEvent.objects.all()
    serializer_class = WebhookEventSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        """
        Retorna eventos de webhook ordenados por data de recebimento.
        """
        return WebhookEvent.objects.all().order_by('-received_at')

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """
        Retorna estatísticas dos eventos de webhook.
        """
        queryset = self.get_queryset()
        
        total_events = queryset.count()
        processed_events = queryset.filter(processed=True).count()
        error_events = queryset.exclude(error_message__isnull=True).exclude(error_message='').count()
        
        # Eventos por tipo
        event_types = queryset.values('event_type').annotate(
            count=Count('event_type')
        ).order_by('-count')
        
        # Eventos por instância
        instances = queryset.values('instance_id').annotate(
            count=Count('instance_id')
        ).order_by('-count')
        
        return Response({
            "total_events": total_events,
            "processed_events": processed_events,
            "error_events": error_events,
            "event_types": list(event_types),
            "instances": list(instances)
        })


class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet para fornecer dados do dashboard.
    
    Agrega informações de diferentes modelos para exibir no dashboard principal.
    """
    permission_classes = [IsAtendenteOrAdmin]

    def list(self, request):
        """
        Retorna dados agregados para o dashboard.
        """
        user = request.user
        
        # Determinar escopo dos dados baseado no usuário
        if user.is_superuser or (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin'):
            clientes = Cliente.objects.all()
            chats = Chat.objects.all()
            mensagens = Mensagem.objects.all()
            instancias = WhatsappInstance.objects.all()
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'cliente':
            # Cliente vê apenas seus próprios dados
            clientes = Cliente.objects.filter(email=user.email)
            chats = Chat.objects.filter(cliente__email=user.email)
            mensagens = Mensagem.objects.filter(chat__cliente__email=user.email)
            instancias = WhatsappInstance.objects.filter(cliente__email=user.email)
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador' and hasattr(user, 'cliente'):
            clientes = Cliente.objects.filter(id=user.cliente.id)
            chats = Chat.objects.filter(cliente=user.cliente)
            mensagens = Mensagem.objects.filter(chat__cliente=user.cliente)
            instancias = WhatsappInstance.objects.filter(cliente=user.cliente)
        else:
            # Usuário sem permissões adequadas
            return Response({
                "error": "Usuário não possui permissões para acessar o dashboard"
            }, status=status.HTTP_403_FORBIDDEN)

        # Estatísticas gerais
        total_clientes = clientes.count()
        total_chats = chats.count()
        total_mensagens = mensagens.count()
        total_instancias = instancias.count()
        
        # Chats por status
        chats_abertos = chats.filter(status="aberto").count()
        chats_fechados = chats.filter(status="fechado").count()
        chats_pendentes = chats.filter(status="pendente").count()
        
        # Instâncias por status
        instancias_conectadas = instancias.filter(status="conectado").count()
        instancias_desconectadas = instancias.filter(status="desconectado").count()
        
        # Atividade recente (últimas 24 horas)
        ontem = timezone.now() - timedelta(days=1)
        chats_recentes = chats.filter(data_inicio__gte=ontem).count()
        mensagens_recentes = mensagens.filter(data_envio__gte=ontem).count()
        
        # Mensagens por tipo
        tipos_mensagem = mensagens.values('tipo').annotate(
            count=Count('tipo')
        ).order_by('-count')
        
        return Response({
            "resumo": {
                "total_clientes": total_clientes,
                "total_chats": total_chats,
                "total_mensagens": total_mensagens,
                "total_instancias": total_instancias
            },
            "chats": {
                "abertos": chats_abertos,
                "fechados": chats_fechados,
                "pendentes": chats_pendentes
            },
            "instancias": {
                "conectadas": instancias_conectadas,
                "desconectadas": instancias_desconectadas
            },
            "atividade_recente": {
                "chats_24h": chats_recentes,
                "mensagens_24h": mensagens_recentes
            },
            "tipos_mensagem": list(tipos_mensagem)
        })


class WApiProxyViewSet(viewsets.ViewSet):
    """
    ViewSet para fazer proxy das requisições para o W-API Backend.
    
    Este ViewSet redireciona requisições para o backend W-API (Flask)
    que está rodando na porta 5000.
    """
    permission_classes = [IsAtendenteOrAdmin]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # URL da WAPI oficial conforme documentação
        self.wapi_base_url = "https://api.w-api.app"
    
    @action(detail=False, methods=['get'], url_path='auth/status')
    def check_status(self, request):
        """
        Verifica o status de uma instância na W-API
        """
        try:
            instance_id = request.query_params.get('instanceId')
            if not instance_id:
                return Response({
                    "error": "instanceId é obrigatório"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Buscar token da instância
            try:
                instance = WhatsappInstance.objects.get(instance_id=instance_id)
                token = instance.token
            except WhatsappInstance.DoesNotExist:
                return Response({
                    "error": "Instância não encontrada"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Fazer requisição para W-API oficial
            import requests
            response = requests.get(
                f"{self.wapi_base_url}/v1/instance/status-instance",
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                },
                params={'instanceId': instance_id},
                timeout=30
            )
            
            logger.info(f"Status response: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            logger.info(f"Response text: {response.text[:500]}")  # Primeiros 500 chars
            
            if response.status_code == 200:
                try:
                    return Response(response.json())
                except ValueError as e:
                    logger.error(f"Erro ao fazer parse do JSON: {e}")
                    logger.error(f"Response text: {response.text}")
                    return Response({
                        "error": "Resposta inválida da W-API",
                        "details": str(e),
                        "response_text": response.text[:200]
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({
                    "error": f"Erro na W-API: {response.status_code}",
                    "response_text": response.text[:200]
                }, status=response.status_code)
                
        except Exception as e:
            logger.error(f"Erro ao verificar status: {str(e)}")
            return Response({
                "error": f"Erro interno: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='auth/qrcode')
    def get_qr_code(self, request):
        """
        Obtém QR Code para uma instância na W-API
        """
        try:
            instance_id = request.query_params.get('instanceId')
            if not instance_id:
                return Response({
                    "error": "instanceId é obrigatório"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Buscar token da instância
            try:
                instance = WhatsappInstance.objects.get(instance_id=instance_id)
                token = instance.token
            except WhatsappInstance.DoesNotExist:
                return Response({
                    "error": "Instância não encontrada"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Fazer requisição para W-API oficial
            import requests
            response = requests.get(
                f"{self.wapi_base_url}/v1/instance/qr-code",
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                },
                params={
                    'instanceId': instance_id,
                    'syncContacts': 'disable',
                    'image': 'enable'
                },
                timeout=30
            )
            
            logger.info(f"QR Code response: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                # Verificar se a resposta é uma imagem PNG
                content_type = response.headers.get('content-type', '')
                logger.info(f"Content-Type: {content_type}")
                
                if 'image/png' in content_type:
                    # Converter imagem PNG para base64
                    import base64
                    image_base64 = base64.b64encode(response.content).decode('utf-8')
                    qr_code_data_url = f"data:image/png;base64,{image_base64}"
                    
                    logger.info(f"QR Code convertido para base64 com sucesso")
                    return Response({
                        "qr_code": qr_code_data_url,
                        "instanceId": instance_id,
                        "message": "QR Code gerado com sucesso"
                    })
                else:
                    # Tentar fazer parse como JSON
                    try:
                        return Response(response.json())
                    except ValueError as e:
                        logger.error(f"Erro ao fazer parse do JSON: {e}")
                        logger.error(f"Response text: {response.text[:200]}")
                        return Response({
                            "error": "Resposta inválida da W-API",
                            "details": str(e),
                            "response_text": response.text[:200]
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({
                    "error": f"Erro na W-API: {response.status_code}",
                    "response_text": response.text[:200]
                }, status=response.status_code)
                
        except Exception as e:
            logger.error(f"Erro ao obter QR Code: {str(e)}")
            return Response({
                "error": f"Erro interno: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='webhooks/test')
    def test_webhook(self, request):
        """
        Proxy para testar webhook de uma instância na W-API.
        Recebe instanceId e url no body.
        """
        try:
            instance_id = request.data.get('instanceId')
            webhook_url = request.data.get('url')
            event_type = request.data.get('event_type', 'test')
            if not instance_id or not webhook_url:
                return Response({
                    "error": "instanceId e url são obrigatórios"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Buscar token da instância
            try:
                instance = WhatsappInstance.objects.get(instance_id=instance_id)
                token = instance.token
            except WhatsappInstance.DoesNotExist:
                return Response({
                    "error": "Instância não encontrada"
                }, status=status.HTTP_404_NOT_FOUND)

            # Fazer requisição para o endpoint /webhooks/test da WAPI
            import requests
            response = requests.post(
                f"{self.wapi_base_url}/v1/webhooks/test",
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                },
                json={
                    'instanceId': instance_id,
                    'url': webhook_url,
                    'event_type': event_type
                },
                timeout=30
            )

            if response.status_code == 200:
                try:
                    return Response(response.json())
                except ValueError as e:
                    return Response({
                        "error": "Resposta inválida da W-API",
                        "details": str(e),
                        "response_text": response.text[:200]
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({
                    "error": f"Erro na W-API: {response.status_code}",
                    "response_text": response.text[:200]
                }, status=response.status_code)

        except Exception as e:
            return Response({
                "error": f"Erro interno: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='auth/disconnect')
    def disconnect_instance(self, request):
        return self._disconnect_instance(request)

    @action(detail=False, methods=['post'], url_path='auth/disconnect/')
    def disconnect_instance_slash(self, request):
        return self._disconnect_instance(request)

    def _disconnect_instance(self, request):
        """
        Desconecta uma instância na W-API oficial
        Parâmetros:
        - instanceId (query param): ID da instância
        Headers:
        - Authorization: Bearer <token> (buscado do banco)
        """
        try:
            instance_id = request.query_params.get('instanceId')
            if not instance_id:
                return Response({
                    "error": "instanceId é obrigatório"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Buscar token da instância
            try:
                instance = WhatsappInstance.objects.get(instance_id=instance_id)
                token = instance.token
            except WhatsappInstance.DoesNotExist:
                return Response({
                    "error": "Instância não encontrada"
                }, status=status.HTTP_404_NOT_FOUND)

            # Fazer requisição para W-API oficial
            import requests
            response = requests.get(
                f"{self.wapi_base_url}/v1/instance/disconnect",
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                },
                params={'instanceId': instance_id},
                timeout=30
            )

            logger.info(f"Disconnect response: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            logger.info(f"Response text: {response.text[:500]}")

            if response.status_code == 200:
                try:
                    # Atualizar status da instância para desconectado
                    instance.status = "desconectado"
                    instance.save()
                    return Response(response.json())
                except ValueError as e:
                    logger.error(f"Erro ao fazer parse do JSON: {e}")
                    logger.error(f"Response text: {response.text}")
                    return Response({
                        "error": "Resposta inválida da W-API",
                        "details": str(e),
                        "response_text": response.text[:200]
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({
                    "error": f"Erro na W-API: {response.status_code}",
                    "response_text": response.text[:200]
                }, status=response.status_code)

        except Exception as e:
            logger.error(f"Erro ao desconectar instância: {str(e)}")
            return Response({
                "error": f"Erro interno: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class RelatorioView(View):
    """
    View para gerar relatórios com filtros por data e usuário
    """
    
    def get(self, request):
        try:
            # Parâmetros de filtro
            data_inicio = request.GET.get('data_inicio')
            data_fim = request.GET.get('data_fim')
            usuario_id = request.GET.get('usuario_id')
            cliente_id = request.GET.get('cliente_id')
            
            # Converter datas
            if data_inicio:
                data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            else:
                data_inicio = timezone.now().date() - timedelta(days=30)
                
            if data_fim:
                data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()
            else:
                data_fim = timezone.now().date()
            
            # Filtros base
            filtros = {}
            if cliente_id:
                filtros['cliente_id'] = cliente_id
            if usuario_id:
                filtros['atendente_id'] = usuario_id
            
            # 1. Quantidade de atendimentos no período
            atendimentos = Chat.objects.filter(
                data_inicio__date__range=[data_inicio, data_fim],
                **filtros
            ).count()
            
            # 2. Quantidade total de clientes no mês
            mes_atual = timezone.now().replace(day=1)
            clientes_mes = Cliente.objects.filter(
                data_cadastro__gte=mes_atual
            ).count()
            
            # 3. Quantidade de mensagens enviadas a mais (comparativo)
            # Mensagens enviadas no período atual
            mensagens_enviadas_periodo = Mensagem.objects.filter(
                data_envio__date__range=[data_inicio, data_fim],
                remetente__icontains='atendente',  # Assumindo que mensagens de atendentes contêm 'atendente'
                **filtros
            ).count()
            
            # Mensagens enviadas no período anterior (mesmo intervalo)
            periodo_anterior_inicio = data_inicio - timedelta(days=(data_fim - data_inicio).days)
            periodo_anterior_fim = data_inicio - timedelta(days=1)
            
            mensagens_enviadas_anterior = Mensagem.objects.filter(
                data_envio__date__range=[periodo_anterior_inicio, periodo_anterior_fim],
                remetente__icontains='atendente',
                **filtros
            ).count()
            
            mensagens_a_mais = mensagens_enviadas_periodo - mensagens_enviadas_anterior
            
            # 4. Quantidade total de mensagens no período
            total_mensagens = Mensagem.objects.filter(
                data_envio__date__range=[data_inicio, data_fim],
                **filtros
            ).count()
            
            # 5. Dados para gráficos
            # Mensagens por dia no período
            mensagens_por_dia = []
            current_date = data_inicio
            while current_date <= data_fim:
                count = Mensagem.objects.filter(
                    data_envio__date=current_date,
                    **filtros
                ).count()
                mensagens_por_dia.append({
                    'data': current_date.strftime('%Y-%m-%d'),
                    'quantidade': count
                })
                current_date += timedelta(days=1)
            
            # Atendimentos por status
            atendimentos_por_status = Chat.objects.filter(
                data_inicio__date__range=[data_inicio, data_fim],
                **filtros
            ).values('status').annotate(
                total=Count('id')
            )
            
            # Top 5 atendentes mais ativos
            top_atendentes = Chat.objects.filter(
                data_inicio__date__range=[data_inicio, data_fim],
                **filtros
            ).values('atendente__nome').annotate(
                total_atendimentos=Count('id')
            ).order_by('-total_atendimentos')[:5]
            
            # Tipos de mensagem
            tipos_mensagem = Mensagem.objects.filter(
                data_envio__date__range=[data_inicio, data_fim],
                **filtros
            ).values('tipo').annotate(
                total=Count('id')
            )
            
            # 6. Métricas adicionais
            # Tempo médio de atendimento
            chats_finalizados = Chat.objects.filter(
                data_inicio__date__range=[data_inicio, data_fim],
                data_fim__isnull=False,
                **filtros
            )
            
            tempo_medio_atendimento = 0
            if chats_finalizados.exists():
                total_tempo = sum([
                    (chat.data_fim - chat.data_inicio).total_seconds() / 60  # em minutos
                    for chat in chats_finalizados
                ])
                tempo_medio_atendimento = total_tempo / chats_finalizados.count()
            
            # Taxa de satisfação (assumindo que mensagens com emoji positivo indicam satisfação)
            mensagens_satisfacao = Mensagem.objects.filter(
                data_envio__date__range=[data_inicio, data_fim],
                conteudo__icontains='👍',
                **filtros
            ).count()
            
            taxa_satisfacao = 0
            if total_mensagens > 0:
                taxa_satisfacao = (mensagens_satisfacao / total_mensagens) * 100
            
            relatorio = {
                'periodo': {
                    'inicio': data_inicio.strftime('%Y-%m-%d'),
                    'fim': data_fim.strftime('%Y-%m-%d')
                },
                'metricas': {
                    'atendimentos_periodo': atendimentos,
                    'clientes_mes': clientes_mes,
                    'mensagens_enviadas_a_mais': mensagens_a_mais,
                    'total_mensagens': total_mensagens,
                    'tempo_medio_atendimento': round(tempo_medio_atendimento, 2),
                    'taxa_satisfacao': round(taxa_satisfacao, 2)
                },
                'graficos': {
                    'mensagens_por_dia': mensagens_por_dia,
                    'atendimentos_por_status': list(atendimentos_por_status),
                    'top_atendentes': list(top_atendentes),
                    'tipos_mensagem': list(tipos_mensagem)
                }
            }
            
            return JsonResponse({
                'success': True,
                'data': relatorio
            })
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Erro ao gerar relatório',
                'details': str(e)
            }, status=500)


@api_view(["POST"])
def recuperar_status_whatsapp(request):
    """
    Endpoint de recuperação: atualiza e retorna o status WhatsApp de todos os clientes.
    """
    from core.models import Cliente
    clientes = Cliente.objects.all()
    serializer = ClienteSerializer(clientes, many=True)
    return Response(serializer.data)


class WebhookMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet para listar mensagens completas do WhatsApp (com mídia, status, etc) vindas do modelo webhook.Message.
    """
    queryset = Message.objects.all()
    serializer_class = WebhookMessageSerializer
    permission_classes = [IsAtendenteOrAdmin]

    def get_queryset(self):
        queryset = Message.objects.all()
        chat_id = self.request.query_params.get('chat_id')
        if chat_id:
            queryset = queryset.filter(chat__chat_id=chat_id)
        return queryset.order_by('timestamp')


@api_view(['GET'])
@permission_classes([AllowAny])
def test_chats_public(request):
    """
    Endpoint público para testar a API de chats
    """
    try:
        from core.models import Chat
        from .serializers import ChatSerializer
        
        # Buscar alguns chats para teste
        chats = Chat.objects.all()[:5]
        serializer = ChatSerializer(chats, many=True)
        
        return Response({
            'status': 'success',
            'message': 'API funcionando corretamente',
            'total_chats': chats.count(),
            'chats': serializer.data
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

