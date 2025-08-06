import React, { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Download,
  Play,
  Pause,
  Loader2,
  AlertTriangle,
  MessageCircle
} from 'lucide-react'
import { Slider } from './ui/slider'

// Tipos de mídia suportados
const MediaType = {
  AUDIO: 'audio',
  IMAGE: 'image',
  VIDEO: 'video',
  STICKER: 'sticker',
  DOCUMENT: 'document'
}

/**
 * Componente para processar e exibir mídias do WhatsApp
 */
export const MediaProcessor = ({ message }) => {
  const [mediaType, setMediaType] = useState(null)
  const [mediaUrl, setMediaUrl] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  // Processar dados da mensagem para extrair informações de mídia
  useEffect(() => {
    console.log('🎵 DEBUG MediaProcessor - Dados da mensagem:', message)
    
    try {
      let content = null
      
      // Tentar extrair conteúdo da mensagem
      if (message.content) {
        if (typeof message.content === 'string') {
          try {
            content = JSON.parse(message.content)
          } catch (e) {
            // Se não for JSON, usar como texto
            content = { conversation: message.content }
          }
        } else {
          content = message.content
        }
      } else if (message.conteudo) {
        if (typeof message.conteudo === 'string') {
          try {
            content = JSON.parse(message.conteudo)
          } catch (e) {
            content = { conversation: message.conteudo }
          }
        } else {
          content = message.conteudo
        }
      }

      console.log('🎵 Conteúdo processado:', content)

      // Detectar tipo de mídia
      if (content) {
        if (content.audioMessage) {
          setMediaType(MediaType.AUDIO)
          processAudioMessage(content.audioMessage)
        } else if (content.imageMessage) {
          setMediaType(MediaType.IMAGE)
          processImageMessage(content.imageMessage)
        } else if (content.videoMessage) {
          setMediaType(MediaType.VIDEO)
          processVideoMessage(content.videoMessage)
        } else if (content.stickerMessage) {
          setMediaType(MediaType.STICKER)
          processStickerMessage(content.stickerMessage)
        } else if (content.documentMessage) {
          setMediaType(MediaType.DOCUMENT)
          processDocumentMessage(content.documentMessage)
        } else {
          // Fallback para mensagem de texto
          setMediaType(null)
          setIsLoading(false)
        }
      } else {
        setError('Não foi possível processar o conteúdo da mensagem')
        setIsLoading(false)
      }
    } catch (error) {
      console.error('❌ Erro ao processar mídia:', error)
      setError('Erro ao processar mídia')
      setIsLoading(false)
    }
  }, [message])

  // Processar mensagem de áudio
  const processAudioMessage = (audioMessage) => {
    console.log('🎵 Processando áudio:', audioMessage)
    
    let url = null
    
    // Prioridade 1: URL da pasta /wapi/midias/ (sistema integrado)
    if (audioMessage.url && audioMessage.url.startsWith('/wapi/midias/')) {
      const filename = audioMessage.url.split('/').pop()
      url = `http://localhost:8000/api/wapi-media/audios/${filename}`
    }
    // Prioridade 2: Nome do arquivo na pasta /wapi/midias/
    else if (audioMessage.fileName) {
      url = `http://localhost:8000/api/wapi-media/audios/${audioMessage.fileName}`
    }
    // Prioridade 3: URL direta do JSON
    else if (audioMessage.url) {
      url = audioMessage.url
    }
    // Fallback: usar endpoint da API para servir áudio pelo ID da mensagem
    else if (message.id) {
      url = `http://localhost:8000/api/audio/message/${message.id}/`
    }

    if (url) {
      setMediaUrl(url)
      setIsLoading(false)
    } else {
      setError('Não foi possível obter URL do áudio')
      setIsLoading(false)
    }
  }

  // Processar mensagem de imagem
  const processImageMessage = (imageMessage) => {
    console.log('🖼️ Processando imagem:', imageMessage)
    
    let url = null
    
    // Prioridade 1: URL da pasta /wapi/midias/
    if (imageMessage.url && imageMessage.url.startsWith('/wapi/midias/')) {
      const filename = imageMessage.url.split('/').pop()
      url = `http://localhost:8000/api/wapi-media/images/${filename}`
    }
    // Prioridade 2: URL direta do JSON
    else if (imageMessage.url) {
      url = imageMessage.url
    }
    // Fallback: usar endpoint da API
    else if (message.id) {
      url = `http://localhost:8000/api/image/message/${message.id}/`
    }

    if (url) {
      setMediaUrl(url)
      setIsLoading(false)
    } else {
      setError('Não foi possível obter URL da imagem')
      setIsLoading(false)
    }
  }

  // Processar mensagem de vídeo
  const processVideoMessage = (videoMessage) => {
    console.log('🎬 Processando vídeo:', videoMessage)
    
    let url = null
    
    // Prioridade 1: URL da pasta /wapi/midias/
    if (videoMessage.url && videoMessage.url.startsWith('/wapi/midias/')) {
      const filename = videoMessage.url.split('/').pop()
      url = `http://localhost:8000/api/wapi-media/videos/${filename}`
    }
    // Prioridade 2: URL direta do JSON
    else if (videoMessage.url) {
      url = videoMessage.url
    }
    // Fallback: usar endpoint da API
    else if (message.id) {
      url = `http://localhost:8000/api/video/message/${message.id}/`
    }

    if (url) {
      setMediaUrl(url)
      setIsLoading(false)
    } else {
      setError('Não foi possível obter URL do vídeo')
      setIsLoading(false)
    }
  }

  // Processar mensagem de sticker
  const processStickerMessage = (stickerMessage) => {
    console.log('😀 Processando sticker:', stickerMessage)
    
    let url = null
    
    // Prioridade 1: URL da pasta /wapi/midias/
    if (stickerMessage.url && stickerMessage.url.startsWith('/wapi/midias/')) {
      const filename = stickerMessage.url.split('/').pop()
      url = `http://localhost:8000/api/wapi-media/stickers/${filename}`
    }
    // Prioridade 2: URL direta do JSON
    else if (stickerMessage.url) {
      url = stickerMessage.url
    }
    // Fallback: usar endpoint da API
    else if (message.id) {
      url = `http://localhost:8000/api/sticker/message/${message.id}/`
    }

    if (url) {
      setMediaUrl(url)
      setIsLoading(false)
    } else {
      setError('Não foi possível obter URL do sticker')
      setIsLoading(false)
    }
  }

  // Processar mensagem de documento
  const processDocumentMessage = (documentMessage) => {
    console.log('📄 Processando documento:', documentMessage)
    
    let url = null
    
    // Prioridade 1: URL da pasta /wapi/midias/
    if (documentMessage.url && documentMessage.url.startsWith('/wapi/midias/')) {
      const filename = documentMessage.url.split('/').pop()
      url = `http://localhost:8000/api/wapi-media/documents/${filename}`
    }
    // Prioridade 2: URL direta do JSON
    else if (documentMessage.url) {
      url = documentMessage.url
    }
    // Fallback: usar endpoint da API
    else if (message.id) {
      url = `http://localhost:8000/api/document/message/${message.id}/`
    }

    if (url) {
      setMediaUrl(url)
      setIsLoading(false)
    } else {
      setError('Não foi possível obter URL do documento')
      setIsLoading(false)
    }
  }

  // Renderizar erro
  if (error) {
    return (
      <div className="space-y-2">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-accent border border-border rounded-lg p-4"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-500 rounded-lg text-white">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-foreground">Mídia não disponível</p>
              <p className="text-xs text-muted-foreground">{error}</p>
            </div>
          </div>
        </motion.div>
      </div>
    )
  }

  // Renderizar loading
  if (isLoading) {
    return (
      <div className="space-y-2">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-accent border border-border rounded-lg p-4"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-muted rounded-lg">
              <Loader2 className="w-5 h-5 animate-spin" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-foreground">Carregando mídia...</p>
              <p className="text-xs text-muted-foreground">Aguarde um momento</p>
            </div>
          </div>
        </motion.div>
      </div>
    )
  }

  // Renderizar mídia baseada no tipo
  switch (mediaType) {
    case MediaType.AUDIO:
      return <AudioPlayer message={message} mediaUrl={mediaUrl} />
    case MediaType.IMAGE:
      return <ImageDisplay message={message} mediaUrl={mediaUrl} />
    case MediaType.VIDEO:
      return <VideoDisplay message={message} mediaUrl={mediaUrl} />
    case MediaType.STICKER:
      return <StickerDisplay message={message} mediaUrl={mediaUrl} />
    case MediaType.DOCUMENT:
      return <DocumentDisplay message={message} mediaUrl={mediaUrl} />
    default:
      return null
  }
}

