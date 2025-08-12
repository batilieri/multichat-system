// Script para testar detecção de áudio no navegador
console.log('🎵 TESTE DE DETECÇÃO DE ÁUDIO');

// Função para testar dados de áudio
function testAudioDetection() {
  console.log('🧪 Testando detecção de áudio...');
  
  // Dados de teste baseados na mensagem real
  const testMessage = {
    id: 861,
    tipo: 'audio',
    type: 'audio',
    content: '[Áudio]',
    conteudo: '{"audioMessage": {"url": "https://mmg.whatsapp.net/v/t62.7117-24/11418572_639123605874985_2074276734782391920_n.enc?ccb=11-4&oh=01_Q5Aa2AH90VmSBOTtBIXsGxf0r5vMtkmkC4BsJLVg9s4HdByRdQ&oe=68B5B693&_nc_sid=5e03e0&mms3=true", "mimetype": "audio/ogg; codecs=opus", "fileSha256": "+ylX/pg8Tsa+zRJ8fgO0rpPycxdXtmLUZvZeZybjRAE=", "fileLength": "20718", "seconds": 8, "ptt": true, "mediaKey": "FnIfz9Ka/QzEPkAzlOQ9x0m3WBwUQaG265dvhLjnFl0="}}',
    mediaUrl: null,
    mediaType: null,
    from_me: false,
    fromMe: false,
    isOwn: false,
    data_envio: '2025-08-02T16:15:23.752936+00:00',
    timestamp: '2025-08-02T16:15:23.752936+00:00',
    sender: '556993291093',
    status: 'sent'
  };
  
  console.log('📄 Mensagem de teste:', testMessage);
  
  // Simular processamento do ChatView
  let conteudoProcessado = testMessage.conteudo;
  let mediaUrl = null;
  let mediaType = null;
  
  if (typeof conteudoProcessado === 'string' && conteudoProcessado.startsWith('{')) {
    try {
      const jsonContent = JSON.parse(conteudoProcessado);
      console.log('📄 JSON Content:', jsonContent);
      
      if (jsonContent.audioMessage) {
        mediaUrl = jsonContent.audioMessage.url;
        mediaType = 'audio';
        conteudoProcessado = '[Áudio]';
        console.log('✅ Áudio detectado:', { mediaUrl, mediaType, conteudoProcessado });
      }
    } catch (error) {
      console.error('❌ Erro ao processar JSON:', error);
    }
  }
  
  const processedMessage = {
    ...testMessage,
    content: conteudoProcessado,
    mediaUrl: mediaUrl,
    mediaType: mediaType
  };
  
  console.log('🔄 Mensagem processada:', processedMessage);
  
  // Verificar se seria renderizado como áudio
  const tipo = processedMessage.tipo || processedMessage.type;
  console.log('🎯 Tipo da mensagem:', tipo);
  console.log('🎯 Seria renderizado como áudio?', tipo === 'audio');
  
  return processedMessage;
}

// Função para verificar MessageType
function checkMessageType() {
  console.log('🔍 Verificando MessageType...');
  
  // Tentar acessar MessageType de diferentes formas
  const possiblePaths = [
    'MessageType',
    'window.MessageType',
    'global.MessageType',
    'this.MessageType'
  ];
  
  possiblePaths.forEach(path => {
    try {
      const value = eval(path);
      if (value && value.AUDIO) {
        console.log(`✅ ${path}.AUDIO:`, value.AUDIO);
      }
    } catch (e) {
      console.log(`❌ ${path} não encontrado`);
    }
  });
}

// Função para verificar componentes React
function checkReactComponents() {
  console.log('⚛️ Verificando componentes React...');
  
  // Verificar se estamos no contexto do React
  if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
    console.log('✅ React DevTools disponível');
    
    // Tentar encontrar componentes
    const components = window.__REACT_DEVTOOLS_GLOBAL_HOOK__.renderers;
    if (components) {
      console.log('📦 Renderers disponíveis:', Object.keys(components));
    }
  } else {
    console.log('❌ React DevTools não disponível');
  }
}

// Função para simular renderização
function simulateRendering(message) {
  console.log('🎨 Simulando renderização...');
  
  const tipo = message.tipo || message.type;
  console.log('🎯 Tipo:', tipo);
  
  if (tipo === 'audio') {
    console.log('✅ Seria renderizado como AudioPlayer');
    
    // Verificar se tem dados necessários
    const hasUrl = message.mediaUrl || (message.content && message.content.includes('audioMessage'));
    console.log('📁 Tem URL?', hasUrl);
    
    if (hasUrl) {
      console.log('✅ Dados suficientes para renderizar áudio');
    } else {
      console.log('❌ Faltam dados para renderizar áudio');
    }
  } else {
    console.log('❌ NÃO seria renderizado como áudio');
  }
}

// Executar testes
console.log('🚀 Iniciando testes...');
checkMessageType();
checkReactComponents();
const testMessage = testAudioDetection();
simulateRendering(testMessage);

// Adicionar ao console global
window.testAudio = {
  testAudioDetection,
  checkMessageType,
  checkReactComponents,
  simulateRendering,
  testMessage
};

console.log('✅ Funções de teste disponíveis em window.testAudio');
console.log('💡 Use: window.testAudio.testAudioDetection() para testar novamente'); 