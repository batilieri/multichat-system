// Teste de Ctrl+V para imagens
console.log('🧪 Teste de Ctrl+V para imagens iniciado...')

// Simular uma imagem no clipboard
function simulateImagePaste() {
  console.log('📸 Simulando imagem no clipboard...')
  
  // Criar um evento de paste simulado
  const pasteEvent = new Event('paste', { bubbles: true })
  
  // Simular dados do clipboard com uma imagem
  const mockImageFile = new File(['fake-image-data'], 'test-image.png', { type: 'image/png' })
  
  // Adicionar dados ao evento
  Object.defineProperty(pasteEvent, 'clipboardData', {
    value: {
      items: [
        {
          type: 'image/png',
          getAsFile: () => mockImageFile
        }
      ]
    }
  })
  
  // Disparar o evento
  document.dispatchEvent(pasteEvent)
  
  console.log('✅ Evento de paste simulado disparado')
}

// Função para testar se o listener está funcionando
function testPasteListener() {
  console.log('🔍 Verificando se o listener de paste está ativo...')
  
  // Verificar se há listeners de paste no documento
  const listeners = getEventListeners(document)
  console.log('📋 Listeners encontrados:', listeners)
  
  // Verificar se o componente ChatView está montado
  const chatView = document.querySelector('[data-testid="chat-view"]') || 
                   document.querySelector('.chat-view') ||
                   document.querySelector('.messages-container')
  
  if (chatView) {
    console.log('✅ ChatView encontrado, listener deve estar ativo')
  } else {
    console.log('❌ ChatView não encontrado')
  }
}

// Função para criar uma imagem de teste
function createTestImage() {
  console.log('🎨 Criando imagem de teste...')
  
  // Criar um canvas com uma imagem simples
  const canvas = document.createElement('canvas')
  canvas.width = 100
  canvas.height = 100
  const ctx = canvas.getContext('2d')
  
  // Desenhar um quadrado colorido
  ctx.fillStyle = '#FF0000'
  ctx.fillRect(0, 0, 100, 100)
  ctx.fillStyle = '#FFFFFF'
  ctx.font = '16px Arial'
  ctx.fillText('TESTE', 20, 50)
  
  // Converter para blob
  canvas.toBlob((blob) => {
    console.log('📄 Blob criado:', blob)
    
    // Criar arquivo
    const file = new File([blob], 'teste-imagem.png', { type: 'image/png' })
    console.log('📁 Arquivo criado:', file)
    
    // Simular paste com este arquivo
    const pasteEvent = new Event('paste', { bubbles: true })
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
    
    document.dispatchEvent(pasteEvent)
    console.log('✅ Paste simulado com imagem real')
  }, 'image/png')
}

// Função para verificar se o toast está funcionando
function testToast() {
  console.log('🔔 Testando sistema de toast...')
  
  // Verificar se o toast está disponível
  if (window.toast) {
    window.toast({
      title: "🧪 Teste de Toast",
      description: "Sistema de toast funcionando!",
      duration: 3000,
    })
    console.log('✅ Toast funcionando')
  } else {
    console.log('❌ Toast não encontrado')
  }
}

// Função para verificar o estado do processamento
function checkProcessingState() {
  console.log('🔍 Verificando estado de processamento...')
  
  // Verificar se há indicador de processamento
  const processingIndicator = document.querySelector('.animate-spin')
  if (processingIndicator) {
    console.log('✅ Indicador de processamento encontrado')
  } else {
    console.log('❌ Indicador de processamento não encontrado')
  }
  
  // Verificar se o input está desabilitado
  const input = document.querySelector('input[type="text"]')
  if (input && input.disabled) {
    console.log('✅ Input desabilitado durante processamento')
  } else {
    console.log('❌ Input não está desabilitado')
  }
}

// Função principal de teste
function runTests() {
  console.log('🚀 Iniciando testes de Ctrl+V...')
  console.log('=' * 50)
  
  // Teste 1: Verificar listener
  testPasteListener()
  
  // Teste 2: Testar toast
  testToast()
  
  // Teste 3: Simular paste simples
  setTimeout(() => {
    console.log('\n📸 Teste 1: Paste simples')
    simulateImagePaste()
  }, 1000)
  
  // Teste 4: Criar e simular imagem real
  setTimeout(() => {
    console.log('\n📸 Teste 2: Imagem real')
    createTestImage()
  }, 2000)
  
  // Teste 5: Verificar estado
  setTimeout(() => {
    console.log('\n📸 Teste 3: Verificar estado')
    checkProcessingState()
  }, 3000)
}

// Expor funções para teste manual
window.testImagePaste = {
  simulateImagePaste,
  testPasteListener,
  createTestImage,
  testToast,
  checkProcessingState,
  runTests
}

console.log('📋 Funções de teste disponíveis:')
console.log('- window.testImagePaste.simulateImagePaste()')
console.log('- window.testImagePaste.testPasteListener()')
console.log('- window.testImagePaste.createTestImage()')
console.log('- window.testImagePaste.testToast()')
console.log('- window.testImagePaste.checkProcessingState()')
console.log('- window.testImagePaste.runTests()')

// Executar testes automaticamente
setTimeout(runTests, 500)

console.log('✅ Script de teste carregado!') 