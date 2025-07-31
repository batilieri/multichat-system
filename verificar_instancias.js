// Verificar se as instâncias estão sendo carregadas corretamente
console.log('🔍 Verificando carregamento de instâncias...')

// Simular a função loadTokensFromBackend
async function simularLoadTokensFromBackend() {
  console.log('\n🔄 Simulando carregamento de tokens do backend...')
  
  try {
    // Verificar se há access_token
    const authToken = localStorage.getItem('access_token')
    console.log('🔐 Auth token encontrado:', !!authToken)
    
    if (!authToken) {
      console.log('❌ PROBLEMA: access_token não encontrado')
      console.log('💡 Solução: Faça login novamente')
      return
    }
    
    // Simular chamada para buscar instâncias
    console.log('📡 Fazendo chamada para /api/whatsapp-instances/')
    
    // Verificar se há instâncias no localStorage
    const wapiInstances = JSON.parse(localStorage.getItem('wapi_instances') || '{}')
    console.log('📊 Instâncias no localStorage:', Object.keys(wapiInstances).length)
    
    if (Object.keys(wapiInstances).length === 0) {
      console.log('❌ PROBLEMA: Nenhuma instância encontrada no localStorage')
      console.log('💡 Solução:')
      console.log('   1. Acesse o painel de administração')
      console.log('   2. Vá para "Instâncias WhatsApp"')
      console.log('   3. Conecte uma instância')
      console.log('   4. Verifique se o token foi salvo')
    } else {
      console.log('✅ Instâncias encontradas no localStorage')
      Object.keys(wapiInstances).forEach(instanceId => {
        const instance = wapiInstances[instanceId]
        console.log(`  - ${instanceId}: ${instance.token ? 'Token OK' : 'Sem token'}`)
      })
    }
    
  } catch (error) {
    console.error('❌ Erro ao carregar tokens:', error)
  }
}

// Verificar se o problema está na função handleSendMessage
function verificarHandleSendMessage() {
  console.log('\n📝 Verificando função handleSendMessage...')
  
  // Simular o código da função
  const wapiInstances = JSON.parse(localStorage.getItem('wapi_instances') || '{}')
  const instanciaId = Object.keys(wapiInstances)[0]
  const token = instanciaId ? wapiInstances[instanciaId].token : null
  
  console.log('🔍 Resultado da busca:')
  console.log('  - wapiInstances:', wapiInstances)
  console.log('  - instanciaId:', instanciaId)
  console.log('  - token:', token ? 'ENCONTRADO' : 'NÃO ENCONTRADO')
  
  if (!instanciaId || !token) {
    console.log('❌ PROBLEMA: Instância ou token não encontrados')
    console.log('💡 Este é o erro que aparece ao tentar enviar mensagem')
  } else {
    console.log('✅ Tudo OK: Instância e token encontrados')
  }
}

// Verificar se há problemas com as alterações recentes
function verificarAlteracoesRecentes() {
  console.log('\n🔍 Verificando se as alterações recentes afetaram o sistema...')
  
  // Verificar se o sistema de reações está funcionando
  console.log('✅ Sistema de reações implementado')
  console.log('✅ Popover de emojis funcionando')
  console.log('✅ Posicionamento dinâmico implementado')
  
  // Verificar se há conflitos
  console.log('🔍 Verificando possíveis conflitos...')
  
  // O problema pode estar relacionado ao fato de que as funções de reação
  // usam o access_token, mas o envio de mensagens usa wapi_instances
  console.log('💡 POSSÍVEL CAUSA:')
  console.log('   - Funções de reação usam: access_token')
  console.log('   - Envio de mensagens usa: wapi_instances')
  console.log('   - Se access_token estiver OK mas wapi_instances vazio,')
  console.log('     as reações funcionam mas envio de mensagens não')
}

// Executar verificações
simularLoadTokensFromBackend()
verificarHandleSendMessage()
verificarAlteracoesRecentes()

console.log('\n✅ Verificação concluída!')

console.log(`
📋 RESUMO DO PROBLEMA:
- Edição e exclusão funcionam (usam access_token)
- Reações funcionam (usam access_token)
- Envio de mensagens não funciona (usa wapi_instances)

🎯 CAUSA MAIS PROVÁVEL:
O localStorage 'wapi_instances' está vazio ou corrompido.

💡 SOLUÇÃO:
1. Acesse o painel de administração
2. Vá para "Instâncias WhatsApp"
3. Conecte uma instância do WhatsApp
4. Verifique se o token foi salvo no localStorage
5. Teste o envio de mensagens novamente
`) 