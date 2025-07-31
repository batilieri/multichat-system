// Teste de informações do chat
console.log('🧪 Teste de informações do chat iniciado...')

// Função para verificar informações do chat atual
function checkChatInfo() {
  console.log('🔍 Verificando informações do chat...')
  
  // Verificar se o componente ChatView está montado
  const chatView = document.querySelector('[data-testid="chat-view"]') || 
                   document.querySelector('.chat-view') ||
                   document.querySelector('.messages-container')
  
  if (chatView) {
    console.log('✅ ChatView encontrado')
  } else {
    console.log('❌ ChatView não encontrado')
  }
  
  // Verificar se há um chat selecionado
  const chatInfo = window.chatInfo || window.currentChat
  if (chatInfo) {
    console.log('📱 Informações do chat:', chatInfo)
  } else {
    console.log('❌ Informações do chat não encontradas')
  }
  
  // Verificar se há token
  const token = localStorage.getItem('access_token')
  if (token) {
    console.log('🔑 Token encontrado:', token.substring(0, 20) + '...')
  } else {
    console.log('❌ Token não encontrado')
  }
  
  // Verificar se há instâncias W-API
  const wapiInstances = JSON.parse(localStorage.getItem('wapi_instances') || '{}')
  console.log('📱 Instâncias W-API:', Object.keys(wapiInstances))
}

// Função para simular envio de imagem e verificar logs
function testImageSend() {
  console.log('📸 Testando envio de imagem...')
  
  // Simular uma imagem no clipboard
  const canvas = document.createElement('canvas')
  canvas.width = 100
  canvas.height = 100
  const ctx = canvas.getContext('2d')
  
  ctx.fillStyle = '#FF0000'
  ctx.fillRect(0, 0, 100, 100)
  ctx.fillStyle = '#FFFFFF'
  ctx.font = '16px Arial'
  ctx.fillText('TESTE', 20, 50)
  
  canvas.toBlob((blob) => {
    const file = new File([blob], 'teste-chat.png', { type: 'image/png' })
    
    const reader = new FileReader()
    reader.onload = (e) => {
      const base64 = e.target.result.split(',')[1]
      
      console.log('📄 Base64 gerado:', base64.substring(0, 50) + '...')
      
      // Simular evento de paste
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
      console.log('✅ Evento de paste disparado')
    }
    reader.readAsDataURL(file)
  }, 'image/png')
}

// Função para verificar se a área de imagem pendente aparece
function checkPendingImageArea() {
  console.log('🔍 Verificando área de imagem pendente...')
  
  const pendingArea = document.querySelector('.bg-accent\\/30')
  if (pendingArea) {
    console.log('✅ Área de imagem pendente encontrada')
    
    const image = pendingArea.querySelector('img')
    const captionInput = pendingArea.querySelector('input[placeholder="Legenda (opcional)"]')
    const sendButton = document.querySelector('button[onclick*="handleSendPendingImage"]')
    
    if (image) console.log('✅ Imagem preview encontrada')
    if (captionInput) console.log('✅ Campo de legenda encontrado')
    if (sendButton) console.log('✅ Botão enviar encontrado')
    
    return true
  } else {
    console.log('❌ Área de imagem pendente não encontrada')
    return false
  }
}

// Função para verificar logs do console
function checkConsoleLogs() {
  console.log('📋 Verificando logs do console...')
  
  // Simular verificação de logs
  console.log('🔍 Logs que devem aparecer:')
  console.log('- 📱 Chat encontrado: {id, chat_id, cliente}')
  console.log('- 🔑 Token encontrado: ...')
  console.log('- 🌐 API URL: http://localhost:8000')
  console.log('- 📸 Imagem pendente encontrada: {type, filename, dataLength}')
  console.log('- 📝 Legenda: ...')
  console.log('- 📡 Response status: ...')
}

// Expor funções globalmente
window.testChatInfo = {
  checkChatInfo,
  testImageSend,
  checkPendingImageArea,
  checkConsoleLogs
}

console.log('📋 Funções de teste disponíveis:')
console.log('- window.testChatInfo.checkChatInfo()')
console.log('- window.testChatInfo.testImageSend()')
console.log('- window.testChatInfo.checkPendingImageArea()')
console.log('- window.testChatInfo.checkConsoleLogs()')

// Executar testes automáticos
setTimeout(() => {
  console.log('🔄 Executando testes automáticos...')
  checkChatInfo()
  
  setTimeout(() => {
    testImageSend()
    
    setTimeout(() => {
      checkPendingImageArea()
      checkConsoleLogs()
    }, 1000)
  }, 1000)
}, 1000)

console.log('✅ Script de teste de informações do chat carregado!') 