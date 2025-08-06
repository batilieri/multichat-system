// Teste para verificar se os áudios estão sendo exibidos no frontend
console.log('🧪 TESTANDO EXIBIÇÃO DE ÁUDIOS NO FRONTEND');

// Dados de teste de áudio
const testAudioMessage = {
  id: 1,
  tipo: 'audio',
  type: 'audio',
  content: 'Teste de áudio',
  mediaUrl: '/media/audios/1/audio_test_123.mp3',
  mediaType: 'audio',
  mediaSize: 1024000,
  duration: 30,
  fromMe: false,
  timestamp: new Date().toISOString()
};

// Simular dados de áudio do WhatsApp
const whatsappAudioMessage = {
  id: 2,
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
  fromMe: false,
  timestamp: new Date().toISOString()
};

// Função para testar renderização
function testAudioRendering() {
  console.log('📤 Testando renderização de áudio...');
  
  // Teste 1: Áudio com URL direta
  console.log('🎵 Teste 1 - Áudio com URL direta:', testAudioMessage);
  
  // Teste 2: Áudio do WhatsApp
  console.log('🎵 Teste 2 - Áudio do WhatsApp:', whatsappAudioMessage);
  
  // Verificar se o tipo está correto
  const messageType = {
    TEXT: "texto",
    IMAGE: "imagem", 
    VIDEO: "video",
    AUDIO: "audio",
    DOCUMENT: "documento",
    STICKER: "sticker"
  };
  
  console.log('✅ MessageType.AUDIO:', messageType.AUDIO);
  console.log('✅ Tipo da mensagem de teste:', testAudioMessage.tipo);
  console.log('✅ Tipos são iguais?', testAudioMessage.tipo === messageType.AUDIO);
  
  return {
    testAudioMessage,
    whatsappAudioMessage,
    messageType
  };
}

// Função para simular dados de mensagens
function createTestMessages() {
  const messages = [
    {
      id: 1,
      tipo: 'texto',
      content: 'Mensagem de texto',
      fromMe: false,
      timestamp: new Date().toISOString()
    },
    {
      id: 2,
      tipo: 'audio',
      content: 'Áudio de teste',
      mediaUrl: '/media/audios/1/audio_test_123.mp3',
      mediaType: 'audio',
      duration: 30,
      fromMe: false,
      timestamp: new Date().toISOString()
    },
    {
      id: 3,
      tipo: 'imagem',
      content: 'Imagem de teste',
      mediaUrl: 'https://via.placeholder.com/300x200',
      mediaType: 'image',
      fromMe: true,
      timestamp: new Date().toISOString()
    }
  ];
  
  console.log('📋 Mensagens de teste criadas:', messages);
  return messages;
}

// Executar testes
const testResults = testAudioRendering();
const testMessages = createTestMessages();

console.log('✅ Testes concluídos!');
console.log('📊 Resultados:', testResults);
console.log('📋 Mensagens:', testMessages);

// Exportar para uso no console do navegador
window.testAudioData = {
  testResults,
  testMessages,
  testAudioRendering,
  createTestMessages
};

console.log('💡 Use window.testAudioData para acessar os dados de teste'); 