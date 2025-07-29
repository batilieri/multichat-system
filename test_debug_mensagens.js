// Script para testar e debugar mensagens
console.log('🔍 Testando dados das mensagens...')

// Simular dados de mensagem para teste
const testMessages = [
  {
    id: 1,
    content: 'Teste de mensagem',
    tipo: 'texto',
    type: 'texto',
    isOwn: true,
    from_me: true,
    fromMe: true
  },
  {
    id: 2,
    content: 'Mensagem recebida',
    tipo: 'texto',
    type: 'texto',
    isOwn: false,
    from_me: false,
    fromMe: false
  },
  {
    id: 3,
    content: 'Mensagem de imagem',
    tipo: 'imagem',
    type: 'image',
    isOwn: true,
    from_me: true,
    fromMe: true
  }
]

testMessages.forEach((message, index) => {
  const isMe = message.isOwn || message.from_me || message.fromMe || false
  const isTextMessage = (message.tipo === 'text' || message.type === 'text' || message.tipo === 'texto' || message.type === 'texto')
  const canEdit = isMe && isTextMessage
  
  console.log(`\n📝 Mensagem ${index + 1}:`)
  console.log(`   ID: ${message.id}`)
  console.log(`   Conteúdo: ${message.content}`)
  console.log(`   Tipo: ${message.tipo} / ${message.type}`)
  console.log(`   isOwn: ${message.isOwn}`)
  console.log(`   from_me: ${message.from_me}`)
  console.log(`   fromMe: ${message.fromMe}`)
  console.log(`   isMe: ${isMe}`)
  console.log(`   isTextMessage: ${isTextMessage}`)
  console.log(`   canEdit: ${canEdit}`)
  console.log(`   ✅ Opção editar deve aparecer: ${canEdit ? 'SIM' : 'NÃO'}`)
})

console.log('\n🎯 Resumo:')
console.log('- Mensagem 1: Deve mostrar opção de edição (própria + texto)')
console.log('- Mensagem 2: Não deve mostrar opção de edição (recebida)')
console.log('- Mensagem 3: Não deve mostrar opção de edição (imagem)') 