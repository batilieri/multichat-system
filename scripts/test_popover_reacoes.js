// Teste do popover de reações
console.log('🧪 Testando popover de reações...')

// Simular o comportamento do popover
let showReactionPicker = false

function toggleReactionPicker() {
  showReactionPicker = !showReactionPicker
  console.log('🔄 Popover de reações:', showReactionPicker ? 'ABERTO' : 'FECHADO')
  
  // Simular a exibição do popover
  if (showReactionPicker) {
    console.log('📱 Emojis disponíveis: 👍, ❤️, 😂, 😮, 😢, 😡, 🔥, 👏, 🎉, 💯, ⭐, ✅, ❌, ⚡, 💎')
  }
}

function handleReaction(emoji) {
  console.log(`🎯 Reação selecionada: ${emoji}`)
  showReactionPicker = false
  console.log('🔄 Popover fechado após seleção')
}

// Simular cliques
console.log('🖱️ Clique no ícone de reação para abrir o popover')
toggleReactionPicker() // Abrir

console.log('🎯 Testando seleção de emoji...')
handleReaction('🔥') // Simular seleção

console.log('✅ Teste do popover concluído!')

// Instruções para testar no navegador
console.log(`
📋 INSTRUÇÕES PARA TESTAR:
1. Abra o chat no navegador
2. Clique no ícone 😊 (SmilePlus) ao lado de uma mensagem
3. O popover deve aparecer com os emojis
4. Clique em um emoji para reagir
5. O popover deve fechar automaticamente
6. A reação deve aparecer na mensagem
7. Clique na reação para removê-la
`) 