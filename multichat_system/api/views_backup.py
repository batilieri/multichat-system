from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.conf import settings

from core.models import Cliente, Departamento, Chat, Mensagem, WebhookEvent, WhatsappInstance
from authentication.models import Usuario
from .serializers import (
    ClienteSerializer, DepartamentoSerializer, ChatSerializer,
    MensagemSerializer, WebhookEventSerializer, WhatsappInstanceSerializer
)
from .permissions import IsAdminOrReadOnly, IsAtendenteOrAdmin, IsClienteOwner # Importações corrigidas
from .wapi_integration import WAPiIntegration


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

        Administradores veem todos os clientes. Colaboradores veem apenas o cliente
        ao qual estão associados.
        """
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin'):
            return Cliente.objects.all()
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador' and hasattr(user, 'cliente'):
            return Cliente.objects.filter(id=user.cliente.id)
        return Cliente.objects.none()

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrReadOnly])
    def connect_wapi(self, request, pk=None):
        """
        Conecta uma instância do W-APi a um cliente existente.

        Recebe `instance_id` e `token` no corpo da requisição.
        Cria ou atualiza uma `WhatsappInstance` e tenta iniciar a sessão na W-APi.
        """
        cliente = self.get_object()
        instance_id = request.data.get("instance_id")
        token = request.data.get("token")
        webhook_url = request.data.get("webhook_url", f"https://{settings.ALLOWED_HOSTS[0]}/webhook/whatsapp/") # URL do seu webhook

        if not instance_id or not token:
            return Response({"error": "instance_id e token são obrigatórios"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Atualiza ou cria a instância do WhatsApp associada ao cliente
            whatsapp_instance, created = WhatsappInstance.objects.update_or_create(
                cliente=cliente,
                defaults={
                    "instance_id": instance_id,
                    "token": token,
                    "status": "pending", # Status inicial
                    "qr_code": "", # Limpa QR code anterior
                }
            )

            # Tenta iniciar a sessão na API W-APi
            wapi = WAPiIntegration(instance_id, token, settings.WAPI_BASE_URL)
            start_response = wapi.start_session(webhook_url=webhook_url)

            # Atualiza o status da instância com base na resposta da W-APi
            whatsapp_instance.status = start_response.get("status", "connected")
            whatsapp_instance.qr_code = start_response.get("qrcode", "")
            whatsapp_instance.save()

            return Response({"message": "Instância W-APi conectada com sucesso!", "data": WhatsappInstanceSerializer(whatsapp_instance).data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

    Permite operações CRUD em chats. Apenas administradores e atendentes podem acessar.
    """
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [IsAtendenteOrAdmin]

    def get_queryset(self):
        """
        Retorna o queryset de chats baseado no tipo de usuário logado.

        Administradores veem todos os chats. Colaboradores veem apenas chats
        do cliente ao qual estão associados.
        """
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin'):
            return Chat.objects.all()
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador' and hasattr(user, 'cliente'):
            return Chat.objects.filter(cliente=user.cliente)
        return Chat.objects.none()


class MensagemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar mensagens.

    Permite operações CRUD em mensagens. Apenas administradores e atendentes podem acessar.
    """
    queryset = Mensagem.objects.all()
    serializer_class = MensagemSerializer
    permission_classes = [IsAtendenteOrAdmin]

    def get_queryset(self):
        """
        Retorna o queryset de mensagens baseado no tipo de usuário logado.

        Administradores veem todas as mensagens. Colaboradores veem apenas mensagens
        de chats do cliente ao qual estão associados.
        """
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin'):
            return Mensagem.objects.all()
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador' and hasattr(user, 'cliente'):
            # Filtra mensagens de chats associados ao cliente do colaborador
            return Mensagem.objects.filter(chat__cliente=user.cliente)
        return Mensagem.objects.none()


class WebhookEventViewSet(viewsets.ModelViewSet):
    """
    ViewSet para visualizar eventos de webhook.

    Apenas administradores podem acessar. Não permite criação, atualização ou exclusão via API.
    """
    queryset = WebhookEvent.objects.all()
    serializer_class = WebhookEventSerializer
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ["get"]


class WhatsappInstanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar instâncias do WhatsApp.

    Permite operações CRUD em instâncias do WhatsApp. Apenas administradores podem criar, atualizar ou excluir.
    Colaboradores podem apenas visualizar instâncias associadas ao seu cliente.
    """
    queryset = WhatsappInstance.objects.all()
    serializer_class = WhatsappInstanceSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        """
        Retorna o queryset de instâncias do WhatsApp baseado no tipo de usuário logado.

        Administradores veem todas as instâncias. Colaboradores veem apenas instâncias
        do cliente ao qual estão associados.
        """
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin'):
            return WhatsappInstance.objects.all()
        elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador' and hasattr(user, 'cliente'):
            return WhatsappInstance.objects.filter(cliente=user.cliente)
        return WhatsappInstance.objects.none()

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrReadOnly])
    def get_qr_code(self, request, pk=None):
        """
        Obtém o QR Code para uma instância do WhatsApp.

        Tenta obter o QR Code da W-APi para a instância especificada.
        """
        instance = self.get_object()
        try:
            wapi = WAPiIntegration(instance.instance_id, instance.token, settings.WAPI_BASE_URL)
            status_response = wapi.get_session_status()
            qr_code = status_response.get("qrcode", "")
            instance.qr_code = qr_code
            instance.status = status_response.get("status", instance.status)
            instance.save()
            return Response({"qr_code": qr_code, "status": instance.status}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOrReadOnly])
    def disconnect(self, request, pk=None):
        """
        Desconecta uma instância do WhatsApp.

        Tenta desconectar a instância da W-APi.
        """
        instance = self.get_object()
        try:
            wapi = WAPiIntegration(instance.instance_id, instance.token, settings.WAPI_BASE_URL)
            disconnect_response = wapi.disconnect_session()
            instance.status = "disconnected"
            instance.save()
            return Response({"message": "Instância desconectada com sucesso!", "data": disconnect_response}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



