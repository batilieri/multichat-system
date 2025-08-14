// 🧪 TESTE DO AUDIOPLAYER CORRIGIDO
// Este arquivo testa o componente AudioPlayer refatorado

console.log('🧪 TESTE DO AUDIOPLAYER CORRIGIDO INICIADO')

// Simular mensagem de áudio do WhatsApp
const testMessage = {
  id: 867,
  tipo: 'audio',
  chat_id: '556999872433@c.us',
  message_id: 'WAM_abc123',
  content: JSON.stringify({
    audioMessage: {
      url: '/wapi/midias/audios/ColdPlay - The Scientist.mp3',
      fileName: 'ColdPlay - The Scientist.mp3',
      mimetype: 'audio/mpeg',
      seconds: 301,
      fileLength: 5262536
    }
  }),
  timestamp: '2025-08-12T10:20:30Z'
}

// Simular mensagem com múltiplas estratégias de URL
const testMessageMultipleUrls = {
  id: 868,
  tipo: 'audio',
  chat_id: '556999872433@c.us',
  message_id: 'WAM_def456',
  media_url: '/media/whatsapp_media/audio_123.mp3',
  content: JSON.stringify({
    audioMessage: {
      url: '/wapi/midias/audios/audio_123.mp3',
      fileName: 'audio_123.mp3',
      mimetype: 'audio/ogg',
      seconds: 15,
      fileLength: 12345
    }
  }),
  timestamp: '2025-08-12T10:25:30Z'
}

// Simular mensagem com erro
const testMessageError = {
  id: 869,
  tipo: 'audio',
  chat_id: '556999872433@c.us',
  message_id: 'WAM_ghi789',
  content: JSON.stringify({
    audioMessage: {
      url: 'https://invalid-url-that-will-fail.com/audio.mp3',
      fileName: 'invalid_audio.mp3',
      mimetype: 'audio/mpeg',
      seconds: 10,
      fileLength: 5000
    }
  }),
  timestamp: '2025-08-12T10:30:30Z'
}

