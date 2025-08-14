import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Pause, 
  SkipBack, 
  SkipForward, 
  Volume2, 
  VolumeX,
  Repeat,
  Shuffle,
  List,
  X,
  Settings,
  Download,
  Share2,
  Heart,
  Clock,
  FileAudio,
  ChevronUp,
  ChevronDown
} from 'lucide-react';
import { Button } from './ui/button';
import { Slider } from './ui/slider';
import { Badge } from './ui/badge';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from './ui/dialog';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from './ui/dropdown-menu';
import { useAudioPlayerContext } from '../contexts/AudioPlayerContext';
import { useToast } from './ui/use-toast';

const GlobalAudioPlayer = () => {
  const {
    currentAudio,
    isPlaying,
    currentTime,
    duration,
    volume,
    isMuted,
    playbackRate,
    isLooping,
    isShuffled,
    queue,
    currentIndex,
    hasAudio,
    globalVolume,
    globalMuted,
    crossfade,
    equalizer,
    effects,
    
    // Controles
    play,
    pause,
    stop,
    seek,
    setVolume,
    toggleMute,
    setPlaybackRate,
    toggleLoop,
    toggleShuffle,
    addToQueue,
    removeFromQueue,
    clearQueue,
    playNext,
    playPrevious,
    shuffleQueue,
    setGlobalVolume,
    toggleGlobalMute,
    toggleCrossfade,
    setEqualizerBand,
    toggleEqualizer,
    toggleEffect,
    
    // Funções de utilidade
    getCurrentAudioInfo,
    getQueueInfo,
    formatTime
  } = useAudioPlayerContext();

  const [showQueue, setShowQueue] = useState(false);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const { toast } = useToast();

  // Se não há áudio, não mostrar o player
  if (!hasAudio) {
    return null;
  }

  const audioInfo = getCurrentAudioInfo();
  const queueInfo = getQueueInfo();

  const handlePlayPause = () => {
    if (isPlaying) {
      pause();
    } else if (currentAudio) {
      play(currentAudio);
    }
  };

  const handleSeek = (value) => {
    if (duration > 0) {
      const time = (value[0] / 100) * duration;
      seek(time);
    }
  };

  const handleVolumeChange = (value) => {
    const newVolume = value[0] / 100;
    setVolume(newVolume);
  };

  const handleSkip = (seconds) => {
    const newTime = Math.max(0, Math.min(duration, currentTime + seconds));
    seek(newTime);
  };

  const handleDownload = () => {
    if (currentAudio?.url) {
      const link = document.createElement('a');
      link.href = currentAudio.url;
      link.download = `audio_${currentAudio.id || Date.now()}.ogg`;
      link.click();
      
      toast({
        title: "Download iniciado",
        description: "O áudio está sendo baixado...",
      });
    }
  };

  const handleShare = () => {
    if (navigator.share && currentAudio) {
      navigator.share({
        title: 'Áudio do MultiChat',
        text: `Ouça este áudio: ${currentAudio.title || 'Áudio'}`,
        url: currentAudio.url
      });
    } else {
      // Fallback: copiar URL para clipboard
      navigator.clipboard.writeText(currentAudio?.url || '');
      toast({
        title: "URL copiada",
        description: "A URL do áudio foi copiada para a área de transferência",
      });
    }
  };

  const handleFavorite = () => {
    // Implementar lógica de favoritos
    toast({
      title: "Favorito",
      description: "Funcionalidade de favoritos em desenvolvimento",
    });
  };

  const sliderValue = duration > 0 ? [(currentTime / duration) * 100] : [0];
  const volumeSliderValue = [volume * 100];

  return (
    <AnimatePresence>
      <motion.div
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 100, opacity: 0 }}
        className={`fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50 transition-all duration-300 ${
          isMinimized ? 'h-16' : 'h-24'
        }`}
      >
        {/* Barra principal do player */}
        <div className="flex items-center justify-between px-4 py-2 h-full">
          {/* Informações do áudio atual */}
          <div className="flex items-center gap-3 flex-1 min-w-0">
            {/* Thumbnail/ícone */}
            <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center text-white flex-shrink-0">
              <FileAudio className="w-6 h-6" />
            </div>
            
            {/* Detalhes do áudio */}
            <div className="flex-1 min-w-0">
              <p className="font-medium text-sm truncate">
                {currentAudio?.title || currentAudio?.filename || 'Áudio'}
              </p>
              <p className="text-xs text-gray-500 truncate">
                {currentAudio?.remetente || 'Usuário'}
              </p>
              {!isMinimized && (
                <p className="text-xs text-gray-400">
                  {formatTime(currentTime)} / {formatTime(duration)}
                </p>
              )}
            </div>
          </div>

          {/* Controles principais */}
          <div className="flex items-center gap-2">
            {/* Botão anterior */}
            <Button
              variant="ghost"
              size="sm"
              onClick={playPrevious}
              disabled={!queueInfo.hasPrevious}
              className="h-8 w-8 p-0"
            >
              <SkipBack className="w-4 h-4" />
            </Button>

            {/* Botão play/pause */}
            <Button
              variant="default"
              size="sm"
              onClick={handlePlayPause}
              className="h-10 w-10 p-0 rounded-full"
            >
              {isPlaying ? (
                <Pause className="w-5 h-5" />
              ) : (
                <Play className="w-5 h-5 ml-0.5" />
              )}
            </Button>

            {/* Botão próximo */}
            <Button
              variant="ghost"
              size="sm"
              onClick={playNext}
              disabled={!queueInfo.hasNext}
              className="h-8 w-8 p-0"
            >
              <SkipForward className="w-4 h-4" />
            </Button>
          </div>

          {/* Controles secundários */}
          <div className="flex items-center gap-2">
            {/* Controles de loop e shuffle */}
            <Button
              variant={isLooping ? "default" : "ghost"}
              size="sm"
              onClick={toggleLoop}
              className="h-8 w-8 p-0"
              title="Repetir"
            >
              <Repeat className="w-4 h-4" />
            </Button>
            
            <Button
              variant={isShuffled ? "default" : "ghost"}
              size="sm"
              onClick={toggleShuffle}
              className="h-8 w-8 p-0"
              title="Embaralhar"
            >
              <Shuffle className="w-4 h-4" />
            </Button>

            {/* Controle de volume */}
            <div className="relative group">
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleMute}
                className="h-8 w-8 p-0"
                title="Volume"
              >
                {isMuted ? (
                  <VolumeX className="w-4 h-4" />
                ) : (
                  <Volume2 className="w-4 h-4" />
                )}
              </Button>
              
              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 p-2 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity">
                <Slider
                  value={volumeSliderValue}
                  onValueChange={handleVolumeChange}
                  max={100}
                  step={1}
                  orientation="vertical"
                  className="h-20"
                />
              </div>
            </div>

            {/* Botão da fila */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowQueue(!showQueue)}
              className="h-8 w-8 p-0 relative"
              title="Fila de reprodução"
            >
              <List className="w-4 h-4" />
              {queue.length > 0 && (
                <Badge className="absolute -top-1 -right-1 h-5 w-5 p-0 text-xs">
                  {queue.length}
                </Badge>
              )}
            </Button>

            {/* Botão de configurações */}
            <Dialog>
              <DialogTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0"
                  title="Configurações"
                >
                  <Settings className="w-4 h-4" />
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>Configurações do Player</DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  {/* Velocidade de reprodução */}
                  <div>
                    <label className="text-sm font-medium">Velocidade de reprodução</label>
                    <div className="grid grid-cols-3 gap-2 mt-2">
                      {[0.5, 0.75, 1, 1.25, 1.5, 2].map(rate => (
                        <Button
                          key={rate}
                          variant={playbackRate === rate ? "default" : "outline"}
                          size="sm"
                          onClick={() => setPlaybackRate(rate)}
                          className="w-full"
                        >
                          {rate}x
                        </Button>
                      ))}
                    </div>
                  </div>

                  {/* Equalizador */}
                  <div>
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">Equalizador</label>
                      <Button
                        variant={equalizer.enabled ? "default" : "outline"}
                        size="sm"
                        onClick={toggleEqualizer}
                      >
                        {equalizer.enabled ? "Ativado" : "Desativado"}
                      </Button>
                    </div>
                    {equalizer.enabled && (
                      <div className="mt-2 space-y-2">
                        {equalizer.bands.map((band, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <span className="text-xs w-8">{index * 100}Hz</span>
                            <Slider
                              value={[band]}
                              onValueChange={([value]) => setEqualizerBand(index, value)}
                              min={-12}
                              max={12}
                              step={1}
                              className="flex-1"
                            />
                            <span className="text-xs w-8">{band}dB</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Efeitos */}
                  <div>
                    <label className="text-sm font-medium">Efeitos</label>
                    <div className="grid grid-cols-2 gap-2 mt-2">
                      {Object.entries(effects).map(([effect, enabled]) => (
                        <Button
                          key={effect}
                          variant={enabled ? "default" : "outline"}
                          size="sm"
                          onClick={() => toggleEffect(effect)}
                          className="w-full capitalize"
                        >
                          {effect}
                        </Button>
                      ))}
                    </div>
                  </div>

                  {/* Crossfade */}
                  <div>
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">Crossfade</label>
                      <Button
                        variant={crossfade ? "default" : "outline"}
                        size="sm"
                        onClick={toggleCrossfade}
                      >
                        {crossfade ? "Ativado" : "Desativado"}
                      </Button>
                    </div>
                  </div>
                </div>
              </DialogContent>
            </Dialog>

            {/* Botão de minimizar */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMinimized(!isMinimized)}
              className="h-8 w-8 p-0"
              title={isMinimized ? "Expandir" : "Minimizar"}
            >
              {isMinimized ? (
                <ChevronUp className="w-4 h-4" />
              ) : (
                <ChevronDown className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Barra de progresso */}
        {!isMinimized && (
          <div className="px-4 pb-2">
            <Slider
              value={sliderValue}
              onValueChange={handleSeek}
              max={100}
              step={0.1}
              className="w-full"
            />
          </div>
        )}

        {/* Fila de reprodução */}
        <AnimatePresence>
          {showQueue && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="bg-gray-50 border-t border-gray-200 overflow-hidden"
            >
              <div className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium">Fila de reprodução</h3>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={shuffleQueue}
                      disabled={queue.length === 0}
                    >
                      <Shuffle className="w-4 h-4 mr-1" />
                      Embaralhar
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={clearQueue}
                      disabled={queue.length === 0}
                    >
                      Limpar
                    </Button>
                  </div>
                </div>
                
                {queue.length === 0 ? (
                  <p className="text-sm text-gray-500 text-center py-4">
                    Nenhum áudio na fila
                  </p>
                ) : (
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {queue.map((audio, index) => (
                      <div
                        key={index}
                        className={`flex items-center gap-3 p-2 rounded-lg ${
                          index === currentIndex ? 'bg-green-100 border border-green-200' : 'bg-white border border-gray-200'
                        }`}
                      >
                        <div className="w-8 h-8 bg-green-500 rounded flex items-center justify-center text-white text-xs">
                          {index + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">
                            {audio.title || audio.filename || 'Áudio'}
                          </p>
                          <p className="text-xs text-gray-500 truncate">
                            {audio.remetente || 'Usuário'}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFromQueue(index)}
                          className="h-6 w-6 p-0"
                        >
                          <X className="w-3 h-3" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Player de áudio oculto */}
        <audio 
          ref={audioRef}
          className="hidden"
          preload="metadata"
          src={currentAudio?.url}
        />
      </motion.div>
    </AnimatePresence>
  );
};

export default GlobalAudioPlayer; 