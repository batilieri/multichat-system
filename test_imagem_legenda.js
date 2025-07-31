// Teste de imagem com legenda
console.log('🧪 Teste de imagem com legenda iniciado...')

// Função para simular Ctrl+V com imagem
function testImageWithCaption() {
  console.log('📸 Simulando Ctrl+V com imagem para testar legenda...')
  
  // Criar uma imagem de teste
  const canvas = document.createElement('canvas')
  canvas.width = 200
  canvas.height = 150
  const ctx = canvas.getContext('2d')
  
  // Desenhar algo na imagem
  ctx.fillStyle = '#4F46E5'
  ctx.fillRect(0, 0, 200, 150)
  ctx.fillStyle = '#FFFFFF'
  ctx.font = 'bold 20px Arial'
  ctx.fillText('IMAGEM TESTE', 30, 80)
  ctx.font = '14px Arial'
  ctx.fillText('Para testar legenda', 30, 100)
  
  // Converter para blob
  canvas.toBlob((blob) => {
    // Criar arquivo
    const file = new File([blob], 'teste-legenda.png', { type: 'image/png' })
    
    // Converter para Base64
    const reader = new FileReader()
    reader.onload = (e) => {
      const base64 = e.target.result.split(',')[1]
      
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
      console.log('📝 Agora você deve ver a imagem no input com campo de legenda')
    }
    reader.readAsDataURL(file)
  }, 'image/png')
}

// Função para verificar se a área de imagem pendente está visível
function checkPendingImageArea() {
  console.log('🔍 Verificando área de imagem pendente...')
  
  const pendingArea = document.querySelector('.bg-accent\\/30')
  if (pendingArea) {
    console.log('✅ Área de imagem pendente encontrada')
    
    const image = pendingArea.querySelector('img')
    const captionInput = pendingArea.querySelector('input[placeholder="Legenda (opcional)"]')
    const cancelButton = pendingArea.querySelector('button[title="Cancelar"]')
    
    if (image) console.log('✅ Imagem preview encontrada')
    if (captionInput) console.log('✅ Campo de legenda encontrado')
    if (cancelButton) console.log('✅ Botão cancelar encontrado')
    
    return true
  } else {
    console.log('❌ Área de imagem pendente não encontrada')
    return false
  }
}

// Função para testar envio com legenda
function testSendWithCaption() {
  console.log('📤 Testando envio com legenda...')
  
  const captionInput = document.querySelector('input[placeholder="Legenda (opcional)"]')
  if (captionInput) {
    // Adicionar legenda
    captionInput.value = 'Teste de legenda automática'
    captionInput.dispatchEvent(new Event('input', { bubbles: true }))
    
    console.log('✅ Legenda adicionada: "Teste de legenda automática"')
    
    // Simular clique no botão enviar
    const sendButton = document.querySelector('button[onclick*="handleSendPendingImage"]') ||
                      document.querySelector('button:has(.h-5.w-5)')
    
    if (sendButton) {
      console.log('📤 Clicando no botão enviar...')
      sendButton.click()
    } else {
      console.log('❌ Botão enviar não encontrado')
    }
  } else {
    console.log('❌ Campo de legenda não encontrado')
  }
}

// Função para testar cancelamento
function testCancelImage() {
  console.log('❌ Testando cancelamento de imagem...')
  
  const cancelButton = document.querySelector('button[title="Cancelar"]')
  if (cancelButton) {
    console.log('📤 Clicando no botão cancelar...')
    cancelButton.click()
  } else {
    console.log('❌ Botão cancelar não encontrado')
  }
}

// Expor funções globalmente
window.testImageCaption = {
  testImageWithCaption,
  checkPendingImageArea,
  testSendWithCaption,
  testCancelImage
}

console.log('📋 Funções de teste disponíveis:')
console.log('- window.testImageCaption.testImageWithCaption()')
console.log('- window.testImageCaption.checkPendingImageArea()')
console.log('- window.testImageCaption.testSendWithCaption()')
console.log('- window.testImageCaption.testCancelImage()')

// Executar teste automático
setTimeout(() => {
  console.log('🔄 Executando teste automático...')
  testImageWithCaption()
  
  // Verificar área após 1 segundo
  setTimeout(() => {
    checkPendingImageArea()
  }, 1000)
}, 2000)

console.log('✅ Script de teste de imagem com legenda carregado!') 