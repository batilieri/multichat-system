# Sistema de Controle de Acesso - MultiChat

## Visão Geral

O sistema MultiChat implementa um controle de acesso baseado em roles (papéis) que define diferentes níveis de permissão para usuários do sistema.

## Tipos de Usuário

### 1. Administrador (`admin`)
- **Acesso total** a todas as funcionalidades do sistema
- Pode criar, editar e excluir qualquer tipo de usuário (admin, cliente, colaborador)
- Pode gerenciar todos os clientes
- Pode acessar relatórios e configurações
- Pode gerenciar instâncias do WhatsApp

### 2. Cliente (`cliente`)
- Pode criar apenas **colaboradores** associados à sua empresa
- Pode visualizar e gerenciar apenas seus próprios colaboradores
- Pode acessar relatórios e configurações
- Pode gerenciar instâncias do WhatsApp
- **NÃO** pode criar outros clientes ou administradores

### 3. Colaborador (`colaborador`)
- Acesso limitado apenas ao **chat**
- Pode visualizar apenas chats do cliente ao qual está associado
- Pode enviar e receber mensagens
- **NÃO** pode acessar:
  - Relatórios
  - Configurações
  - Gerenciamento de usuários
  - Instâncias do WhatsApp

## Estrutura de Permissões

### Backend (Django)

#### Permissões Implementadas

1. **`IsAdminOrReadOnly`**: Apenas admins podem criar/editar/excluir
2. **`IsAtendenteOrAdmin`**: Admins e colaboradores podem acessar
3. **`IsClienteOrAdmin`**: Admins e clientes podem acessar
4. **`IsColaboradorOnly`**: Apenas colaboradores
5. **`IsClienteUser`**: Apenas clientes
6. **`IsAdminOrCliente`**: Admins e clientes

#### Views Protegidas

- **`ClienteViewSet`**: Apenas admins podem criar/editar clientes
- **`UsuarioViewSet`**: Admins podem criar qualquer usuário, clientes apenas colaboradores
- **`DashboardViewSet`**: Todos os tipos podem acessar, mas com dados filtrados
- **`ChatViewSet`**: Colaboradores veem apenas chats do seu cliente
- **`MensagemViewSet`**: Colaboradores veem apenas mensagens do seu cliente

### Frontend (React)

#### Contexto de Autenticação

O `AuthContext` fornece funções para verificar permissões:

```javascript
const {
  isAdmin,
  isCliente,
  isColaborador,
  canCreateUsers,
  canAccessReports,
  canAccessSettings,
  canAccessWhatsApp
} = useAuth();
```

#### Rotas Protegidas

- **`/usuarios`**: Apenas admins e clientes
- **`/whatsapp`**: Apenas admins e clientes
- **`/relatorios`**: Apenas admins e clientes
- **`/configuracoes`**: Apenas admins e clientes
- **`/chats`**: Todos os tipos (com dados filtrados)

#### Componentes Adaptativos

- **`Sidebar`**: Mostra apenas itens de menu baseados nas permissões
- **`UserManagement`**: Interface diferente para admins e clientes
- **`Dashboard`**: Dados filtrados por tipo de usuário

## Fluxo de Trabalho

### 1. Criação de Usuários

1. **Administrador** cria um **Cliente**
2. **Cliente** faz login e cria **Colaboradores** para sua empresa
3. **Colaboradores** fazem login e acessam apenas o chat

### 2. Hierarquia de Acesso

```
Administrador
├── Pode criar Clientes
├── Pode criar Colaboradores
└── Acesso total ao sistema

Cliente
├── Pode criar apenas Colaboradores
├── Gerencia seus próprios colaboradores
└── Acesso a relatórios e configurações

Colaborador
├── Acesso apenas ao chat
├── Vê apenas chats do seu cliente
└── Sem acesso a relatórios/configurações
```

## Configuração Inicial

### 1. Criar Usuário Administrador

Execute o script de configuração inicial:

```bash
cd multichat_system
python create_admin_user.py
```

Isso criará:
- **Admin**: `admin@multichat.com` / `admin123`
- **Cliente**: `cliente@exemplo.com`
- **Colaborador**: `colaborador@exemplo.com` / `colab123`

### 2. Migrações do Banco

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Testar o Sistema

1. Faça login como administrador
2. Crie um cliente
3. Faça login como cliente
4. Crie colaboradores
5. Faça login como colaborador
6. Teste o acesso limitado

## Segurança

### Medidas Implementadas

1. **Autenticação JWT**: Tokens seguros para autenticação
2. **Verificação de Permissões**: Backend e frontend
3. **Filtros de Dados**: Usuários veem apenas dados relevantes
4. **Rotas Protegidas**: Frontend bloqueia acesso não autorizado
5. **Validação de Dados**: Backend valida todas as operações

### Boas Práticas

1. **Altere as senhas padrão** após o primeiro login
2. **Use HTTPS** em produção
3. **Configure CORS** adequadamente
4. **Monitore logs** de acesso
5. **Faça backups** regulares

## Personalização

### Adicionar Novos Tipos de Usuário

1. Adicione o novo tipo em `authentication/models.py`
2. Crie permissões específicas em `api/permissions.py`
3. Atualize as views para incluir a nova lógica
4. Modifique o frontend para suportar o novo tipo

### Modificar Permissões

1. Edite as classes de permissão em `api/permissions.py`
2. Atualize as views que usam essas permissões
3. Modifique o frontend conforme necessário
4. Teste todas as funcionalidades afetadas

## Troubleshooting

### Problemas Comuns

1. **Usuário não consegue acessar funcionalidades**
   - Verifique o tipo de usuário no banco de dados
   - Confirme se as permissões estão corretas

2. **Dados não aparecem**
   - Verifique os filtros de queryset nas views
   - Confirme se o usuário está associado ao cliente correto

3. **Erro de permissão**
   - Verifique se o token JWT é válido
   - Confirme se o usuário tem as permissões necessárias

### Logs Úteis

```bash
# Ver logs do Django
python manage.py runserver --verbosity=2

# Ver logs do frontend
npm run dev
```

## Suporte

Para dúvidas ou problemas com o sistema de controle de acesso, consulte:

1. Logs do sistema
2. Documentação do Django REST Framework
3. Documentação do React
4. Issues do projeto no repositório 

O repositório remoto do frontend foi adicionado com sucesso como `frontend`.

Agora, para enviar o código do frontend para o repositório correto, siga estes passos:

1. Entre na pasta do frontend:
```sh
cd multichat-frontend
```

2. Inicialize o repositório Git (se ainda não estiver inicializado):
```sh
git init
```

3. Adicione o repositório remoto (caso não exista):
```sh
git remote add origin https://github.com/batilieri/multichat-frontend.git
```

4. Adicione todos os arquivos e faça um commit:
```sh
git add .
git commit -m "feat: primeiro commit do frontend"
```

5. Envie para o GitHub:
```sh
git push -u origin main
```

Se aparecer algum erro, por favor, copie a mensagem aqui para que eu possa te ajudar a resolver! Se quiser, posso executar os comandos para você. Deseja que eu faça isso? 