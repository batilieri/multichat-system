# Sistema de Edição de Mensagens

## 📋 Visão Geral

O sistema permite editar mensagens de texto enviadas pelo usuário através da API W-API do WhatsApp. A edição é feita tanto no WhatsApp quanto no banco de dados local.

## 🔧 Como Funciona

### 1. **Exclusão de Mensagens**
- **Endpoint W-API**: `DELETE /message/delete-message`
- **Parâmetros**: `phone`, `messageId`, `instanceId`
- **Classe**: `DeletaMensagem` em `wapi/mensagem/deletar/deletarMensagens.py`
- **Funcionalidade**: Remove mensagens do WhatsApp (apenas mensagens enviadas pelo usuário)

### 2. **Edição de Mensagens**
- **Endpoint W-API**: `POST /message/edit-message`
- **Parâmetros**: `phone`, `messageId`, `text`, `instanceId`
- **Classe**: `EditarMensagem` em `wapi/mensagem/editar/editarMensagens.py`
- **Funcionalidade**: Edita o texto de mensagens enviadas pelo usuário

## 🚀 Implementação

### Backend (Django)

#### Endpoint de Edição
```python
# URL: /api/mensagens/{id}/editar/
# Método: POST
# Parâmetros: {"novo_texto": "texto editado"}

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
```

#### Validações Implementadas

1. **Existência da Mensagem**
   ```python
   mensagem = self.get_object()
   ```

2. **Message ID do WhatsApp**
   ```python
   if not mensagem.message_id:
       return Response({
           'error': 'Esta mensagem não pode ser editada',
           'details': 'A mensagem não possui ID do WhatsApp necessário para edição'
       }, status=400)
   ```

3. **Mensagem Enviada pelo Usuário**
   ```python
   if not mensagem.from_me:
       return Response({
           'error': 'Apenas mensagens enviadas por você podem ser editadas',
           'details': 'Esta mensagem foi recebida, não enviada'
       }, status=400)
   ```

4. **Tipo de Mensagem (Texto)**
   ```python
   if mensagem.tipo not in ['texto', 'text']:
       return Response({
           'error': 'Apenas mensagens de texto podem ser editadas',
           'details': f'Tipo de mensagem atual: {mensagem.tipo}'
       }, status=400)
   ```

5. **Validação do Texto**
   ```python
   # Tamanho máximo
   if len(novo_texto) > 4096:
       return Response({
           'error': 'Texto muito longo',
           'details': f'O texto tem {len(novo_texto)} caracteres, máximo permitido: 4096'
       }, status=400)
   
   # Verificar se mudou
   if novo_texto == mensagem.conteudo:
       return Response({
           'error': 'Texto não foi alterado',
           'details': 'O novo texto é idêntico ao texto atual'
       }, status=400)
   ```

6. **Permissões do Usuário**
   ```python
   if not (user.is_superuser or 
           (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'admin') or
           (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'cliente' and mensagem.chat.cliente == user.cliente) or
           (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'colaborador' and mensagem.chat.cliente == user.cliente)):
       return Response({
           'error': 'Você não tem permissão para editar esta mensagem',
           'details': 'Apenas o proprietário do chat ou administradores podem editar mensagens'
       }, status=403)
   ```

### Frontend (React)

#### Componente Message.jsx

```javascript
const handleEdit = async () => {
    // Verificar se a mensagem pode ser editada
    if (message.type !== 'texto' && message.type !== 'text') {
        toast({
            title: "Não é possível editar",
            description: "Apenas mensagens de texto podem ser editadas",
            duration: 3000,
        })
        return
    }
    
    // Abrir modal de edição
    const textoOriginal = message.content || message.conteudo || ''
    setEditText(textoOriginal)
    setShowEditModal(true)
}

const handleSaveEdit = async () => {
    const textoLimpo = editText.trim()
    
    // Validações
    if (!textoLimpo) {
        toast({
            title: "Erro",
            description: "O texto não pode estar vazio",
            duration: 3000,
        })
        return
    }

    if (textoLimpo.length > 4096) {
        toast({
            title: "Erro",
            description: "O texto é muito longo (máximo 4096 caracteres)",
            duration: 3000,
        })
        return
    }

    // Enviar para API
    const response = await fetch(`/api/mensagens/${message.id}/editar/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            novo_texto: textoLimpo
        }),
    })
    
    if (response.ok) {
        // Atualizar localmente
        message.content = textoLimpo
        message.conteudo = textoLimpo
        
        toast({
            title: "✅ Mensagem editada",
            description: "A mensagem foi editada com sucesso no WhatsApp e no sistema",
            duration: 3000,
        })
    }
}
```

## 📡 Integração W-API

### Classe EditarMensagem

```python
class EditarMensagem:
    def __init__(self, instance_id, token):
        self.instance_id = instance_id
        self.token = token
        self.base_url = "https://api.w-api.app/v1/message"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

    def editar_mensagem(self, phone, message_id, new_text):
        """
        Edita uma mensagem já enviada
        
        Args:
            phone (str): Número do telefone (formato: 5569999267344)
            message_id (str): ID da mensagem a ser editada
            new_text (str): Novo texto da mensagem
            
        Returns:
            dict: Resposta da API
        """
        url = f'{self.base_url}/edit-message?instanceId={self.instance_id}'
        
        data = {
            "phone": phone,
            "text": new_text,
            "messageId": message_id
        }
        
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()
```

### Classe DeletaMensagem

```python
class DeletaMensagem:
    def deletar(self, phone_number, message_ids):
        """
        Deleta uma ou várias mensagens
        
        Args:
            phone_number (str): Número de telefone
            message_ids (str ou list): ID(s) da(s) mensagem(ns)
            
        Returns:
            dict: Resultado da operação
        """
        url = f"{self.base_url}/delete-message"
        params = {
            'phone': phone_number,
            'messageId': message_id,
            'instanceId': self.instance_id
        }
        
        response = requests.delete(url, headers=self.headers, params=params)
        return response.json()