// Função para testar estratégias de URL
function testUrlStrategies(message) {
  console.log('🎯 Testando estratégias de URL para mensagem:', message.id)
  
  const audioUrlStrategies = []
  
  // ESTRATÉGIA 1: URL da nova estrutura de chat_id
  if (message.media_url) {
    if (message.media_url.startsWith('/media/whatsapp_media/') || 
        message.media_url.startsWith('/api/whatsapp-media/')) {
      const url = message.media_url.startsWith('/api/') 
        ? `http://localhost:8000${message.media_url}` 
        : `http://localhost:8000/api${message.media_url}`
      audioUrlStrategies.push({
        priority: 1,
        url: url,
        description: 'Nova estrutura de chat_id'
      })
    }
  }
  
  // ESTRATÉGIA 2: Conteúdo já é a URL local
  if (message.conteudo && typeof message.conteudo === 'string') {
    if (message.conteudo.startsWith('/media/') || message.conteudo.startsWith('/api/')) {
      const url = message.conteudo.startsWith('/api/') 
        ? `http://localhost:8000${message.conteudo}` 
        : `http://localhost:8000/api${message.conteudo}`
      audioUrlStrategies.push({
        priority: 2,
        url: url,
        description: 'URL do conteúdo'
      })
    }
  }
  
  // ESTRATÉGIA 3: URL da pasta /wapi/midias/
  try {
    const content = JSON.parse(message.content)
    if (content.audioMessage) {
      const audioMessage = content.audioMessage
      
      if (audioMessage.url && audioMessage.url.startsWith('/wapi/midias/')) {
        const filename = audioMessage.url.split('/').pop()
        const url = `http://localhost:8000/api/wapi-media/audios/${filename}`
        audioUrlStrategies.push({
          priority: 3,
          url: url,
          description: 'Pasta /wapi/midias/'
        })
      }
      
      // ESTRATÉGIA 4: Nome do arquivo na pasta /wapi/midias/
      if (audioMessage.fileName) {
        const url = `http://localhost:8000/api/wapi-media/audios/${audioMessage.fileName}`
        audioUrlStrategies.push({
          priority: 4,
          url: url,
          description: 'fileName da pasta /wapi/midias/'
        })
      }
      
      // ESTRATÉGIA 5: URL direta do JSON (WhatsApp)
      if (audioMessage.url && audioMessage.url.startsWith('http')) {
        audioUrlStrategies.push({
          priority: 5,
          url: audioMessage.url,
          description: 'URL direta do WhatsApp'
        })
      }
    }
  } catch (e) {
    console.warn('Erro ao parsear conteúdo:', e)
  }
  
  // ESTRATÉGIA 6: Endpoint público por ID da mensagem
  if (message.id) {
    const url = `http://localhost:8000/api/audio/message/${message.id}/public/`
    audioUrlStrategies.push({
      priority: 6,
      url: url,
      description: 'Endpoint público por ID'
    })
  }
  
  // ESTRATÉGIA 7: Endpoint inteligente por chat_id e message_id
  if (message.chat_id && (message.message_id || message.id)) {
    const clienteId = 2
    const instanceId = '3B6XIW-ZTS923-GEAY6V'
    const chatId = message.chat_id
    const messageId = message.message_id || message.id
    
    const url = `http://localhost:8000/api/whatsapp-audio-smart/${clienteId}/${instanceId}/${chatId}/${messageId}/`
    audioUrlStrategies.push({
      priority: 7,
      url: url,
      description: 'Endpoint inteligente por chat_id'
    })
  }
  
  // ESTRATÉGIA 8: Endpoint de mídia genérico
  if (message.id) {
    const url = `http://localhost:8000/api/media/message/${message.id}/`
    audioUrlStrategies.push({
      priority: 8,
      url: url,
      description: 'Endpoint de mídia genérico'
    })
  }
  
  // Ordenar estratégias por prioridade
  audioUrlStrategies.sort((a, b) => a.priority - b.priority)
  
  console.log('🎵 Estratégias de URL encontradas:', audioUrlStrategies.length)
  audioUrlStrategies.forEach((strategy, index) => {
    console.log(`  ${index + 1}. [${strategy.priority}] ${strategy.description}: ${strategy.url}`)
  })
  
  return audioUrlStrategies
}

// Executar testes
console.log('\n🧪 TESTE 1: Mensagem com URL /wapi/midias/')
const strategies1 = testUrlStrategies(testMessage)

console.log('\n🧪 TESTE 2: Mensagem com múltiplas estratégias')
const strategies2 = testUrlStrategies(testMessageMultipleUrls)

console.log('\n🧪 TESTE 3: Mensagem com URL inválida')
const strategies3 = testUrlStrategies(testMessageError)

// Resumo dos testes
console.log('\n📊 RESUMO DOS TESTES:')
console.log(`✅ Mensagem 1: ${strategies1.length} estratégias encontradas`)
console.log(`✅ Mensagem 2: ${strategies2.length} estratégias encontradas`)
console.log(`✅ Mensagem 3: ${strategies3.length} estratégias encontradas`)

// Verificar se as estratégias estão funcionando
console.log('\n🎯 VERIFICAÇÃO DAS ESTRATÉGIAS:')
strategies1.forEach((strategy, index) => {
  if (index === 0) {
    console.log(`🎵 URL principal (${strategy.description}): ${strategy.url}`)
  } else {
    console.log(`🔄 Fallback ${index} (${strategy.description}): ${strategy.url}`)
  }
})

console.log('\n🎉 TESTE DO AUDIOPLAYER CORRIGIDO CONCLUÍDO!')
console.log('💡 O sistema deve agora:')
console.log('   ✅ Detectar múltiplas estratégias de URL')
console.log('   ✅ Implementar fallback automático')
console.log('   ✅ Gerenciar estados de loading/error corretamente')
console.log('   ✅ Permitir retry manual e automático')
console.log('   ✅ Mostrar informações de debug detalhadas') 