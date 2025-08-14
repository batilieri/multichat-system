import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { useAudioPlayer } from '../hooks/use-audio-player';

// Tipos de ações
const AudioPlayerActions = {
  PLAY: 'PLAY',
  PAUSE: 'PAUSE',
  STOP: 'STOP',
  SEEK: 'SEEK',
  SET_VOLUME: 'SET_VOLUME',
  TOGGLE_MUTE: 'TOGGLE_MUTE',
  SET_PLAYBACK_RATE: 'SET_PLAYBACK_RATE',
  TOGGLE_LOOP: 'TOGGLE_LOOP',
  TOGGLE_SHUFFLE: 'TOGGLE_SHUFFLE',
  ADD_TO_QUEUE: 'ADD_TO_QUEUE',
  REMOVE_FROM_QUEUE: 'REMOVE_FROM_QUEUE',
  CLEAR_QUEUE: 'CLEAR_QUEUE',
  PLAY_NEXT: 'PLAY_NEXT',
  PLAY_PREVIOUS: 'PLAY_PREVIOUS',
  SHUFFLE_QUEUE: 'SHUFFLE_QUEUE',
  SET_CURRENT_AUDIO: 'SET_CURRENT_AUDIO',
  UPDATE_PLAYER_STATE: 'UPDATE_PLAYER_STATE'
};

// Estado inicial
const initialState = {
  currentAudio: null,
  isPlaying: false,
  currentTime: 0,
  duration: 0,
  volume: 1,
  isMuted: false,
  playbackRate: 1,
  isLooping: false,
  isShuffled: false,
  queue: [],
  currentIndex: 0,
  hasAudio: false,
  globalVolume: 1,
  globalMuted: false,
  crossfade: false,
  crossfadeDuration: 1000,
  equalizer: {
    enabled: false,
    bands: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] // 10 bandas de equalização
  },
  effects: {
    reverb: false,
    delay: false,
    compression: false
  }
};

// Reducer para gerenciar o estado
function audioPlayerReducer(state, action) {
  switch (action.type) {
    case AudioPlayerActions.PLAY:
      return {
        ...state,
        isPlaying: true,
        currentAudio: action.payload
      };
      
    case AudioPlayerActions.PAUSE:
      return {
        ...state,
        isPlaying: false
      };
      
    case AudioPlayerActions.STOP:
      return {
        ...state,
        isPlaying: false,
        currentTime: 0,
        currentAudio: null
      };
      
    case AudioPlayerActions.SEEK:
      return {
        ...state,
        currentTime: action.payload
      };
      
    case AudioPlayerActions.SET_VOLUME:
      return {
        ...state,
        volume: action.payload,
        isMuted: action.payload === 0
      };
      
    case AudioPlayerActions.TOGGLE_MUTE:
      return {
        ...state,
        isMuted: !state.isMuted
      };
      
    case AudioPlayerActions.SET_PLAYBACK_RATE:
      return {
        ...state,
        playbackRate: action.payload
      };
      
    case AudioPlayerActions.TOGGLE_LOOP:
      return {
        ...state,
        isLooping: !state.isLooping
      };
      
    case AudioPlayerActions.TOGGLE_SHUFFLE:
      return {
        ...state,
        isShuffled: !state.isShuffled
      };
      
    case AudioPlayerActions.ADD_TO_QUEUE:
      return {
        ...state,
        queue: [...state.queue, action.payload]
      };
      
    case AudioPlayerActions.REMOVE_FROM_QUEUE:
      return {
        ...state,
        queue: state.queue.filter((_, index) => index !== action.payload)
      };
      
    case AudioPlayerActions.CLEAR_QUEUE:
      return {
        ...state,
        queue: [],
        currentIndex: 0
      };
      
    case AudioPlayerActions.PLAY_NEXT:
      const nextIndex = (state.currentIndex + 1) % state.queue.length;
      return {
        ...state,
        currentIndex: nextIndex,
        currentAudio: state.queue[nextIndex] || null
      };
      
    case AudioPlayerActions.PLAY_PREVIOUS:
      const prevIndex = state.currentIndex > 0 ? state.currentIndex - 1 : state.queue.length - 1;
      return {
        ...state,
        currentIndex: prevIndex,
        currentAudio: state.queue[prevIndex] || null
      };
      
    case AudioPlayerActions.SHUFFLE_QUEUE:
      const shuffled = [...state.queue];
      for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
      }
      return {
        ...state,
        queue: shuffled
      };
      
    case AudioPlayerActions.SET_CURRENT_AUDIO:
      return {
        ...state,
        currentAudio: action.payload,
        hasAudio: !!action.payload
      };
      
    case AudioPlayerActions.UPDATE_PLAYER_STATE:
      return {
        ...state,
        ...action.payload
      };
      
    default:
      return state;
  }
}

