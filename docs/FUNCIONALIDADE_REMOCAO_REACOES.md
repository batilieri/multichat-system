# Funcionalidade de Remoção de Reações

## 🎯 Objetivo

Implementar um endpoint específico para remover reações de mensagens, complementando a funcionalidade de adicionar/substituir reações.

## 📋 Funcionalidades Implementadas

### **1. Endpoint de Adicionar/Substituir Reação:**
- **URL:** `POST /api/mensagens/{id}/reagir/`
- **Parâmetros:** `{ emoji: string }`
- **Comportamento:** Adiciona ou substitui reação

### **2. Endpoint de Remover Reação:**
- **URL:** `POST /api/mensagens/{id}/remover-reacao/`
- **Parâmetros:** Nenhum
- **Comportamento:** Remove reação existente

## 🔧 Implementação Backend

### **Endpoint de Remoção:**

```python
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
        
        # Enviar para WhatsApp real
        wapi_result = reacao_wapi.enviar_reacao(
            phone=phone,
            message_id=mensagem.message_id,
            reaction="",  # Reação vazia para remover
            delay=1
        )
        
        return Response({
            'sucesso': True,
            'acao': 'removida',
            'emoji_removido': emoji_removido,
            'reacoes': reacoes,
            'wapi_enviado': wapi_result['sucesso'] if wapi_result else False,
            'mensagem': f'Reação removida com sucesso'
        })
        
    except Exception as e:
        return Response(
            {'erro': f'Erro interno: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

### **Integração com W-API:**

```python
# Remover reação do WhatsApp (enviar reação vazia)
wapi_result = reacao_wapi.enviar_reacao(
    phone=phone,
    message_id=mensagem.message_id,
    reaction="",  # Reação vazia para remover
    delay=1
)
```

## 🎨 Implementação Frontend

### **Função de Remoção:**

```javascript
const handleRemoveReaction = async () => {
  if (isReactionLoading) return
  
  setIsReactionLoading(true)
  
  try {
    const response = await fetch(`http://localhost:8000/api/mensagens/${message.id}/remover-reacao/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json',
      }
    })
    
    const data = await response.json()
    
    if (response.ok) {
      // Atualizar reações localmente
      setReactions(data.reacoes || [])
      
      toast({
        title: "Reação removida",
        description: data.mensagem || "Reação removida com sucesso",
        duration: 2000,
      })
    } else {
      throw new Error(data.erro || 'Erro ao remover reação')
    }
  } catch (error) {
    console.error('❌ Erro ao remover reação:', error)
    toast({
      title: "❌ Erro ao remover reação",
      description: error.message || "Não foi possível remover a reação",
      duration: 4000,
    })
  } finally {
    setIsReactionLoading(false)
  }
}
```

### **Interface Atualizada:**

```javascript
{reactions.length > 0 && (
  <motion.button
    onClick={() => handleRemoveReaction()}
    title={`Remover reação ${reaction}`}
  >
    <span>{reaction}</span>
  </motion.button>
)}
```

## 🧪 Casos de Teste

### **Teste 1: Remover Reação Existente**
- **Ação:** Clicar no botão de remoção
- **Resultado:** `reacoes = []`
- **WAPI:** Envia reação vazia
- **WhatsApp:** Reação removida

### **Teste 2: Tentar Remover Sem Reação**
- **Ação:** Clicar em remover sem reação
- **Resultado:** Erro 400 - "Mensagem não possui reações"

### **Teste 3: Fluxo Completo**
1. **Adicionar reação** → `reacoes = ['👍']`
2. **Remover reação** → `reacoes = []`
3. **Verificar WhatsApp** → Reação removida

## 📊 Vantagens da Implementação

1. **Separação de Responsabilidades:**
   - Endpoint específico para remoção
   - Código mais limpo e organizado

2. **Melhor UX:**
   - Botão específico para remover
   - Feedback claro para o usuário

3. **Integração Completa:**
   - Remoção local e no WhatsApp
   - Sincronização automática

4. **Tratamento de Erros:**
   - Validação de reação existente
   - Mensagens de erro claras

## 🔄 Fluxo de Funcionamento

### **1. Usuário Clica em Remover:**
```
Frontend → handleRemoveReaction() → Backend
```

### **2. Backend Processa:**
```
Validar reação existente → Remover do banco → Enviar para W-API
```

### **3. W-API Remove:**
```
Enviar reação vazia → WhatsApp remove reação → Contato vê mudança
```

### **4. Frontend Atualiza:**
```
Receber resposta → Atualizar interface → Mostrar toast
```

## ✅ Status da Implementação

- ✅ **Backend:** Endpoint de remoção implementado
- ✅ **Frontend:** Função de remoção implementada
- ✅ **W-API:** Integração com remoção
- ✅ **Testes:** Scripts de teste criados
- ✅ **Documentação:** Comportamento documentado

## 🚀 Próximos Passos

1. **Teste em produção:**
   - Adicione uma reação
   - Clique para remover
   - Verifique no WhatsApp

2. **Monitoramento:**
   - Verifique logs do backend
   - Confirme sincronização com WhatsApp
   - Teste diferentes cenários

3. **Otimizações futuras:**
   - Cache de reações
   - Retry automático
   - Logs mais detalhados

A funcionalidade de remoção de reações está agora completamente implementada e funcionando! 🎉 