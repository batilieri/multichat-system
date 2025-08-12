// Teste de criação de base64 no frontend
console.log('🧪 Testando criação de base64...')

// Função para criar uma imagem de teste
function createTestImage() {
  const canvas = document.createElement('canvas')
  canvas.width = 100
  canvas.height = 100
  const ctx = canvas.getContext('2d')
  
  // Criar uma imagem simples
  ctx.fillStyle = '#FF0000'
  ctx.fillRect(0, 0, 100, 100)
  ctx.fillStyle = '#FFFFFF'
  ctx.font = '16px Arial'
  ctx.fillText('TESTE', 20, 50)
  
  return canvas
}

// Função para converter para base64
function convertToBase64(canvas) {
  return canvas.toDataURL('image/png').split(',')[1]
}

// Função para simular o processo do frontend
function simulateFrontendProcess() {
  console.log('📸 Criando imagem de teste...')
  const canvas = createTestImage()
  
  console.log('🔄 Convertendo para base64...')
  const base64 = convertToBase64(canvas)
  
  console.log('📄 Base64 criado:', base64.substring(0, 50) + '...')
  console.log('📏 Tamanho do base64:', base64.length, 'caracteres')
  
  // Simular o payload que seria enviado
  const payload = {
    image_data: base64,
    image_type: 'base64',
    caption: 'Teste de imagem'
  }
  
  console.log('📦 Payload que seria enviado:', {
    image_data: base64.substring(0, 50) + '...',
    image_type: payload.image_type,
    caption: payload.caption
  })
  
  return payload
}

// Função para testar se o base64 é válido
function testBase64Validity(base64) {
  try {
    // Tentar decodificar
    const binaryString = atob(base64)
    console.log('✅ Base64 é válido')
    console.log('📏 Tamanho decodificado:', binaryString.length, 'bytes')
    return true
  } catch (e) {
    console.log('❌ Base64 inválido:', e)
    return false
  }
}

// Função para simular o evento de paste
function simulatePasteEvent() {
  console.log('📋 Simulando evento de paste...')
  
  const canvas = createTestImage()
  canvas.toBlob((blob) => {
    const file = new File([blob], 'teste.png', { type: 'image/png' })
    
    console.log('📄 Arquivo criado:', {
      name: file.name,
      size: file.size,
      type: file.type
    })
    
    // Simular o processo do frontend
    const reader = new FileReader()
    reader.onload = (e) => {
      const base64 = e.target.result.split(',')[1]
      console.log('🔄 Base64 do paste:', base64.substring(0, 50) + '...')
      
      // Testar validade
      testBase64Validity(base64)
      
      // Simular payload
      const payload = {
        image_data: base64,
        image_type: 'base64',
        caption: 'Imagem do paste'
      }
      
      console.log('📦 Payload do paste:', {
        image_data: base64.substring(0, 50) + '...',
        image_type: payload.image_type,
        caption: payload.caption
      })
    }
    reader.readAsDataURL(file)
  }, 'image/png')
}

// Função para verificar se o chat está sendo encontrado
function checkChatInfo() {
  console.log('🔍 Verificando informações do chat...')
  
  // Verificar se há um chat selecionado
  const chatElements = document.querySelectorAll('[data-chat-id], [data-testid*="chat"]')
  console.log('📱 Elementos de chat encontrados:', chatElements.length)
  
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

// Executar testes
console.log('🚀 Iniciando testes de base64...')

// Teste 1: Criação de base64
const payload = simulateFrontendProcess()

// Teste 2: Validade do base64
testBase64Validity(payload.image_data)

// Teste 3: Simulação de paste
simulatePasteEvent()

// Teste 4: Informações do chat
checkChatInfo()

console.log('✅ Testes de base64 concluídos!')

// Expor funções globalmente
window.testBase64 = {
  createTestImage,
  convertToBase64,
  simulateFrontendProcess,
  testBase64Validity,
  simulatePasteEvent,
  checkChatInfo
}

console.log('📋 Funções disponíveis:')
console.log('- window.testBase64.createTestImage()')
console.log('- window.testBase64.convertToBase64(canvas)')
console.log('- window.testBase64.simulateFrontendProcess()')
console.log('- window.testBase64.testBase64Validity(base64)')
console.log('- window.testBase64.simulatePasteEvent()')
console.log('- window.testBase64.checkChatInfo()') 