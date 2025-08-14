import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Pause, 
  Mic, 
  Loader2, 
  Heart, 
  Download, 
  Share2, 
  MoreVertical,
  Volume2,
  VolumeX,
  SkipBack,
  SkipForward,
  Repeat,
  Shuffle,
  Clock,
  FileAudio,
  AlertTriangle,
  CheckCircle,
  X
} from 'lucide-react';
import { Button } from './ui/button';
import { Slider } from './ui/slider';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from './ui/dropdown-menu';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from './ui/dialog';
import { Badge } from './ui/badge';
import { useToast } from './ui/use-toast';
import audioService from '../services/audio-service';

const AdvancedAudioPlayer = ({ 
  message, 
  isOwnMessage = false, 
  onReaction,
  onForward,
  onDelete,
  onFavorite,
  showAdvancedControls = true 
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [showVolumeSlider, setShowVolumeSlider] = useState(false);
  const [isLooping, setIsLooping] = useState(false);
  const [isShuffled, setIsShuffled] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [showAdvancedModal, setShowAdvancedModal] = useState(false);
  const [reactions, setReactions] = useState(message.reacoes || message.reactions || []);
  const [isFavorited, setIsFavorited] = useState(message.isFavorited || false);
  
  const audioRef = useRef(null);
  const { toast } = useToast();

  // Determinar URL do áudio usando o serviço inteligente ou fallback
  useEffect(() => {
    const fetchAudio = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        let audioData = null;
        
        // Tentar usar o serviço inteligente primeiro
        try {
          audioData = await audioService.getAudioSmart(message);
        } catch (serviceError) {
          console.log('Serviço de áudio não disponível, usando fallback:', serviceError);
        }
        
        // Se o serviço não funcionou, usar fallback
        if (!audioData || !audioData.url) {
          // Fallback: tentar construir URL baseada na estrutura da mensagem
          if (message.chat_id) {
            const chatId = message.chat_id;
            const clienteId = message.cliente_id || 2;
            const instanceId = message.instance_id || 'DTBDM1-YC2NM5-79C0T4';
            const messageId = message.message_id || message.id;
            
            audioData = {
              id: messageId,
              url: `http://localhost:8000/api/whatsapp-audio/${clienteId}/${instanceId}/${chatId}/${messageId}/`,
              title: `Áudio ${messageId}`,
              filename: `msg_${messageId}.ogg`,
              type: 'audio/ogg'
            };
          } else if (message.id) {
            // Fallback para mensagens com ID
            audioData = {
              id: message.id,
              url: `http://localhost:8000/api/audio/message/${message.id}/public/`,
              title: `Áudio ${message.id}`,
              filename: `audio_${message.id}.ogg`,
              type: 'audio/ogg'
            };
          }
        }
        
        if (audioData && audioData.url) {
          setAudioUrl(audioData.url);
          console.log('🎵 Áudio encontrado:', audioData);
        } else {
          setError('Não foi possível obter dados do áudio');
        }
      } catch (error) {
        console.error('Erro ao buscar áudio:', error);
        setError(`Erro ao buscar áudio: ${error.message}`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAudio();
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
      if (isLooping) {
        audio.play();
      }
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
  }, [audioUrl, isLooping]);

  // Configurar volume e playback rate
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume;
      audioRef.current.playbackRate = playbackRate;
    }
  }, [volume, isMuted, playbackRate]);

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

  const handleSliderChange = (value) => {
    if (audioRef.current && duration > 0) {
      const newTime = (value[0] / 100) * duration;
      audioRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const handleVolumeChange = (value) => {
    const newVolume = value[0] / 100;
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const skipTime = (seconds) => {
    if (audioRef.current) {
      const newTime = Math.max(0, Math.min(duration, currentTime + seconds));
      audioRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const toggleLoop = () => {
    setIsLooping(!isLooping);
  };

  const toggleShuffle = () => {
    setIsShuffled(!isShuffled);
  };

  const changePlaybackRate = (rate) => {
    setPlaybackRate(rate);
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleReaction = (emoji) => {
    const newReactions = [...reactions];
    const existingIndex = newReactions.findIndex(r => r.emoji === emoji);
    
    if (existingIndex >= 0) {
      newReactions[existingIndex].count++;
    } else {
      newReactions.push({ emoji, count: 1 });
    }
    
    setReactions(newReactions);
    if (onReaction) {
      onReaction(message.id, emoji);
    }
  };

  const handleFavorite = () => {
    setIsFavorited(!isFavorited);
    if (onFavorite) {
      onFavorite(message.id, !isFavorited);
    }
  };

  const handleDownload = () => {
    if (audioUrl) {
      const link = document.createElement('a');
      link.href = audioUrl;
      link.download = `audio_${message.message_id || message.id || Date.now()}.ogg`;
      link.click();
      
      toast({
        title: "Download iniciado",
        description: "O áudio está sendo baixado...",
      });
    }
  };

  const handleForward = () => {
    if (onForward) {
      onForward(message);
    }
  };

  const handleDelete = () => {
    if (onDelete) {
      onDelete(message.id);
    }
  };

  // Gerar waveform visual (simulado)
  const generateWaveform = () => {
    const bars = 30;
    const waveform = [];
    for (let i = 0; i < bars; i++) {
      const height = Math.random() * 0.7 + 0.3;
      waveform.push(height);
    }
    return waveform;
  };

  const waveform = generateWaveform();
  const sliderValue = duration > 0 ? [(currentTime / duration) * 100] : [0];
  const volumeSliderValue = [volume * 100];

  // Se há erro, mostrar mensagem
  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-3 p-3 bg-red-50 border border-red-200 rounded-lg"
      >
        <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
          <AlertTriangle className="w-5 h-5 text-red-600" />
        </div>
        <div className="flex-1">
          <p className="text-sm text-red-800">Erro ao carregar áudio</p>
          <p className="text-xs text-red-600">{error}</p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => window.location.reload()}
        >
          Tentar novamente
        </Button>
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
          <Loader2 className="w-5 h-5 text-gray-600 animate-spin" />
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
      className={`flex flex-col gap-3 p-4 rounded-lg max-w-md ${
        isOwnMessage 
          ? 'bg-green-500 text-white' 
          : 'bg-white border border-gray-200 text-gray-800'
      }`}
    >
      {/* Cabeçalho com informações da mensagem */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="relative">
            <div className={`w-8 h-8 rounded-full overflow-hidden ${
              isOwnMessage ? 'bg-green-400' : 'bg-gray-200'
            }`}>
              <div className="w-full h-full flex items-center justify-center text-xs">
                {message.remetente ? message.remetente.slice(-2) : '??'}
              </div>
            </div>
            <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full flex items-center justify-center ${
              isOwnMessage ? 'bg-green-600' : 'bg-green-500'
            }`}>
              <Mic className="w-2 h-2 text-white" />
            </div>
          </div>
          <div>
            <p className="text-sm font-medium">
              {message.remetente || 'Usuário'}
            </p>
            <p className="text-xs opacity-75">
              {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : ''}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-1">
          {isFavorited && (
            <Heart className="w-4 h-4 fill-current text-red-500" />
          )}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <MoreVertical className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={handleFavorite}>
                <Heart className="w-4 h-4 mr-2" />
                {isFavorited ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleDownload}>
                <Download className="w-4 h-4 mr-2" />
                Baixar áudio
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleForward}>
                <Share2 className="w-4 h-4 mr-2" />
                Encaminhar
              </DropdownMenuItem>
              {onDelete && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleDelete} className="text-red-600">
                    <X className="w-4 h-4 mr-2" />
                    Excluir
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Controles principais */}
      <div className="flex items-center gap-3">
        {/* Botão Play/Pause */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={togglePlay}
          className={`w-12 h-12 rounded-full flex items-center justify-center ${
            isOwnMessage ? 'bg-white text-green-500' : 'bg-green-500 text-white'
          }`}
        >
          {isPlaying ? (
            <Pause className="w-6 h-6" />
          ) : (
            <Play className="w-6 h-6 ml-1" />
          )}
        </motion.button>

        {/* Informações do áudio */}
        <div className="flex-1 min-w-0">
          <p className="font-medium truncate">
            {message.filename || 'Áudio'}
          </p>
          <p className="text-xs opacity-75">
            {formatTime(currentTime)} / {formatTime(duration)}
          </p>
        </div>

        {/* Controles de volume */}
        <div className="relative">
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleMute}
            className="h-8 w-8 p-0"
          >
            {isMuted ? (
              <VolumeX className="w-4 h-4" />
            ) : (
              <Volume2 className="w-4 h-4" />
            )}
          </Button>
          
          <AnimatePresence>
            {showVolumeSlider && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 p-2 bg-white border border-gray-200 rounded-lg shadow-lg"
                onMouseEnter={() => setShowVolumeSlider(true)}
                onMouseLeave={() => setShowVolumeSlider(false)}
              >
                <Slider
                  value={volumeSliderValue}
                  onValueChange={handleVolumeChange}
                  max={100}
                  step={1}
                  orientation="vertical"
                  className="h-20"
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Slider de progresso */}
      <div className="space-y-2">
        <Slider
          value={sliderValue}
          onValueChange={handleSliderChange}
          max={100}
          step={0.1}
          className="w-full"
        />
        <div className="flex justify-between text-xs opacity-75">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* Controles avançados */}
      {showAdvancedControls && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => skipTime(-10)}
              className="h-8 w-8 p-0"
            >
              <SkipBack className="w-4 h-4" />
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => skipTime(10)}
              className="h-8 w-8 p-0"
            >
              <SkipForward className="w-4 h-4" />
            </Button>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant={isLooping ? "default" : "ghost"}
              size="sm"
              onClick={toggleLoop}
              className="h-8 w-8 p-0"
            >
              <Repeat className="w-4 h-4" />
            </Button>
            
            <Button
              variant={isShuffled ? "default" : "ghost"}
              size="sm"
              onClick={toggleShuffle}
              className="h-8 w-8 p-0"
            >
              <Shuffle className="w-4 h-4" />
            </Button>
          </div>

          <Dialog>
            <DialogTrigger asChild>
              <Button variant="ghost" size="sm" className="h-8 px-2">
                <Clock className="w-4 h-4 mr-1" />
                {playbackRate}x
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Velocidade de reprodução</DialogTitle>
              </DialogHeader>
              <div className="grid grid-cols-3 gap-2">
                {[0.5, 0.75, 1, 1.25, 1.5, 2].map(rate => (
                  <Button
                    key={rate}
                    variant={playbackRate === rate ? "default" : "outline"}
                    onClick={() => changePlaybackRate(rate)}
                    className="w-full"
                  >
                    {rate}x
                  </Button>
                ))}
              </div>
            </DialogContent>
          </Dialog>
        </div>
      )}

      {/* Waveform visual */}
      <div className="flex items-end gap-0.5 h-16">
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

      {/* Reações */}
      {reactions.length > 0 && (
        <div className="flex items-center gap-2 flex-wrap">
          {reactions.map((reaction, index) => (
            <Badge key={index} variant="secondary" className="text-xs">
              {reaction.emoji} {reaction.count}
            </Badge>
          ))}
        </div>
      )}

      {/* Botões de reação rápida */}
      <div className="flex items-center gap-2">
        {['👍', '❤️', '😂', '😮', '😢', '😡'].map(emoji => (
          <Button
            key={emoji}
            variant="ghost"
            size="sm"
            onClick={() => handleReaction(emoji)}
            className="h-8 w-8 p-0 text-lg"
          >
            {emoji}
          </Button>
        ))}
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

export default AdvancedAudioPlayer; 