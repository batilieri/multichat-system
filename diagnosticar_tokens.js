// Diagnóstico de problemas com tokens e instâncias
console.log('🔍 Diagnosticando problemas com tokens e instâncias...')

// Verificar localStorage
function verificarLocalStorage() {
  console.log('\n📋 Verificando localStorage:')
  
  // Verificar wapi_instances
  const wapiInstances = localStorage.getItem('wapi_instances')
  console.log('🔑 wapi_instances:', wapiInstances)
  
  if (wapiInstances) {
    try {
      const parsed = JSON.parse(wapiInstances)
      console.log('✅ wapi_instances parseado:', parsed)
      console.log('📊 Número de instâncias:', Object.keys(parsed).length)
      
      Object.keys(parsed).forEach(instanceId => {
        const instance = parsed[instanceId]
        console.log(`  - Instância ${instanceId}:`, {
          token: instance.token ? `${instance.token.substring(0, 8)}...` : 'NENHUM',
          hasToken: !!instance.token
        })
      })
    } catch (error) {
      console.error('❌ Erro ao fazer parse de wapi_instances:', error)
    }
  } else {
    console.log('❌ wapi_instances não encontrado no localStorage')
  }
  
  // Verificar access_token
  const accessToken = localStorage.getItem('access_token')
  console.log('🔐 access_token:', accessToken ? `${accessToken.substring(0, 8)}...` : 'NENHUM')
  
  // Verificar user
  const user = localStorage.getItem('user')
  console.log('👤 user:', user ? 'ENCONTRADO' : 'NENHUM')
}

// Simular o processo de busca de instância e token
function simularBuscaInstancia() {
  console.log('\n🔄 Simulando busca de instância e token:')
  
  const wapiInstances = JSON.parse(localStorage.getItem('wapi_instances') || '{}')
  const instanciaId = Object.keys(wapiInstances)[0]
  const token = instanciaId ? wapiInstances[instanciaId].token : null
  
  console.log('🔍 Instância encontrada:', instanciaId || 'NENHUMA')
  console.log('🔑 Token encontrado:', token ? 'SIM' : 'NÃO')
  
  if (!instanciaId || !token) {
    console.log('❌ PROBLEMA: Instância ou token não encontrados')
    console.log('💡 Solução: Conectar uma instância no painel de administração')
  } else {
    console.log('✅ Tudo OK: Instância e token encontrados')
  }
}

// Verificar se há problemas com as alterações recentes
function verificarAlteracoesRecentes() {
  console.log('\n🔍 Verificando se há problemas com alterações recentes:')
  
  // Verificar se o localStorage foi limpo acidentalmente
  const allKeys = Object.keys(localStorage)
  console.log('📋 Todas as chaves no localStorage:', allKeys)
  
  // Verificar se há chaves relacionadas ao sistema
  const systemKeys = allKeys.filter(key => 
    key.includes('wapi') || 
    key.includes('token') || 
    key.includes('user') || 
    key.includes('auth')
  )
  console.log('🔧 Chaves do sistema:', systemKeys)
}

// Executar diagnóstico
verificarLocalStorage()
simularBuscaInstancia()
verificarAlteracoesRecentes()

console.log('\n✅ Diagnóstico concluído!')

console.log(`
📋 POSSÍVEIS SOLUÇÕES:
1. Se wapi_instances estiver vazio:
   - Acesse o painel de administração
   - Conecte uma instância do WhatsApp
   - Verifique se o token foi salvo

2. Se access_token estiver ausente:
   - Faça login novamente
   - Verifique se a sessão não expirou

3. Se houver erro de parse:
   - Limpe o localStorage: localStorage.clear()
   - Faça login novamente
   - Reconecte as instâncias

4. Se tudo estiver OK mas ainda não funcionar:
   - Verifique se o backend está rodando
   - Verifique se a API está acessível
`) 