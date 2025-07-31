// Teste do posicionamento do popover de reações
console.log('🧪 Testando posicionamento do popover...')

// Simular diferentes tipos de mensagens
const mensagens = [
  { id: 1, content: "Mensagem recebida", isMe: false, from_me: false },
  { id: 2, content: "Mensagem enviada", isMe: true, from_me: true }
]

function testarPosicionamento(mensagem) {
  const isMe = mensagem.isMe || mensagem.from_me || false
  const posicao = isMe ? 'left-0' : 'right-0'
  const lado = isMe ? 'ESQUERDA' : 'DIREITA'
  
  console.log(`\n📝 Mensagem: "${mensagem.content}"`)
  console.log(`👤 Tipo: ${isMe ? 'Enviada por mim' : 'Recebida'}`)
  console.log(`📍 Popover posicionado: ${lado} (${posicao})`)
  console.log(`🎯 Posição CSS: absolute bottom-full ${posicao}`)
}

// Testar posicionamento para cada tipo de mensagem
mensagens.forEach(testarPosicionamento)

console.log('\n✅ Teste de posicionamento concluído!')

console.log(`
📋 RESUMO DO POSICIONAMENTO:
- Mensagens RECEBIDAS (lado esquerdo): Popover à DIREITA
- Mensagens ENVIADAS (lado direito): Popover à ESQUERDA

🎯 Lógica:
- isMe = false → right-0 (popover à direita)
- isMe = true → left-0 (popover à esquerda)
`) 