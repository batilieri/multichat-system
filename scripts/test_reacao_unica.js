// Teste do comportamento de reação única
console.log('🧪 Testando comportamento de reação única...')

// Simular reações
let reactions = []

function testReaction(emoji) {
  console.log(`\n🎯 Testando reação: ${emoji}`)
  console.log(`📊 Reações antes: [${reactions.join(', ')}]`)
  
  if (reactions.includes(emoji)) {
    // Se já tem essa reação, remover
    reactions = []
    console.log(`✅ Reação removida: ${emoji}`)
  } else {
    // Se não tem reação ou tem outra, substituir
    reactions = [emoji]
    console.log(`✅ Reação ${reactions.length === 1 ? 'adicionada' : 'substituída'}: ${emoji}`)
  }
  
  console.log(`📊 Reações depois: [${reactions.join(', ')}]`)
}

// Testes
console.log('\n🚀 Iniciando testes...')

// Teste 1: Adicionar primeira reação
testReaction('👍')

// Teste 2: Substituir por outra reação
testReaction('❤️')

// Teste 3: Substituir por terceira reação
testReaction('😂')

// Teste 4: Remover reação existente (clicando na mesma)
testReaction('😂')

// Teste 5: Adicionar nova reação após remoção
testReaction('😮')

console.log('\n✅ Testes concluídos!')
console.log('\n📋 COMPORTAMENTO ESPERADO:')
console.log('1. ✅ Apenas uma reação por mensagem')
console.log('2. ✅ Clicar em emoji diferente substitui a anterior')
console.log('3. ✅ Clicar no mesmo emoji remove a reação')
console.log('4. ✅ Sempre apenas uma reação ou nenhuma') 