// Componente para exibir áudio
const AudioPlayer = ({ message, mediaUrl }) => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const audioRef = useRef(null)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const updateTime = () => setCurrentTime(audio.currentTime)
    const updateDuration = () => setDuration(audio.duration)
    const handlePlay = () => setIsPlaying(true)
    const handlePause = () => setIsPlaying(false)
    const handleEnded = () => setIsPlaying(false)
    const handleLoadedData = () => {
      setIsLoading(false)
      setDuration(audio.duration)
    }

    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('loadedmetadata', updateDuration)
    audio.addEventListener('play', handlePlay)
    audio.addEventListener('pause', handlePause)
    audio.addEventListener('ended', handleEnded)
    audio.addEventListener('loadeddata', handleLoadedData)

    return () => {
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('loadedmetadata', updateDuration)
      audio.removeEventListener('play', handlePlay)
      audio.removeEventListener('pause', handlePause)
      audio.removeEventListener('ended', handleEnded)
      audio.removeEventListener('loadeddata', handleLoadedData)
    }
  }, [])

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
      } else {
        audioRef.current.play()
      }
    }
  }

  const handleSliderChange = (value) => {
    if (audioRef.current && duration > 0) {
      const newTime = (value[0] / 100) * duration
      audioRef.current.currentTime = newTime
      setCurrentTime(newTime)
    }
  }

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }

  const sliderValue = duration > 0 ? [(currentTime / duration) * 100] : [0]

  return (
    <div className="space-y-2">
      {/* Comentário do áudio */}
      {message.content && message.tipo !== 'texto' && (
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-sm opacity-90 mb-2"
        >
          {message.content}
        </motion.p>
      )}
      {/* Áudio no estilo do documento */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-accent border border-border rounded-lg p-4 hover:bg-accent/80 transition-colors"
      >
        <div className="flex items-center gap-3">
          {/* Ícone Play/Loading */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={togglePlay}
            disabled={isLoading}
            className={`p-2 rounded-lg shadow-sm transition-colors ${
              isLoading 
                ? 'bg-muted text-muted-foreground cursor-not-allowed' 
                : 'bg-primary text-primary-foreground hover:bg-primary/90'
            }`}
            title={isLoading ? 'Carregando...' : (isPlaying ? 'Pausar' : 'Reproduzir')}
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : isPlaying ? (
              <Pause className="w-5 h-5" />
            ) : (
              <Play className="w-5 h-5" />
            )}
          </motion.button>
          
          {/* Informações do áudio */}
          <div className="flex-1 min-w-0">
            <p className="font-medium text-foreground truncate">
              {message.filename || 'Áudio'}
            </p>
            <p className="text-xs text-muted-foreground">
              {isLoading ? 'Carregando...' : (message.duration || formatTime(duration))}
            </p>
            
            {/* Slider de progresso */}
            {!isLoading && (
              <div className="mt-2">
                <Slider
                  value={sliderValue}
                  onValueChange={handleSliderChange}
                  max={100}
                  step={0.1}
                  className="w-full"
                  disabled={isLoading}
                />
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>{formatTime(currentTime)}</span>
                  <span>{formatTime(duration)}</span>
                </div>
              </div>
            )}
          </div>
          
          {/* Botão de download */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 hover:bg-background rounded-lg transition-colors"
            title="Baixar áudio"
            onClick={() => {
              if (mediaUrl) {
                const link = document.createElement('a')
                link.href = mediaUrl
                link.download = `audio_${message.id || Date.now()}.mp3`
                link.click()
              }
            }}
          >
            <Download className="w-4 h-4 text-foreground/80" />
          </motion.button>
        </div>
        
        {/* Player de áudio oculto para funcionalidade */}
        <audio 
          ref={audioRef}
          className="hidden"
          preload="metadata"
          src={mediaUrl}
          onError={(e) => {
            console.error('Erro ao carregar áudio:', e)
            setIsLoading(false)
          }}
        />
      </motion.div>
    </div>
  )
}

// Componente para exibir imagem
const ImageDisplay = ({ message, mediaUrl }) => {
  return (
    <div className="space-y-2">
      {/* Comentário da imagem */}
      {message.content && message.tipo !== 'texto' && (
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-sm opacity-90 mb-2"
        >
          {message.content}
        </motion.p>
      )}
      
      {/* Imagem */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative group"
      >
        <img
          src={mediaUrl}
          alt="Imagem"
          className="rounded-lg max-h-[300px] w-auto object-cover shadow-sm hover:shadow-md transition-shadow duration-200"
        />
        <motion.button
          initial={{ opacity: 0 }}
          whileHover={{ opacity: 1 }}
          className="absolute top-2 right-2 p-2 bg-black/80 text-white rounded-full hover:bg-black/90 transition-colors shadow-lg"
          onClick={() => {
            if (mediaUrl) {
              const link = document.createElement('a')
              link.href = mediaUrl
              link.download = `image_${message.id || Date.now()}.jpg`
              link.click()
            }
          }}
        >
          <Download className="w-4 h-4" />
        </motion.button>
      </motion.div>
    </div>
  )
}

// Componente para exibir vídeo
const VideoDisplay = ({ message, mediaUrl }) => {
  return (
    <div className="space-y-2">
      {/* Comentário do vídeo */}
      {message.content && message.tipo !== 'texto' && (
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-sm opacity-90 mb-2"
        >
          {message.content}
        </motion.p>
      )}
      
      {/* Vídeo */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative group"
      >
        <video 
          controls 
          className="rounded-lg max-h-[300px] w-auto object-cover shadow-sm hover:shadow-md transition-shadow duration-200"
        >
          <source src={mediaUrl} type="video/mp4" />
        </video>
        <motion.button
          initial={{ opacity: 0 }}
          whileHover={{ opacity: 1 }}
          className="absolute top-2 right-2 p-2 bg-black/80 text-white rounded-full hover:bg-black/90 transition-colors shadow-lg"
          onClick={() => {
            if (mediaUrl) {
              const link = document.createElement('a')
              link.href = mediaUrl
              link.download = `video_${message.id || Date.now()}.mp4`
              link.click()
            }
          }}
        >
          <Download className="w-4 h-4" />
        </motion.button>
      </motion.div>
    </div>
  )
}

// Componente para exibir sticker
const StickerDisplay = ({ message, mediaUrl }) => {
  return (
    <div className="space-y-2">
      {/* Sticker */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative group"
      >
        <img
          src={mediaUrl}
          alt="Sticker"
          className="rounded-lg max-h-[200px] w-auto object-cover shadow-sm hover:shadow-md transition-shadow duration-200"
        />
        <motion.button
          initial={{ opacity: 0 }}
          whileHover={{ opacity: 1 }}
          className="absolute top-2 right-2 p-2 bg-black/80 text-white rounded-full hover:bg-black/90 transition-colors shadow-lg"
          onClick={() => {
            if (mediaUrl) {
              const link = document.createElement('a')
              link.href = mediaUrl
              link.download = `sticker_${message.id || Date.now()}.webp`
              link.click()
            }
          }}
        >
          <Download className="w-4 h-4" />
        </motion.button>
      </motion.div>
    </div>
  )
}

// Componente para exibir documento
const DocumentDisplay = ({ message, mediaUrl }) => {
  return (
    <div className="space-y-2">
      {/* Comentário do documento */}
      {message.content && message.tipo !== 'texto' && (
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-sm opacity-90 mb-2"
        >
          {message.content}
        </motion.p>
      )}
      
      {/* Documento */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-accent border border-border rounded-lg p-4 hover:bg-accent/80 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary rounded-lg">
            <MessageCircle className="w-5 h-5 text-primary-foreground" />
          </div>
          <div className="flex-1">
            <p className="font-medium text-foreground">
              {message.documentFilename || 'Documento'}
            </p>
            <p className="text-xs text-muted-foreground">
              {message.documentMimetype || 'Tipo desconhecido'}
            </p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 hover:bg-background rounded-lg transition-colors"
            title="Baixar documento"
            onClick={() => {
              if (mediaUrl) {
                const link = document.createElement('a')
                link.href = mediaUrl
                link.download = message.documentFilename || 'documento'
                link.click()
              }
            }}
          >
            <Download className="w-4 h-4 text-foreground/80" />
          </motion.button>
        </div>
      </motion.div>
    </div>
  )
}

export default MediaProcessor 