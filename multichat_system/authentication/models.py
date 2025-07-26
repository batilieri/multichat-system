from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    """
    Modelo de usuário customizado para o sistema MultiChat.

    Estende o AbstractUser do Django para incluir campos adicionais como:
    - tipo_usuario: Define o papel do usuário (administrador, colaborador).
    - cliente: Relaciona o usuário a um cliente específico (para colaboradores).
    - telefone: Número de telefone do usuário.
    - nome: Nome completo do usuário.

    Atributos:
        username (str): Nome de usuário único.
        email (str): Endereço de e-mail único.
        first_name (str): Primeiro nome do usuário.
        last_name (str): Sobrenome do usuário.
        tipo_usuario (str): Tipo de usuário (admin, colaborador).
        cliente (ForeignKey, opcional): Cliente associado ao usuário (para tipo 'colaborador').
        telefone (str): Número de telefone do usuário.
        nome (str): Nome completo do usuário.
    """
    TIPO_USUARIO_CHOICES = [
        ("admin", "Administrador"),
        ("cliente", "Cliente"),
        ("colaborador", "Colaborador"),
    ]

    nome = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nome Completo")
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default="colaborador",
        verbose_name="Tipo de Usuário"
    )
    cliente = models.ForeignKey(
        "core.Cliente",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Cliente Associado"
    )
    departamento = models.ForeignKey(
        "core.Departamento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Departamento"
    )
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    # Corrigir conflito de related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='multichat_usuarios',
        related_query_name='multichat_usuario',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='multichat_usuarios',
        related_query_name='multichat_usuario',
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["username"]

    def __str__(self):
        """
        Retorna a representação em string do objeto Usuario.
        """
        return self.username



