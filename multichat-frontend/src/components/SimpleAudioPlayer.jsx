import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Volume2, Play, Pause, Download, Heart, Share2, MoreVertical } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

const SimpleAudioPlayer = ({ message, isOwnMessage = false }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  
  const audioRef = useRef(null);

  // Determinar URL do áudio
  useEffect(() => {
    let url = null;
    
    try {
      // Prioridade 1: Nova estrutura de armazenamento por chat_id
      if (message.chat_id) {
        const chatId = message.chat_id;
        const clienteId = message.cliente_id || 2;
        // **CORREÇÃO: Usar a instância correta onde estão os arquivos**
        const instanceId = message.instance_id || 'DTBDM1-YC2NM5-79C0T4';
        const messageId = message.message_id || message.id;
        
        url = `http://localhost:8000/api/whatsapp-audio/${clienteId}/${instanceId}/${chatId}/${messageId}/`;
        console.log('🎵 URL por chat_id:', url);
      }
      // Prioridade 2: URL da pasta /wapi/midias/ (sistema integrado)
      else if (message.content || message.conteudo) {
        try {
          const contentData = typeof message.content === 'string' ? JSON.parse(message.content) : message.content;
          const conteudoData = typeof message.conteudo === 'string' ? JSON.parse(message.conteudo) : message.conteudo;
          
          const audioMessage = contentData?.audioMessage || conteudoData?.audioMessage;
          
          if (audioMessage) {
            if (audioMessage.localPath) {
              const filename = audioMessage.fileName || audioMessage.localPath.split('/').pop();
              url = `http://localhost:8000/api/local-audio/${encodeURIComponent(filename)}/`;
            } else if (audioMessage.url) {
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
        console.log('🎵 URL final do áudio:', url);
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
        audioRef.current.play().catch(e => {
          console.error('Erro ao reproduzir áudio:', e);
          setError('Erro ao reproduzir áudio');
        });
      }
    }
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  // Se há erro, mostrar mensagem
  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-3 p-3 bg-red-50 border border-red-200 rounded-lg"
      >
        <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
          <Volume2 className="w-5 h-5 text-red-600" />
        </div>
        <div className="flex-1">
          <p className="text-sm text-red-800">Erro ao carregar áudio</p>
          <p className="text-xs text-red-600">{error}</p>
        </div>
      </motion.div>
    );
  }

  // Se está carregando, mostrar loading
  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-3 p-3 bg-gray-50 border border-gray-200 rounded-lg"
      >
        <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
          <div className="w-5 h-5 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"></div>
        </div>
        <div className="flex-1">
          <p className="text-sm text-gray-800">Carregando áudio...</p>
        </div>
      </motion.div>
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
      {/* Ícone de áudio */}
      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
        isOwnMessage ? 'bg-green-400' : 'bg-orange-100'
      }`}>
        <Volume2 className={`w-5 h-5 ${isOwnMessage ? 'text-white' : 'text-orange-600'}`} />
      </div>

      {/* Controles de áudio */}
      <div className="flex-1 min-w-0">
        {/* Botão Play/Pause */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={togglePlay}
          className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isOwnMessage ? 'bg-white text-green-500' : 'bg-orange-500 text-white'
          }`}
        >
          {isPlaying ? (
            <Pause className="w-4 h-4" />
          ) : (
            <Play className="w-4 h-4 ml-0.5" />
          )}
        </motion.button>

        {/* Informações do áudio */}
        <div className="mt-2">
          <p className={`text-xs ${isOwnMessage ? 'text-white' : 'text-gray-600'}`}>
            {formatTime(currentTime)} / {formatTime(duration)}
          </p>
          
          {/* Barra de progresso simples */}
          <div className="mt-1 h-1 bg-gray-300 rounded-full overflow-hidden">
            <div 
              className={`h-full ${isOwnMessage ? 'bg-white' : 'bg-orange-500'}`}
              style={{ width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%` }}
            />
          </div>
        </div>
      </div>

      {/* Botões de ação */}
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0"
          title="Favoritar"
        >
          <Heart className="w-4 h-4" />
        </Button>
        
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0"
          title="Download"
        >
          <Download className="w-4 h-4" />
        </Button>
        
        <Button
          variant="ghost"
          size="sm"
          className="h-8 w-8 p-0"
          title="Mais opções"
        >
          <MoreVertical className="w-4 h-4" />
        </Button>
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

export default SimpleAudioPlayer; 