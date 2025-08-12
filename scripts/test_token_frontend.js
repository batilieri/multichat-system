// Teste para verificar tokens no localStorage
console.log('🔍 Verificando tokens no localStorage...')

// Verificar access_token
const accessToken = localStorage.getItem('access_token')
console.log('🔑 access_token:', accessToken ? accessToken.substring(0, 50) + '...' : 'Não encontrado')

// Verificar wapi_instances
const wapiInstances = localStorage.getItem('wapi_instances')
console.log('📱 wapi_instances:', wapiInstances)

if (wapiInstances) {
  try {
    const parsed = JSON.parse(wapiInstances)
    console.log('📋 wapi_instances (parsed):', parsed)
    
    const instanciaId = Object.keys(parsed)[0]
    const token = instanciaId ? parsed[instanciaId].token : null
    
    console.log('🆔 Instância ID:', instanciaId)
    console.log('🔑 Token da instância:', token ? token.substring(0, 50) + '...' : 'Não encontrado')
  } catch (e) {
    console.error('❌ Erro ao fazer parse do wapi_instances:', e)
  }
}

// Simular o método usado em handleSendMessage
console.log('\n🧪 Simulando handleSendMessage...')
const wapiInstances2 = JSON.parse(localStorage.getItem('wapi_instances') || '{}')
const instanciaId2 = Object.keys(wapiInstances2)[0]
const token2 = instanciaId2 ? wapiInstances2[instanciaId2].token : null

console.log('✅ Instância encontrada:', !!instanciaId2)
console.log('✅ Token encontrado:', !!token2)

if (!instanciaId2 || !token2) {
  console.log('❌ Nenhuma instância/token encontrada no navegador')
} else {
  console.log('✅ Dados válidos encontrados')
} 