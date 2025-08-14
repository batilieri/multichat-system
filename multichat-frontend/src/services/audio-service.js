// Serviço para gerenciar áudios do backend
class AudioService {
  constructor() {
    this.baseUrl = 'http://localhost:8000/api';
    this.cache = new Map();
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutos
  }

  // Limpar cache expirado
  _cleanExpiredCache() {
    const now = Date.now();
    for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp > this.cacheTimeout) {
        this.cache.delete(key);
      }
    }
  }

  // Gerar chave de cache
  _getCacheKey(chatId, messageId) {
    return `${chatId}_${messageId}`;
  }

  // Buscar áudio por chat_id e message_id
  async getAudioByChatAndMessage(chatId, messageId, clienteId = 2, instanceId = 'DTBDM1-YC2NM5-79C0T4') {
    const cacheKey = this._getCacheKey(chatId, messageId);
    
    // Verificar cache
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheTimeout) {
        return cached.data;
      }
    }

    try {
      // Construir URL para o áudio
      const url = `${this.baseUrl}/whatsapp-audio/${clienteId}/${instanceId}/${chatId}/${messageId}/`;
      
      // Verificar se o áudio existe fazendo uma requisição HEAD
      const response = await fetch(url, { method: 'HEAD' });
      
      if (!response.ok) {
        throw new Error(`Áudio não encontrado: ${response.status}`);
      }

      const audioData = {
        id: messageId,
        chatId,
        clienteId,
        instanceId,
        url,
        title: `Áudio ${messageId}`,
        filename: `msg_${messageId}.ogg`,
        type: 'audio/ogg',
        source: 'whatsapp'
      };

      // Armazenar no cache
      this.cache.set(cacheKey, {
        data: audioData,
        timestamp: Date.now()
      });

      return audioData;
    } catch (error) {
      console.error('Erro ao buscar áudio:', error);
      throw error;
    }
  }

  // Buscar áudio por ID da mensagem
  async getAudioByMessageId(messageId) {
    try {
      const url = `${this.baseUrl}/audio/message/${messageId}/public/`;
      
      const response = await fetch(url, { method: 'HEAD' });
      
      if (!response.ok) {
        throw new Error(`Áudio não encontrado: ${response.status}`);
      }

      return {
        id: messageId,
        url,
        title: `Áudio ${messageId}`,
        filename: `audio_${messageId}.ogg`,
        type: 'audio/ogg',
        source: 'public'
      };
    } catch (error) {
      console.error('Erro ao buscar áudio por ID:', error);
      throw error;
    }
  }

  // Buscar áudio por nome do arquivo
  async getAudioByFilename(filename) {
    try {
      const url = `${this.baseUrl}/local-audio/${encodeURIComponent(filename)}/`;
      
      const response = await fetch(url, { method: 'HEAD' });
      
      if (!response.ok) {
        throw new Error(`Áudio não encontrado: ${response.status}`);
      }

      return {
        id: filename,
        url,
        title: filename,
        filename,
        type: 'audio/ogg',
        source: 'local'
      };
    } catch (error) {
      console.error('Erro ao buscar áudio por nome:', error);
      throw error;
    }
  }

  // Buscar áudio da pasta wapi/midias
  async getAudioFromWapi(filename) {
    try {
      const url = `${this.baseUrl}/wapi-media/audios/${filename}`;
      
      const response = await fetch(url, { method: 'HEAD' });
      
      if (!response.ok) {
        throw new Error(`Áudio não encontrado: ${response.status}`);
      }

      return {
        id: filename,
        url,
        title: filename,
        filename,
        type: 'audio/ogg',
        source: 'wapi'
      };
    } catch (error) {
      console.error('Erro ao buscar áudio da pasta wapi:', error);
      throw error;
    }
  }

  // Buscar áudio inteligente (tenta múltiplas fontes)
  async getAudioSmart(message) {
    try {
      // Prioridade 1: Nova estrutura de armazenamento por chat_id
      if (message.chat_id) {
        try {
          return await this.getAudioByChatAndMessage(
            message.chat_id,
            message.message_id || message.id,
            message.cliente_id || 2,
            message.instance_id || 'DTBDM1-YC2NM5-79C0T4'
          );
        } catch (error) {
          console.log('Falha ao buscar áudio por chat_id, tentando outras fontes...');
        }
      }

      // Prioridade 2: URL da pasta /wapi/midias/ (sistema integrado)
      if (message.content || message.conteudo) {
        try {
          const contentData = typeof message.content === 'string' ? JSON.parse(message.content) : message.content;
          const conteudoData = typeof message.conteudo === 'string' ? JSON.parse(message.conteudo) : message.conteudo;
          
          const audioMessage = contentData?.audioMessage || conteudoData?.audioMessage;
          
          if (audioMessage) {
            if (audioMessage.fileName) {
              try {
                return await this.getAudioFromWapi(audioMessage.fileName);
              } catch (error) {
                console.log('Falha ao buscar áudio da pasta wapi...');
              }
            }
            
            if (audioMessage.localPath) {
              const filename = audioMessage.localPath.split('/').pop();
              try {
                return await this.getAudioByFilename(filename);
              } catch (error) {
                console.log('Falha ao buscar áudio local...');
              }
            }
          }
        } catch (e) {
          console.log('Erro ao processar conteúdo JSON:', e);
        }
      }

      // Prioridade 3: URL processada do backend
      if (message.mediaUrl) {
        if (message.mediaUrl.startsWith('/media/')) {
          return {
            id: message.id,
            url: `${this.baseUrl}${message.mediaUrl}`,
            title: message.filename || `Áudio ${message.id}`,
            filename: message.filename || `audio_${message.id}.ogg`,
            type: 'audio/ogg',
            source: 'media'
          };
        } else if (message.mediaUrl.startsWith('audios/')) {
          return {
            id: message.id,
            url: `${this.baseUrl}/media/${message.mediaUrl}`,
            title: message.filename || `Áudio ${message.id}`,
            filename: message.filename || `audio_${message.id}.ogg`,
            type: 'audio/ogg',
            source: 'media'
          };
        } else if (message.mediaUrl.startsWith('http')) {
          return {
            id: message.id,
            url: message.mediaUrl,
            title: message.filename || `Áudio ${message.id}`,
            filename: message.filename || `audio_${message.id}.ogg`,
            type: 'audio/ogg',
            source: 'external'
          };
        }
      }

      // Fallback: usar endpoint público da API para servir áudio pelo ID da mensagem
      if (message.id) {
        try {
          return await this.getAudioByMessageId(message.id);
        } catch (error) {
          console.log('Falha ao buscar áudio por ID da mensagem...');
        }
      }

      throw new Error('Não foi possível encontrar o áudio em nenhuma fonte');
    } catch (error) {
      console.error('Erro ao buscar áudio inteligente:', error);
      throw error;
    }
  }

  // Verificar se um áudio existe
  async checkAudioExists(url) {
    try {
      const response = await fetch(url, { method: 'HEAD' });
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  // Obter informações do áudio (duração, formato, etc.)
  async getAudioInfo(url) {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      
      return new Promise((resolve, reject) => {
        const audio = new Audio();
        audio.preload = 'metadata';
        
        audio.onloadedmetadata = () => {
          resolve({
            duration: audio.duration,
            size: blob.size,
            type: blob.type,
            url: url
          });
        };
        
        audio.onerror = () => {
          reject(new Error('Erro ao carregar metadados do áudio'));
        };
        
        audio.src = url;
      });
    } catch (error) {
      console.error('Erro ao obter informações do áudio:', error);
      throw error;
    }
  }

  // Buscar áudios de um chat específico
  async getChatAudios(chatId, clienteId = 2, instanceId = 'DTBDM1-YC2NM5-79C0T4') {
    try {
      // Esta função seria implementada se houvesse um endpoint para listar áudios de um chat
      // Por enquanto, retorna um array vazio
      return [];
    } catch (error) {
      console.error('Erro ao buscar áudios do chat:', error);
      throw error;
    }
  }

  // Buscar áudios de um usuário específico
  async getUserAudios(userId) {
    try {
      // Esta função seria implementada se houvesse um endpoint para listar áudios de um usuário
      // Por enquanto, retorna um array vazio
      return [];
    } catch (error) {
      console.error('Erro ao buscar áudios do usuário:', error);
      throw error;
    }
  }

  // Limpar cache
  clearCache() {
    this.cache.clear();
  }

  // Obter estatísticas do cache
  getCacheStats() {
    this._cleanExpiredCache();
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys())
    };
  }
}

// Instância singleton do serviço
const audioService = new AudioService();

export default audioService; 