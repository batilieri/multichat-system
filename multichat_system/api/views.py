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
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ClienteSerializer
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes

from core.models import Cliente, Departamento, Chat, Mensagem, WebhookEvent, WhatsappInstance, MediaFile
from authentication.models import Usuario
from authentication.serializers import UsuarioRegistroSerializer, UsuarioPerfilSerializer
from .serializers import (
    ClienteSerializer, DepartamentoSerializer, ChatSerializer,
    MensagemSerializer, WebhookEventSerializer, WhatsappInstanceSerializer,
    MediaFileSerializer
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
import sys
import os
from django.http import FileResponse, Http404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
import os
from pathlib import Path
import re

# Adicionar o caminho para o módulo wapi
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'wapi'))

logger = logging.getLogger(__name__)

# Classe EnviarImagem integrada para evitar problemas de importação
class EnviarImagem:
    def __init__(self, instance_id, token):
        self.instance_id = instance_id
        self.token = token
        self.base_url = "https://api.w-api.app/v1/message/send-image"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def enviar_imagem_url(self, phone, image_url, caption="", message_id=None, delay=0):
        params = {"instanceId": self.instance_id}
        payload = {"phone": phone, "image": image_url}
        
        if caption:
            payload["caption"] = caption
        if message_id:
            payload["messageId"] = message_id
        if delay > 0:
            payload["delayMessage"] = delay

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                params=params,
                data=json.dumps(payload)
            )

            return {
                "sucesso": response.status_code == 200,
                "status_code": response.status_code,
                "dados": response.json() if response.status_code == 200 else None,
                "erro": response.text if response.status_code != 200 else None
            }
        except Exception as e:
            return {
                "sucesso": False,
                "status_code": None,
                "dados": None,
                "erro": f"Erro na requisição: {str(e)}"
            }

    def enviar_imagem_base64(self, phone, image_base64, caption="", message_id=None, delay=0):
        params = {"instanceId": self.instance_id}
        payload = {"phone": phone, "image": image_base64}
        
        if caption:
            payload["caption"] = caption
        if message_id:
            payload["messageId"] = message_id
        if delay > 0:
            payload["delayMessage"] = delay

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                params=params,
                data=json.dumps(payload)
            )

            return {
                "sucesso": response.status_code == 200,
                "status_code": response.status_code,
                "dados": response.json() if response.status_code == 200 else None,
                "erro": response.text if response.status_code != 200 else None
            }
        except Exception as e:
            return {
                "sucesso": False,
                "status_code": None,
                "dados": None,
                "erro": f"Erro na requisição: {str(e)}"
            }

    def enviar_imagem_simples(self, phone, image_data, caption="", message_id=None, delay=0):
        """
        Versão simplificada que detecta automaticamente se é URL ou Base64
        """
        # Detectar se é URL ou Base64
        if image_data.startswith(('http://', 'https://')):
            return self.enviar_imagem_url(phone, image_data, caption, message_id, delay)
        else:
            return self.enviar_imagem_base64(phone, image_data, caption, message_id, delay)


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
        Endpoint para verificar atualizações em tempo real
        Busca diretamente do banco de dados para garantir precisão
        """
        from django.core.cache import cache
        from django.db.models import Q

        try:
            last_check = request.GET.get('last_check')
            if last_check:
                try:
                    if ' ' in last_check and '+00:00' in last_check:
                        last_check = last_check.replace(' +00:00', '+00:00')
                    elif ' ' in last_check:
                        last_check = last_check.replace(' ', '+')

                    last_check = timezone.datetime.fromisoformat(last_check.replace('Z', '+00:00'))
                except ValueError as e:
                    print(f"Erro ao parsear timestamp: {last_check}, erro: {e}")
                    last_check = timezone.now() - timezone.timedelta(minutes=5)
            else:
                last_check = timezone.now() - timezone.timedelta(minutes=5)

            user = request.user
            current_time = timezone.now()
            new_updates = []

            # Buscar chats do usuário
            base_queryset = Chat.objects.select_related('cliente', 'atendente')

            if user.is_superuser or (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin'):
                chats = base_queryset.all()
            elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'cliente' and hasattr(user, 'cliente') and user.cliente:
                chats = base_queryset.filter(cliente=user.cliente)
            elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador' and hasattr(user, 'cliente') and user.cliente:
                chats = base_queryset.filter(cliente=user.cliente)
            else:
                chats = Chat.objects.none()

            # Buscar novas mensagens diretamente do banco
            novas_mensagens = Mensagem.objects.filter(
                chat__in=chats,
                data_envio__gt=last_check
            ).select_related('chat').order_by('data_envio')

            # Buscar chats atualizados
            chats_atualizados = chats.filter(
                Q(last_message_at__gt=last_check) | 
                Q(data_inicio__gt=last_check)
            )

            # Criar atualizações para novas mensagens
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
                        'status': 'read' if msg.lida else 'sent',
                        'message_id': msg.message_id
                    },
                    'chat_update': {
                        'chat_id': msg.chat.chat_id,
                        'last_message_at': msg.data_envio.isoformat(),
                        'message_count': msg.chat.mensagens.count(),
                        'chat_name': msg.chat.chat_name or msg.chat.chat_id,
                        'sender_name': msg.remetente
                    }
                })

            # Criar atualizações para chats modificados
            for chat in chats_atualizados:
                # Verificar se já não foi incluído por uma nova mensagem
                if not any(update.get('chat_id') == chat.chat_id for update in new_updates):
                    new_updates.append({
                        'type': 'chat_updated',
                        'chat_id': chat.chat_id,
                        'last_message_at': chat.last_message_at.isoformat() if chat.last_message_at else None,
                        'message_count': chat.mensagens.count(),
                        'chat_name': chat.chat_name or chat.chat_id
                    })

            # Verificar cache para atualizações em tempo real (backup)
            cache_updates = cache.get("realtime_updates", [])
            for update in cache_updates:
                try:
                    update_timestamp = update.get('timestamp')
                    if update_timestamp:
                        if ' ' in update_timestamp and '+00:00' in update_timestamp:
                            update_timestamp = update_timestamp.replace(' +00:00', '+00:00')
                        elif ' ' in update_timestamp:
                            update_timestamp = update_timestamp.replace(' ', '+')

                        update_time = timezone.datetime.fromisoformat(update_timestamp.replace('Z', '+00:00'))
                        if update_time > last_check:
                            # Adicionar apenas se não estiver já na lista
                            if not any(existing.get('chat_id') == update.get('chat_id') for existing in new_updates):
                                new_updates.append(update)
                except (ValueError, TypeError) as e:
                    print(f"Erro ao processar update do cache: {update.get('timestamp')}, erro: {e}")
                    continue

            return Response({
                'timestamp': current_time.isoformat(),
                'updates': new_updates,
                'has_updates': len(new_updates) > 0,
                'total_updates': len(new_updates)
            })

        except Exception as e:
            logger.error(f"❌ Erro no endpoint check_updates: {e}")
            return Response({
                'error': str(e)
            }, status=500)


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
        after = request.query_params.get('after')  # Novo parâmetro para buscar mensagens após uma data
        
        if chat_id:
            queryset = queryset.filter(chat__chat_id=chat_id)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if lida is not None:
            queryset = queryset.filter(lida=lida.lower() == 'true')
        
        # Filtrar mensagens após uma data específica (para atualizações incrementais)
        if after:
            try:
                from datetime import datetime
                import pytz
                
                # Converter a string ISO para datetime
                if 'T' in after and 'Z' in after:
                    # Formato ISO com Z
                    after_dt = datetime.fromisoformat(after.replace('Z', '+00:00'))
                elif 'T' in after:
                    # Formato ISO sem Z
                    after_dt = datetime.fromisoformat(after)
                else:
                    # Formato simples
                    after_dt = datetime.fromisoformat(after)
                
                # Filtrar mensagens mais recentes que a data especificada
                queryset = queryset.filter(data_envio__gt=after_dt)
                logger.info(f'🔍 Filtrando mensagens após {after_dt} para chat {chat_id}')
            except Exception as e:
                logger.warning(f'⚠️ Erro ao processar parâmetro after={after}: {e}')
        
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
            # Log detalhado para debug
            pk = kwargs.get("pk")
            logger.info(f'🔍 Tentando excluir mensagem com ID: {pk}')
            
            # Verificar se a mensagem existe
            try:
                mensagem = self.get_object()
                logger.info(f'✅ Mensagem encontrada: ID={mensagem.id}, message_id={mensagem.message_id}, from_me={mensagem.from_me}')
            except Mensagem.DoesNotExist:
                logger.error(f'❌ Mensagem não encontrada: ID={pk}')
                return Response({
                    'error': 'Mensagem não encontrada',
                    'details': f'Mensagem com ID {pk} não existe no banco de dados'
                }, status=status.HTTP_404_NOT_FOUND)
            
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
            logger.info(f'🔄 Excluindo da W-API: phone_number={mensagem.chat.chat_id}, message_id={mensagem.message_id}')
            resultado_wapi = deletador.deletar(
                phone_number=mensagem.chat.chat_id,
                message_ids=mensagem.message_id
            )
            
            logger.info(f'📡 Resultado W-API: {resultado_wapi}')
            
            # Sempre excluir do banco local, independente do resultado da W-API
            mensagem.delete()
            
            if resultado_wapi.get('success'):
                logger.info(f'✅ Mensagem {mensagem.message_id} excluída com sucesso da W-API e do banco')
                
                return Response({
                    'success': True,
                    'message': 'Mensagem excluída com sucesso',
                    'wapi_result': resultado_wapi
                }, status=status.HTTP_200_OK)
            else:
                # Se falhou na W-API, mas excluiu do banco local
                logger.warning(f'⚠️ Mensagem {mensagem.message_id} excluída do banco, mas falhou na W-API: {resultado_wapi}')
                
                return Response({
                    'success': True,
                    'message': 'Mensagem excluída localmente (erro na W-API)',
                    'wapi_result': resultado_wapi,
                    'warning': 'A mensagem foi removida localmente, mas pode não ter sido excluída do WhatsApp'
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f'❌ Erro ao excluir mensagem: {e}')
            return Response({
                'error': 'Erro interno do servidor'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='editar')
    def editar_mensagem(self, request, pk=None):
        """
        Edita uma mensagem no WhatsApp e no banco de dados.
        
        Requisitos:
        - Mensagem deve existir no banco
        - Mensagem deve ter message_id (ID do WhatsApp)
        - Mensagem deve ser from_me=True (enviada pelo usuário)
        - Mensagem deve ser do tipo texto
        - Usuário deve ter permissão para editar mensagens do cliente
        """
        try:
            # Log detalhado para debug
            logger.info(f'✏️ Tentando editar mensagem com ID: {pk}')
            
            # Verificar se a mensagem existe
            try:
                mensagem = self.get_object()
                logger.info(f'✅ Mensagem encontrada: ID={mensagem.id}, message_id={mensagem.message_id}, from_me={mensagem.from_me}, tipo={mensagem.tipo}')
            except Mensagem.DoesNotExist:
                logger.error(f'❌ Mensagem não encontrada: ID={pk}')
                return Response({
                    'error': 'Mensagem não encontrada',
                    'details': f'Mensagem com ID {pk} não existe no banco de dados'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Verificar se a mensagem tem message_id (ID do WhatsApp)
            if not mensagem.message_id:
                logger.warning(f'⚠️ Mensagem {mensagem.id} não tem message_id')
                return Response({
                    'error': 'Esta mensagem não pode ser editada',
                    'details': 'A mensagem não possui ID do WhatsApp necessário para edição'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar se é uma mensagem enviada pelo usuário (from_me=True)
            if not mensagem.from_me:
                logger.warning(f'⚠️ Tentativa de editar mensagem não enviada pelo usuário: ID={mensagem.id}')
                return Response({
                    'error': 'Apenas mensagens enviadas por você podem ser editadas',
                    'details': 'Esta mensagem foi recebida, não enviada'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar se é uma mensagem de texto
            if mensagem.tipo not in ['texto', 'text']:
                logger.warning(f'⚠️ Tentativa de editar mensagem não-texto: tipo={mensagem.tipo}')
                return Response({
                    'error': 'Apenas mensagens de texto podem ser editadas',
                    'details': f'Tipo de mensagem atual: {mensagem.tipo}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obter o novo texto da requisição
            novo_texto = request.data.get('novo_texto')
            if not novo_texto or not novo_texto.strip():
                return Response({
                    'error': 'Novo texto é obrigatório',
                    'details': 'O campo novo_texto não pode estar vazio'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            novo_texto = novo_texto.strip()
            
            # Validar tamanho do texto (limite do WhatsApp)
            if len(novo_texto) > 4096:
                return Response({
                    'error': 'Texto muito longo',
                    'details': f'O texto tem {len(novo_texto)} caracteres, máximo permitido: 4096'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar se o texto realmente mudou
            if novo_texto == mensagem.conteudo:
                return Response({
                    'error': 'Texto não foi alterado',
                    'details': 'O novo texto é idêntico ao texto atual'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar permissões do usuário
            user = request.user
            if not (user.is_superuser or 
                    (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin') or
                    (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'cliente' and mensagem.chat.cliente == user.cliente) or
                    (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador' and mensagem.chat.cliente == user.cliente)):
                logger.warning(f'⚠️ Usuário {user.username} tentou editar mensagem sem permissão')
                return Response({
                    'error': 'Você não tem permissão para editar esta mensagem',
                    'details': 'Apenas o proprietário do chat ou administradores podem editar mensagens'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Buscar a instância WhatsApp do cliente
            try:
                instancia = WhatsappInstance.objects.get(cliente=mensagem.chat.cliente)
                logger.info(f'✅ Instância encontrada: {instancia.instance_id}')
            except WhatsappInstance.DoesNotExist:
                logger.error(f'❌ Instância WhatsApp não encontrada para cliente: {mensagem.chat.cliente}')
                return Response({
                    'error': 'Instância WhatsApp não encontrada',
                    'details': 'Este cliente não possui uma instância WhatsApp configurada'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Importar e usar a classe EditarMensagem
            import sys
            import os
            # Adicionar o diretório wapi ao path
            wapi_path = os.path.join(os.path.dirname(__file__), '..', '..', 'wapi')
            if wapi_path not in sys.path:
                sys.path.append(wapi_path)
            
            try:
                from mensagem.editar.editarMensagens import EditarMensagem
            except ImportError as e:
                logger.error(f'❌ Erro ao importar EditarMensagem: {e}')
                return Response({
                    'error': 'Erro interno: módulo de edição não encontrado',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Criar instância do editor
            editor = EditarMensagem(instancia.instance_id, instancia.token)
            
            # Editar na W-API
            logger.info(f'🔄 Editando na W-API: phone_number={mensagem.chat.chat_id}, message_id={mensagem.message_id}, novo_texto={novo_texto[:50]}...')
            resultado_wapi = editor.editar_mensagem(
                phone=mensagem.chat.chat_id,
                message_id=mensagem.message_id,
                new_text=novo_texto
            )
            
            logger.info(f'📡 Resultado W-API: {resultado_wapi}')
            
            # Verificar se a edição foi bem-sucedida na W-API
            if "erro" not in resultado_wapi:
                # Atualizar o conteúdo no banco local
                mensagem.conteudo = novo_texto
                mensagem.save()
                
                logger.info(f'✅ Mensagem {mensagem.message_id} editada com sucesso na W-API e no banco')
                
                return Response({
                    'success': True,
                    'message': 'Mensagem editada com sucesso',
                    'wapi_result': resultado_wapi,
                    'novo_texto': novo_texto,
                    'message_id': mensagem.message_id,
                    'chat_id': mensagem.chat.chat_id
                }, status=status.HTTP_200_OK)
            else:
                # Se falhou na W-API, retornar erro
                logger.error(f'❌ Erro ao editar mensagem na W-API: {resultado_wapi}')
                
                return Response({
                    'error': 'Erro ao editar mensagem no WhatsApp',
                    'details': resultado_wapi.get('erro', 'Erro desconhecido na W-API'),
                    'wapi_result': resultado_wapi
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f'❌ Erro ao editar mensagem: {e}')
            return Response({
                'error': 'Erro interno do servidor',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='reagir')
    def reagir_mensagem(self, request, pk=None):
        """
        Adiciona ou remove uma reação de uma mensagem e envia para o WhatsApp real
        """
        try:
            mensagem = self.get_object()
            
            # Validar dados da requisição
            emoji = request.data.get('emoji')
            if not emoji:
                return Response(
                    {'erro': 'Emoji é obrigatório'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obter reações atuais
            reacoes = mensagem.reacoes or []
            
            # Verificar se já existe uma reação
            if reacoes and emoji in reacoes:
                # Se já tem essa reação, remover
                reacoes = []
                action = 'removida'
            else:
                # Se não tem reação ou tem outra, substituir
                reacoes = [emoji]
                action = 'adicionada' if not reacoes else 'substituída'
            
            # Salvar no banco
            mensagem.reacoes = reacoes
            mensagem.save()
            
            # Tentar enviar reação para o WhatsApp real
            wapi_result = None
            try:
                # Buscar instância e token
                from core.utils import get_whatsapp_instance_by_message
                instance = get_whatsapp_instance_by_message(mensagem, prefer_connected=True)
                
                if instance and instance.token and mensagem.message_id:
                    # Importar e usar a classe de reação
                    from mensagem.reacao.enviarReacao import EnviarReacao
                    
                    reacao_wapi = EnviarReacao(instance.instance_id, instance.token)
                    
                    # Extrair número do telefone do chat_id
                    phone = mensagem.chat.chat_id.split('@')[0] if '@' in mensagem.chat.chat_id else mensagem.chat.chat_id
                    
                    # Enviar reação para o WhatsApp
                    wapi_result = reacao_wapi.enviar_reacao(
                        phone=phone,
                        message_id=mensagem.message_id,
                        reaction=emoji,
                        delay=1
                    )
                    
                    if wapi_result['sucesso']:
                        logger.info(f'Reação enviada para WhatsApp: emoji={emoji}, mensagem_id={mensagem.message_id}')
                    else:
                        logger.warning(f'Falha ao enviar reação para WhatsApp: {wapi_result["erro"]}')
                        
            except Exception as e:
                logger.error(f'Erro ao enviar reação para WhatsApp: {str(e)}')
                # Não falhar a operação se o envio para WhatsApp falhar
            
            logger.info(f'Reação {action}: emoji={emoji}, mensagem_id={mensagem.id}')
            
            return Response({
                'sucesso': True,
                'acao': action,
                'emoji': emoji,
                'reacoes': reacoes,
                'wapi_enviado': wapi_result['sucesso'] if wapi_result else False,
                'mensagem': f'Reação {action} com sucesso'
            })
            
        except Mensagem.DoesNotExist:
            return Response(
                {'erro': 'Mensagem não encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f'Erro ao gerenciar reação: {str(e)}')
            return Response(
                {'erro': f'Erro interno: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='remover-reacao')
    def remover_reacao(self, request, pk=None):
        """
        Remove a reação de uma mensagem e envia para o WhatsApp real
        """
        try:
            mensagem = self.get_object()
            
            # Obter reações atuais
            reacoes = mensagem.reacoes or []
            
            if not reacoes:
                return Response(
                    {'erro': 'Mensagem não possui reações para remover'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Remover reação
            emoji_removido = reacoes[0]  # Pega o primeiro emoji (único)
            reacoes = []
            
            # Salvar no banco
            mensagem.reacoes = reacoes
            mensagem.save()
            
            # Tentar remover reação do WhatsApp real
            wapi_result = None
            try:
                # Buscar instância e token
                from core.utils import get_whatsapp_instance_by_message
                instance = get_whatsapp_instance_by_message(mensagem, prefer_connected=True)
                
                if instance and instance.token and mensagem.message_id:
                    # Importar e usar a classe de reação
                    from mensagem.reacao.enviarReacao import EnviarReacao
                    
                    reacao_wapi = EnviarReacao(instance.instance_id, instance.token)
                    
                    # Extrair número do telefone do chat_id
                    phone = mensagem.chat.chat_id.split('@')[0] if '@' in mensagem.chat.chat_id else mensagem.chat.chat_id
                    
                    # Remover reação do WhatsApp usando endpoint específico
                    wapi_result = reacao_wapi.remover_reacao(
                        phone=phone,
                        message_id=mensagem.message_id,
                        delay=1
                    )
                    
                    if wapi_result['sucesso']:
                        logger.info(f'Reação removida do WhatsApp: emoji={emoji_removido}, mensagem_id={mensagem.message_id}')
                    else:
                        logger.warning(f'Falha ao remover reação do WhatsApp: {wapi_result["erro"]}')
                        
            except Exception as e:
                logger.error(f'Erro ao remover reação do WhatsApp: {str(e)}')
                # Não falhar a operação se o envio para WhatsApp falhar
            
            logger.info(f'Reação removida: emoji={emoji_removido}, mensagem_id={mensagem.id}')
            
            return Response({
                'sucesso': True,
                'acao': 'removida',
                'emoji_removido': emoji_removido,
                'reacoes': reacoes,
                'wapi_enviado': wapi_result['sucesso'] if wapi_result else False,
                'mensagem': f'Reação removida com sucesso'
            })
            
        except Mensagem.DoesNotExist:
            return Response(
                {'erro': 'Mensagem não encontrada'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f'Erro ao remover reação: {str(e)}')
            return Response(
                {'erro': f'Erro interno: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='enviar-imagem')
    def enviar_imagem(self, request, pk=None):
        """
        Envia uma imagem para o WhatsApp
        """
        try:
            chat = self.get_object()
            
            # Validar dados da requisição
            image_data = request.data.get('image_data')
            image_type = request.data.get('image_type')  # 'url' ou 'base64'
            caption = request.data.get('caption', '')
            message_id = request.data.get('message_id')
            
            if not image_data:
                return Response(
                    {'erro': 'Dados da imagem são obrigatórios'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Buscar instância e token
            from core.utils import get_whatsapp_instance_by_chat
            instance = get_whatsapp_instance_by_chat(chat, prefer_connected=True)
            
            if not instance or not instance.token:
                return Response(
                    {'erro': 'Instância do WhatsApp não encontrada'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Usar a classe EnviarImagem definida no topo do arquivo
            imagem_wapi = EnviarImagem(instance.instance_id, instance.token)
            
            # Extrair número do telefone do chat_id
            phone = chat.chat_id.split('@')[0] if '@' in chat.chat_id else chat.chat_id
            
            # Enviar imagem para o WhatsApp
            if image_type == 'url':
                wapi_result = imagem_wapi.enviar_imagem_url(
                    phone=phone,
                    image_url=image_data,
                    caption=caption,
                    message_id=message_id,
                    delay=1
                )
            else:  # base64
                wapi_result = imagem_wapi.enviar_imagem_base64(
                    phone=phone,
                    image_base64=image_data,
                    caption=caption,
                    message_id=message_id,
                    delay=1
                )
            
            if wapi_result['sucesso']:
                logger.info(f'Imagem enviada para WhatsApp: chat_id={chat.chat_id}')
                return Response({
                    'sucesso': True,
                    'mensagem': 'Imagem enviada com sucesso',
                    'dados': wapi_result['dados']
                })
            else:
                logger.warning(f'Falha ao enviar imagem para WhatsApp: {wapi_result["erro"]}')
                return Response({
                    'sucesso': False,
                    'erro': wapi_result['erro']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f'Erro ao enviar imagem: {str(e)}')
            return Response(
                {'erro': f'Erro interno: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='enviar-imagem')
    def enviar_imagem_mensagem(self, request):
        """
        Envia uma imagem para o WhatsApp (endpoint alternativo)
        """
        try:
            # Obter chat_id da requisição
            chat_id = request.data.get('chat_id')
            if not chat_id:
                return Response(
                    {'erro': 'chat_id é obrigatório'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Buscar o chat
            try:
                chat = Chat.objects.get(id=chat_id)
            except Chat.DoesNotExist:
                return Response(
                    {'error': True, 'message': 'Chat não encontrado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Log para debug - verificar dados recebidos
            logger.info(f'=== DEBUG ENVIO IMAGEM ===')
            logger.info(f'Headers: {dict(request.headers)}')
            logger.info(f'Dados recebidos: {request.data}')
            logger.info(f'User: {request.user}')
            logger.info(f'Auth: {request.auth}')
            
            # Validar dados da requisição
            image_data = request.data.get('image_data')
            image_type = request.data.get('image_type', 'base64')  # 'url' ou 'base64'
            caption = request.data.get('caption', '')
            message_id = request.data.get('message_id')
            
            logger.info(f'image_data: {image_data[:50] if image_data else "None"}...')
            logger.info(f'image_data length: {len(image_data) if image_data else 0}')
            logger.info(f'image_type: {image_type}')
            logger.info(f'caption: {caption}')
            logger.info(f'chat_id: {request.data.get("chat_id")}')
            
            if not image_data:
                return Response(
                    {'error': True, 'message': 'Dados da imagem são obrigatórios'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar formato da imagem
            if image_type not in ['url', 'base64']:
                logger.error(f'image_type inválido: {image_type}')
                return Response(
                    {'error': True, 'message': 'Formato de imagem inválido. Forneça uma imagem em base64 ou URL.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Buscar instância e token
            from core.utils import get_whatsapp_instance_by_chat
            instance = get_whatsapp_instance_by_chat(chat, prefer_connected=True)
            
            if not instance or not instance.token:
                return Response(
                    {'erro': 'Instância do WhatsApp não encontrada'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Usar a classe EnviarImagem definida no topo do arquivo
            imagem_wapi = EnviarImagem(instance.instance_id, instance.token)
            
            # Extrair número do telefone do chat_id
            phone = chat.chat_id.split('@')[0] if '@' in chat.chat_id else chat.chat_id
            
            # Enviar imagem para o WhatsApp
            if image_type == 'url':
                wapi_result = imagem_wapi.enviar_imagem_url(
                    phone=phone,
                    image_url=image_data,
                    caption=caption,
                    message_id=message_id,
                    delay=1
                )
            else:  # base64
                wapi_result = imagem_wapi.enviar_imagem_base64(
                    phone=phone,
                    image_base64=image_data,
                    caption=caption,
                    message_id=message_id,
                    delay=1
                )
            
            if wapi_result['sucesso']:
                logger.info(f'Imagem enviada para WhatsApp: chat_id={chat.chat_id}')
                return Response({
                    'sucesso': True,
                    'mensagem': 'Imagem enviada com sucesso',
                    'dados': wapi_result['dados']
                })
            else:
                logger.warning(f'Falha ao enviar imagem para WhatsApp: {wapi_result["erro"]}')
                return Response({
                    'sucesso': False,
                    'erro': wapi_result['erro']
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f'Erro ao enviar imagem: {str(e)}')
            return Response(
                {'erro': f'Erro interno: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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


@api_view(['GET'])
def serve_audio(request, audio_path):
    """
    Serve áudios processados
    """
    try:
        # Construir caminho completo do arquivo
        full_path = os.path.join(settings.MEDIA_ROOT, audio_path)
        
        # Verificar se o arquivo existe
        if not os.path.exists(full_path):
            raise Http404("Áudio não encontrado")
        
        # Verificar se é um arquivo de áudio
        if not full_path.lower().endswith(('.mp3', '.ogg', '.wav', '.m4a')):
            raise Http404("Arquivo não é um áudio válido")
        
        # Servir o arquivo
        response = FileResponse(open(full_path, 'rb'))
        response['Content-Type'] = 'audio/mpeg'
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(full_path)}"'
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Erro ao servir áudio: {e}")
        return Response({'error': 'Erro ao servir áudio'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def serve_audio_by_message(request, message_id):
    """
    Serve áudio processado pelo ID da mensagem - INTEGRADO COM /wapi/midias/
    """
    try:
        # Buscar mensagem de áudio
        mensagem = Mensagem.objects.get(id=message_id, tipo='audio')
        
        logger.info(f"Servindo áudio para mensagem {message_id}")
        
        # Tentar extrair caminho do áudio do conteúdo JSON
        audio_path = None
        
        if mensagem.conteudo:
            try:
                conteudo_json = json.loads(mensagem.conteudo)
                audio_message = conteudo_json.get('audioMessage', {})
                
                # Prioridade 1: localPath (arquivo já baixado)
                if audio_message.get('localPath') and os.path.exists(audio_message['localPath']):
                    full_path = audio_message['localPath']
                    logger.info(f"Usando localPath: {full_path}")
                
                # Prioridade 2: url relativa para /wapi/midias/
                elif audio_message.get('url') and audio_message['url'].startswith('/wapi/midias/'):
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # Voltar para raiz do projeto
                    full_path = os.path.join(project_root, audio_message['url'][1:])  # Remove '/' inicial
                    logger.info(f"Usando URL relativa: {full_path}")
                
                # Prioridade 3: procurar por nome do arquivo
                elif audio_message.get('fileName'):
                    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                    full_path = os.path.join(project_root, 'wapi', 'midias', 'audios', audio_message['fileName'])
                    logger.info(f"Procurando por fileName: {full_path}")
                
                else:
                    logger.warning(f"Nenhum caminho de áudio encontrado no JSON: {audio_message}")
                    
            except json.JSONDecodeError:
                logger.error(f"Erro ao decodificar JSON do conteúdo da mensagem {message_id}")
        
        # Fallback: procurar na pasta /wapi/midias/audios/
        if not audio_path or not os.path.exists(full_path):
            logger.info(f"Procurando áudio na pasta wapi/midias/audios/")
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            audios_dir = os.path.join(project_root, 'wapi', 'midias', 'audios')
            
            if os.path.exists(audios_dir):
                # Procurar arquivos de áudio na pasta
                for ext in ['*.mp3', '*.ogg', '*.m4a', '*.wav']:
                    import glob
                    arquivos = glob.glob(os.path.join(audios_dir, ext))
                    if arquivos:
                        # Usar o primeiro arquivo encontrado (pode ser melhorado)
                        full_path = arquivos[0]
                        logger.info(f"Usando primeiro áudio encontrado: {full_path}")
                        break
        
        # Verificar se o arquivo existe
        if not full_path or not os.path.exists(full_path):
            logger.error(f"Arquivo de áudio não encontrado para mensagem {message_id}")
            raise Http404("Arquivo de áudio não encontrado")
        
        # Servir o arquivo
        response = FileResponse(open(full_path, 'rb'))
        
        # Determinar Content-Type baseado na extensão
        if full_path.lower().endswith('.mp3'):
            response['Content-Type'] = 'audio/mpeg'
        elif full_path.lower().endswith('.ogg'):
            response['Content-Type'] = 'audio/ogg'
        elif full_path.lower().endswith('.m4a'):
            response['Content-Type'] = 'audio/mp4'
        elif full_path.lower().endswith('.wav'):
            response['Content-Type'] = 'audio/wav'
        else:
            response['Content-Type'] = 'audio/mpeg'
        
        response['Content-Disposition'] = f'inline; filename="audio_{message_id}.{os.path.splitext(full_path)[1][1:]}"'
        
        logger.info(f"OK - Servindo áudio da mensagem {message_id}: {full_path}")
        return response
        
    except Mensagem.DoesNotExist:
        logger.error(f"ERRO - Mensagem de áudio não encontrada: {message_id}")
        raise Http404("Mensagem de áudio não encontrada")
    except Exception as e:
        logger.error(f"ERRO - Erro ao servir áudio da mensagem {message_id}: {e}")
        return Response({'error': 'Erro ao servir áudio'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def serve_wapi_media(request, media_type, filename):
    """
    Serve mídias baixadas da pasta /wapi/midias/
    """
    try:
        # Validar tipo de mídia
        allowed_types = ['audios', 'imagens', 'videos', 'documentos', 'stickers']
        if media_type not in allowed_types:
            raise Http404("Tipo de mídia não suportado")
        
        # Mapear tipos de mídia para pastas
        media_type_mapping = {
            'audios': 'audio',
            'imagens': 'image',
            'videos': 'video',
            'documentos': 'document',
            'stickers': 'sticker'
        }
        
        # Construir caminho do arquivo - tentar múltiplas localizações
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Mapear tipo de mídia para pasta correta
        folder_name = media_type_mapping.get(media_type, media_type)
        
        # Tentar diferentes caminhos
        possible_paths = [
            # Caminho original wapi/midias/
            os.path.join(project_root, 'wapi', 'midias', media_type, filename),
            # Caminho migrado media_storage/ com mapeamento correto
            os.path.join(project_root, 'multichat_system', 'media_storage', 'cliente_2', 'instance_3B6XIW-ZTS923-GEAY6V', folder_name, filename),
            # Caminho alternativo
            os.path.join(project_root, 'media_storage', 'cliente_2', 'instance_3B6XIW-ZTS923-GEAY6V', folder_name, filename),
        ]
        
        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        # Verificar se o arquivo existe
        if not file_path:
            logger.error(f"Arquivo não encontrado em nenhum caminho: {filename}")
            logger.error(f"Caminhos tentados: {possible_paths}")
            raise Http404("Arquivo não encontrado")
        
        if not os.path.exists(file_path):
            logger.error(f"Arquivo não encontrado: {file_path}")
            raise Http404("Arquivo não encontrado")
        
        # Verificar se é um arquivo válido (não diretório)
        if not os.path.isfile(file_path):
            raise Http404("Caminho inválido")
        
        # Determinar Content-Type baseado na extensão e tipo
        content_type = 'application/octet-stream'  # Default
        
        file_ext = os.path.splitext(filename)[1].lower()
        
        if media_type == 'audios':
            if file_ext == '.mp3':
                content_type = 'audio/mpeg'
            elif file_ext == '.ogg':
                content_type = 'audio/ogg'
            elif file_ext == '.m4a':
                content_type = 'audio/mp4'
            elif file_ext == '.wav':
                content_type = 'audio/wav'
        elif media_type == 'imagens':
            if file_ext in ['.jpg', '.jpeg']:
                content_type = 'image/jpeg'
            elif file_ext == '.png':
                content_type = 'image/png'
            elif file_ext == '.gif':
                content_type = 'image/gif'
            elif file_ext == '.webp':
                content_type = 'image/webp'
        elif media_type == 'videos':
            if file_ext == '.mp4':
                content_type = 'video/mp4'
            elif file_ext == '.webm':
                content_type = 'video/webm'
            elif file_ext == '.avi':
                content_type = 'video/avi'
        
        # Servir o arquivo
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Type'] = content_type
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        logger.info(f"OK - Servindo mídia: {media_type}/{filename}")
        return response
        
    except Exception as e:
        logger.error(f"ERRO - Erro ao servir mídia {media_type}/{filename}: {e}")
        return Response({'error': 'Erro ao servir mídia'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def serve_whatsapp_media(request, cliente_id, instance_id, chat_id, media_type, filename):
    """
    Serve mídias da nova estrutura organizada por chat_id
    """
    import os
    import mimetypes
    from django.http import HttpResponse, Http404
    
    try:
        # Validar tipo de mídia
        allowed_types = ['audio', 'imagens', 'videos', 'documentos', 'stickers']
        if media_type not in allowed_types:
            raise Http404("Tipo de mídia não suportado")
        
        # Construir caminho do arquivo
        base_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),  # multichat_system/
            'media_storage',
            f'cliente_{cliente_id}',
            f'instance_{instance_id}',
            'chats',
            str(chat_id),
            media_type,
            filename
        )
        
        # Verificar se o arquivo existe
        if not os.path.exists(base_path):
            logger.error(f"Arquivo não encontrado: {base_path}")
            raise Http404("Arquivo não encontrado")
        
        # Determinar content-type baseado na extensão
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            content_type = 'application/octet-stream'
        
        # Ler e retornar o arquivo
        with open(base_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
        
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        logger.info(f"✅ Servindo mídia: cliente_{cliente_id}/instance_{instance_id}/chats/{chat_id}/{media_type}/{filename}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Erro ao servir mídia WhatsApp: {e}")
        return Response({'error': 'Erro ao servir mídia'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serve_audio_message(request, message_id):
    """
    Serve áudio processado de uma mensagem específica
    """
    try:
        from core.models import Mensagem
        
        # Buscar mensagem
        message = Mensagem.objects.get(id=message_id)
        
        # Verificar se é uma mensagem de áudio
        if message.tipo != 'audio':
            return Response({'error': 'Mensagem não é de áudio'}, status=400)
        
        # Tentar diferentes caminhos para o arquivo de áudio
        audio_paths = [
            f"media/audios/{message_id}.mp3",
            f"media/audios/{message_id}.ogg",
            f"media/audios/{message_id}.m4a",
            f"wapi/midias/audios/{message_id}.mp3",
            f"wapi/midias/audios/{message_id}.ogg",
            f"wapi/midias/audios/{message_id}.m4a"
        ]
        
        for audio_path in audio_paths:
            if os.path.exists(audio_path):
                with open(audio_path, 'rb') as audio_file:
                    response = HttpResponse(audio_file.read(), content_type='audio/mpeg')
                    response['Content-Disposition'] = f'attachment; filename="audio_{message_id}.mp3"'
                    return response
        
        return Response({'error': 'Arquivo de áudio não encontrado'}, status=404)
        
    except Mensagem.DoesNotExist:
        return Response({'error': 'Mensagem não encontrada'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serve_image_message(request, message_id):
    """
    Serve imagem processada de uma mensagem específica
    """
    try:
        from core.models import Mensagem
        
        # Buscar mensagem
        message = Mensagem.objects.get(id=message_id)
        
        # Verificar se é uma mensagem de imagem
        if message.tipo != 'imagem':
            return Response({'error': 'Mensagem não é de imagem'}, status=400)
        
        # Tentar diferentes caminhos para o arquivo de imagem
        image_paths = [
            f"media/images/{message_id}.jpg",
            f"media/images/{message_id}.png",
            f"media/images/{message_id}.jpeg",
            f"wapi/midias/images/{message_id}.jpg",
            f"wapi/midias/images/{message_id}.png",
            f"wapi/midias/images/{message_id}.jpeg"
        ]
        
        for image_path in image_paths:
            if os.path.exists(image_path):
                with open(image_path, 'rb') as image_file:
                    response = HttpResponse(image_file.read(), content_type='image/jpeg')
                    response['Content-Disposition'] = f'attachment; filename="image_{message_id}.jpg"'
                    return response
        
        return Response({'error': 'Arquivo de imagem não encontrado'}, status=404)
        
    except Mensagem.DoesNotExist:
        return Response({'error': 'Mensagem não encontrada'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serve_video_message(request, message_id):
    """
    Serve vídeo processado de uma mensagem específica
    """
    try:
        from core.models import Mensagem
        
        # Buscar mensagem
        message = Mensagem.objects.get(id=message_id)
        
        # Verificar se é uma mensagem de vídeo
        if message.tipo != 'video':
            return Response({'error': 'Mensagem não é de vídeo'}, status=400)
        
        # Tentar diferentes caminhos para o arquivo de vídeo
        video_paths = [
            f"media/videos/{message_id}.mp4",
            f"media/videos/{message_id}.avi",
            f"media/videos/{message_id}.mov",
            f"wapi/midias/videos/{message_id}.mp4",
            f"wapi/midias/videos/{message_id}.avi",
            f"wapi/midias/videos/{message_id}.mov"
        ]
        
        for video_path in video_paths:
            if os.path.exists(video_path):
                with open(video_path, 'rb') as video_file:
                    response = HttpResponse(video_file.read(), content_type='video/mp4')
                    response['Content-Disposition'] = f'attachment; filename="video_{message_id}.mp4"'
                    return response
        
        return Response({'error': 'Arquivo de vídeo não encontrado'}, status=404)
        
    except Mensagem.DoesNotExist:
        return Response({'error': 'Mensagem não encontrada'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serve_sticker_message(request, message_id):
    """
    Serve sticker processado de uma mensagem específica
    """
    try:
        from core.models import Mensagem
        
        # Buscar mensagem
        message = Mensagem.objects.get(id=message_id)
        
        # Verificar se é uma mensagem de sticker
        if message.tipo != 'sticker':
            return Response({'error': 'Mensagem não é de sticker'}, status=400)
        
        # Tentar diferentes caminhos para o arquivo de sticker
        sticker_paths = [
            f"media/stickers/{message_id}.webp",
            f"media/stickers/{message_id}.png",
            f"media/stickers/{message_id}.gif",
            f"wapi/midias/stickers/{message_id}.webp",
            f"wapi/midias/stickers/{message_id}.png",
            f"wapi/midias/stickers/{message_id}.gif"
        ]
        
        for sticker_path in sticker_paths:
            if os.path.exists(sticker_path):
                with open(sticker_path, 'rb') as sticker_file:
                    response = HttpResponse(sticker_file.read(), content_type='image/webp')
                    response['Content-Disposition'] = f'attachment; filename="sticker_{message_id}.webp"'
                    return response
        
        return Response({'error': 'Arquivo de sticker não encontrado'}, status=404)
        
    except Mensagem.DoesNotExist:
        return Response({'error': 'Mensagem não encontrada'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serve_document_message(request, message_id):
    """
    Serve documento processado de uma mensagem específica
    """
    try:
        from core.models import Mensagem
        
        # Buscar mensagem
        message = Mensagem.objects.get(id=message_id)
        
        # Verificar se é uma mensagem de documento
        if message.tipo != 'documento':
            return Response({'error': 'Mensagem não é de documento'}, status=400)
        
        # Tentar diferentes caminhos para o arquivo de documento
        document_paths = [
            f"media/documents/{message_id}.pdf",
            f"media/documents/{message_id}.doc",
            f"media/documents/{message_id}.docx",
            f"wapi/midias/documents/{message_id}.pdf",
            f"wapi/midias/documents/{message_id}.doc",
            f"wapi/midias/documents/{message_id}.docx"
        ]
        
        for document_path in document_paths:
            if os.path.exists(document_path):
                with open(document_path, 'rb') as document_file:
                    response = HttpResponse(document_file.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="document_{message_id}.pdf"'
                    return response
        
        return Response({'error': 'Arquivo de documento não encontrado'}, status=404)
        
    except Mensagem.DoesNotExist:
        return Response({'error': 'Mensagem não encontrada'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


class MediaFileViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar arquivos de mídia.
    
    Permite visualizar e gerenciar arquivos de mídia baixados do WhatsApp.
    """
    queryset = MediaFile.objects.all()
    serializer_class = MediaFileSerializer
    permission_classes = [IsAtendenteOrAdmin]
    
    def get_queryset(self):
        """
        Filtra mídias baseado no tipo de usuário:
        - Administradores veem todas as mídias
        - Clientes veem apenas suas mídias
        - Colaboradores veem mídias do cliente ao qual estão associados
        """
        user = self.request.user
        
        if user.is_superuser:
            return MediaFile.objects.all()
        elif hasattr(user, 'cliente'):
            return MediaFile.objects.filter(cliente=user.cliente)
        elif hasattr(user, 'departamento') and user.departamento:
            return MediaFile.objects.filter(cliente=user.departamento.cliente)
        else:
            return MediaFile.objects.none()
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retorna estatísticas das mídias"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'por_tipo': queryset.values('media_type').annotate(count=Count('id')),
            'por_status': queryset.values('download_status').annotate(count=Count('id')),
            'por_cliente': queryset.values('cliente__nome').annotate(count=Count('id')),
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Endpoint para download direto do arquivo"""
        media_file = self.get_object()
        
        if not media_file.file_path or media_file.download_status != 'success':
            return Response(
                {'error': 'Arquivo não disponível para download'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            from django.http import FileResponse
            import os
            
            if os.path.exists(media_file.file_path):
                response = FileResponse(open(media_file.file_path, 'rb'))
                response['Content-Type'] = media_file.mimetype
                response['Content-Disposition'] = f'attachment; filename="{media_file.file_name}"'
                return response
            else:
                return Response(
                    {'error': 'Arquivo não encontrado no servidor'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {'error': f'Erro ao servir arquivo: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@permission_classes([AllowAny])
def serve_audio_message_public(request, message_id):
    """
    Serve áudio processado de uma mensagem específica - SEM AUTENTICAÇÃO
    """
    try:
        from core.models import Mensagem
        
        # Buscar mensagem
        message = Mensagem.objects.get(id=message_id)
        
        # Verificar se é uma mensagem de áudio
        if message.tipo != 'audio':
            return Response({'error': 'Mensagem não é de áudio'}, status=400)
        
        # Primeiro, tentar buscar na nova estrutura usando o mesmo método do serializer
        from pathlib import Path
        import glob
        
        # Tentar encontrar o arquivo na nova estrutura
        if hasattr(message.chat, 'cliente') and message.chat.cliente.whatsapp_instances.first():
            instance = message.chat.cliente.whatsapp_instances.first()
            cliente_id = message.chat.cliente.id
            instance_id = instance.instance_id
            chat_id = message.chat.chat_id
            
            base_path = Path(__file__).parent.parent / "media_storage" / f"cliente_{cliente_id}" / f"instance_{instance_id}" / "chats" / str(chat_id) / "audio"
            
            if base_path.exists():
                # Usar os mesmos padrões de busca do serializer
                search_patterns = [
                    f"msg_{message.message_id[:8]}_*.ogg",
                    f"msg_{message.message_id[:8]}_*.*",
                    f"msg_{message.message_id}.*",
                    f"msg_{message.message_id}_*.*",
                    f"*{message.message_id[:8]}*.*",
                    f"*{message.message_id}*.*"
                ]
                
                for pattern in search_patterns:
                    arquivos = list(base_path.glob(pattern))
                    if arquivos:
                        found_file = arquivos[0]
                        content_type = 'audio/ogg' if found_file.suffix == '.ogg' else 'audio/mpeg'
                        
                        with open(found_file, 'rb') as audio_file:
                            response = HttpResponse(audio_file.read(), content_type=content_type)
                            response['Content-Disposition'] = f'inline; filename="{found_file.name}"'
                            response['Access-Control-Allow-Origin'] = '*'
                            return response
        
        # Se não encontrou arquivo local, tentar extrair URL do WhatsApp do conteúdo JSON
        import json
        try:
            if message.conteudo and isinstance(message.conteudo, str) and message.conteudo.startswith('{'):
                parsed_content = json.loads(message.conteudo)
                if 'audioMessage' in parsed_content and 'url' in parsed_content['audioMessage']:
                    whatsapp_url = parsed_content['audioMessage']['url']
                    # Aqui você poderia implementar download do áudio do WhatsApp se necessário
                    # Por enquanto, retornar erro informativo
                    return Response({
                        'error': 'Arquivo não baixado localmente',
                        'whatsapp_url': whatsapp_url,
                        'message': 'O áudio está disponível no WhatsApp mas não foi baixado para o servidor'
                    }, status=404)
        except (json.JSONDecodeError, KeyError):
            pass
        
        # Tentar caminhos legados
        audio_paths = [
            f"media/audios/{message_id}.mp3",
            f"media/audios/{message_id}.ogg",
            f"media/audios/{message_id}.m4a",
            f"wapi/midias/audios/{message_id}.mp3",
            f"wapi/midias/audios/{message_id}.ogg",
            f"wapi/midias/audios/{message_id}.m4a"
        ]
        
        for audio_path in audio_paths:
            if os.path.exists(audio_path):
                with open(audio_path, 'rb') as audio_file:
                    response = HttpResponse(audio_file.read(), content_type='audio/mpeg')
                    response['Content-Disposition'] = f'attachment; filename="audio_{message_id}.mp3"'
                    return response
        
        return Response({'error': 'Arquivo de áudio não encontrado em nenhum local'}, status=404)
        
    except Mensagem.DoesNotExist:
        return Response({'error': 'Mensagem não encontrada'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def serve_whatsapp_audio(request, cliente_id, instance_id, chat_id, message_id):
    """
    Serve áudio da estrutura media_storage do WhatsApp
    """
    try:
        logger.info(f"Servindo áudio WhatsApp: cliente={cliente_id}, instance={instance_id}, chat={chat_id}, message={message_id}")
        
        # Buscar mensagem para obter informações do áudio
        try:
            mensagem = Mensagem.objects.get(
                message_id=message_id,
                tipo='audio',
                chat__chat_id=chat_id
            )
        except Mensagem.DoesNotExist:
            logger.warning(f"Mensagem de áudio não encontrada: {message_id}")
            return Response({'error': 'Mensagem não encontrada'}, status=404)
        
        # Extrair caminho do arquivo do conteúdo JSON
        audio_path = None
        try:
            conteudo_json = json.loads(mensagem.conteudo)
            audio_message = conteudo_json.get('audioMessage', {})
            
            # Prioridade 1: localPath (caminho absoluto)
            if audio_message.get('localPath'):
                audio_path = audio_message['localPath']
                logger.info(f"Usando localPath: {audio_path}")
            
            # Prioridade 2: directPath (caminho relativo)
            elif audio_message.get('directPath'):
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                audio_path = os.path.join(project_root, 'media_storage', audio_message['directPath'])
                logger.info(f"Usando directPath: {audio_path}")
            
            # Prioridade 3: fileName (buscar por nome)
            elif audio_message.get('fileName'):
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                audio_path = os.path.join(project_root, 'media_storage', f"{cliente_id}", instance_id, 'chats', chat_id, 'audio', audio_message['fileName'])
                logger.info(f"Usando fileName: {audio_path}")
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Erro ao processar conteúdo JSON: {e}")
            return Response({'error': 'Erro ao processar dados do áudio'}, status=500)
        
        if not audio_path or not os.path.exists(audio_path):
            logger.warning(f"Arquivo de áudio não encontrado: {audio_path}")
            return Response({'error': 'Arquivo de áudio não encontrado'}, status=404)
        
        # Servir arquivo
        try:
            with open(audio_path, 'rb') as audio_file:
                response = HttpResponse(audio_file.read(), content_type='audio/ogg')
                response['Content-Disposition'] = f'inline; filename="{os.path.basename(audio_path)}"'
                return response
        except Exception as e:
            logger.error(f"Erro ao ler arquivo de áudio: {e}")
            return Response({'error': 'Erro ao ler arquivo'}, status=500)
            
    except Exception as e:
        logger.error(f"Erro ao servir áudio WhatsApp: {e}")
        return Response({'error': 'Erro interno do servidor'}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def serve_local_audio(request, filename):
    """
    Serve áudio local por nome do arquivo
    """
    try:
        logger.info(f"Servindo áudio local: {filename}")
        
        # Buscar em todas as pastas de áudio
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        audio_dirs = [
            os.path.join(project_root, 'media_storage'),
            os.path.join(project_root, 'wapi', 'midias', 'audios'),
            os.path.join(project_root, 'media', 'audios')
        ]
        
        audio_path = None
        for audio_dir in audio_dirs:
            if os.path.exists(audio_dir):
                # Buscar arquivo recursivamente
                for root, dirs, files in os.walk(audio_dir):
                    if filename in files:
                        audio_path = os.path.join(root, filename)
                        break
                if audio_path:
                    break
        
        if not audio_path or not os.path.exists(audio_path):
            logger.warning(f"Arquivo de áudio não encontrado: {filename}")
            return Response({'error': 'Arquivo de áudio não encontrado'}, status=404)
        
        # Determinar mimetype
        ext = os.path.splitext(filename)[1].lower()
        mimetypes = {
            '.ogg': 'audio/ogg; codecs=opus',
            '.mp3': 'audio/mpeg',
            '.m4a': 'audio/mp4',
            '.wav': 'audio/wav'
        }
        content_type = mimetypes.get(ext, 'audio/ogg')
        
        # Servir arquivo
        try:
            with open(audio_path, 'rb') as audio_file:
                response = HttpResponse(audio_file.read(), content_type=content_type)
                response['Content-Disposition'] = f'inline; filename="{filename}"'
                return response
        except Exception as e:
            logger.error(f"Erro ao ler arquivo de áudio: {e}")
            return Response({'error': 'Erro ao ler arquivo'}, status=500)
            
    except Exception as e:
        logger.error(f"Erro ao servir áudio local: {e}")
        return Response({'error': 'Erro interno do servidor'}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def test_mensagens_public(request):
    """
    Endpoint público temporário para testar mensagens sem autenticação
    """
    try:
        from core.models import Mensagem
        
        # Buscar mensagens de áudio
        mensagens = Mensagem.objects.filter(tipo='audio').order_by('-data_envio')[:5]
        
        if not mensagens.exists():
            return Response({'error': 'Nenhuma mensagem de áudio encontrada'}, status=404)
        
        # Serializar mensagens
        from .serializers import MensagemSerializer
        serializer = MensagemSerializer(mensagens, many=True)
        
        return Response({
            'mensagens': serializer.data,
            'total': mensagens.count()
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def serve_audio_by_hash_mapping(request, message_id):
    """
    Serve áudio usando mapeamento inteligente por hash - SEM AUTENTICAÇÃO
    Mapeia message_id com arquivos baseados em hash/timestamp automaticamente
    """
    try:
        from pathlib import Path
        import re
        from core.models import Mensagem
        
        # Buscar a mensagem para obter informações do chat
        try:
            message = Mensagem.objects.get(id=message_id)
            chat = message.chat
        except Mensagem.DoesNotExist:
            return Response({'error': 'Mensagem não encontrada'}, status=404)
        
        # Obter informações do cliente e instância
        cliente = chat.cliente
        instance = cliente.whatsapp_instances.first()
        
        if not instance:
            return Response({'error': 'Instância WhatsApp não encontrada'}, status=404)
        
        cliente_id = cliente.id
        instance_id = instance.instance_id
        chat_id = chat.chat_id
        
        # Construir caminho base do diretório de áudio
        base_path = Path(__file__).parent.parent / "media_storage" / f"cliente_{cliente_id}" / f"instance_{instance_id}" / "chats" / str(chat_id) / "audio"
        
        print(f"🔍 Mapeamento inteligente para message_id: {message_id}")
        print(f"🔍 Chat ID: {chat_id}")
        print(f"🔍 Caminho base: {base_path}")
        
        if not base_path.exists():
            print(f"❌ Diretório não encontrado: {base_path}")
            return Response({'error': 'Diretório de áudio não encontrado'}, status=404)
        
        # Listar todos os arquivos de áudio disponíveis
        all_audio_files = list(base_path.glob("*.ogg")) + list(base_path.glob("*.mp3")) + list(base_path.glob("*.m4a"))
        
        if not all_audio_files:
            print(f"❌ Nenhum arquivo de áudio encontrado no diretório")
            return Response({'error': 'Nenhum arquivo de áudio disponível'}, status=404)
        
        print(f"🔍 Arquivos de áudio disponíveis:")
        for file in all_audio_files:
            print(f"   - {file.name}")
        
        # ALGORITMO DE MAPEAMENTO INTELIGENTE AVANÇADO
        found_file = None
        
        # Estratégia 1: Busca por correspondência exata do message_id
        message_id_short = message_id[:8]  # Primeiros 8 caracteres
        
        for audio_file in all_audio_files:
            filename = audio_file.name
            
            # Verificar se o filename contém o message_id completo ou parcial
            if message_id in filename or message_id_short in filename:
                found_file = audio_file
                print(f"✅ Arquivo encontrado por correspondência exata: {filename}")
                break
        
        # Estratégia 2: Busca por correspondência de chat_id e timestamp
        if not found_file:
            print(f"🔍 Buscando por correspondência de chat_id e timestamp...")
            
            # Extrair timestamp da mensagem (se disponível)
            message_timestamp = None
            if hasattr(message, 'data_envio') and message.data_envio:
                message_timestamp = message.data_envio.strftime("%Y%m%d")
                print(f"🔍 Timestamp da mensagem: {message_timestamp}")
            
            # Buscar arquivos que correspondam ao chat_id e timestamp
            for audio_file in all_audio_files:
                filename = audio_file.name
                
                # Verificar se o arquivo tem timestamp correspondente
                if message_timestamp and message_timestamp in filename:
                    found_file = audio_file
                    print(f"✅ Arquivo encontrado por timestamp: {filename}")
                    break
        
        # Estratégia 3: Busca por arquivo mais recente no chat
        if not found_file:
            print(f"🔍 Buscando por arquivo mais recente no chat...")
            
            # Filtrar arquivos com timestamp
            timestamped_files = []
            for audio_file in all_audio_files:
                filename = audio_file.name
                if "msg_" in filename and "_2025" in filename:
                    timestamped_files.append(audio_file)
            
            if timestamped_files:
                # Ordenar por data de modificação (mais recente primeiro)
                timestamped_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                found_file = timestamped_files[0]
                print(f"✅ Usando arquivo mais recente: {found_file.name}")
        
        # Estratégia 4: Fallback para qualquer arquivo disponível no chat
        if not found_file:
            print(f"🔍 Usando fallback: primeiro arquivo disponível no chat")
            found_file = all_audio_files[0]
            print(f"✅ Arquivo selecionado por fallback: {found_file.name}")
        
        if found_file:
            print(f"✅ Arquivo final selecionado: {found_file}")
            print(f"📏 Tamanho: {found_file.stat().st_size} bytes")
            
            # Determinar content-type baseado na extensão
            content_type = 'audio/ogg'  # Padrão
            if found_file.suffix.lower() == '.mp3':
                content_type = 'audio/mpeg'
            elif found_file.suffix.lower() == '.m4a':
                content_type = 'audio/mp4'
            elif found_file.suffix.lower() == '.wav':
                content_type = 'audio/wav'
            
            # Ler e servir o arquivo
            with open(found_file, 'rb') as f:
                response = HttpResponse(f.read(), content_type=content_type)
                response['Content-Disposition'] = f'inline; filename="{found_file.name}"'
                response['Access-Control-Allow-Origin'] = '*'
                response['Cache-Control'] = 'public, max-age=3600'  # Cache por 1 hora
                
                # Adicionar headers informativos para debug
                response['X-Audio-File'] = found_file.name
                response['X-Message-ID'] = message_id
                response['X-Chat-ID'] = chat_id
                response['X-Mapping-Strategy'] = 'intelligent_hash_based'
                
                return response
        else:
            print(f"❌ Nenhum arquivo de áudio encontrado")
            return Response({
                'error': 'Arquivo de áudio não encontrado',
                'message_id': message_id,
                'chat_id': chat_id,
                'available_files': [f.name for f in all_audio_files],
                'mapping_strategy': 'intelligent_hash_based',
                'debug_info': {
                    'cliente_id': cliente_id,
                    'instance_id': instance_id,
                    'chat_id': chat_id,
                    'message_timestamp': message.data_envio.isoformat() if hasattr(message, 'data_envio') and message.data_envio else None
                }
            }, status=404)
            
    except Exception as e:
        print(f"❌ Erro no mapeamento inteligente: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def serve_media_by_message_id(request, message_id):
    """
    Endpoint inteligente para servir qualquer mídia (audio, image, video, document) pelo message_id
    Encontra automaticamente o arquivo baseado na estrutura media_storage
    """
    try:
        from core.models import Mensagem
        from pathlib import Path
        import os
        import json
        
        logger.info(f"🔍 Buscando mídia para message_id: {message_id}")
        
        # Buscar a mensagem no banco
        try:
            mensagem = Mensagem.objects.get(id=message_id)
            logger.info(f"✅ Mensagem encontrada: ID={mensagem.id}, Message_ID={mensagem.message_id}, Tipo={mensagem.tipo}")
        except Mensagem.DoesNotExist:
            logger.warning(f"❌ Mensagem não encontrada: {message_id}")
            return HttpResponse("Mensagem não encontrada", status=404)
        
        # Extrair o hash do message_id (primeiros 8 caracteres)
        hash_id = None
        if mensagem.message_id and len(mensagem.message_id) >= 8:
            hash_id = mensagem.message_id[:8]
            logger.info(f"🔑 Hash extraído: {hash_id}")
        else:
            logger.warning(f"❌ Message_ID inválido: {mensagem.message_id}")
            return HttpResponse("Message_ID inválido", status=400)
        
        # Obter informações do cliente e instância
        cliente = mensagem.chat.cliente
        cliente_nome = cliente.nome.replace(' ', '_')
        chat_id = mensagem.chat.chat_id
        
        # Buscar instância do cliente
        from core.utils import get_client_whatsapp_instance
        instance = get_client_whatsapp_instance(cliente, prefer_connected=False)
        if not instance:
            logger.warning(f"❌ Instância não encontrada para cliente: {cliente.nome}")
            return HttpResponse("Instância não encontrada", status=404)
            
        instance_id = instance.instance_id
        logger.info(f"📱 Cliente: {cliente_nome}, Instance: {instance_id}, Chat: {chat_id}")
        
        # Construir caminho base da mídia
        base_path = Path(settings.BASE_DIR) / 'media_storage' / cliente_nome / f'instance_{instance_id}' / 'chats' / chat_id
        logger.info(f"📁 Caminho base: {base_path}")
        
        # Definir tipos de mídia e extensões possíveis
        media_types = {
            'audio': ['ogg', 'mp3', 'wav', 'm4a', 'aac'],
            'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
            'video': ['mp4', 'webm', 'avi', 'mov'],
            'document': ['pdf', 'doc', 'docx', 'txt', 'xlsx', 'zip']
        }
        
        # Tentar encontrar o arquivo
        found_file = None
        media_type_found = None
        
        for media_type, extensions in media_types.items():
            media_dir = base_path / media_type
            if media_dir.exists():
                logger.info(f"🔍 Verificando diretório: {media_dir}")
                
                # Buscar arquivos que comecem com msg_{hash_id}
                for file_path in media_dir.glob(f'msg_{hash_id}*'):
                    if file_path.is_file():
                        logger.info(f"✅ Arquivo encontrado: {file_path}")
                        found_file = file_path
                        media_type_found = media_type
                        break
                
                if found_file:
                    break
        
        if not found_file:
            logger.warning(f"❌ Arquivo não encontrado para hash: {hash_id}")
            return HttpResponse("Arquivo de mídia não encontrado", status=404)
        
        logger.info(f"🎯 Servindo arquivo: {found_file} (Tipo: {media_type_found})")
        
        # Determinar o content_type baseado na extensão
        content_types = {
            'ogg': 'audio/ogg',
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'm4a': 'audio/mp4',
            'aac': 'audio/aac',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'mp4': 'video/mp4',
            'webm': 'video/webm',
            'avi': 'video/x-msvideo',
            'mov': 'video/quicktime',
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'zip': 'application/zip'
        }
        
        file_extension = found_file.suffix.lower().lstrip('.')
        content_type = content_types.get(file_extension, 'application/octet-stream')
        
        # Servir o arquivo
        try:
            response = FileResponse(
                open(found_file, 'rb'),
                content_type=content_type,
                as_attachment=False
            )
            response['Cache-Control'] = 'public, max-age=3600'
            response['Access-Control-Allow-Origin'] = '*'
            
            logger.info(f"✅ Mídia servida com sucesso: {found_file}")
            return response
            
        except Exception as file_error:
            logger.error(f"❌ Erro ao abrir arquivo: {file_error}")
            return HttpResponse("Erro ao abrir arquivo", status=500)
        
    except Exception as e:
        logger.error(f"❌ Erro geral ao servir mídia: {e}")
        import traceback
        traceback.print_exc()
        return HttpResponse("Erro interno do servidor", status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def serve_whatsapp_audio_smart(request, cliente_id, instance_id, chat_id, message_id):
    """
    Endpoint inteligente para servir áudio da estrutura media_storage do WhatsApp
    Faz auto-detecção do arquivo baseado no message_id
    """
    try:
        logger.info(f"🎵 Endpoint inteligente: cliente={cliente_id}, instance={instance_id}, chat={chat_id}, message={message_id}")
        
        # **CORREÇÃO: Buscar mensagem com mais flexibilidade**
        mensagem = None
        try:
            # Tentar buscar por message_id primeiro
            mensagem = Mensagem.objects.get(
                message_id=message_id,
                tipo='audio'
            )
            logger.info(f"🎵 Mensagem encontrada por message_id: {mensagem.id}")
        except Mensagem.DoesNotExist:
            try:
                # Fallback: buscar por ID da mensagem
                mensagem = Mensagem.objects.get(
                    id=message_id,
                    tipo='audio'
                )
                logger.info(f"🎵 Mensagem encontrada por ID: {mensagem.id}")
            except Mensagem.DoesNotExist:
                # **CORREÇÃO: Buscar por chat_id se não encontrar por message_id**
                try:
                    mensagem = Mensagem.objects.filter(
                        chat__chat_id=chat_id,
                        tipo='audio'
                    ).order_by('-data_envio').first()
                    
                    if mensagem:
                        logger.info(f"🎵 Mensagem encontrada por chat_id: {mensagem.id}")
                    else:
                        logger.warning(f"Mensagem de áudio não encontrada para chat: {chat_id}")
                        return Response({'error': 'Mensagem não encontrada'}, status=404)
                        
                except Exception as e:
                    logger.error(f"Erro ao buscar mensagem por chat_id: {e}")
                    return Response({'error': 'Erro ao buscar mensagem'}, status=500)
        
        # **CORREÇÃO: Construir caminho para o arquivo na estrutura media_storage**
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        audio_dir = os.path.join(project_root, 'media_storage', str(cliente_id), instance_id, 'chats', chat_id, 'audio')
        
        logger.info(f"🎵 Procurando em: {audio_dir}")
        
        if not os.path.exists(audio_dir):
            logger.warning(f"Diretório de áudio não encontrado: {audio_dir}")
            # **CORREÇÃO: Tentar criar diretório se não existir**
            try:
                os.makedirs(audio_dir, exist_ok=True)
                logger.info(f"🎵 Diretório criado: {audio_dir}")
            except Exception as e:
                logger.error(f"Erro ao criar diretório: {e}")
                return Response({'error': 'Diretório de áudio não encontrado'}, status=404)
        
        # **CORREÇÃO: Procurar por arquivo que contenha o message_id no nome**
        audio_file = None
        
        # Prioridade 1: Procurar por message_id exato
        for filename in os.listdir(audio_dir):
            if message_id in filename:
                audio_file = filename
                logger.info(f"🎵 Arquivo encontrado por message_id: {audio_file}")
                break
        
        # Prioridade 2: Se não encontrou, procurar por ID da mensagem
        if not audio_file and mensagem.id:
            for filename in os.listdir(audio_dir):
                if str(mensagem.id) in filename:
                    audio_file = filename
                    logger.info(f"🎵 Arquivo encontrado por ID: {audio_file}")
                    break
        
        # Prioridade 3: Se ainda não encontrou, procurar por qualquer arquivo de áudio
        if not audio_file:
            for filename in os.listdir(audio_dir):
                if filename.lower().endswith(('.ogg', '.mp3', '.m4a', '.wav')):
                    audio_file = filename
                    logger.info(f"🎵 Usando primeiro arquivo de áudio encontrado: {audio_file}")
                    break
        
        if not audio_file:
            logger.warning(f"Arquivo de áudio não encontrado para message_id: {message_id}")
            # Listar arquivos disponíveis para debug
            available_files = os.listdir(audio_dir)
            logger.info(f"Arquivos disponíveis: {available_files}")
            return Response({
                'error': 'Arquivo de áudio não encontrado',
                'message_id': message_id,
                'available_files': available_files,
                'search_dir': audio_dir,
                'suggestion': 'Verifique se o arquivo foi baixado corretamente'
            }, status=404)
        
        audio_path = os.path.join(audio_dir, audio_file)
        logger.info(f"🎵 Servindo arquivo: {audio_path}")
        
        # **CORREÇÃO: Servir arquivo com melhor tratamento de erros**
        try:
            with open(audio_path, 'rb') as audio_file_obj:
                # **CORREÇÃO: Determinar Content-Type baseado na extensão**
                content_type = 'audio/ogg'  # padrão
                if audio_path.lower().endswith('.mp3'):
                    content_type = 'audio/mpeg'
                elif audio_path.lower().endswith('.m4a'):
                    content_type = 'audio/mp4'
                elif audio_path.lower().endswith('.wav'):
                    content_type = 'audio/wav'
                
                response = HttpResponse(audio_file_obj.read(), content_type=content_type)
                response['Content-Disposition'] = f'inline; filename="{audio_file}"'
                
                # **CORREÇÃO: Adicionar headers para CORS e cache**
                response['Access-Control-Allow-Origin'] = '*'
                response['Cache-Control'] = 'public, max-age=3600'
                response['X-Audio-File'] = audio_file
                response['X-Message-ID'] = message_id
                response['X-Chat-ID'] = chat_id
                
                logger.info(f"🎵 Áudio servido com sucesso: {audio_file}")
                return response
                
        except Exception as e:
            logger.error(f"Erro ao ler arquivo de áudio: {e}")
            return Response({'error': 'Erro ao ler arquivo'}, status=500)
            
    except Exception as e:
        logger.error(f"Erro ao servir áudio inteligente: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': 'Erro interno do servidor'}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def test_mensagens_public(request):
    """
    Endpoint público para testar mensagens (sem autenticação)
    """
    try:
        # Buscar mensagens de áudio para teste
        mensagens = Mensagem.objects.filter(tipo='audio')[:10]
        
        if mensagens.exists():
            # Serializar mensagens
            from .serializers import MensagemSerializer
            serializer = MensagemSerializer(mensagens, many=True)
            
            return Response({
                'status': 'success',
                'count': len(mensagens),
                'mensagens': serializer.data,
                'message': 'Mensagens de áudio encontradas'
            })
        else:
            return Response({
                'status': 'warning',
                'count': 0,
                'mensagens': [],
                'message': 'Nenhuma mensagem de áudio encontrada'
            })
            
    except Exception as e:
        logger.error(f"Erro no endpoint público de mensagens: {e}")
        return Response({
            'status': 'error',
            'error': str(e)
        }, status=500)