```

## 🧪 Testes

### Script de Teste Completo

```python
# test_edicao_mensagens_completo.py

def test_edit_message():
    """Testa a edição de mensagens via API."""
    
    # Buscar mensagem válida
    mensagem_test = Mensagem.objects.filter(
        from_me=True,
        message_id__isnull=False,
        tipo__in=['texto', 'text']
    ).first()
    
    # Testar endpoint
    response = requests.post(
        f"http://localhost:8000/api/mensagens/{mensagem_test.id}/editar/",
        json={"novo_texto": "Texto editado via API"},
        headers={'Authorization': 'Bearer TOKEN'}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")

def test_wapi_edit_direct():
    """Testa edição direta via W-API."""
    
    # Buscar instância
    instancia = mensagem_test.chat.cliente.whatsappinstance_set.first()
    
    # Criar editor
    editor = EditarMensagem(instancia.instance_id, instancia.token)
    
    # Editar
    resultado = editor.editar_mensagem(
        phone=mensagem_test.chat.chat_id,
        message_id=mensagem_test.message_id,
        new_text="Teste direto W-API"
    )
    
    print(f"Resultado: {resultado}")
```

## 🔒 Segurança e Permissões

### Níveis de Acesso

1. **Superusuário**: Pode editar qualquer mensagem
2. **Administrador**: Pode editar qualquer mensagem
3. **Cliente**: Pode editar apenas mensagens de seus próprios chats
4. **Colaborador**: Pode editar mensagens de chats do cliente ao qual está associado

### Validações de Segurança

- ✅ Verificação de propriedade da mensagem
- ✅ Validação de tipo de mensagem
- ✅ Verificação de message_id
- ✅ Validação de tamanho do texto
- ✅ Verificação de permissões do usuário

## 📊 Logs e Monitoramento

### Logs Implementados

```python
logger.info(f'✏️ Tentando editar mensagem com ID: {pk}')
logger.info(f'✅ Mensagem encontrada: ID={mensagem.id}, message_id={mensagem.message_id}')
logger.warning(f'⚠️ Tentativa de editar mensagem não enviada pelo usuário: ID={mensagem.id}')
logger.error(f'❌ Erro ao editar mensagem na W-API: {resultado_wapi}')
```

### Respostas da API

#### Sucesso (200)
```json
{
    "success": true,
    "message": "Mensagem editada com sucesso",
    "wapi_result": {...},
    "novo_texto": "texto editado",
    "message_id": "3EB0C767D123456789",
    "chat_id": "5511999999999@c.us"
}
```

#### Erro de Validação (400)
```json
{
    "error": "Apenas mensagens enviadas por você podem ser editadas",
    "details": "Esta mensagem foi recebida, não enviada"
}
```

#### Erro de Permissão (403)
```json
{
    "error": "Você não tem permissão para editar esta mensagem",
    "details": "Apenas o proprietário do chat ou administradores podem editar mensagens"
}
```

## 🚀 Como Usar

### 1. Via Frontend
1. Abra um chat
2. Clique no menu de uma mensagem enviada por você
3. Selecione "Editar"
4. Digite o novo texto
5. Clique em "Salvar"

### 2. Via API
```bash
curl -X POST http://localhost:8000/api/mensagens/123/editar/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"novo_texto": "Texto editado"}'
```

### 3. Via Script Python
```python
from wapi.mensagem.editar.editarMensagens import EditarMensagem

editor = EditarMensagem("instance_id", "token")
resultado = editor.editar_mensagem("5511999999999", "message_id", "novo texto")
print(resultado)
```

## ⚠️ Limitações

1. **Apenas mensagens de texto** podem ser editadas
2. **Apenas mensagens enviadas pelo usuário** (from_me=True)
3. **Máximo 4096 caracteres** por mensagem
4. **Tempo limitado** para edição (depende do WhatsApp)
5. **Apenas texto** pode ser editado (não mídia)

## 🔄 Fluxo Completo

1. **Usuário solicita edição** no frontend
2. **Frontend valida** tipo de mensagem e permissões
3. **API recebe requisição** e valida todos os parâmetros
4. **Sistema busca instância** WhatsApp do cliente
5. **W-API é chamada** para editar no WhatsApp
6. **Banco local é atualizado** com novo texto
7. **Frontend é atualizado** com novo conteúdo
8. **Usuário recebe confirmação** da edição

## 📝 Notas Importantes

- A edição só funciona para mensagens enviadas pelo usuário
- O WhatsApp tem limitações de tempo para edição
- Mensagens em grupos podem ter restrições adicionais
- O sistema mantém sincronização entre WhatsApp e banco local
- Logs detalhados facilitam debug e monitoramento 