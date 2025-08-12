// Teste de conversão base64
console.log('🧪 Testando conversão base64...')

// Simular uma imagem pequena
const testImageData = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='

console.log('📸 Dados de teste:')
console.log('- Dados:', testImageData)
console.log('- Tamanho:', testImageData.length)
console.log('- É base64 válido?', /^[A-Za-z0-9+/]*={0,2}$/.test(testImageData))

// Testar se pode ser decodificado
try {
  const decoded = atob(testImageData)
  console.log('✅ Base64 válido - pode ser decodificado')
  console.log('- Tamanho decodificado:', decoded.length)
} catch (e) {
  console.log('❌ Base64 inválido:', e.message)
}

// Simular o que o frontend envia
const payload = {
  chat_id: '5511999999999@c.us',
  instancia: 'test-instance',
  token: 'test-token',
  image_data: testImageData,
  image_type: 'base64',
  caption: 'Teste'
}

console.log('📦 Payload simulado:', payload)
console.log('✅ Teste concluído!') 