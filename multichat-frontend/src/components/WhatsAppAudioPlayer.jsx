import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Play, Pause, Mic, Loader2 } from 'lucide-react';

const WhatsAppAudioPlayer = ({ message, isOwnMessage = false }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const audioRef = useRef(null);

  // Determinar URL do áudio
  useEffect(() => {
    let url = null;
    
    try {
      // Prioridade 1: Nova estrutura de armazenamento por chat_id
      if (message.chat_id) {
        const chatId = message.chat_id;
        const clienteId = 2; // Cliente Elizeu
        const instanceId = '3B6XIW-ZTS923-GEAY6V';
        const messageId = message.message_id || message.id;
        
        // Construir URL para arquivos na pasta media_storage
        url = `http://localhost:8000/api/whatsapp-audio/${clienteId}/${instanceId}/${chatId}/${messageId}/`;
      }
      // Prioridade 2: URL da pasta /wapi/midias/ (sistema integrado)
      else if (message.content || message.conteudo) {
        try {
          const contentData = typeof message.content === 'string' ? JSON.parse(message.content) : message.content;
          const conteudoData = typeof message.conteudo === 'string' ? JSON.parse(message.conteudo) : message.conteudo;
          
          const audioMessage = contentData?.audioMessage || conteudoData?.audioMessage;
          
          if (audioMessage) {
            if (audioMessage.localPath) {
              // Usar caminho local se disponível
              const filename = audioMessage.fileName || audioMessage.localPath.split('/').pop();
              url = `http://localhost:8000/api/local-audio/${encodeURIComponent(filename)}/`;
            } else if (audioMessage.url) {
              // Usar URL se disponível
              url = audioMessage.url.startsWith('http') ? audioMessage.url : `http://localhost:8000${audioMessage.url}`;
            }
          }
        } catch (e) {
          console.log('Erro ao processar conteúdo JSON:', e);
        }
      }
      
      // Fallback: usar endpoint público da API para servir áudio pelo ID da mensagem
      if (!url && message.id) {
        url = `http://localhost:8000/api/audio/message/${message.id}/public/`;
      }
      
      if (url) {
        setAudioUrl(url);
      } else {
        setError('Não foi possível obter URL do áudio');
        setIsLoading(false);
      }
    } catch (e) {
      console.error('Erro ao determinar URL do áudio:', e);
      setError('Erro ao processar áudio');
      setIsLoading(false);
    }
  }, [message]);

  const [audioUrl, setAudioUrl] = useState(null);

  // Configurar áudio quando URL estiver disponível
  useEffect(() => {
    if (!audioUrl) return;

    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const updateDuration = () => setDuration(audio.duration);
    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };
    const handleLoadedData = () => {
      setIsLoading(false);
      setDuration(audio.duration);
      setError(null);
    };
    const handleError = (e) => {
      console.error('Erro ao carregar áudio:', e);
      setError('Erro ao carregar áudio');
      setIsLoading(false);
    };

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('loadedmetadata', updateDuration);
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('loadeddata', handleLoadedData);
    audio.addEventListener('error', handleError);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('loadedmetadata', updateDuration);
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('loadeddata', handleLoadedData);
      audio.removeEventListener('error', handleError);
    };
  }, [audioUrl]);

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
    }
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  // Gerar waveform visual (simulado)
  const generateWaveform = () => {
    const bars = 20;
    const waveform = [];
    for (let i = 0; i < bars; i++) {
      // Simular altura baseada na posição e duração
      const height = Math.random() * 0.6 + 0.2; // Entre 20% e 80%
      waveform.push(height);
    }
    return waveform;
  };

  const waveform = generateWaveform();

  // Se há erro, mostrar mensagem
  if (error) {
    return (
      <div className="flex items-center gap-3 p-3 bg-red-50 border border-red-200 rounded-lg">
        <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
          <Mic className="w-5 h-5 text-red-600" />
        </div>
        <div className="flex-1">
          <p className="text-sm text-red-800">Erro ao carregar áudio</p>
          <p className="text-xs text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  // Se está carregando, mostrar loading
  if (isLoading) {
    return (
      <div className="flex items-center gap-3 p-3 bg-gray-50 border border-gray-200 rounded-lg">
        <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
          <Loader2 className="w-5 h-5 text-gray-600 animate-spin" />
        </div>
        <div className="flex-1">
          <p className="text-sm text-gray-800">Carregando áudio...</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex items-center gap-3 p-3 rounded-lg max-w-sm ${
        isOwnMessage 
          ? 'bg-green-500 text-white' 
          : 'bg-white border border-gray-200 text-gray-800'
      }`}
    >
      {/* Foto de perfil com ícone de microfone */}
      <div className="relative">
        <div className={`w-10 h-10 rounded-full overflow-hidden ${
          isOwnMessage ? 'bg-green-400' : 'bg-gray-200'
        }`}>
          {/* Foto de perfil simulada */}
          <div className="w-full h-full flex items-center justify-center text-xs">
            {message.remetente ? message.remetente.slice(-2) : '??'}
          </div>
        </div>
        {/* Ícone de microfone sobreposto */}
        <div className={`absolute -bottom-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center ${
          isOwnMessage ? 'bg-green-600' : 'bg-green-500'
        }`}>
          <Mic className="w-3 h-3 text-white" />
        </div>
      </div>

      {/* Controles de áudio */}
      <div className="flex-1 min-w-0">
        {/* Botão Play/Pause */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={togglePlay}
          className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isOwnMessage ? 'bg-white text-green-500' : 'bg-green-500 text-white'
          }`}
        >
          {isPlaying ? (
            <Pause className="w-4 h-4" />
          ) : (
            <Play className="w-4 h-4 ml-0.5" />
          )}
        </motion.button>

        {/* Indicador de progresso */}
        <div className="mt-2">
          <div className="flex items-center gap-2">
            {/* Ponto de progresso */}
            <div className={`w-2 h-2 rounded-full ${
              isOwnMessage ? 'bg-white' : 'bg-green-500'
            }`} />
            
            {/* Linha pontilhada */}
            <div className="flex-1 h-0.5 bg-gray-300 relative">
              <div 
                className={`h-full ${
                  isOwnMessage ? 'bg-white' : 'bg-green-500'
                }`}
                style={{ width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%` }}
              />
            </div>
          </div>
          
          {/* Tempo atual */}
          <p className={`text-xs mt-1 ${
            isOwnMessage ? 'text-white' : 'text-gray-600'
          }`}>
            {formatTime(currentTime)}
          </p>
        </div>
      </div>

      {/* Waveform visual */}
      <div className="flex items-end gap-0.5 h-12">
        {waveform.map((height, index) => (
          <div
            key={index}
            className={`w-1 rounded-full ${
              isOwnMessage ? 'bg-white' : 'bg-green-500'
            }`}
            style={{ height: `${height * 100}%` }}
          />
        ))}
      </div>

      {/* Tempo total e status */}
      <div className="text-right">
        <p className={`text-xs ${
          isOwnMessage ? 'text-white' : 'text-gray-600'
        }`}>
          {formatTime(duration)}
        </p>
        {/* Indicador de status para mensagens próprias */}
        {isOwnMessage && (
          <div className="flex justify-end mt-1">
            <div className="flex">
              <div className="w-3 h-3 border border-white rounded-full" />
              <div className="w-3 h-3 border border-white rounded-full ml-0.5" />
            </div>
          </div>
        )}
      </div>

      {/* Player de áudio oculto */}
      <audio 
        ref={audioRef}
        className="hidden"
        preload="metadata"
        src={audioUrl}
        onError={(e) => {
          console.error('Erro ao carregar áudio:', e);
          setError('Erro ao carregar áudio');
          setIsLoading(false);
        }}
      />
    </motion.div>
  );
};

export default WhatsAppAudioPlayer; 