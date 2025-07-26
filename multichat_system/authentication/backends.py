from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Backend de autenticação customizado que permite login usando email.
    
    Este backend permite que os usuários façam login usando seu endereço de email
    em vez do nome de usuário tradicional.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica um usuário usando email e senha.
        
        Args:
            request: A requisição HTTP
            username: Pode ser um email ou username
            password: A senha do usuário
            **kwargs: Argumentos adicionais
            
        Returns:
            User object se autenticado com sucesso, None caso contrário
        """
        if username is None:
            username = kwargs.get('email')
        if username is None or password is None:
            return None
        
        try:
            # Tenta encontrar o usuário por email ou username
            user = User.objects.get(
                Q(email=username) | Q(username=username)
            )
        except User.DoesNotExist:
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
    
    def get_user(self, user_id):
        """
        Retorna um usuário pelo ID.
        
        Args:
            user_id: O ID do usuário
            
        Returns:
            User object se encontrado, None caso contrário
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None 