from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Usuario
from .serializers import (
    CustomTokenObtainPairSerializer, UsuarioRegistroSerializer,
    UsuarioPerfilSerializer, AlterarSenhaSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    View customizada para obter tokens JWT.

    Utiliza um serializer customizado para incluir informações adicionais do usuário
    no payload do token.
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        """
        Sobrescreve o método post para incluir dados do usuário na resposta.
        """
        response = super().post(request, *args, **kwargs)
        
        # Adicionar dados do usuário à resposta
        if response.status_code == 200:
            email = request.data.get('email')
            try:
                user = Usuario.objects.get(email=email)
                user_data = UsuarioPerfilSerializer(user).data
                response.data['user'] = user_data
            except Usuario.DoesNotExist:
                pass
        
        return response


class UsuarioRegistroView(viewsets.ModelViewSet):
    """
    ViewSet para registro de novos usuários.

    Permite a criação de novos usuários com base no serializer `UsuarioRegistroSerializer`.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioRegistroSerializer
    permission_classes = [AllowAny] # Permite que qualquer um se registre
    http_method_names = ["post"]


class UsuarioPerfilView(viewsets.ModelViewSet):
    """
    ViewSet para visualização e atualização do perfil do usuário.

    Permite que o usuário autenticado visualize e atualize seu próprio perfil.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioPerfilSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "patch"]

    def get_object(self):
        """
        Retorna o objeto de usuário associado à requisição.
        """
        return self.request.user

    @action(detail=False, methods=["post"], serializer_class=AlterarSenhaSerializer)
    def alterar_senha(self, request):
        """
        Permite que o usuário autenticado altere sua senha.

        Recebe a senha antiga e a nova senha. Valida a senha antiga antes de atualizar.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.request.user.set_password(serializer.validated_data["nova_senha"])
        self.request.user.save()

        return Response({"detail": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar usuários.

    Permite operações CRUD em usuários. Apenas administradores podem acessar.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioPerfilSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retorna o queryset de usuários.

        - Superusuários e admins veem todos os usuários
        - Clientes veem apenas colaboradores associados a eles
        - Colaboradores veem apenas a si mesmos
        """
        if self.request.user.is_superuser or (hasattr(self.request.user, 'tipo_usuario') and self.request.user.tipo_usuario == 'admin'):
            return Usuario.objects.all()
        elif hasattr(self.request.user, 'tipo_usuario') and self.request.user.tipo_usuario == 'cliente':
            # Clientes veem apenas colaboradores associados a eles
            return Usuario.objects.filter(cliente=self.request.user.cliente, tipo_usuario='colaborador')
        else:
            # Colaboradores veem apenas a si mesmos
            return Usuario.objects.filter(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        """
        Cria um novo usuário. Administradores e clientes podem criar usuários.
        """
        # Verificar se o usuário tem permissão para criar usuários
        can_create = (
            request.user.is_superuser or 
            (hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'admin') or
            (hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'cliente')
        )
        
        if not can_create:
            return Response({"error": "Apenas administradores e clientes podem criar usuários"}, status=status.HTTP_403_FORBIDDEN)
        
        # Se for cliente, só pode criar colaboradores
        if hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'cliente':
            if request.data.get('tipo_usuario') != 'colaborador':
                return Response({"error": "Clientes só podem criar colaboradores"}, status=status.HTTP_403_FORBIDDEN)
            
            # Forçar o cliente do usuário criado para ser o mesmo do cliente logado
            request.data['cliente'] = request.user.cliente.id
        
        serializer = UsuarioRegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response(UsuarioPerfilSerializer(user).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Atualiza um usuário. Administradores e clientes podem atualizar usuários.
        """
        # Verificar se o usuário tem permissão para atualizar usuários
        can_update = (
            request.user.is_superuser or 
            (hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'admin') or
            (hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'cliente')
        )
        
        if not can_update:
            return Response({"error": "Apenas administradores e clientes podem atualizar usuários"}, status=status.HTTP_403_FORBIDDEN)
        
        # Se for cliente, só pode atualizar colaboradores associados a ele
        if hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'cliente':
            user_to_update = self.get_object()
            if user_to_update.cliente != request.user.cliente or user_to_update.tipo_usuario != 'colaborador':
                return Response({"error": "Clientes só podem atualizar colaboradores associados a eles"}, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Remove um usuário. Administradores e clientes podem remover usuários.
        """
        # Verificar se o usuário tem permissão para remover usuários
        can_delete = (
            request.user.is_superuser or 
            (hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'admin') or
            (hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'cliente')
        )
        
        if not can_delete:
            return Response({"error": "Apenas administradores e clientes podem remover usuários"}, status=status.HTTP_403_FORBIDDEN)
        
        # Se for cliente, só pode remover colaboradores associados a ele
        if hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'cliente':
            user_to_delete = self.get_object()
            if user_to_delete.cliente != request.user.cliente or user_to_delete.tipo_usuario != 'colaborador':
                return Response({"error": "Clientes só podem remover colaboradores associados a eles"}, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)




