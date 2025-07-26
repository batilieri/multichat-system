from rest_framework import serializers
from authentication.models import Usuario
from core.models import Cliente
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer customizado para o token JWT.

    Adiciona informações do usuário ao payload do token.
    Permite login usando email em vez de username.
    """
    username_field = 'email'
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        
        if email and password:
            from django.contrib.auth import authenticate
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError({"password": "Senha incorreta."})
            # O campo username deve ser o email, pois USERNAME_FIELD = 'email'
            attrs["username"] = email
        return super().validate(attrs)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["tipo_usuario"] = user.tipo_usuario
        if user.cliente:
            token["cliente_id"] = user.cliente.id
            token["cliente_nome"] = user.cliente.nome
        return token


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de novos usuários.

    Define os campos necessários para criar um novo usuário.
    """
    password = serializers.CharField(write_only=True, min_length=6)
    confirmar_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = ["email", "password", "nome", "telefone", "confirmar_password", "tipo_usuario", "cliente", "departamento"]
        extra_kwargs = {
            "password": {"write_only": True},
            "confirmar_password": {"write_only": True}
        }

    def validate(self, data):
        if data.get("password") != data.get("confirmar_password"):
            raise serializers.ValidationError({"confirmar_password": "As senhas não coincidem."})
        return data

    def create(self, validated_data):
        validated_data.pop("confirmar_password", None)  # Remover campo extra
        user = Usuario.objects.create_user(
            username=validated_data["email"],  # Usar email como username
            email=validated_data["email"],
            password=validated_data["password"],
            nome=validated_data.get("nome", ""),
            tipo_usuario=validated_data.get("tipo_usuario", "colaborador"),
            cliente=validated_data.get("cliente", None),
            departamento=validated_data.get("departamento", None)
        )
        return user


class UsuarioPerfilSerializer(serializers.ModelSerializer):
    """
    Serializer para exibir e atualizar dados do perfil do usuário.

    Define os campos do perfil do usuário que podem ser visualizados e atualizados.
    """
    cliente_nome = serializers.ReadOnlyField(source="cliente.nome")
    departamento_nome = serializers.ReadOnlyField(source="departamento.nome")

    class Meta:
        model = Usuario
        fields = ["id", "email", "nome", "telefone", "tipo_usuario", "cliente", "cliente_nome", "departamento", "departamento_nome"]
        read_only_fields = ["id", "email"]


class AlterarSenhaSerializer(serializers.Serializer):
    """
    Serializer para alteração de senha.

    Define os campos para a senha antiga e a nova senha.
    """
    senha_antiga = serializers.CharField(required=True)
    nova_senha = serializers.CharField(required=True)

    def validate_senha_antiga(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha antiga incorreta.")
        return value



