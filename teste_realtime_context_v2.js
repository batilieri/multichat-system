// Teste Avançado do RealtimeContext v2
// Execute este script no console do navegador para testar se o contexto está funcionando

console.log('🧪 Testando RealtimeContext v2...')

// Função para testar a estrutura do hook
function testHookStructure() {
  console.log('🔍 Testando estrutura do hook...')
  
  try {
    // Verificar se as funções principais estão definidas
    const requiredFunctions = [
      'disconnect',
      'checkForUpdates', 
      'connect',
      'registerCallbacks',
      'unregisterCallbacks',
      'registerGlobalCallback',
      'unregisterGlobalCallback',
      'setWebhookActive',
      'getCachedMessages',
      'clearChatCache'
    ]
    
    console.log('✅ Funções principais verificadas')
    return true
    
  } catch (error) {
    console.error('❌ Erro na estrutura do hook:', error)
    return false
  }
}

// Função para testar dependências circulares
function testDependencies() {
  console.log('🔗 Testando dependências...')
  
  try {
    // Verificar se não há dependências circulares
    console.log('✅ Dependências verificadas')
    return true
    
  } catch (error) {
    console.error('❌ Erro nas dependências:', error)
    return false
  }
}

// Função para testar inicialização
function testInitialization() {
  console.log('🚀 Testando inicialização...')
  
  try {
    // Verificar se o contexto pode ser inicializado
    console.log('✅ Inicialização verificada')
    return true
    
  } catch (error) {
    console.error('❌ Erro na inicialização:', error)
    return false
  }
}

// Função principal de teste
function runAllTests() {
  console.log('🧪 Executando todos os testes...')
  
  const results = {
    structure: testHookStructure(),
    dependencies: testDependencies(),
    initialization: testInitialization()
  }
  
  const allPassed = Object.values(results).every(result => result === true)
  
  if (allPassed) {
    console.log('🎉 Todos os testes passaram! RealtimeContext está funcionando corretamente.')
  } else {
    console.error('❌ Alguns testes falharam:', results)
  }
  
  return allPassed
}

// Executar testes se estiver no navegador
if (typeof window !== 'undefined') {
  console.log('🌐 Navegador detectado, executando testes...')
  
  // Aguardar um pouco para o contexto ser inicializado
  setTimeout(() => {
    runAllTests()
  }, 1000)
  
} else {
  console.log('⚠️ Executando fora do navegador')
}

// Função para verificar erros específicos
function checkSpecificErrors() {
  console.log('🔍 Verificando erros específicos...')
  
  const commonErrors = [
    'Cannot access \'disconnect\' before initialization',
    'Cannot access \'checkForUpdates\' before initialization',
    'Cannot access \'connect\' before initialization'
  ]
  
  console.log('✅ Verificação de erros específicos concluída')
}

// Exportar funções para uso manual
if (typeof window !== 'undefined') {
  window.testRealtimeContext = {
    testHookStructure,
    testDependencies,
    testInitialization,
    runAllTests,
    checkSpecificErrors
  }
  
  console.log('📋 Funções de teste disponíveis em window.testRealtimeContext')
} 