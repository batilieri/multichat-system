import { useState, useRef, useCallback, useEffect } from 'react';

export const useAudioPlayer = () => {
  const [currentAudio, setCurrentAudio] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [isLooping, setIsLooping] = useState(false);
  const [isShuffled, setIsShuffled] = useState(false);
  const [queue, setQueue] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  
  const audioRef = useRef(null);
  const audioContextRef = useRef(null);

  // Inicializar contexto de áudio para análise
  useEffect(() => {
    if (typeof window !== 'undefined' && window.AudioContext) {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    return () => {
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  // Configurar eventos do áudio
  useEffect(() => {
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
      } else if (queue.length > 0) {
        playNext();
      }
    };
    const handleLoadedData = () => {
      setDuration(audio.duration);
    };
    const handleError = (e) => {
      console.error('Erro no player de áudio:', e);
      setIsPlaying(false);
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
  }, [isLooping, queue]);

  // Aplicar configurações de áudio
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume;
      audioRef.current.playbackRate = playbackRate;
    }
  }, [volume, isMuted, playbackRate]);

  const play = useCallback(async (audioData) => {
    try {
      if (audioRef.current) {
        // Parar áudio atual se estiver tocando
        if (isPlaying) {
          audioRef.current.pause();
        }
        
        // Configurar novo áudio
        audioRef.current.src = audioData.url;
        audioRef.current.currentTime = 0;
        
        // Tentar reproduzir
        await audioRef.current.play();
        setCurrentAudio(audioData);
        setIsPlaying(true);
        setCurrentTime(0);
      }
    } catch (error) {
      console.error('Erro ao reproduzir áudio:', error);
      setIsPlaying(false);
    }
  }, [isPlaying]);

  const pause = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  }, []);

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
      setCurrentTime(0);
      setCurrentAudio(null);
    }
  }, []);

  const togglePlay = useCallback(() => {
    if (isPlaying) {
      pause();
    } else if (currentAudio) {
      play(currentAudio);
    }
  }, [isPlaying, currentAudio, play, pause]);

  const seek = useCallback((time) => {
    if (audioRef.current && duration > 0) {
      const newTime = Math.max(0, Math.min(duration, time));
      audioRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  }, [duration]);

  const seekPercentage = useCallback((percentage) => {
    if (duration > 0) {
      const time = (percentage / 100) * duration;
      seek(time);
    }
  }, [duration, seek]);

  const skipTime = useCallback((seconds) => {
    if (audioRef.current) {
      const newTime = Math.max(0, Math.min(duration, currentTime + seconds));
      seek(newTime);
    }
  }, [currentTime, duration, seek]);

  const setVolumeLevel = useCallback((level) => {
    const newVolume = Math.max(0, Math.min(1, level));
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  }, []);

  const toggleMute = useCallback(() => {
    setIsMuted(!isMuted);
  }, [isMuted]);

  const setPlaybackSpeed = useCallback((speed) => {
    setPlaybackRate(speed);
  }, []);

  const toggleLoop = useCallback(() => {
    setIsLooping(!isLooping);
  }, [isLooping]);

  const toggleShuffle = useCallback(() => {
    setIsShuffled(!isShuffled);
  }, [isShuffled]);

  // Funções de fila
  const addToQueue = useCallback((audioData) => {
    setQueue(prev => [...prev, audioData]);
  }, []);

  const removeFromQueue = useCallback((index) => {
    setQueue(prev => prev.filter((_, i) => i !== index));
  }, []);

  const clearQueue = useCallback(() => {
    setQueue([]);
    setCurrentIndex(0);
  }, []);

  const playNext = useCallback(() => {
    if (queue.length > 0) {
      const nextIndex = (currentIndex + 1) % queue.length;
      setCurrentIndex(nextIndex);
      play(queue[nextIndex]);
    }
  }, [queue, currentIndex, play]);

  const playPrevious = useCallback(() => {
    if (queue.length > 0) {
      const prevIndex = currentIndex > 0 ? currentIndex - 1 : queue.length - 1;
      setCurrentIndex(prevIndex);
      play(queue[prevIndex]);
    }
  }, [queue, currentIndex, play]);

  const shuffleQueue = useCallback(() => {
    if (queue.length > 0) {
      const shuffled = [...queue];
      for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
      }
      setQueue(shuffled);
    }
  }, [queue]);

  // Funções de análise de áudio
  const getAudioInfo = useCallback(async (audioUrl) => {
    try {
      if (!audioContextRef.current) return null;
      
      const response = await fetch(audioUrl);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await audioContextRef.current.decodeAudioData(arrayBuffer);
      
      return {
        duration: audioBuffer.duration,
        sampleRate: audioBuffer.sampleRate,
        numberOfChannels: audioBuffer.numberOfChannels,
        length: audioBuffer.length
      };
    } catch (error) {
      console.error('Erro ao analisar áudio:', error);
      return null;
    }
  }, []);

  const generateWaveform = useCallback(async (audioUrl, resolution = 100) => {
    try {
      if (!audioContextRef.current) return null;
      
      const response = await fetch(audioUrl);
      const arrayBuffer = await response.arrayBuffer();
      const audioBuffer = await audioContextRef.current.decodeAudioData(arrayBuffer);
      
      const channelData = audioBuffer.getChannelData(0);
      const samples = channelData.length;
      const blockSize = Math.floor(samples / resolution);
      const waveform = [];
      
      for (let i = 0; i < resolution; i++) {
        const start = blockSize * i;
        let sum = 0;
        for (let j = 0; j < blockSize; j++) {
          sum += Math.abs(channelData[start + j]);
        }
        waveform.push(sum / blockSize);
      }
      
      return waveform;
    } catch (error) {
      console.error('Erro ao gerar waveform:', error);
      return null;
    }
  }, []);

  // Funções de controle global
  const pauseAll = useCallback(() => {
    pause();
    // Pausar todos os outros players se necessário
  }, [pause]);

  const resumeAll = useCallback(() => {
    if (currentAudio) {
      play(currentAudio);
    }
  }, [currentAudio, play]);

  // Estado do player
  const playerState = {
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
    hasAudio: !!currentAudio
  };

  // Controles do player
  const controls = {
    play,
    pause,
    stop,
    togglePlay,
    seek,
    seekPercentage,
    skipTime,
    setVolumeLevel,
    toggleMute,
    setPlaybackSpeed,
    toggleLoop,
    toggleShuffle,
    addToQueue,
    removeFromQueue,
    clearQueue,
    playNext,
    playPrevious,
    shuffleQueue,
    pauseAll,
    resumeAll,
    getAudioInfo,
    generateWaveform
  };

  return {
    ...playerState,
    ...controls,
    audioRef
  };
}; 