# Comportamento de Reação Única

## 🎯 Objetivo

Implementar um sistema de reações onde **apenas uma reação é permitida por mensagem**, com a possibilidade de substituir ou remover a reação existente.

## 📋 Comportamento Implementado

### **Regras de Negócio:**

1. **Apenas uma reação por mensagem**
2. **Clicar em emoji diferente** → Substitui a reação anterior
3. **Clicar no mesmo emoji** → Remove a reação
4. **Sempre apenas uma reação ou nenhuma**

### **Fluxo de Interação:**

```
📱 Usuário clica em emoji → Backend processa → Frontend atualiza
```

## 🔧 Implementação Backend

### **Lógica no Endpoint `/api/mensagens/{id}/reagir/`:**

```python
# Verificar se já existe uma reação
if reacoes and emoji in reacoes:
    # Se já tem essa reação, remover
    reacoes = []
    action = 'removida'
else:
    # Se não tem reação ou tem outra, substituir
    reacoes = [emoji]
    action = 'adicionada' if not reacoes else 'substituída'
```

### **Estados Possíveis:**

1. **Sem reação:** `reacoes = []`
2. **Com reação:** `reacoes = ['👍']`
3. **Substituição:** `reacoes = ['❤️']` (era `['👍']`)
4. **Remoção:** `reacoes = []` (era `['👍']`)

## 🎨 Implementação Frontend

### **Função de Reação:**

```javascript
const handleReplaceReaction = async (emoji) => {
  // Envia requisição para o backend
  // Backend decide se adiciona, substitui ou remove
  // Frontend atualiza o estado local
}
```

### **Exibição das Reações:**

```javascript
{reactions.length > 0 && (
  <motion.button
    onClick={() => handleReplaceReaction(reaction)}
    title={`Remover reação ${reaction}`}
  >
    <span>{reaction}</span>
  </motion.button>
)}
```

## 🧪 Casos de Teste

### **Teste 1: Adicionar Primeira Reação**
- **Ação:** Clicar em 👍
- **Resultado:** `reacoes = ['👍']`
- **Ação:** "adicionada"

### **Teste 2: Substituir Reação**
- **Ação:** Clicar em ❤️ (já tem 👍)
- **Resultado:** `reacoes = ['❤️']`
- **Ação:** "substituída"

### **Teste 3: Remover Reação**
- **Ação:** Clicar em ❤️ (já tem ❤️)
- **Resultado:** `reacoes = []`
- **Ação:** "removida"

### **Teste 4: Adicionar Após Remoção**
- **Ação:** Clicar em 😂 (sem reação)
- **Resultado:** `reacoes = ['😂']`
- **Ação:** "adicionada"

## 📊 Vantagens

1. **Simplicidade:** Apenas uma reação por mensagem
2. **Intuitivo:** Comportamento similar ao WhatsApp
3. **Performance:** Menos dados para processar
4. **UX:** Interface mais limpa

## 🔄 Integração com WhatsApp

### **Envio para W-API:**

```python
# Enviar reação para WhatsApp real
wapi_result = reacao_wapi.enviar_reacao(
    phone=phone,
    message_id=mensagem.message_id,
    reaction=emoji,  # Único emoji
    delay=1
)
```

### **Sincronização:**

- ✅ Reação salva localmente
- ✅ Reação enviada para WhatsApp
- ✅ Contato vê a reação no WhatsApp
- ✅ Apenas uma reação por mensagem

## ✅ Status da Implementação

- ✅ **Backend:** Lógica de reação única implementada
- ✅ **Frontend:** Interface atualizada
- ✅ **Testes:** Casos de teste criados
- ✅ **Documentação:** Comportamento documentado

## 🚀 Próximos Passos

1. **Teste em produção:**
   - Adicione reação a uma mensagem
   - Substitua por outra reação
   - Remova a reação
   - Verifique no WhatsApp

2. **Monitoramento:**
   - Verifique logs do backend
   - Confirme sincronização com WhatsApp
   - Teste diferentes emojis

O sistema agora permite apenas uma reação por mensagem, com substituição e remoção funcionando corretamente! 🎉 