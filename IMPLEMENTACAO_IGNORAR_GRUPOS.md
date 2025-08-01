# Implementação: Ignorar Grupos nos Webhooks

## Objetivo

Configurar o sistema para ignorar automaticamente mensagens de grupos (`@g.us`) e não criar chats para elas, processando apenas mensagens de chats individuais.

## Implementação

### 1. Modificação da Função `normalize_chat_id`

**Arquivo:** `multichat_system/webhook/views.py`

**Função modificada:** `normalize_chat_id(chat_id)` (linha 37)

**Mudanças:**
- Adicionada verificação para grupos (`@g.us`)
- Retorna `None` quando detecta um grupo
- Mantém funcionalidade existente para chats individuais

**Código adicionado:**
```python
def normalize_chat_id(chat_id):
    """
    Normaliza o chat_id para garantir que seja um número de telefone válido
    Remove sufixos como @lid, @c.us, etc e extrai apenas o número
    Retorna None se for um grupo (contém @g.us)
    """
    if not chat_id:
        return None
    
    # Verificar se é um grupo (contém @g.us)
    if '@g.us' in chat_id:
        logger.info(f"🚫 Ignorando grupo: {chat_id}")
        return None
    
    # ... resto da função permanece igual
```

### 2. Comportamento Automático

Como as funções `save_message_to_chat` e `save_message_to_chat_with_from_me` já usam `normalize_chat_id`, elas automaticamente:

1. **Detectam grupos** através da verificação `@g.us`
2. **Retornam `False`** quando `normalize_chat_id` retorna `None`
3. **Não criam chats** para grupos
4. **Não salvam mensagens** de grupos
5. **Registram no log** que o grupo foi ignorado

## Testes Realizados

### Script de Teste: `testar_ignorar_grupos.py`

**Testes executados:**

1. **Normalização de Chat ID** - 6/6 testes passaram:
   - ✅ Grupos são detectados e retornam `None`
   - ✅ Chats individuais são normalizados corretamente

2. **Exemplos de grupos ignorados:**
   - `556992962029-1415646286@g.us` → `None`
   - `120363373541551792@g.us` → `None`
   - `5511999999999-123456789@g.us` → `None`

3. **Exemplos de chats individuais processados:**
   - `111141053288574@lid` → `111141053288574`
   - `5511999999999@c.us` → `5511999999999`
   - `5511888888888` → `5511888888888`

## Benefícios

1. **Performance:** Reduz processamento desnecessário
2. **Limpeza:** Mantém apenas chats individuais no sistema
3. **Foco:** Sistema focado em conversas individuais
4. **Logs:** Registra quando grupos são ignorados
5. **Compatibilidade:** Mantém funcionalidade existente para chats individuais

## Comportamento do Sistema

### Para Grupos:
- ❌ **Não cria chats**
- ❌ **Não salva mensagens**
- ✅ **Registra no log:** `🚫 Ignorando grupo: [chat_id]`
- ✅ **Retorna `False`** nas funções de salvamento

### Para Chats Individuais:
- ✅ **Cria chats normalmente**
- ✅ **Salva mensagens normalmente**
- ✅ **Normaliza chat_id corretamente**
- ✅ **Mantém todas as funcionalidades**

## Verificação Manual

Para verificar se está funcionando:

1. **Enviar mensagem de grupo** via webhook
2. **Verificar logs** - deve aparecer: `🚫 Ignorando grupo: [chat_id]`
3. **Verificar banco** - não deve criar chat nem mensagem
4. **Enviar mensagem individual** - deve funcionar normalmente

## Status

✅ **IMPLEMENTAÇÃO CONCLUÍDA**

- Grupos são detectados automaticamente
- Grupos são ignorados sem criar chats
- Chats individuais funcionam normalmente
- Testes confirmam o funcionamento
- Logs registram quando grupos são ignorados

## Próximos Passos

1. Monitorar logs em produção
2. Verificar se grupos estão sendo ignorados corretamente
3. Considerar adicionar mais tipos de grupos se necessário 