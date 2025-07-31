// Teste do sistema de reações
// Este script testa a funcionalidade de reações no frontend

console.log('🧪 Testando sistema de reações...')

// Simular dados de uma mensagem
const message = {
  id: 1,
  content: "Teste de mensagem",
  reacoes: ["👍", "❤️"],
  from_me: false
}

// Simular função de reação
const handleReaction = async (emoji) => {
  console.log(`🎯 Enviando reação: ${emoji}`)
  
  // Simular chamada à API
  try {
    const response = await fetch(`http://localhost:8000/api/mensagens/${message.id}/reagir/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ emoji })
    })
    
    const data = await response.json()
    console.log('✅ Resposta da API:', data)
    
    if (response.ok) {
      console.log('✅ Reação enviada com sucesso')
      return data.reacoes || []
    } else {
      throw new Error(data.erro || 'Erro ao enviar reação')
    }
  } catch (error) {
    console.error('❌ Erro ao enviar reação:', error)
    throw error
  }
}

// Simular função de remoção de reação
const handleRemoveReaction = async (emoji) => {
  console.log(`🗑️ Removendo reação: ${emoji}`)
  
  try {
    const response = await fetch(`http://localhost:8000/api/mensagens/${message.id}/reagir/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ emoji })
    })
    
    const data = await response.json()
    console.log('✅ Resposta da API:', data)
    
    if (response.ok) {
      console.log('✅ Reação removida com sucesso')
      return data.reacoes || []
    } else {
      throw new Error(data.erro || 'Erro ao remover reação')
    }
  } catch (error) {
    console.error('❌ Erro ao remover reação:', error)
    throw error
  }
}

// Testar emojis comuns
const commonEmojis = ['👍', '❤️', '😂', '😮', '😢', '😡', '🔥', '👏', '🎉', '💯', '⭐', '✅', '❌', '⚡', '💎']

console.log('📋 Emojis disponíveis:', commonEmojis)
console.log('📝 Mensagem de teste:', message)

// Função para testar reações
const testReactions = async () => {
  console.log('\n🧪 Iniciando testes de reações...')
  
  // Teste 1: Adicionar reação
  try {
    console.log('\n1️⃣ Testando adição de reação...')
    const newReactions = await handleReaction('🔥')
    console.log('✅ Reação adicionada:', newReactions)
  } catch (error) {
    console.error('❌ Falha ao adicionar reação:', error)
  }
  
  // Teste 2: Remover reação
  try {
    console.log('\n2️⃣ Testando remoção de reação...')
    const updatedReactions = await handleRemoveReaction('👍')
    console.log('✅ Reação removida:', updatedReactions)
  } catch (error) {
    console.error('❌ Falha ao remover reação:', error)
  }
  
  // Teste 3: Adicionar múltiplas reações
  try {
    console.log('\n3️⃣ Testando múltiplas reações...')
    for (const emoji of ['🎉', '⭐', '💯']) {
      const reactions = await handleReaction(emoji)
      console.log(`✅ Reação ${emoji} adicionada:`, reactions)
    }
  } catch (error) {
    console.error('❌ Falha ao adicionar múltiplas reações:', error)
  }
}

// Executar testes se estiver no navegador
if (typeof window !== 'undefined') {
  // Aguardar um pouco para carregar
  setTimeout(() => {
    testReactions()
  }, 1000)
} else {
  console.log('🌐 Execute este script no navegador para testar as reações')
}

console.log('✅ Script de teste de reações carregado') 