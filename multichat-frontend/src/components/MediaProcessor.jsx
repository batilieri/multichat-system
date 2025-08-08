import React, { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Download,
  Play,
  Pause,
  Loader2,
  AlertTriangle,
  MessageCircle,
  Eye
} from 'lucide-react'
import { Slider } from './ui/slider'
import { ImageModal } from './ImageModal'

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
    console.log('🎵 DEBUG MediaProcessor - Tipo:', message.tipo || message.type)
    console.log('🎵 DEBUG MediaProcessor - Content/Conteudo:', message.content || message.conteudo)
    
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
      
      // PRIORIDADE 1: Verificar se o backend já processou e definiu o tipo
      const tipo = message.tipo || message.type;
      console.log('🎯 Tipo da mensagem:', tipo);
      
      if (tipo === 'audio' || tipo === MediaType.AUDIO) {
        console.log('🎵 Tipo áudio detectado pelo backend')
        setMediaType(MediaType.AUDIO)
        processAudioMessage(content?.audioMessage || {})
      } else if (tipo === 'image' || tipo === 'imagem' || tipo === MediaType.IMAGE) {
        console.log('🖼️ Tipo imagem detectado pelo backend')
        setMediaType(MediaType.IMAGE)
        processImageMessage(content?.imageMessage || {})
      } else if (tipo === 'video' || tipo === MediaType.VIDEO) {
        console.log('🎬 Tipo vídeo detectado pelo backend')
        setMediaType(MediaType.VIDEO)
        processVideoMessage(content?.videoMessage || {})
      } else if (tipo === 'sticker' || tipo === MediaType.STICKER) {
        console.log('😀 Tipo sticker detectado pelo backend')
        setMediaType(MediaType.STICKER)
        processStickerMessage(content?.stickerMessage || {})
      } else if (tipo === 'document' || tipo === 'documento' || tipo === MediaType.DOCUMENT) {
        console.log('📄 Tipo documento detectado pelo backend')
        setMediaType(MediaType.DOCUMENT)
        processDocumentMessage(content?.documentMessage || {})
      }
      // PRIORIDADE 2: Detectar pelo conteúdo JSON (método antigo)
      else if (content) {
        if (content.audioMessage) {
          console.log('🎵 Tipo áudio detectado pelo conteúdo JSON')
          setMediaType(MediaType.AUDIO)
          processAudioMessage(content.audioMessage)
        } else if (content.imageMessage) {
          console.log('🖼️ Tipo imagem detectado pelo conteúdo JSON')
          setMediaType(MediaType.IMAGE)
          processImageMessage(content.imageMessage)
        } else if (content.videoMessage) {
          console.log('🎬 Tipo vídeo detectado pelo conteúdo JSON')
          setMediaType(MediaType.VIDEO)
          processVideoMessage(content.videoMessage)
        } else if (content.stickerMessage) {
          console.log('😀 Tipo sticker detectado pelo conteúdo JSON')
          setMediaType(MediaType.STICKER)
          processStickerMessage(content.stickerMessage)
        } else if (content.documentMessage) {
          console.log('📄 Tipo documento detectado pelo conteúdo JSON')
          setMediaType(MediaType.DOCUMENT)
          processDocumentMessage(content.documentMessage)
        } else {
          console.log('⚠️ Nenhum tipo de mídia detectado no conteúdo JSON')
          setError('Tipo de mídia não suportado')
          setIsLoading(false)
        }
      } else {
        console.log('⚠️ Nenhum conteúdo encontrado')
        setError('Conteúdo não encontrado')
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
    
    // Verificação menos restritiva: sempre tentar processar áudio se temos um audioMessage ou alguma fonte
    const hasMediaUrl = message.media_url && (message.media_url.startsWith('/media/') || message.media_url.startsWith('/api/'))
    const hasAudioMessageUrl = audioMessage && audioMessage.url
    const hasAudioFileName = audioMessage && audioMessage.fileName
    const hasDirectContent = message.conteudo && typeof message.conteudo === 'string' && (message.conteudo.startsWith('/media/') || message.conteudo.startsWith('/api/'))
    
    console.log('🎵 Verificação de fontes de áudio:', {
      hasMediaUrl,
      hasAudioMessageUrl,
      hasAudioFileName,
      hasDirectContent,
      hasChatId: !!message.chat_id,
      hasMessageId: !!message.id,
      audioMessage
    })
    
    // Se não há nenhuma fonte possível de áudio
    if (!hasMediaUrl && !hasAudioMessageUrl && !hasAudioFileName && !hasDirectContent && !message.chat_id && !message.id) {
      console.log('🎵 Nenhuma fonte de áudio válida encontrada')
      setError('Arquivo de áudio não disponível')
      setIsLoading(false)
      return
    }
    
    // Prioridade 1: URL da nova estrutura de chat_id (backend modificado)
    if (message.media_url && (message.media_url.startsWith('/media/whatsapp_media/') || message.media_url.startsWith('/api/whatsapp-media/'))) {
      url = message.media_url.startsWith('/api/') ? `http://localhost:8000${message.media_url}` : `http://localhost:8000/api${message.media_url}`
      console.log('🎵 URL da nova estrutura:', url)
    }
    // Prioridade 2: Conteúdo já é a URL local (serializer modificado)
    else if ((message.conteudo || message.content) && 
             (typeof (message.conteudo || message.content) === 'string') &&
             ((message.conteudo || message.content).startsWith('/media/whatsapp_media/') || 
              (message.conteudo || message.content).startsWith('/api/whatsapp-media/'))) {
      const contentUrl = message.conteudo || message.content
      url = contentUrl.startsWith('/api/') ? `http://localhost:8000${contentUrl}` : `http://localhost:8000/api${contentUrl}`
      console.log('🎵 URL do conteúdo processado:', url)
    }
    // Prioridade 3: Nova estrutura de armazenamento por chat_id
    else if (message.chat_id) {
      // Usar endpoint inteligente que detecta o arquivo automaticamente
      const chatId = message.chat_id
      const clienteId = 2 // Cliente Elizeu
      const instanceId = '3B6XIW-ZTS923-GEAY6V'
      const messageId = message.message_id || message.id
      
      // Usar endpoint que faz auto-detecção do arquivo baseado no message_id
      url = `http://localhost:8000/api/whatsapp-audio-smart/${clienteId}/${instanceId}/${chatId}/${messageId}`
      console.log('🎵 URL inteligente por chat_id e message_id:', url)
    }
    // Prioridade 4: URL da pasta /wapi/midias/ (sistema antigo)
    else if (audioMessage.url && audioMessage.url.startsWith('/wapi/midias/')) {
      const filename = audioMessage.url.split('/').pop()
      url = `http://localhost:8000/api/wapi-media/audios/${filename}`
      console.log('🎵 URL /wapi/midias/:', url)
    }
    // Prioridade 5: Nome do arquivo na pasta /wapi/midias/
    else if (audioMessage.fileName) {
      url = `http://localhost:8000/api/wapi-media/audios/${audioMessage.fileName}`
      console.log('🎵 URL por fileName:', url)
    }
    // Prioridade 6: URL direta do WhatsApp (quando arquivo não foi baixado localmente)
    else if (audioMessage.url && audioMessage.url.startsWith('https://')) {
      // Para URLs do WhatsApp, tentar usar endpoint público que pode baixar/servir
      if (message.id) {
        url = `http://localhost:8000/api/audio/message/${message.id}/public/`
        console.log('🎵 URL pública por ID para download do WhatsApp:', url)
      } else {
        // Como último recurso, usar URL direta (pode não funcionar devido a CORS)
        url = audioMessage.url
        console.log('🎵 URL direta do WhatsApp (pode ter problemas de CORS):', url)
      }
    }
    // Prioridade 7: URL direta local
    else if (audioMessage.url) {
      url = audioMessage.url
      console.log('🎵 URL direta local:', url)
    }
    // Fallback: usar endpoint público da API para servir áudio pelo ID da mensagem
    else if (message.id) {
      url = `http://localhost:8000/api/audio/message/${message.id}/public/`
      console.log('🎵 URL fallback público por ID:', url)
    }

    console.log('🎵 URL final determinada:', url)

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
    
    // Prioridade 1: URL da nova estrutura de chat_id (backend modificado)
    if (message.media_url && (message.media_url.startsWith('/media/whatsapp_media/') || message.media_url.startsWith('/api/whatsapp-media/'))) {
      url = message.media_url.startsWith('/api/') ? `http://localhost:8000${message.media_url}` : `http://localhost:8000/api${message.media_url}`
      console.log('🖼️ URL da nova estrutura:', url)
    }
    // Prioridade 2: Conteúdo já é a URL local (serializer modificado)
    else if ((message.conteudo || message.content) && 
             (typeof (message.conteudo || message.content) === 'string') &&
             ((message.conteudo || message.content).startsWith('/media/whatsapp_media/') || 
              (message.conteudo || message.content).startsWith('/api/whatsapp-media/'))) {
      const contentUrl = message.conteudo || message.content
      url = contentUrl.startsWith('/api/') ? `http://localhost:8000${contentUrl}` : `http://localhost:8000/api${contentUrl}`
      console.log('🖼️ URL do conteúdo processado:', url)
    }
    // Prioridade 3: URL da pasta /wapi/midias/
    else if (imageMessage.url && imageMessage.url.startsWith('/wapi/midias/')) {
      const filename = imageMessage.url.split('/').pop()
      url = `http://localhost:8000/api/wapi-media/imagens/${filename}`
    }
    // Prioridade 4: URL direta do JSON
    else if (imageMessage.url) {
      url = imageMessage.url
    }
    // Prioridade 5: Tentar construir URL baseada no message_id
    else if (message.id) {
      // Tentar diferentes extensões comuns
      const extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
      for (const ext of extensions) {
        const testUrl = `http://localhost:8000/api/wapi-media/imagens/${message.id}.${ext}`
        // Aqui poderíamos fazer uma verificação prévia, mas por enquanto vamos usar a primeira
        url = testUrl
        break
      }
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
    // Prioridade 3: Tentar construir URL baseada no message_id
    else if (message.id) {
      const extensions = ['mp4', 'webm', 'avi']
      for (const ext of extensions) {
        const testUrl = `http://localhost:8000/api/wapi-media/videos/${message.id}.${ext}`
        url = testUrl
        break
      }
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
    // Prioridade 3: Tentar construir URL baseada no message_id
    else if (message.id) {
      const extensions = ['webp', 'gif', 'png']
      for (const ext of extensions) {
        const testUrl = `http://localhost:8000/api/wapi-media/stickers/${message.id}.${ext}`
        url = testUrl
        break
      }
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
      url = `http://localhost:8000/api/wapi-media/documentos/${filename}`
    }
    // Prioridade 2: URL direta do JSON
    else if (documentMessage.url) {
      url = documentMessage.url
    }
    // Prioridade 3: Tentar construir URL baseada no message_id
    else if (message.id) {
      const extensions = ['pdf', 'doc', 'docx', 'txt']
      for (const ext of extensions) {
        const testUrl = `http://localhost:8000/api/wapi-media/documentos/${message.id}.${ext}`
        url = testUrl
        break
      }
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
          className="bg-accent/50 border border-border rounded-lg p-3"
        >
          <div className="flex items-center gap-2">
            <div className="p-1 bg-orange-500 rounded text-white">
              <AlertTriangle className="w-4 h-4" />
            </div>
            <div className="flex-1">
              <p className="text-sm text-foreground opacity-80">
                {message.tipo === 'audio' ? '[Áudio não disponível]' :
                 message.tipo === 'image' || message.tipo === 'imagem' ? '[Imagem não disponível]' :
                 message.tipo === 'video' ? '[Vídeo não disponível]' :
                 message.tipo === 'document' || message.tipo === 'documento' ? '[Documento não disponível]' :
                 '[Mídia não disponível]'}
              </p>
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
  const [volume, setVolume] = useState(1)
  const [isMuted, setIsMuted] = useState(false)
  const [audioError, setAudioError] = useState(false)
  const audioRef = useRef(null)
  
  // Extrair informações do audioMessage se disponível
  const getAudioInfo = () => {
    try {
      const content = message.content || message.conteudo
      if (typeof content === 'string' && content.startsWith('{')) {
        const parsed = JSON.parse(content)
        if (parsed.audioMessage) {
          return {
            seconds: parsed.audioMessage.seconds || 0,
            waveform: parsed.audioMessage.waveform,
            fileSize: parsed.audioMessage.fileLength
          }
        }
      }
    } catch (e) {
      // Ignore parsing errors
    }
    return null
  }
  
  const audioInfo = getAudioInfo()

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
    const handleError = () => {
      setIsLoading(false)
      setAudioError(true)
      console.error('Erro ao carregar áudio:', mediaUrl)
    }

    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('loadedmetadata', updateDuration)
    audio.addEventListener('play', handlePlay)
    audio.addEventListener('pause', handlePause)
    audio.addEventListener('ended', handleEnded)
    audio.addEventListener('loadeddata', handleLoadedData)
    audio.addEventListener('error', handleError)

    return () => {
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('loadedmetadata', updateDuration)
      audio.removeEventListener('play', handlePlay)
      audio.removeEventListener('pause', handlePause)
      audio.removeEventListener('ended', handleEnded)
      audio.removeEventListener('loadeddata', handleLoadedData)
      audio.removeEventListener('error', handleError)
    }
  }, [mediaUrl])

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
      } else {
        audioRef.current.play().catch(error => {
          console.error('Erro ao reproduzir áudio:', error)
        })
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

  const handleVolumeChange = (value) => {
    const newVolume = value[0] / 100
    setVolume(newVolume)
    if (audioRef.current) {
      audioRef.current.volume = newVolume
    }
  }

  const toggleMute = () => {
    if (audioRef.current) {
      if (isMuted) {
        audioRef.current.volume = volume
        setIsMuted(false)
      } else {
        audioRef.current.volume = 0
        setIsMuted(true)
      }
    }
  }

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }

  const sliderValue = duration > 0 ? [(currentTime / duration) * 100] : [0]
  const volumeValue = [volume * 100]

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
      
      {/* Player de áudio melhorado */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-accent border border-border rounded-lg p-4 hover:bg-accent/80 transition-colors"
      >
        <div className="space-y-3">
          {/* Controles principais */}
          <div className="flex items-center gap-3">
            {/* Botão Play/Pause */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={togglePlay}
              disabled={isLoading || audioError}
              className={`p-3 rounded-full shadow-sm transition-colors ${
                isLoading 
                  ? 'bg-muted text-muted-foreground cursor-not-allowed'
                  : audioError
                  ? 'bg-red-500/20 text-red-500 cursor-not-allowed'
                  : 'bg-primary text-primary-foreground hover:bg-primary/90'
              }`}
              title={
                isLoading ? 'Carregando...' : 
                audioError ? 'Áudio não disponível' :
                (isPlaying ? 'Pausar' : 'Reproduzir')
              }
            >
              {isLoading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : audioError ? (
                <AlertTriangle className="w-6 h-6" />
              ) : isPlaying ? (
                <Pause className="w-6 h-6" />
              ) : (
                <Play className="w-6 h-6" />
              )}
            </motion.button>
            
            {/* Informações do áudio */}
            <div className="flex-1 min-w-0">
              <p className="font-medium text-foreground truncate">
                {message.filename || 'Áudio'}
              </p>
              <p className="text-xs text-muted-foreground">
                {isLoading ? 'Carregando...' : 
                 audioError ? (audioInfo ? `${formatTime(audioInfo.seconds)} - Arquivo não disponível` : 'Arquivo não disponível') :
                 (message.duration || (audioInfo ? formatTime(audioInfo.seconds) : formatTime(duration)))}
              </p>
              {audioInfo && audioInfo.fileSize && (
                <p className="text-xs text-muted-foreground opacity-70">
                  {Math.round(audioInfo.fileSize / 1024)}KB
                </p>
              )}
            </div>
            
            {/* Controles de volume */}
            <div className="flex items-center gap-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={toggleMute}
                className="p-2 hover:bg-background rounded-lg transition-colors"
                title={isMuted ? 'Ativar som' : 'Silenciar'}
              >
                {isMuted ? (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 14.142M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                  </svg>
                )}
              </motion.button>
              
              <div className="w-20">
                <Slider
                  value={volumeValue}
                  onValueChange={handleVolumeChange}
                  max={100}
                  step={1}
                  className="w-full"
                  disabled={isLoading}
                />
              </div>
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
          
          {/* Slider de progresso */}
          {!isLoading && (
            <div className="space-y-2">
              <Slider
                value={sliderValue}
                onValueChange={handleSliderChange}
                max={100}
                step={0.1}
                className="w-full"
                disabled={isLoading}
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>{formatTime(currentTime)}</span>
                <span>{formatTime(duration)}</span>
              </div>
            </div>
          )}
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
  const [imageError, setImageError] = useState(false)
  const [imageLoading, setImageLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleImageLoad = () => {
    setImageLoading(false)
    setImageError(false)
  }

  const handleImageError = () => {
    setImageLoading(false)
    setImageError(true)
    console.error('Erro ao carregar imagem:', mediaUrl)
  }

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
        {imageLoading && (
          <div className="flex items-center justify-center h-48 bg-muted rounded-lg">
            <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
          </div>
        )}
        
        {imageError ? (
          <div className="flex items-center justify-center h-48 bg-red-50 border border-red-200 rounded-lg">
            <div className="text-center">
              <AlertTriangle className="w-8 h-8 text-red-500 mx-auto mb-2" />
              <p className="text-sm text-red-600">Erro ao carregar imagem</p>
              <p className="text-xs text-red-500 mt-1">URL: {mediaUrl}</p>
            </div>
          </div>
        ) : (
          <div className="relative">
            <img
              src={mediaUrl}
              alt="Imagem"
              className={`rounded-lg max-h-[300px] w-auto object-cover shadow-sm hover:shadow-md transition-shadow duration-200 cursor-pointer ${
                imageLoading ? 'hidden' : ''
              }`}
              onLoad={handleImageLoad}
              onError={handleImageError}
              onClick={() => setIsModalOpen(true)}
            />
            
            {/* Overlay com botões */}
            {!imageLoading && !imageError && (
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors rounded-lg">
                <div className="absolute top-2 right-2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-2 bg-black/80 text-white rounded-full hover:bg-black/90 transition-colors shadow-lg"
                    onClick={(e) => {
                      e.stopPropagation()
                      setIsModalOpen(true)
                    }}
                    title="Visualizar imagem"
                  >
                    <Eye className="w-4 h-4" />
                  </motion.button>
                  
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-2 bg-black/80 text-white rounded-full hover:bg-black/90 transition-colors shadow-lg"
                    onClick={(e) => {
                      e.stopPropagation()
                      if (mediaUrl) {
                        const link = document.createElement('a')
                        link.href = mediaUrl
                        link.download = `image_${message.id || Date.now()}.jpg`
                        link.click()
                      }
                    }}
                    title="Baixar imagem"
                  >
                    <Download className="w-4 h-4" />
                  </motion.button>
                </div>
              </div>
            )}
          </div>
        )}
      </motion.div>
      
      {/* Modal de visualização */}
      <ImageModal
        isOpen={isModalOpen}
        imageUrl={mediaUrl}
        onClose={() => setIsModalOpen(false)}
        imageAlt={message.content || "Imagem"}
      />
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