// Contexto do player de áudio
const AudioPlayerContext = createContext();

// Provider do contexto
export const AudioPlayerProvider = ({ children }) => {
  const [state, dispatch] = useReducer(audioPlayerReducer, initialState);
  const audioPlayer = useAudioPlayer();

  // Sincronizar estado do hook com o contexto
  useEffect(() => {
    dispatch({
      type: AudioPlayerActions.UPDATE_PLAYER_STATE,
      payload: {
        currentAudio: audioPlayer.currentAudio,
        isPlaying: audioPlayer.isPlaying,
        currentTime: audioPlayer.currentTime,
        duration: audioPlayer.duration,
        volume: audioPlayer.volume,
        isMuted: audioPlayer.isMuted,
        playbackRate: audioPlayer.playbackRate,
        isLooping: audioPlayer.isLooping,
        isShuffled: audioPlayer.isShuffled,
        queue: audioPlayer.queue,
        currentIndex: audioPlayer.currentIndex,
        hasAudio: audioPlayer.hasAudio
      }
    });
  }, [
    audioPlayer.currentAudio,
    audioPlayer.isPlaying,
    audioPlayer.currentTime,
    audioPlayer.duration,
    audioPlayer.volume,
    audioPlayer.isMuted,
    audioPlayer.playbackRate,
    audioPlayer.isLooping,
    audioPlayer.isShuffled,
    audioPlayer.queue,
    audioPlayer.currentIndex,
    audioPlayer.hasAudio
  ]);

  // Funções de controle que disparam ações
  const play = (audioData) => {
    audioPlayer.play(audioData);
    dispatch({ type: AudioPlayerActions.PLAY, payload: audioData });
  };

  const pause = () => {
    audioPlayer.pause();
    dispatch({ type: AudioPlayerActions.PAUSE });
  };

  const stop = () => {
    audioPlayer.stop();
    dispatch({ type: AudioPlayerActions.STOP });
  };

  const seek = (time) => {
    audioPlayer.seek(time);
    dispatch({ type: AudioPlayerActions.SEEK, payload: time });
  };

  const setVolume = (volume) => {
    audioPlayer.setVolumeLevel(volume);
    dispatch({ type: AudioPlayerActions.SET_VOLUME, payload: volume });
  };

  const toggleMute = () => {
    audioPlayer.toggleMute();
    dispatch({ type: AudioPlayerActions.TOGGLE_MUTE });
  };

  const setPlaybackRate = (rate) => {
    audioPlayer.setPlaybackSpeed(rate);
    dispatch({ type: AudioPlayerActions.SET_PLAYBACK_RATE, payload: rate });
  };

  const toggleLoop = () => {
    audioPlayer.toggleLoop();
    dispatch({ type: AudioPlayerActions.TOGGLE_LOOP });
  };

  const toggleShuffle = () => {
    audioPlayer.toggleShuffle();
    dispatch({ type: AudioPlayerActions.TOGGLE_SHUFFLE });
  };

  const addToQueue = (audioData) => {
    audioPlayer.addToQueue(audioData);
    dispatch({ type: AudioPlayerActions.ADD_TO_QUEUE, payload: audioData });
  };

  const removeFromQueue = (index) => {
    audioPlayer.removeFromQueue(index);
    dispatch({ type: AudioPlayerActions.REMOVE_FROM_QUEUE, payload: index });
  };

  const clearQueue = () => {
    audioPlayer.clearQueue();
    dispatch({ type: AudioPlayerActions.CLEAR_QUEUE });
  };

  const playNext = () => {
    audioPlayer.playNext();
    dispatch({ type: AudioPlayerActions.PLAY_NEXT });
  };

  const playPrevious = () => {
    audioPlayer.playPrevious();
    dispatch({ type: AudioPlayerActions.PLAY_PREVIOUS });
  };

  const shuffleQueue = () => {
    audioPlayer.shuffleQueue();
    dispatch({ type: AudioPlayerActions.SHUFFLE_QUEUE });
  };

  // Funções avançadas
  const setGlobalVolume = (volume) => {
    dispatch({
      type: AudioPlayerActions.UPDATE_PLAYER_STATE,
      payload: { globalVolume: volume }
    });
  };

  const toggleGlobalMute = () => {
    dispatch({
      type: AudioPlayerActions.UPDATE_PLAYER_STATE,
      payload: { globalMuted: !state.globalMuted }
    });
  };

  const toggleCrossfade = () => {
    dispatch({
      type: AudioPlayerActions.UPDATE_PLAYER_STATE,
      payload: { crossfade: !state.crossfade }
    });
  };

  const setCrossfadeDuration = (duration) => {
    dispatch({
      type: AudioPlayerActions.UPDATE_PLAYER_STATE,
      payload: { crossfadeDuration: duration }
    });
  };

  const setEqualizerBand = (bandIndex, value) => {
    const newBands = [...state.equalizer.bands];
    newBands[bandIndex] = value;
    dispatch({
      type: AudioPlayerActions.UPDATE_PLAYER_STATE,
      payload: {
        equalizer: {
          ...state.equalizer,
          bands: newBands
        }
      }
    });
  };

  const toggleEqualizer = () => {
    dispatch({
      type: AudioPlayerActions.UPDATE_PLAYER_STATE,
      payload: {
        equalizer: {
          ...state.equalizer,
          enabled: !state.equalizer.enabled
        }
      }
    });
  };

  const toggleEffect = (effectName) => {
    dispatch({
      type: AudioPlayerActions.UPDATE_PLAYER_STATE,
      payload: {
        effects: {
          ...state.effects,
          [effectName]: !state.effects[effectName]
        }
      }
    });
  };

  // Funções de utilidade
  const getCurrentAudioInfo = () => {
    if (!state.currentAudio) return null;
    
    return {
      ...state.currentAudio,
      progress: state.duration > 0 ? (state.currentTime / state.duration) * 100 : 0,
      timeRemaining: state.duration - state.currentTime,
      formattedCurrentTime: formatTime(state.currentTime),
      formattedDuration: formatTime(state.duration),
      formattedTimeRemaining: formatTime(state.duration - state.currentTime)
    };
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const getQueueInfo = () => {
    return {
      total: state.queue.length,
      current: state.currentIndex + 1,
      next: state.queue[state.currentIndex + 1] || null,
      previous: state.queue[state.currentIndex - 1] || null,
      hasNext: state.currentIndex < state.queue.length - 1,
      hasPrevious: state.currentIndex > 0
    };
  };

  // Valor do contexto
  const contextValue = {
    // Estado
    ...state,
    
    // Controles básicos
    play,
    pause,
    stop,
    seek,
    setVolume,
    toggleMute,
    setPlaybackRate,
    toggleLoop,
    toggleShuffle,
    
    // Controles de fila
    addToQueue,
    removeFromQueue,
    clearQueue,
    playNext,
    playPrevious,
    shuffleQueue,
    
    // Controles avançados
    setGlobalVolume,
    toggleGlobalMute,
    toggleCrossfade,
    setCrossfadeDuration,
    setEqualizerBand,
    toggleEqualizer,
    toggleEffect,
    
    // Funções de utilidade
    getCurrentAudioInfo,
    getQueueInfo,
    formatTime,
    
    // Referência do áudio
    audioRef: audioPlayer.audioRef
  };

  return (
    <AudioPlayerContext.Provider value={contextValue}>
      {children}
    </AudioPlayerContext.Provider>
  );
};

// Hook para usar o contexto
export const useAudioPlayerContext = () => {
  const context = useContext(AudioPlayerContext);
  if (!context) {
    throw new Error('useAudioPlayerContext deve ser usado dentro de um AudioPlayerProvider');
  }
  return context;
};

// Hook para usar apenas o estado (sem funções)
export const useAudioPlayerState = () => {
  const context = useContext(AudioPlayerContext);
  if (!context) {
    throw new Error('useAudioPlayerState deve ser usado dentro de um AudioPlayerProvider');
  }
  
  // Retornar apenas o estado, sem as funções
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
    crossfadeDuration,
    equalizer,
    effects
  } = context;
  
  return {
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
    crossfadeDuration,
    equalizer,
    effects
  };
};

export { AudioPlayerActions };
export default AudioPlayerContext; 