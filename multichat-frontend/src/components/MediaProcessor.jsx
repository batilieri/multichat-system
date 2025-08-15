import React, { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Download,
  Play,
  Pause,
  Loader2,
  AlertTriangle,
  MessageCircle,
  Eye,
  Clock
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
  const [fallbackUrls, setFallbackUrls] = useState([])
  const [currentUrlIndex, setCurrentUrlIndex] = useState(0)

  // Processar dados da mensagem para extrair informações de mídia
  useEffect(() => {
    console.log('🎵 DEBUG MediaProcessor - Dados da mensagem:', message)
    console.log('🎵 DEBUG MediaProcessor - ID:', message.id)
    console.log('🎵 DEBUG MediaProcessor - Message_ID:', message.message_id)
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
      
      // Prioridade 1: Tipo explícito da mensagem
      const messageType = message.tipo || message.type
      if (messageType) {
        if (messageType === 'audio' || messageType === 'Audio') {
          console.log('🎵 Tipo áudio detectado pelo campo tipo')
          setMediaType(MediaType.AUDIO)
          processAudioMessage(content, message, setMediaUrl, setIsLoading, setError, setFallbackUrls, setCurrentUrlIndex)
          return
        } else if (messageType === 'image' || messageType === 'imagem') {
          console.log('🖼️ Tipo imagem detectado pelo campo tipo')
          setMediaType(MediaType.IMAGE)
          processImageMessage(content, message, setMediaUrl, setIsLoading, setError)
          return
        } else if (messageType === 'video') {
          console.log('🎬 Tipo vídeo detectado pelo campo tipo')
          setMediaType(MediaType.VIDEO)
          processVideoMessage(content, message, setMediaUrl, setIsLoading, setError)
          return
        } else if (messageType === 'sticker') {
          console.log('😀 Tipo sticker detectado pelo campo tipo')
          setMediaType(MediaType.STICKER)
          processStickerMessage(content, message, setMediaUrl, setIsLoading, setError)
          return
        } else if (messageType === 'document' || messageType === 'documento') {
          console.log('📄 Tipo documento detectado pelo campo tipo')
          setMediaType(MediaType.DOCUMENT)
          processDocumentMessage(content, message, setMediaUrl, setIsLoading, setError)
          return
        }
      }
      
      // Prioridade 2: Conteúdo JSON com tipo de mídia
      if (content) {
        if (content.audioMessage) {
          console.log('🎵 Tipo áudio detectado pelo conteúdo JSON')
          setMediaType(MediaType.AUDIO)
          processAudioMessage(content.audioMessage, message, setMediaUrl, setIsLoading, setError, setFallbackUrls, setCurrentUrlIndex)
          return
        } else if (content.imageMessage) {
          console.log('🖼️ Tipo imagem detectado pelo conteúdo JSON')
          setMediaType(MediaType.IMAGE)
          processImageMessage(content.imageMessage, message, setMediaUrl, setIsLoading, setError)
          return
        } else if (content.videoMessage) {
          console.log('🎬 Tipo vídeo detectado pelo conteúdo JSON')
          setMediaType(MediaType.VIDEO)
          processVideoMessage(content.videoMessage, message, setMediaUrl, setIsLoading, setError)
          return
        } else if (content.stickerMessage) {
          console.log('😀 Tipo sticker detectado pelo conteúdo JSON')
          setMediaType(MediaType.STICKER)
          processStickerMessage(content.stickerMessage, message, setMediaUrl, setIsLoading, setError)
          return
        } else if (content.documentMessage) {
          console.log('📄 Tipo documento detectado pelo conteúdo JSON')
          setMediaType(MediaType.DOCUMENT)
          processDocumentMessage(content.documentMessage, message, setMediaUrl, setIsLoading, setError)
          return
        }
      }
      
      // Se chegou aqui, não conseguiu detectar o tipo
      console.log('⚠️ Nenhum tipo de mídia detectado')
      setError('Tipo de mídia não suportado')
      setIsLoading(false)

    } catch (error) {
      console.error('❌ Erro ao processar mídia:', error)
      setError('Erro ao processar mídia')
      setIsLoading(false)
    }
  }, [message])

  // Função para tentar próxima URL de fallback
  const tryNextFallbackUrl = () => {
    if (currentUrlIndex < fallbackUrls.length - 1) {
      const nextIndex = currentUrlIndex + 1
      const nextUrl = fallbackUrls[nextIndex]
      
      console.log(`🎵 Tentando URL de fallback ${nextIndex + 1}/${fallbackUrls.length}: ${nextUrl.description}`)
      console.log(`🎵 URL: ${nextUrl.url}`)
      
      setCurrentUrlIndex(nextIndex)
      setMediaUrl(nextUrl.url)
      setError(null)
      setIsLoading(true)
      
      return true
    } else {
      console.log('🎵 Todas as URLs de fallback foram tentadas')
      setError('Não foi possível carregar a mídia com nenhuma das URLs disponíveis')
      setIsLoading(false)
      return false
    }
  }

  // Função para resetar e tentar novamente
  const resetAndRetry = () => {
    console.log('🎵 Resetando e tentando novamente...')
    setCurrentUrlIndex(0)
    setError(null)
    setIsLoading(true)
    
    if (fallbackUrls.length > 0) {
      const firstUrl = fallbackUrls[0]
      console.log(`🎵 Tentando primeira URL novamente: ${firstUrl.description}`)
      setMediaUrl(firstUrl.url)
    }
  }

  // Listener para eventos de erro de áudio
  useEffect(() => {
    const handleAudioLoadError = (event) => {
      const { message: errorMessage, mediaUrl: errorUrl, retryCount } = event.detail
      
      console.log('🎵 Evento de erro de áudio recebido:', {
        message: errorMessage,
        url: errorUrl,
        retryCount
      })
      
      // Se o erro é da URL atual e temos URLs de fallback, tentar próxima
      if (errorUrl === mediaUrl && fallbackUrls.length > 0) {
        console.log('🎵 Tentando próxima URL de fallback automaticamente...')
        tryNextFallbackUrl()
      }
    }

    window.addEventListener('audioLoadError', handleAudioLoadError)
    
    return () => {
      window.removeEventListener('audioLoadError', handleAudioLoadError)
    }
  }, [mediaUrl, fallbackUrls])

  // Renderizar erro
  if (error) {
    return (
      <div className="space-y-2">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-accent/50 border border-border rounded-lg p-4"
        >
          <div className="space-y-3">
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
                <p className="text-xs text-muted-foreground mt-1">
                  {error}
                </p>
              </div>
            </div>
            
            {/* Botões de ação */}
            <div className="flex gap-2">
              {/* Botão de retry */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={resetAndRetry}
                className="px-3 py-1 bg-primary text-primary-foreground rounded text-sm"
              >
                Tentar Novamente
              </motion.button>
              
              {/* Botão de próxima URL de fallback */}
              {fallbackUrls.length > 0 && currentUrlIndex < fallbackUrls.length - 1 && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={tryNextFallbackUrl}
                  className="px-3 py-1 bg-secondary text-secondary-foreground rounded text-sm"
                >
                  Próxima URL ({currentUrlIndex + 1}/{fallbackUrls.length})
                </motion.button>
              )}
              
              {/* Informações de debug */}
              {fallbackUrls.length > 0 && (
                <div className="text-xs text-muted-foreground ml-auto">
                  {fallbackUrls.length} URLs de fallback disponíveis
                </div>
              )}
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

// Funções de processamento de mídia
const processAudioMessage = (audioMessage, message, setMediaUrl, setIsLoading, setError, setFallbackUrls, setCurrentUrlIndex) => {
  console.log('🎵 Processando áudio:', audioMessage)
  
  // Array de estratégias de URL em ordem de prioridade
  const audioUrlStrategies = []
  
  // Verificar se temos dados de áudio válidos
  if (!audioMessage) {
    console.log('🎵 Nenhum audioMessage fornecido')
    setError('Dados de áudio não encontrados')
    setIsLoading(false)
    return
  }
  
  // ESTRATÉGIA 1: Endpoint inteligente baseado no message_id (PRIORITÁRIO)
  if (message.id) {
    const url = `http://localhost:8000/api/media/message/${message.id}/`
    audioUrlStrategies.push({
      priority: 1,
      url: url,
      description: 'Endpoint inteligente por message_id'
    })
  }
  
  // ESTRATÉGIA 2: URL da nova estrutura de chat_id (backend modificado)
  if (message.media_url) {
    if (message.media_url.startsWith('/media/whatsapp_media/') || 
        message.media_url.startsWith('/api/whatsapp-media/')) {
      const url = message.media_url.startsWith('/api/') 
        ? `http://localhost:8000${message.media_url}` 
        : `http://localhost:8000/api${message.media_url}`
      audioUrlStrategies.push({
        priority: 2,
        url: url,
        description: 'Nova estrutura de chat_id'
      })
    }
  }
  
  // ESTRATÉGIA 3: Conteúdo já é a URL local (serializer modificado)
  if (message.conteudo && typeof message.conteudo === 'string') {
    if (message.conteudo.startsWith('/media/') || message.conteudo.startsWith('/api/')) {
      const url = message.conteudo.startsWith('/api/') 
        ? `http://localhost:8000${message.conteudo}` 
        : `http://localhost:8000/api${message.conteudo}`
      audioUrlStrategies.push({
        priority: 3,
        url: url,
        description: 'URL do conteúdo'
      })
    }
  }
  
  // ESTRATÉGIA 4: URL da pasta /wapi/midias/
  if (audioMessage.url && audioMessage.url.startsWith('/wapi/midias/')) {
    const filename = audioMessage.url.split('/').pop()
    const url = `http://localhost:8000/api/wapi-media/audios/${filename}`
    audioUrlStrategies.push({
      priority: 4,
      url: url,
      description: 'Pasta /wapi/midias/'
    })
  }
  
  // ESTRATÉGIA 5: Nome do arquivo na pasta /wapi/midias/
  if (audioMessage.fileName) {
    const url = `http://localhost:8000/api/wapi-media/audios/${audioMessage.fileName}`
    audioUrlStrategies.push({
      priority: 5,
      url: url,
      description: 'fileName da pasta /wapi/midias/'
    })
  }
  
  // ESTRATÉGIA 6: URL direta do JSON (WhatsApp)
  if (audioMessage.url && audioMessage.url.startsWith('http')) {
    audioUrlStrategies.push({
      priority: 6,
      url: audioMessage.url,
      description: 'URL direta do WhatsApp'
    })
  }
  
  // ESTRATÉGIA 7: Endpoint público por ID da mensagem (fallback)
  if (message.id) {
    const url = `http://localhost:8000/api/audio/message/${message.id}/public/`
    audioUrlStrategies.push({
      priority: 7,
      url: url,
      description: 'Endpoint público por ID (fallback)'
    })
  }
  
  // ESTRATÉGIA 7: Endpoint inteligente por chat_id e message_id
  if (message.chat_id && (message.message_id || message.id)) {
    const clienteId = 2 // Cliente Elizeu (hardcoded por enquanto)
    const instanceId = '3B6XIW-ZTS923-GEAY6V' // Instance ID hardcoded
    const chatId = message.chat_id
    const messageId = message.message_id || message.id
    
    const url = `http://localhost:8000/api/whatsapp-audio-smart/${clienteId}/${instanceId}/${chatId}/${messageId}/`
    audioUrlStrategies.push({
      priority: 7,
      url: url,
      description: 'Endpoint inteligente por chat_id'
    })
  }
  
  // ESTRATÉGIA 8: Endpoint de mídia genérico
  if (message.id) {
    const url = `http://localhost:8000/api/media/message/${message.id}/`
    audioUrlStrategies.push({
      priority: 8,
      url: url,
      description: 'Endpoint de mídia genérico'
    })
  }
  
  // Ordenar estratégias por prioridade
  audioUrlStrategies.sort((a, b) => a.priority - b.priority)
  
  console.log('🎵 Estratégias de URL encontradas:', audioUrlStrategies)
  
  if (audioUrlStrategies.length > 0) {
    // Tentar a primeira estratégia (maior prioridade)
    const primaryStrategy = audioUrlStrategies[0]
    console.log(`🎵 Tentando estratégia ${primaryStrategy.priority}: ${primaryStrategy.description}`)
    console.log(`🎵 URL: ${primaryStrategy.url}`)
    
    setMediaUrl(primaryStrategy.url)
    setIsLoading(false)
    
    // Se houver múltiplas estratégias, armazenar para fallback
    if (audioUrlStrategies.length > 1) {
      const fallbackStrategies = audioUrlStrategies.slice(1)
      console.log('🎵 Estratégias de fallback disponíveis:', 
        fallbackStrategies.map(s => `${s.priority}: ${s.description}`))
      setFallbackUrls(fallbackStrategies)
      setCurrentUrlIndex(0)
    } else {
      setFallbackUrls([])
      setCurrentUrlIndex(0)
    }
  } else {
    console.log('🎵 Nenhuma estratégia de URL encontrada')
    setError('URL de áudio não disponível')
    setIsLoading(false)
    setFallbackUrls([])
    setCurrentUrlIndex(0)
  }
}

// Processar mensagem de imagem
const processImageMessage = (imageMessage, message, setMediaUrl, setIsLoading, setError) => {
  console.log('🖼️ Processando imagem:', imageMessage)
  
  let url = null
  
  // Prioridade 1: Endpoint inteligente baseado no message_id (PRIORITÁRIO)
  if (message.id) {
    url = `http://localhost:8000/api/media/message/${message.id}/`
    console.log('🖼️ URL endpoint inteligente:', url)
  }
  // Prioridade 2: URL da nova estrutura de chat_id (backend modificado)
  else if (message.media_url && (message.media_url.startsWith('/media/whatsapp_media/') || message.media_url.startsWith('/api/whatsapp-media/'))) {
    url = message.media_url.startsWith('/api/') ? `http://localhost:8000${message.media_url}` : `http://localhost:8000/api${message.media_url}`
    console.log('🖼️ URL da nova estrutura:', url)
  }
  // Prioridade 3: Conteúdo já é a URL local (serializer modificado)
  else if ((message.conteudo || message.content) && 
           (typeof (message.conteudo || message.content) === 'string') &&
           ((message.conteudo || message.content).startsWith('/media/whatsapp_media/') || 
            (message.conteudo || message.content).startsWith('/api/whatsapp-media/'))) {
    const contentUrl = message.conteudo || message.content
    url = contentUrl.startsWith('/api/') ? `http://localhost:8000${contentUrl}` : `http://localhost:8000/api${contentUrl}`
    console.log('🖼️ URL do conteúdo processado:', url)
  }
  // Prioridade 4: URL da pasta /wapi/midias/
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
const processVideoMessage = (videoMessage, message, setMediaUrl, setIsLoading, setError) => {
  console.log('🎬 Processando vídeo:', videoMessage)
  
  let url = null
  
  // Prioridade 1: Endpoint inteligente baseado no message_id (PRIORITÁRIO)
  if (message.id) {
    url = `http://localhost:8000/api/media/message/${message.id}/`
  }
  // Prioridade 2: URL da pasta /wapi/midias/
  else if (videoMessage.url && videoMessage.url.startsWith('/wapi/midias/')) {
    const filename = videoMessage.url.split('/').pop()
    url = `http://localhost:8000/api/wapi-media/videos/${filename}`
  }
  // Prioridade 3: URL direta do JSON
  else if (videoMessage.url) {
    url = videoMessage.url
  }
  // Prioridade 4: Tentar construir URL baseada no message_id
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
const processStickerMessage = (stickerMessage, message, setMediaUrl, setIsLoading, setError) => {
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
const processDocumentMessage = (documentMessage, message, setMediaUrl, setIsLoading, setError) => {
  console.log('📄 Processando documento:', documentMessage)
  
  let url = null
  
  // Prioridade 1: Endpoint inteligente baseado no message_id (PRIORITÁRIO)
  if (message.id) {
    url = `http://localhost:8000/api/media/message/${message.id}/`
  }
  // Prioridade 2: URL da pasta /wapi/midias/
  else if (documentMessage.url && documentMessage.url.startsWith('/wapi/midias/')) {
    const filename = documentMessage.url.split('/').pop()
    url = `http://localhost:8000/api/wapi-media/documentos/${filename}`
  }
  // Prioridade 3: URL direta do JSON
  else if (documentMessage.url) {
    url = documentMessage.url
  }
  // Prioridade 4: Tentar construir URL baseada no message_id
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

// Componente para exibir áudio - COMPLETAMENTE REFATORADO
const AudioPlayer = ({ message, mediaUrl }) => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [volume, setVolume] = useState(1)
  const [isMuted, setIsMuted] = useState(false)
  const [audioError, setAudioError] = useState(false)
  const [audioLoaded, setAudioLoaded] = useState(false)
  const [retryCount, setRetryCount] = useState(0)
  const audioRef = useRef(null)
  
  // Debug: monitorar mudanças na mediaUrl
  useEffect(() => {
    console.log('🎵 AudioPlayer - mediaUrl alterada:', mediaUrl)
    if (mediaUrl) {
      setAudioError(false)
      setIsLoading(true)
      setAudioLoaded(false)
      setRetryCount(0)
    }
  }, [mediaUrl])
  
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
            fileSize: parsed.audioMessage.fileLength,
            fileName: parsed.audioMessage.fileName
          }
        }
      }
    } catch (e) {
      console.warn('🎵 Erro ao extrair info do áudio:', e)
    }
    return null
  }
  
  const audioInfo = getAudioInfo()

  // Gerenciar eventos do áudio de forma robusta
  useEffect(() => {
    const audio = audioRef.current
    if (!audio || !mediaUrl) return

    console.log('🎵 Configurando eventos do áudio para URL:', mediaUrl)

    const updateTime = () => {
      if (!isNaN(audio.currentTime)) {
        setCurrentTime(audio.currentTime)
      }
    }
    
    const updateDuration = () => {
      if (!isNaN(audio.duration) && audio.duration > 0) {
        console.log('🎵 Duração do áudio carregada:', audio.duration)
        setDuration(audio.duration)
      }
    }
    
    const handlePlay = () => {
      console.log('🎵 Áudio iniciou reprodução')
      setIsPlaying(true)
    }
    
    const handlePause = () => {
      console.log('🎵 Áudio pausado')
      setIsPlaying(false)
    }
    
    const handleEnded = () => {
      console.log('🎵 Áudio terminou')
      setIsPlaying(false)
      setCurrentTime(0)
    }
    
    const handleLoadedData = () => {
      console.log('🎵 Dados do áudio carregados')
      setIsLoading(false)
      setAudioLoaded(true)
      setAudioError(false)
      
      if (!isNaN(audio.duration) && audio.duration > 0) {
        setDuration(audio.duration)
      }
    }
    
    const handleCanPlay = () => {
      console.log('🎵 Áudio pode ser reproduzido')
      setIsLoading(false)
      setAudioLoaded(true)
      setAudioError(false)
    }
    
    const handleError = (e) => {
      console.error('🎵 Erro ao carregar áudio:', e)
      console.error('🎵 Detalhes do erro:', {
        error: audio.error,
        networkState: audio.networkState,
        readyState: audio.readyState,
        src: audio.src
      })
      setIsLoading(false)
      setAudioError(true)
      setAudioLoaded(false)
      
      // Incrementar contador de tentativas
      setRetryCount(prev => prev + 1)
    }
    
    const handleLoadStart = () => {
      console.log('🎵 Iniciando carregamento do áudio')
      setIsLoading(true)
      setAudioError(false)
    }
    
    const handleProgress = () => {
      if (audio.buffered.length > 0) {
        const bufferedEnd = audio.buffered.end(audio.buffered.length - 1)
        console.log('🎵 Progresso do buffer:', bufferedEnd, 'de', audio.duration)
      }
    }

    // Adicionar todos os event listeners
    audio.addEventListener('timeupdate', updateTime)
    audio.addEventListener('loadedmetadata', updateDuration)
    audio.addEventListener('play', handlePlay)
    audio.addEventListener('pause', handlePause)
    audio.addEventListener('ended', handleEnded)
    audio.addEventListener('loadeddata', handleLoadedData)
    audio.addEventListener('canplay', handleCanPlay)
    audio.addEventListener('error', handleError)
    audio.addEventListener('loadstart', handleLoadStart)
    audio.addEventListener('progress', handleProgress)

    // Cleanup function
    return () => {
      audio.removeEventListener('timeupdate', updateTime)
      audio.removeEventListener('loadedmetadata', updateDuration)
      audio.removeEventListener('play', handlePlay)
      audio.removeEventListener('pause', handlePause)
      audio.removeEventListener('ended', handleEnded)
      audio.removeEventListener('loadeddata', handleLoadedData)
      audio.removeEventListener('canplay', handleCanPlay)
      audio.removeEventListener('error', handleError)
      audio.removeEventListener('loadstart', handleLoadStart)
      audio.removeEventListener('progress', handleProgress)
    }
  }, [mediaUrl])

  // Função robusta para play/pause
  const togglePlay = async () => {
    if (!audioRef.current || !audioLoaded) {
      console.warn('🎵 Áudio não está pronto para reprodução')
      return
    }

    try {
      if (isPlaying) {
        audioRef.current.pause()
      } else {
        // Verificar se o áudio está carregado
        if (audioRef.current.readyState >= 2) { // HAVE_CURRENT_DATA
          await audioRef.current.play()
        } else {
          console.warn('🎵 Áudio não está carregado o suficiente para reprodução')
          setIsLoading(true)
        }
      }
    } catch (error) {
      console.error('🎵 Erro ao controlar reprodução:', error)
      setAudioError(true)
    }
  }

  // Função robusta para slider de progresso
  const handleSliderChange = (value) => {
    if (audioRef.current && duration > 0 && audioLoaded) {
      const newTime = (value[0] / 100) * duration
      if (!isNaN(newTime) && newTime >= 0 && newTime <= duration) {
        audioRef.current.currentTime = newTime
        setCurrentTime(newTime)
      }
    }
  }

  // Função robusta para controle de volume
  const handleVolumeChange = (value) => {
    const newVolume = Math.max(0, Math.min(1, value[0] / 100))
    setVolume(newVolume)
    if (audioRef.current) {
      audioRef.current.volume = newVolume
    }
  }

  // Função robusta para mute
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

  // Função para formatar tempo
  const formatTime = (time) => {
    if (!time || isNaN(time)) return '00:00'
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }

  // Calcular valores dos sliders
  const sliderValue = duration > 0 ? [(currentTime / duration) * 100] : [0]
  const volumeValue = [volume * 100]

  // Debug: mostrar estado atual
  console.log('🎵 AudioPlayer - Estado atual:', {
    isLoading,
    audioLoaded,
    audioError,
    isPlaying,
    currentTime,
    duration,
    mediaUrl,
    retryCount
  })

  // Se não há URL de áudio, mostrar erro
  if (!mediaUrl) {
    return (
      <div className="space-y-2">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-accent/50 border border-border rounded-lg p-4"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-500 rounded-lg text-white">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-foreground">URL de áudio não disponível</p>
              <p className="text-xs text-muted-foreground">
                Não foi possível obter o link para este áudio
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    )
  }

  // Se há erro no carregamento, mostrar mensagem de erro com opções de retry
  if (audioError) {
    return (
      <div className="space-y-2">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-accent/50 border border-border rounded-lg p-4"
        >
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-500 rounded-lg text-white">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <p className="font-medium text-foreground">Erro ao carregar áudio</p>
                <p className="text-xs text-muted-foreground">
                  Não foi possível reproduzir este áudio. Tentativas: {retryCount}
                </p>
              </div>
            </div>
            
            {/* Botões de ação */}
            <div className="flex gap-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  setAudioError(false)
                  setIsLoading(true)
                  setAudioLoaded(false)
                  // Recarregar o áudio
                  if (audioRef.current) {
                    audioRef.current.load()
                  }
                }}
                className="px-3 py-1 bg-primary text-primary-foreground rounded text-sm"
              >
                Tentar Novamente
              </motion.button>
              
              {retryCount >= 3 && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => {
                    // Emitir evento para o componente pai tentar próxima URL
                    const event = new CustomEvent('audioLoadError', {
                      detail: { message, mediaUrl, retryCount }
                    })
                    window.dispatchEvent(event)
                  }}
                  className="px-3 py-1 bg-secondary text-secondary-foreground rounded text-sm"
                >
                  Tentar URL Alternativa
                </motion.button>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    )
  }

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
      
      {/* Player de áudio robusto */}
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
              disabled={isLoading || !audioLoaded}
              className={`p-3 rounded-full shadow-sm transition-colors ${
                isLoading 
                  ? 'bg-muted text-muted-foreground cursor-not-allowed'
                  : !audioLoaded
                  ? 'bg-yellow-500/20 text-yellow-500 cursor-not-allowed'
                  : 'bg-primary text-primary-foreground hover:bg-primary/90'
              }`}
              title={
                isLoading ? 'Carregando...' : 
                !audioLoaded ? 'Áudio não carregado' :
                (isPlaying ? 'Pausar' : 'Reproduzir')
              }
            >
              {isLoading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : !audioLoaded ? (
                <Clock className="w-6 h-6" />
              ) : isPlaying ? (
                <Pause className="w-6 h-6" />
              ) : (
                <Play className="w-6 h-6" />
              )}
            </motion.button>
            
            {/* Informações do áudio */}
            <div className="flex-1 min-w-0">
              <p className="font-medium text-foreground truncate">
                {audioInfo?.fileName || message.filename || 'Áudio'}
              </p>
              <p className="text-xs text-muted-foreground">
                {isLoading ? 'Carregando...' : 
                 !audioLoaded ? 'Preparando...' :
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
          {audioLoaded && (
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
        
        {/* Player de áudio HTML5 oculto */}
        <audio 
          ref={audioRef}
          className="hidden"
          preload="metadata"
          src={mediaUrl}
          crossOrigin="anonymous"
          onLoadStart={() => console.log('🎵 Áudio iniciando carregamento')}
          onCanPlay={() => console.log('🎵 Áudio pode ser reproduzido')}
          onLoadedData={() => console.log('🎵 Dados do áudio carregados')}
          onError={(e) => {
            console.error('🎵 Erro no elemento audio:', e)
            console.error('🎵 Detalhes do erro:', {
              error: e.target.error,
              networkState: e.target.networkState,
              readyState: e.target.readyState
            })
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