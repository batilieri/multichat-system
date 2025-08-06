// Script para debug do frontend - Áudios
console.log('🎵 DEBUG AUDIO FRONTEND');

// Verificar se MessageType está definido corretamente
if (typeof MessageType !== 'undefined') {
  console.log('✅ MessageType.AUDIO:', MessageType.AUDIO);
} else {
  console.log('❌ MessageType não está definido');
}

// Verificar mensagens no localStorage ou estado
function checkMessages() {
  console.log('🔍 Verificando mensagens...');
  
  // Verificar se há mensagens no localStorage
  const storedMessages = localStorage.getItem('messages');
  if (storedMessages) {
    console.log('📦 Mensagens no localStorage:', JSON.parse(storedMessages));
  }
  
  // Verificar se há mensagens no estado do React
  if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
    console.log('⚛️ React DevTools disponível');
  }
}

// Função para simular dados de áudio
function createTestAudioMessage() {
  const testMessage = {
    id: 999,
    tipo: 'audio',
    type: 'audio',
    content: JSON.stringify({
      audioMessage: {
        url: "https://mmg.whatsapp.net/v/t62.7117-24/11418572_639123605874985_2074276734782391920_n.enc?ccb=11-4&oh=01_Q5Aa2AH90VmSBOTtBIXsGxf0r5vMtkmkC4BsJLVg9s4HdByRdQ&oe=68B5B693&_nc_sid=5e03e0&mms3=true",
        mimetype: "audio/ogg; codecs=opus",
        fileSha256: "+ylX/pg8Tsa+zRJ8fgO0rpPycxdXtmLUZvZeZybjRAE=",
        fileLength: "20718",
        seconds: 8,
        ptt: true,
        mediaKey: "FnIfz9Ka/QzEPkAzlOQ9x0m3WBwUQaG265dvhLjnFl0="
      }
    }),
    conteudo: JSON.stringify({
      audioMessage: {
        url: "https://mmg.whatsapp.net/v/t62.7117-24/11418572_639123605874985_2074276734782391920_n.enc?ccb=11-4&oh=01_Q5Aa2AH90VmSBOTtBIXsGxf0r5vMtkmkC4BsJLVg9s4HdByRdQ&oe=68B5B693&_nc_sid=5e03e0&mms3=true",
        mimetype: "audio/ogg; codecs=opus",
        fileSha256: "+ylX/pg8Tsa+zRJ8fgO0rpPycxdXtmLUZvZeZybjRAE=",
        fileLength: "20718",
        seconds: 8,
        ptt: true,
        mediaKey: "FnIfz9Ka/QzEPkAzlOQ9x0m3WBwUQaG265dvhLjnFl0="
      }
    }),
    from_me: false,
    fromMe: false,
    isOwn: false,
    data_envio: new Date().toISOString(),
    timestamp: new Date().toISOString(),
    sender: "556993291093",
    status: "sent"
  };
  
  console.log('🧪 Mensagem de teste criada:', testMessage);
  return testMessage;
}

// Função para testar renderização
function testAudioRendering() {
  console.log('🎵 Testando renderização de áudio...');
  
  const testMessage = createTestAudioMessage();
  
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
  console.log('🎯 MessageType.AUDIO:', MessageType?.AUDIO);
  console.log('🎯 Seria renderizado como áudio?', tipo === MessageType?.AUDIO);
  
  return processedMessage;
}

// Função para verificar componentes
function checkComponents() {
  console.log('🔧 Verificando componentes...');
  
  // Verificar se AudioPlayer está disponível
  if (typeof AudioPlayer !== 'undefined') {
    console.log('✅ AudioPlayer está disponível');
  } else {
    console.log('❌ AudioPlayer não está disponível');
  }
  
  // Verificar se renderMessageContent está disponível
  if (typeof renderMessageContent !== 'undefined') {
    console.log('✅ renderMessageContent está disponível');
  } else {
    console.log('❌ renderMessageContent não está disponível');
  }
}

// Executar debug
console.log('🚀 Iniciando debug...');
checkMessages();
checkComponents();
const testMessage = testAudioRendering();

// Adicionar ao console global para acesso
window.debugAudio = {
  checkMessages,
  checkComponents,
  testAudioRendering,
  createTestAudioMessage,
  testMessage
};

console.log('✅ Debug functions disponíveis em window.debugAudio');
console.log('💡 Use: window.debugAudio.testAudioRendering() para testar novamente'); 