from rest_framework import permissions
from core.models import Cliente


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permissão customizada para permitir acesso de leitura a todos,
    mas apenas administradores podem criar, atualizar ou excluir.
    """
    def has_permission(self, request, view):
        # Permite GET, HEAD, OPTIONS para qualquer usuário autenticado
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Permite escrita apenas para administradores
        return request.user and request.user.is_authenticated and \
               (request.user.is_superuser or (hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'admin'))


class IsAtendenteOrAdmin(permissions.BasePermission):
    """
    Permissão customizada para permitir acesso a atendentes, clientes e administradores.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               (request.user.is_superuser or 
                (hasattr(request.user, 'tipo_usuario') and 
                 (request.user.tipo_usuario == 'admin' or 
                  request.user.tipo_usuario == 'colaborador' or 
                  request.user.tipo_usuario == 'cliente')))


class IsClienteOwner(permissions.BasePermission):
    """
    Permissão para verificar se o usuário pertence ao mesmo cliente do objeto.

    Permite acesso total se o usuário for superuser.
    Para outros usuários, verifica se o objeto possui um atributo 'cliente'
    e se o cliente do usuário logado corresponde ao cliente do objeto.
    """
    def has_object_permission(self, request, view, obj):
        # Superuser tem acesso total
        if request.user.is_superuser:
            return True

        # Verifica se o usuário tem um cliente associado e se o objeto tem um cliente
        if hasattr(request.user, 'cliente') and hasattr(obj, 'cliente'):
            return request.user.cliente == obj.cliente
        
        # Se o objeto for um Cliente, verifica se o usuário é o próprio cliente
        if isinstance(obj, Cliente) and hasattr(request.user, 'cliente'):
            return request.user.cliente == obj

        return False

    def has_permission(self, request, view):
        # Permite acesso se o usuário for superuser ou tiver um objeto 'cliente' associado
        return request.user and request.user.is_authenticated and \
               (request.user.is_superuser or hasattr(request.user, 'cliente'))


class IsMasterUser(permissions.BasePermission):
    """
    Permissão para verificar se o usuário é do tipo 'master' ou superuser.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               (request.user.is_superuser or (hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'master'))


class IsColaboradorUser(permissions.BasePermission):
    """
    Permissão para verificar se o usuário é do tipo 'colaborador' ou superuser.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               (request.user.is_superuser or (hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'colaborador'))


class IsClienteUser(permissions.BasePermission):
    """
    Permissão para verificar se o usuário é do tipo 'cliente' ou superuser.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               (request.user.is_superuser or (hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'cliente'))


class IsAdminOrCliente(permissions.BasePermission):
    """
    Permissão para permitir acesso apenas a administradores e clientes.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               (request.user.is_superuser or 
                (hasattr(request.user, 'tipo_usuario') and 
                 (request.user.tipo_usuario == 'admin' or request.user.tipo_usuario == 'cliente')))


class IsColaboradorOnly(permissions.BasePermission):
    """
    Permissão para permitir acesso apenas a colaboradores (sem acesso a relatórios e configurações).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               (request.user.is_superuser or 
                (hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'colaborador'))


class IsClienteOrAdmin(permissions.BasePermission):
    """
    Permissão para permitir acesso a clientes e administradores (pode criar usuários).
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               (request.user.is_superuser or 
                (hasattr(request.user, 'tipo_usuario') and 
                 (request.user.tipo_usuario == 'admin' or request.user.tipo_usuario == 'cliente')))


class IsClienteInstanceOwner(permissions.BasePermission):
    """
    Permissão para permitir que clientes atualizem o status de suas próprias instâncias do WhatsApp.
    Administradores têm acesso total.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and \
               (request.user.is_superuser or 
                (hasattr(request.user, 'tipo_usuario') and 
                 (request.user.tipo_usuario == 'admin' or request.user.tipo_usuario == 'cliente')))

    def has_object_permission(self, request, view, obj):
        # Superuser tem acesso total
        if request.user.is_superuser:
            return True

        # Administradores têm acesso total
        if hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'admin':
            return True

        # Clientes só podem acessar suas próprias instâncias
        if hasattr(request.user, 'tipo_usuario') and request.user.tipo_usuario == 'cliente':
            if hasattr(obj, 'cliente') and hasattr(request.user, 'cliente'):
                return obj.cliente == request.user.cliente

        return False


