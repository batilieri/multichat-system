// Teste do Sistema de Reações
console.log('🧪 Testando Sistema de Reações...')

// Simular dados de mensagem
const messageData = {
  id: 1,
  content: "Olá! Como você está?",
  timestamp: new Date().toISOString(),
  reactions: [],
  isOwn: false
}

// Simular função de reação
function handleAddReaction(emoji) {
  console.log(`✅ Reação adicionada: ${emoji}`)
  if (messageData.reactions.includes(emoji)) {
    messageData.reactions = messageData.reactions.filter(r => r !== emoji)
    console.log(`❌ Reação removida: ${emoji}`)
  } else {
    messageData.reactions.push(emoji)
    console.log(`➕ Reação adicionada: ${emoji}`)
  }
  console.log('📊 Reações atuais:', messageData.reactions)
}

// Testar reações comuns
const reacoesComuns = ['👍', '❤️', '😂', '😮', '😢', '😡']

console.log('🎯 Testando reações comuns...')
reacoesComuns.forEach(emoji => {
  handleAddReaction(emoji)
})

console.log('🔄 Testando remoção de reações...')
handleAddReaction('👍') // Remove 👍
handleAddReaction('❤️') // Remove ❤️

console.log('✅ Teste do sistema de reações concluído!')
console.log('📋 Reações finais:', messageData.reactions) 