// Teste simples de Ctrl+V para imagens
console.log('🧪 Teste de Ctrl+V iniciado...')

// Função para simular Ctrl+V com imagem
function testCtrlV() {
  console.log('📸 Simulando Ctrl+V com imagem...')
  
  // Criar uma imagem de teste
  const canvas = document.createElement('canvas')
  canvas.width = 100
  canvas.height = 100
  const ctx = canvas.getContext('2d')
  
  // Desenhar algo na imagem
  ctx.fillStyle = '#FF0000'
  ctx.fillRect(0, 0, 100, 100)
  ctx.fillStyle = '#FFFFFF'
  ctx.font = '16px Arial'
  ctx.fillText('TESTE', 20, 50)
  
  // Converter para blob
  canvas.toBlob((blob) => {
    // Criar arquivo
    const file = new File([blob], 'teste.png', { type: 'image/png' })
    
    // Simular evento de paste
    const pasteEvent = new Event('paste', { bubbles: true })
    
    // Adicionar dados ao evento
    Object.defineProperty(pasteEvent, 'clipboardData', {
      value: {
        items: [
          {
            type: 'image/png',
            getAsFile: () => file
          }
        ]
      }
    })
    
    // Disparar o evento
    document.dispatchEvent(pasteEvent)
    
    console.log('✅ Evento de paste disparado com imagem')
  }, 'image/png')
}

// Expor função globalmente
window.testCtrlV = testCtrlV

console.log('📋 Para testar, execute: window.testCtrlV()')
console.log('💡 Ou copie uma imagem real e cole (Ctrl+V) no chat')

// Executar teste automaticamente após 2 segundos
setTimeout(() => {
  console.log('🔄 Executando teste automático...')
  testCtrlV()
}, 2000) 