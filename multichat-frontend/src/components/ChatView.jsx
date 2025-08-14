// Este arquivo foi restaurado para a versão original da base.
// Importe novamente a versão padrão do ChatView.jsx do repositório principal.

import React, { useState, useEffect, useCallback, useMemo, memo } from 'react'
import { motion } from 'framer-motion'
import {
  Send,
  Paperclip,
  Smile,
  Phone,
  Video,
  MoreVertical,
  User,
  Users,
  MessageCircle,
  Calendar,
  MapPin,
  Mail,
  X,
  Edit,
  Ban,
  Trash2,
  Archive,
  VolumeX,
  Star,
  Pin,
  Heart,
  Info,
  CheckCheck,
  Play,
  Bookmark,
  Volume2,
  Plus,
  FileAudio
} from 'lucide-react'
import Message from './Message'
import EmojiPicker from './EmojiPicker'
import { useAuth } from '../contexts/AuthContext'
import { useChatUpdates } from '../hooks/use-realtime-updates'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogDescription
} from './ui/dialog'
import { Button } from './ui/button'
import { enviarMensagemWapi, enviarImagemWapi } from '../lib/wapi'
import PropTypes from 'prop-types'
import ImageUpload from './ImageUpload'
import { toast } from './ui/use-toast'

// Importar componentes extraídos
import {
  ContactInfoModal,
  PinnedMessagesModal,
  ForwardMessageModal,
  FavoritesModal,
  MessageInfoModal,
  ImageModal
} from './modals'

import {
  ChatHeader,
  MessageInput,
  MessagesContainer,
  PendingImagePreview
} from './chat'

const ChatView = ({ chat, instances = [], clients = [] }) => {
  // Constantes
  const MESSAGES_PAGE_SIZE = 50; // Número de mensagens por página

  // Estados para dados carregados internamente
  const [internalClients, setInternalClients] = useState([]);
  const [internalInstances, setInternalInstances] = useState([]);
  const [dataLoaded, setDataLoaded] = useState(false);
  const [editingName, setEditingName] = useState(false);
  
  // Estados para sistema de áudio
  const [showAudioModal, setShowAudioModal] = useState(false);
  const [selectedAudioFiles, setSelectedAudioFiles] = useState([]);
  const [currentAudioIndex, setCurrentAudioIndex] = useState(0);
  const [audioUploadProgress, setAudioUploadProgress] = useState({});
  const [audioPlaybackStatus, setAudioPlaybackStatus] = useState({});
  
  // Carregar dados se não foram passados como props
  useEffect(() => {
    const loadMissingData = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        const promises = [];

        // Carregar clientes se necessário
        if (!clients || clients.length === 0) {
          promises.push(
            fetch(`${API_BASE_URL}/api/clientes/`, {
              headers: { Authorization: `Bearer ${token}` },
            }).then(res => res.json())
          );
        } else {
          promises.push(Promise.resolve(null));
        }

        // Carregar instâncias se necessário
        if (!instances || instances.length === 0) {
          promises.push(
            fetch(`${API_BASE_URL}/api/whatsapp-instances/`, {
              headers: { Authorization: `Bearer ${token}` },
            }).then(res => res.json())
          );
        } else {
          promises.push(Promise.resolve(null));
        }

        const [clientsData, instancesData] = await Promise.all(promises);

        if (clientsData) {
          setInternalClients(clientsData.results || clientsData);
        }
        if (instancesData) {
          setInternalInstances(instancesData.results || instancesData);
        }

        setDataLoaded(true);
      } catch (error) {
        console.error('Erro ao carregar dados necessários:', error);
        setDataLoaded(true);
      }
    };

    loadMissingData();
  }, []); // Corrigido: executa apenas uma vez ao montar

  // Usar dados carregados ou props
  const effectiveClients = clients?.length > 0 ? clients : internalClients;
  const effectiveInstances = instances?.length > 0 ? instances : internalInstances;

  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const [offset, setOffset] = useState(0)
  const [showContactInfo, setShowContactInfo] = useState(false)
  const { apiRequest, user, isCliente } = useAuth();
  const [showPinsModal, setShowPinsModal] = useState(false)
  const [showImageModal, setShowImageModal] = useState(false)
  const [showFavoritesModal, setShowFavoritesModal] = useState(false)
  const [favoritedMessages, setFavoritedMessages] = useState([])
  const [pinnedMessages, setPinnedMessages] = useState([])
  const [showEmojiPicker, setShowEmojiPicker] = useState(false)
  const [showImageUpload, setShowImageUpload] = useState(false)
  const [isProcessingImage, setIsProcessingImage] = useState(false)
  const [pendingImage, setPendingImage] = useState(null)
  const [imageCaption, setImageCaption] = useState('')

  // Estados para encaminhamento de mensagens
  const [forwardModalMessage, setForwardModalMessage] = useState(null)
  const [forwardModalOpen, setForwardModalOpen] = useState(false)
  const [selectedChats, setSelectedChats] = useState([])
  const [forwardSearch, setForwardSearch] = useState('')

  // refs para scroll até mensagem
  const messageRefs = React.useRef({})
  const [infoModalMessage, setInfoModalMessage] = useState(null)

  // Carregar mensagens reais da API
  useEffect(() => {
    console.log('🔄 useEffect - chat mudou:', chat?.chat_id)
    if (chat?.chat_id) {
      console.log('📱 Carregando mensagens para chat:', chat.chat_id)
      // Limpar mensagens anteriores
      setMessages([])
      setLoading(true)
      loadMessages(0, true) // Carregar mensagens e scroll para o final
    } else {
      console.log('❌ Chat ID não encontrado')
      setMessages([])
    }
  }, [chat?.chat_id])

  // Carregar favoritas e mensagens fixadas da API (implementar quando necessário)
  useEffect(() => {
    // TODO: Implementar carregamento de favoritas e mensagens fixadas da API
    setFavoritedMessages([])
    setPinnedMessages([])
  }, [])

  // Fechar emoji picker quando clicar fora
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showEmojiPicker && !event.target.closest('.emoji-picker-container')) {
        setShowEmojiPicker(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [showEmojiPicker])

  // Detectar imagens no clipboard globalmente
  useEffect(() => {
    const handlePaste = async (event) => {
      const items = event.clipboardData?.items
      if (!items) return

      for (let item of items) {
        if (item.type.indexOf('image') !== -1) {
          const file = item.getAsFile()
          if (file) {
            console.log('📸 Imagem detectada no clipboard!')

            // Converter para Base64
            const reader = new FileReader()
            reader.onload = async (e) => {
              const base64 = e.target.result.split(',')[1]

              // Criar dados da imagem
              const imageData = {
                type: 'base64',
                data: base64,
                filename: `clipboard-${Date.now()}.png`,
                caption: ''
              }

              // Mostrar imagem no input para permitir legenda
              setPendingImage(imageData)
              setImageCaption('')
              toast({
                title: "📸 Imagem detectada",
                description: "Adicione uma legenda e clique em enviar",
                duration: 3000,
              })
            }
            reader.readAsDataURL(file)
            break
          }
        }
      }
    }

    // Adicionar listener global
    document.addEventListener('paste', handlePaste)
    return () => document.removeEventListener('paste', handlePaste)
  }, [chat?.id]) // Dependência do chat para garantir que handleSendImage está atualizado

  // Função para adicionar nova mensagem em tempo real
  // Callback memoizado para evitar re-renders desnecessários
  const handleNewMessage = useCallback((newMessage) => {
    console.log('🆕 Nova mensagem recebida em tempo real:', newMessage)

    setMessages(prevMessages => {
      // Verificar se a mensagem já existe para evitar duplicação
      const messageExists = prevMessages.some(msg => msg.id === newMessage.id)
      if (messageExists) {
        console.log('⚠️ Mensagem já existe, ignorando:', newMessage.id)
        return prevMessages
      }

      // Verificar se existe uma mensagem temporária que pode ser atualizada
      const tempMessageIndex = prevMessages.findIndex(msg =>
        msg.isTemporary &&
        msg.content === newMessage.content &&
        msg.from_me === true &&
        Math.abs(new Date(msg.timestamp) - new Date(newMessage.timestamp)) < 5000 // 5 segundos de tolerância
      )

      if (tempMessageIndex !== -1) {
        console.log('🔄 Atualizando mensagem temporária com dados do webhook:', newMessage.id)
        // Atualizar a mensagem temporária com os dados reais
        const updatedMessages = [...prevMessages]
        updatedMessages[tempMessageIndex] = {
          ...newMessage,
          isTemporary: false // Remove a flag temporária
        }
        return updatedMessages
      }

      // Transformar mensagem para o formato esperado
      const transformedMessage = {
        id: newMessage.id,
        type: newMessage.type,
        content: newMessage.content,
        timestamp: newMessage.timestamp,
        sender: newMessage.sender,
        isOwn: newMessage.isOwn,
        status: newMessage.status || 'sent',
        replyTo: null,
        forwarded: false,
        // Campos de mídia (se aplicável)
        mediaUrl: newMessage.mediaUrl,
        mediaType: newMessage.mediaType,
        mediaSize: newMessage.mediaSize,
        mediaCaption: newMessage.mediaCaption,
        mediaHeight: newMessage.mediaHeight,
        mediaWidth: newMessage.mediaWidth,
        jpegThumbnail: newMessage.jpegThumbnail,
        fileSha256: newMessage.fileSha256,
        mediaKey: newMessage.mediaKey,
        directPath: newMessage.directPath,
        mediaKeyTimestamp: newMessage.mediaKeyTimestamp,
        documentUrl: newMessage.documentUrl,
        documentFilename: newMessage.documentFilename,
        documentMimetype: newMessage.documentMimetype,
        documentFileLength: newMessage.documentFileLength,
        documentPageCount: newMessage.documentPageCount,
        locationLatitude: newMessage.locationLatitude,
        locationLongitude: newMessage.locationLongitude,
        locationName: newMessage.locationName,
        locationAddress: newMessage.locationAddress,
        contactName: newMessage.contactName,
        contactNumber: newMessage.contactNumber,
        contactDisplayName: newMessage.contactDisplayName,
        contactVcard: newMessage.contactVcard,
        // Campos de reação
        reaction: newMessage.reaction,
        // Campos de encaminhamento
        forwardedFrom: newMessage.forwardedFrom,
        forwardedFromName: newMessage.forwardedFromName,
        forwardedFromId: newMessage.forwardedFromId,
        // Campos de resposta
        replyToMessageId: newMessage.replyToMessageId,
        replyToMessageContent: newMessage.replyToMessageContent,
        replyToMessageSender: newMessage.replyToMessageSender,
        // Campos de ID
        messageId: newMessage.message_id || newMessage.id
      }

      console.log('✅ Nova mensagem adicionada ao estado:', transformedMessage)
      return [...prevMessages, transformedMessage]
    })

    // Scroll automático para a nova mensagem
    setTimeout(() => {
      const messagesContainer = document.querySelector('.messages-container')
      if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight
      }
    }, 100)
  }, [])

  // Callback memoizado para atualizações de chat
  const handleChatUpdate = useCallback((chatData) => {
    console.log('🔄 Chat atualizado em tempo real:', chatData)
    // Aqui você pode atualizar informações do chat se necessário
  }, [])

  // Usar hook de atualizações em tempo real - OTIMIZADO
  const { isConnected, getCachedMessages, clearChatCache } = useChatUpdates(
    chat?.chat_id,
    handleNewMessage,
    handleChatUpdate
  )

  // Verificar apenas novas mensagens periodicamente - OTIMIZADO
  useEffect(() => {
    if (!chat?.chat_id) return

    const checkNewMessagesInterval = setInterval(async () => {
      console.log('🔍 Verificando apenas mensagens novas...')

      try {
        // Buscar apenas mensagens mais recentes que a última carregada
        const lastMessageTimestamp = messages.length > 0
          ? messages[messages.length - 1]?.timestamp
          : new Date(Date.now() - 60000).toISOString() // 1 minuto atrás se não há mensagens

        // Temporariamente desabilitar o filtro after para debug
        const response = await apiRequest(
          `/api/mensagens/?chat_id=${chat.chat_id}&limit=10`
        )

        if (!response.ok) throw new Error('Erro na resposta da API')
        const data = await response.json()

        if (data.results && data.results.length > 0) {
          console.log(`📨 ${data.results.length} mensagens encontradas`)

          // Processar apenas as mensagens novas
          const newMessages = data.results.map(msg => {
            // Usar a mesma lógica de transformação da loadMessages
            let conteudoProcessado = msg.conteudo || msg.content || ''
            let mediaUrl = null
            let mediaType = null
            let mediaCaption = null

            if (typeof conteudoProcessado === 'string' && conteudoProcessado.startsWith('{')) {
              try {
                const jsonContent = JSON.parse(conteudoProcessado)
                if (jsonContent.imageMessage) {
                  mediaUrl = jsonContent.imageMessage.url
                  mediaType = 'image'
                  mediaCaption = jsonContent.imageMessage.caption
                  conteudoProcessado = mediaCaption || '[Imagem]'
                } else if (jsonContent.videoMessage) {
                  mediaUrl = jsonContent.videoMessage.url
                  mediaType = 'video'
                  mediaCaption = jsonContent.videoMessage.caption
                  conteudoProcessado = mediaCaption || '[Vídeo]'
                } else if (jsonContent.audioMessage) {
                  mediaUrl = jsonContent.audioMessage.url
                  mediaType = 'audio'
                  conteudoProcessado = '[Áudio]'
                } else if (jsonContent.documentMessage) {
                  mediaUrl = jsonContent.documentMessage.url
                  mediaType = 'document'
                  mediaCaption = jsonContent.documentMessage.fileName
                  conteudoProcessado = `[Documento] ${mediaCaption || 'Documento'}`
                } else if (jsonContent.stickerMessage) {
                  mediaUrl = jsonContent.stickerMessage.url
                  mediaType = 'sticker'
                  conteudoProcessado = '[Sticker]'
                } else if (jsonContent.textMessage) {
                  conteudoProcessado = jsonContent.textMessage.text || 'Mensagem de texto'
                } else {
                  conteudoProcessado = '[Mídia]'
                }
              } catch (error) {
                console.warn('⚠️ Erro ao processar JSON:', error)
                conteudoProcessado = '[Conteúdo inválido]'
              }
            }

            return {
              id: msg.id,
              message_id: msg.message_id,
              internalId: msg.id,
              type: msg.tipo,
              content: conteudoProcessado,
              timestamp: msg.data_envio,
              sender: msg.remetente,
              isOwn: msg.fromMe || msg.from_me,
              fromMe: msg.fromMe,
              from_me: msg.from_me,
              status: msg.lida ? 'read' : 'sent',
              replyTo: null,
              forwarded: false,
              mediaUrl: mediaUrl || msg.media_url,
              mediaType: mediaType || msg.media_type,
              mediaCaption: mediaCaption || msg.media_caption,
              mediaSize: msg.media_size,
              mediaHeight: msg.media_height,
              mediaWidth: msg.media_width,
              jpegThumbnail: msg.jpeg_thumbnail,
              fileSha256: msg.file_sha256,
              mediaKey: msg.media_key,
              directPath: msg.direct_path,
              mediaKeyTimestamp: msg.media_key_timestamp,
              documentUrl: msg.document_url,
              documentFilename: msg.document_filename,
              documentMimetype: msg.document_mimetype,
              documentFileLength: msg.document_file_length,
              documentPageCount: msg.document_page_count,
              locationLatitude: msg.location_latitude,
              locationLongitude: msg.location_longitude,
              locationName: msg.location_name,
              locationAddress: msg.location_address,
              contactName: msg.contact_name,
              contactNumber: msg.contact_number,
              contactDisplayName: msg.contact_display_name,
              contactVcard: msg.contact_vcard,
              reaction: msg.reaction,
              forwardedFrom: msg.forwarded_from,
              forwardedFromName: msg.forwarded_from_name,
              forwardedFromId: msg.forwarded_from_id,
              replyToMessageId: msg.reply_to_message_id,
              replyToMessageContent: msg.reply_to_message_content,
              replyToMessageSender: msg.reply_to_message_sender,
              messageId: msg.message_id || msg.id,
              thumbnailHeight: msg.thumbnail_height,
              thumbnailWidth: msg.thumbnail_width
            }
          })

          // Adicionar apenas as mensagens novas ao final e substituir temporárias
          setMessages(prevMessages => {
            const existingIds = new Set(prevMessages.map(msg => msg.id))
            const trulyNewMessages = newMessages.filter(msg => {
              // Verificar se já existe pelo ID
              if (existingIds.has(msg.id)) return false

              // Verificar se já existe pelo conteúdo e timestamp (evita duplicatas)
              const existingByContent = prevMessages.find(existing =>
                existing.content === msg.content &&
                existing.from_me === msg.from_me &&
                Math.abs(new Date(existing.timestamp) - new Date(msg.timestamp)) < 3000 // 3 segundos de tolerância
              )

              if (existingByContent) {
                console.log('⚠️ Ignorando mensagem duplicada:', msg.content)
                return false
              }

              return true
            })

            // Substituir mensagens temporárias por versões reais do backend (sem remover)
            const updatedMessages = prevMessages.map(msg => {
              // Se a mensagem é temporária, verificar se existe uma versão real do backend
              if (msg.isTemporary) {
                const realMessage = newMessages.find(realMsg =>
                  realMsg.content === msg.content &&
                  realMsg.from_me === true &&
                  Math.abs(new Date(realMsg.timestamp) - new Date(msg.timestamp)) < 5000 // 5 segundos de tolerância
                )
                if (realMessage) {
                  console.log('🔄 Atualizando mensagem temporária com dados reais:', realMessage.id)
                  // Retorna a versão real, mantendo a posição na lista
                  return {
                    ...realMessage,
                    isTemporary: false // Remove a flag temporária
                  }
                }
              }
              return msg // Mantém a mensagem como está
            })

            if (trulyNewMessages.length > 0) {
              console.log(`✅ Adicionando ${trulyNewMessages.length} mensagens novas`)
              return [...updatedMessages, ...trulyNewMessages]
            }

            return updatedMessages
          })
        }
      } catch (error) {
        console.error('❌ Erro ao verificar mensagens novas:', error)
      }
    }, 3000) // A cada 3 segundos

    return () => clearInterval(checkNewMessagesInterval)
  }, [chat?.chat_id]) // Remover dependência de messages.length para evitar loops

  // Scroll automático apenas quando novas mensagens são adicionadas
  const [lastMessageCount, setLastMessageCount] = useState(0)

  useEffect(() => {
    if (messages.length > lastMessageCount && messages.length > 0) {
      // Só faz scroll se foram adicionadas novas mensagens
      setTimeout(() => {
        const messagesContainer = document.querySelector('.messages-container')
        if (messagesContainer) {
          messagesContainer.scrollTop = messagesContainer.scrollHeight
        }
      }, 100)
      setLastMessageCount(messages.length)
    }
  }, [messages.length, lastMessageCount])


  const loadMessages = async (offsetValue = 0, scrollToBottom = false) => {
    if (!chat?.chat_id) {
      console.log('❌ Chat ID não encontrado:', chat)
      return
    }
    try {
      setLoading(true)
      console.log('🔍 Carregando mensagens para chat:', chat.chat_id)
      const url = `/api/mensagens/?chat_id=${chat.chat_id}&limit=${MESSAGES_PAGE_SIZE}&offset=${offsetValue}`
      console.log('🌐 URL da requisição:', url)
      const response = await apiRequest(url)
      console.log('📡 Status da resposta:', response.status)
      if (!response.ok) throw new Error('Erro na resposta da API')
      const data = await response.json()
      console.log('📨 Dados recebidos da API:', data)
      console.log('📊 Número de mensagens recebidas:', data.results?.length || data.length || 0)

      // Transformar dados do backend para o formato esperado pelo frontend
      const messagesToProcess = data.results || data || []
      console.log('🔄 Processando mensagens:', messagesToProcess.length)
      const newMessages = messagesToProcess.map((msg, index) => {
        console.log(`📝 Processando mensagem ${index}:`, msg)

        // Verificar se a mensagem tem dados válidos
        if (!msg.id) {
          console.warn('⚠️ Mensagem sem ID:', msg)
        }
        if (!msg.conteudo && !msg.content) {
          console.warn('⚠️ Mensagem sem conteúdo:', msg)
        }

        // Verificar se o conteúdo é JSON válido
        let conteudoProcessado = msg.conteudo || msg.content || ''
        let mediaUrl = null
        let mediaType = null
        let mediaCaption = null

        if (typeof conteudoProcessado === 'string' && conteudoProcessado.startsWith('{')) {
          try {
            const jsonContent = JSON.parse(conteudoProcessado)
            console.log('📄 Conteúdo JSON detectado:', jsonContent)

            // Extrair informações de mídia do JSON
            if (jsonContent.imageMessage) {
              mediaUrl = jsonContent.imageMessage.url
              mediaType = 'image'
              mediaCaption = jsonContent.imageMessage.caption
              conteudoProcessado = mediaCaption || '[Imagem]'
            } else if (jsonContent.videoMessage) {
              mediaUrl = jsonContent.videoMessage.url
              mediaType = 'video'
              mediaCaption = jsonContent.videoMessage.caption
              conteudoProcessado = mediaCaption || '[Vídeo]'
            } else if (jsonContent.audioMessage) {
              mediaUrl = jsonContent.audioMessage.url
              mediaType = 'audio'
              conteudoProcessado = '[Áudio]'
            } else if (jsonContent.documentMessage) {
              mediaUrl = jsonContent.documentMessage.url
              mediaType = 'document'
              mediaCaption = jsonContent.documentMessage.fileName
              conteudoProcessado = `[Documento] ${mediaCaption || 'Documento'}`
            } else if (jsonContent.stickerMessage) {
              mediaUrl = jsonContent.stickerMessage.url
              mediaType = 'sticker'
              conteudoProcessado = '[Sticker]'
            } else if (jsonContent.textMessage) {
              conteudoProcessado = jsonContent.textMessage.text || 'Mensagem de texto'
            } else {
              conteudoProcessado = '[Mídia]'
            }
          } catch (error) {
            console.warn('⚠️ Erro ao processar JSON:', error)
            conteudoProcessado = '[Conteúdo inválido]'
          }
        }

        const transformedMessage = {
          id: msg.id, // Usar sempre o ID interno para identificação
          message_id: msg.message_id, // Preservar o message_id original do WhatsApp
          internalId: msg.id, // Manter o ID interno para referência
          type: msg.tipo,
          content: conteudoProcessado,
          timestamp: msg.data_envio,
          sender: msg.remetente,
          isOwn: msg.fromMe || msg.from_me, // Usar ambos os campos para compatibilidade

          // Debug: verificar campos de propriedade
          fromMe: msg.fromMe,
          from_me: msg.from_me,
          status: msg.lida ? 'read' : 'sent',
          replyTo: null,
          forwarded: false,
          // Campos de mídia extraídos do JSON (prioridade sobre campos do banco)
          mediaUrl: mediaUrl || msg.media_url,
          mediaType: mediaType || msg.media_type,
          mediaCaption: mediaCaption || msg.media_caption,
          // Campos detalhados de mídia (snake_case -> camelCase)
          mediaSize: msg.media_size,
          mediaHeight: msg.media_height,
          mediaWidth: msg.media_width,
          jpegThumbnail: msg.jpeg_thumbnail,
          fileSha256: msg.file_sha256,
          mediaKey: msg.media_key,
          directPath: msg.direct_path,
          mediaKeyTimestamp: msg.media_key_timestamp,
          documentUrl: msg.document_url,
          documentFilename: msg.document_filename,
          documentMimetype: msg.document_mimetype,
          documentFileLength: msg.document_file_length,
          documentPageCount: msg.document_page_count,
          locationLatitude: msg.location_latitude,
          locationLongitude: msg.location_longitude,
          locationName: msg.location_name,
          locationAddress: msg.location_address,
          pollName: msg.poll_name,
          pollOptions: msg.poll_options,
          pollSelectableCount: msg.poll_selectable_count,
          stickerUrl: msg.sticker_url,
          stickerMimetype: msg.sticker_mimetype,
          stickerFileLength: msg.sticker_file_length,
          stickerIsAnimated: msg.sticker_is_animated,
          stickerIsAvatar: msg.sticker_is_avatar,
          stickerIsAi: msg.sticker_is_ai,
          stickerIsLottie: msg.sticker_is_lottie,
          thumbnailDirectPath: msg.thumbnail_direct_path,
          thumbnailSha256: msg.thumbnail_sha256,
          thumbnailEncSha256: msg.thumbnail_enc_sha256,
          thumbnailHeight: msg.thumbnail_height,
          thumbnailWidth: msg.thumbnail_width
        }

        // Log para verificar se o ID está sendo preservado
        console.log(`📝 Mensagem transformada ${index}: ID=${transformedMessage.id}, Tipo=${transformedMessage.type}, isOwn=${transformedMessage.isOwn}, from_me=${transformedMessage.from_me}, fromMe=${transformedMessage.fromMe}`)

        return transformedMessage
      })

      console.log('📝 Mensagens transformadas:', newMessages.length)

      // Remover duplicatas baseado no ID da mensagem
      const uniqueMessages = newMessages.filter((msg, index, self) => {
        const isDuplicate = index !== self.findIndex(m => m.id === msg.id)
        if (isDuplicate) {
          console.log('🚫 Removendo duplicata:', msg.id, msg.content?.substring(0, 50))
        }
        return !isDuplicate
      })

      // Inverter a ordem para exibir de baixo para cima (mais antigas no topo)
      const reversedMessages = [...uniqueMessages].reverse()

      console.log('📝 Mensagens únicas:', uniqueMessages.length)
      console.log('📝 Mensagens finais:', reversedMessages.length)

      if (offsetValue === 0) {
        // Só substitui completamente se for o carregamento inicial
        console.log('✅ Definindo mensagens iniciais:', reversedMessages.length)
        setMessages(reversedMessages)
        setLastMessageCount(reversedMessages.length)
      } else {
        // Para paginação, adiciona ao final
        console.log('✅ Adicionando mensagens à paginação:', reversedMessages.length)
        setMessages(prev => [...prev, ...reversedMessages])
      }
      setHasMore((data.results || data).length === MESSAGES_PAGE_SIZE)
      setOffset(offsetValue + (data.results || data).length)
      // Scroll para o final ao abrir
      if (scrollToBottom) {
        setTimeout(() => {
          const messagesContainer = document.querySelector('.messages-container')
          if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight
          }
        }, 100)
      }
    } catch (error) {
      console.error('Erro ao carregar mensagens:', error)
    } finally {
      setLoading(false)
    }
  }
  const [replyTo, setReplyTo] = useState(null) // Novo estado para resposta

  // Função utilitária para encontrar cliente por email ou nome
  const encontrarCliente = (email, nome, clients) => {
    if (!clients || clients.length === 0) return null;
    // Busca por email (mais confiável)
    if (email) {
      const clientePorEmail = clients.find(c =>
        c.email && c.email.toLowerCase().trim() === email.toLowerCase().trim()
      );
      if (clientePorEmail) return clientePorEmail;
    }
    // Busca por nome apenas se email não encontrar
    if (nome) {
      const clientePorNome = clients.find(c =>
        c.nome && c.nome.toLowerCase().trim() === nome.toLowerCase().trim()
      );
      return clientePorNome;
    }
    return null;
  };

  // Função utilitária para encontrar instância por clienteId
  const encontrarInstancia = (clienteId, instances) => {
    if (!instances || instances.length === 0 || !clienteId) return null;
    return instances.find(inst => {
      // Tenta várias possibilidades de campo
      const instClienteId = inst.cliente_id || inst.clienteId || inst.client_id;
      // Compara como number e string
      return instClienteId != null && (
        instClienteId === clienteId ||
        String(instClienteId) === String(clienteId) ||
        Number(instClienteId) === Number(clienteId)
      );
    });
  };

  const handleSendMessage = async () => {
    if (message.trim()) {
      const mensagemParaEnviar = message;
      setMessage(''); // Limpa imediatamente
      setReplyTo(null);
      // Busca instância e token do localStorage (primeira encontrada)
      const wapiInstances = JSON.parse(localStorage.getItem('wapi_instances') || '{}');
      const instanciaId = Object.keys(wapiInstances)[0];
      const token = instanciaId ? wapiInstances[instanciaId].token : null;
      if (!instanciaId || !token) {
        alert('Nenhuma instância/token encontrada no navegador. Faça login ou conecte uma instância.');
        return;
      }
      try {
        const response = await enviarMensagemWapi({
          chat_id: chat.chat_id,
          instancia: instanciaId,
          token,
          mensagem: mensagemParaEnviar
        });

        // Criar ID único baseado no timestamp para evitar duplicação
        const tempId = `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

        // Adicionar mensagem temporária ao estado
        const tempMessage = {
          id: tempId,
          message_id: response?.messageId || tempId,
          type: 'text',
          content: mensagemParaEnviar,
          timestamp: new Date().toISOString(),
          sender: 'Você',
          isOwn: true,
          from_me: true,
          status: 'sent',
          replyTo: null,
          isTemporary: true // Flag para identificar mensagem temporária
        };

        setMessages(prev => [...prev, tempMessage]);
        setTimeout(() => {
          const messagesContainer = document.querySelector('.messages-container');
          if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
          }
        }, 100);
      } catch (e) {
        alert('Erro ao enviar mensagem: ' + (e?.message || ''));
      }
    }
  }

  // Handler para scroll: se chegar ao topo, carregar mais mensagens
  const handleScroll = (e) => {
    if (e.target.scrollTop === 0 && hasMore && !loading) {
      loadMessages(offset)
    }
  }

  // Função para scroll até a mensagem
  const scrollToMessage = (id) => {
    setShowPinsModal(false)
    setShowFavoritesModal(false)
    setTimeout(() => {
      requestAnimationFrame(() => {
        const el = messageRefs.current[id]
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'center' })
          el.classList.add('ring-2', 'ring-primary')
          setTimeout(() => el.classList.remove('ring-2', 'ring-primary'), 1500)
        }
      })
    }, 350)
  }

  // Função para lidar com resposta
  const handleReply = (msg) => {
    setReplyTo(msg)
  }

  // Função para abrir modal de encaminhar
  const handleForward = (msg) => {
    setForwardModalMessage(msg)
  }
  const handleSelectChat = (chatId) => {
    setSelectedChats(prev => prev.includes(chatId)
      ? prev.filter(id => id !== chatId)
      : [...prev, chatId])
  }
  const handleConfirmForward = () => {
    // Aqui você pode implementar o mock de encaminhamento
    setForwardModalMessage(null)
    setSelectedChats([])
    setForwardSearch("")
  }
  const handleCloseForwardModal = () => {
    setForwardModalMessage(null)
    setSelectedChats([])
    setForwardSearch("")
  }

  // Função para enviar imagem
  const handleSendImage = async (imageData) => {
    if (!imageData) return

    // Verificar se o chat existe
    if (!chat || !chat.id) {
      console.error('❌ Chat não encontrado:', chat)
      toast({
        title: "❌ Erro",
        description: "Chat não encontrado. Selecione um chat válido.",
        duration: 4000,
      })
      return
    }

    console.log('📱 Chat encontrado:', {
      id: chat.id,
      chat_id: chat.chat_id,
      cliente: chat.cliente
    })

    setIsProcessingImage(true)

    try {
      // Busca instância e token do localStorage (mesmo método usado em handleSendMessage)
      const wapiInstances = JSON.parse(localStorage.getItem('wapi_instances') || '{}')
      const instanciaId = Object.keys(wapiInstances)[0]
      const token = instanciaId ? wapiInstances[instanciaId].token : null

      if (!instanciaId || !token) {
        console.error('❌ Nenhuma instância/token encontrada')
        toast({
          title: "❌ Erro de autenticação",
          description: "Nenhuma instância/token encontrada no navegador. Faça login ou conecte uma instância.",
          duration: 4000,
        })
        return
      }

      console.log('🔑 Token encontrado:', token.substring(0, 20) + '...')
      console.log('📱 Instância ID:', instanciaId)
      console.log('📏 Tamanho do image_data:', imageData.data ? imageData.data.length : 0)
      console.log('🏷️ Tipo da imagem:', imageData.type)

      // Log detalhado dos dados da imagem
      console.log('📸 Dados da imagem para envio:')
      console.log('- Tipo:', imageData.type)
      console.log('- Dados (primeiros 100 chars):', imageData.data ? imageData.data.substring(0, 100) + '...' : 'null')
      console.log('- Tamanho total:', imageData.data ? imageData.data.length : 0)
      console.log('- É base64 válido?', imageData.data ? /^[A-Za-z0-9+/]*={0,2}$/.test(imageData.data) : false)

      // Enviar imagem diretamente para a WAPI (mesmo método que handleSendMessage)
      const response = await enviarImagemWapi({
        chat_id: chat.chat_id, // Usar chat_id em vez de chat.id
        instancia: instanciaId,
        token,
        image_data: imageData.data,
        image_type: imageData.type,
        caption: imageData.caption || ''
      })

      // A WAPI retorna diretamente os dados, não um objeto com 'sucesso'
      if (response && response.messageId) {
        // Criar mensagem temporária de imagem
        const tempId = `temp_img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        const tempMessage = {
          id: tempId,
          message_id: response.messageId || tempId,
          type: 'image',
          content: imageData.data,
          caption: imageData.caption || '',
          timestamp: new Date().toISOString(),
          sender: 'Você',
          isOwn: true,
          from_me: true,
          status: 'sent',
          isTemporary: true
        }

        setMessages(prev => [...prev, tempMessage])

        // Scroll para o final
        setTimeout(() => {
          const messagesContainer = document.querySelector('.messages-container')
          if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight
          }
        }, 100)

        // Limpar imagem pendente
        setPendingImage(null)
        setImageCaption('')

        toast({
          title: "✅ Imagem enviada",
          description: "Imagem enviada com sucesso!",
          duration: 3000,
        })
      } else {
        throw new Error(result.erro || 'Erro ao enviar imagem')
      }
    } catch (error) {
      console.error('❌ Erro ao enviar imagem:', error)
      toast({
        title: "❌ Erro ao enviar imagem",
        description: error.message || "Não foi possível enviar a imagem",
        duration: 4000,
      })
    } finally {
      setIsProcessingImage(false)
    }
  }

  // Função para enviar imagem pendente
  const handleSendPendingImage = async () => {
    if (!pendingImage) return

    console.log('📸 Imagem pendente encontrada:', {
      type: pendingImage.type,
      filename: pendingImage.filename,
      dataLength: pendingImage.data?.length || 0
    })

    const imageDataWithCaption = {
      ...pendingImage,
      caption: imageCaption
    }

    console.log('📝 Legenda:', imageCaption)

    await handleSendImage(imageDataWithCaption)
  }

  // Funções para gerenciar arquivos de áudio
  const handleAudioFileSelect = (files) => {
    const audioFiles = Array.from(files).filter(file => file.type.startsWith('audio/'));
    
    if (audioFiles.length === 0) {
      toast({
        title: "Erro",
        description: "Nenhum arquivo de áudio válido selecionado",
        variant: "destructive"
      });
      return;
    }

    const processedFiles = audioFiles.map(file => ({
      file,
      name: file.name,
      size: file.size,
      type: 'audio',
      url: URL.createObjectURL(file),
      id: Date.now() + Math.random()
    }));

    setSelectedAudioFiles(prev => [...prev, ...processedFiles]);
    setShowAudioModal(true);
    setCurrentAudioIndex(0);
  };

  const handleAudioUpload = async () => {
    if (!chat || !chat.chat_id || selectedAudioFiles.length === 0) {
      toast({
        title: "Erro",
        description: "Dados insuficientes para upload",
        variant: "destructive"
      });
      return;
    }

    const token = localStorage.getItem('access_token');
    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

    for (const audioFile of selectedAudioFiles) {
      try {
        setAudioUploadProgress(prev => ({
          ...prev,
          [audioFile.id]: 0
        }));

        const formData = new FormData();
        formData.append('audio', audioFile.file);
        formData.append('chat_id', chat.chat_id);
        formData.append('message_type', 'audio');

        const response = await fetch(`${API_BASE_URL}/api/upload-audio/`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        });

        if (response.ok) {
          setAudioUploadProgress(prev => ({
            ...prev,
            [audioFile.id]: 100
          }));

          toast({
            title: "Sucesso",
            description: `Áudio ${audioFile.name} enviado com sucesso`,
          });

          // Limpar arquivo após upload bem-sucedido
          setTimeout(() => {
            setSelectedAudioFiles(prev => prev.filter(f => f.id !== audioFile.id));
            setAudioUploadProgress(prev => {
              const newProgress = { ...prev };
              delete newProgress[audioFile.id];
              return newProgress;
            });
          }, 2000);

        } else {
          throw new Error('Falha ao enviar áudio');
        }
      } catch (error) {
        console.error('Erro ao enviar áudio:', error);
        toast({
          title: "Erro",
          description: `Falha ao enviar áudio ${audioFile.name}`,
          variant: "destructive"
        });
      }
    }
  };

  const handleAudioPlayback = (audioId, status) => {
    setAudioPlaybackStatus(prev => ({
      ...prev,
      [audioId]: {
        ...prev[audioId],
        ...status,
        reproduzidaEm: new Date().toLocaleTimeString()
      }
    }));
  };

  const removeAudioFile = (audioId) => {
    setSelectedAudioFiles(prev => prev.filter(f => f.id !== audioId));
    setAudioUploadProgress(prev => {
      const newProgress = { ...prev };
      delete newProgress[audioId];
      return newProgress;
    });
    
    if (selectedAudioFiles.length === 1) {
      setShowAudioModal(false);
    }
  };

  const nextAudio = () => {
    if (currentAudioIndex < selectedAudioFiles.length - 1) {
      setCurrentAudioIndex(prev => prev + 1);
    }
  };

  const previousAudio = () => {
    if (currentAudioIndex > 0) {
      setCurrentAudioIndex(prev => prev - 1);
    }
  };

  // Função para lidar com seleção de emoji
  const handleEmojiSelect = (emoji) => {
    // Adicionar emoji à mensagem (pode adicionar quantos quiser)
    setMessage(prev => prev + emoji)
  }

  // Filtrar chats para o modal de encaminhamento
  const filteredChats = useMemo(() => {
    // Mock de chats para demonstração - em produção viria da API
    const mockChats = [
      { id: 1, chat_id: '5511999999999', contact_name: 'João Silva', is_group: false },
      { id: 2, chat_id: '5511888888888', contact_name: 'Maria Santos', is_group: false },
      { id: 3, chat_id: '5511777777777', group_name: 'Família', is_group: true },
      { id: 4, chat_id: '5511666666666', group_name: 'Trabalho', is_group: true }
    ]

    if (!forwardSearch.trim()) {
      return mockChats
    }

    const searchTerm = forwardSearch.toLowerCase()
    return mockChats.filter(chat => {
      const name = chat.is_group ? (chat.group_name || 'Grupo') : (chat.contact_name || chat.chat_id || 'Contato')
      return name.toLowerCase().includes(searchTerm) ||
        chat.chat_id.toLowerCase().includes(searchTerm)
    })
  }, [forwardSearch])

  // Memoizar grupos de mensagens para evitar recálculos desnecessários
  const messageGroups = useMemo(() => {
    console.log('📅 Agrupando mensagens:', messages.length)
    const groups = {}
    messages.forEach(msg => {
      try {
        const date = new Date(msg.timestamp).toLocaleDateString('pt-BR', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
        if (!groups[date]) {
          groups[date] = []
        }
        groups[date].push(msg)
      } catch (error) {
        console.error('❌ Erro ao processar data da mensagem:', error, msg)
      }
    })
    console.log('📅 Grupos criados:', Object.keys(groups).length)
    return groups
  }, [messages])

  // Função para abrir modal de dados da mensagem
  const handleShowInfo = (msg) => {
    setInfoModalMessage(msg)
  }

  const handleDelete = (messageId) => {
    // Remover a mensagem da lista local
    setMessages(prevMessages => prevMessages.filter(msg => msg.id !== messageId))
  }
  const mockContactFromApi = {
    name: "Caio Henrique",
    phone: "+55 11 91234-5678",
    isMuted: false,
    isStarred: true,
    foto_perfil: "https://randomuser.me/api/portraits/men/75.jpg",
    notificationSound: true,
    // Outros dados que você usar no modal:
    // (exemplo, para ações rápidas, etc)
    // ...
  };

  // Dados do contato memoizados para evitar re-renders desnecessários
  const stableContactInfo = useMemo(() => {
    if (!chat) return null;
    
    return {
      name: chat.contact_name || chat.sender_name || 'Contato',
      phone: chat.contact_number || 'N/A',
      photo: chat.foto_perfil || chat.profile_picture || null,
      isStarred: false,
      isMuted: false,
    }
  }, [
    chat?.contact_name,
    chat?.sender_name,
    chat?.contact_number,
    chat?.foto_perfil,
    chat?.profile_picture,
  ]);

  // Funções estáveis para evitar re-renders
  const handleCloseContactInfo = useCallback(() => {
    setShowContactInfo(false);
  }, []);

  const handleOpenContactInfo = useCallback(() => {
    setShowContactInfo(true);
  }, []);

  return (
    <div className="flex flex-col flex-1 w-full max-w-full min-w-0 h-full bg-background overflow-x-auto">
      {/* Header do chat */}
      <ChatHeader
        chat={chat}
        isConnected={isConnected}
        favoritedMessages={favoritedMessages}
        pinnedMessages={pinnedMessages}
        onOpenContactInfo={handleOpenContactInfo}
        onOpenImageModal={() => setShowImageModal(true)}
        onOpenFavoritesModal={() => setShowFavoritesModal(true)}
        onOpenPinsModal={() => setShowPinsModal(true)}
      />
      {/* Modal para exibir imagem em destaque */}
      <ImageModal
        showImageModal={showImageModal}
        setShowImageModal={setShowImageModal}
        imageSrc={chat.foto_perfil || chat.profile_picture}
        imageAlt="Foto do contato"
      />

      {/* Área de mensagens */}
      <MessagesContainer
        messages={messages}
        loading={loading}
        hasMore={hasMore}
        messageRefs={messageRefs}
        messageGroups={messageGroups}
        onScroll={handleScroll}
        onLoadMore={() => loadMessages(offset)}
        profilePicture={chat.foto_perfil || chat.profile_picture}
        onReply={handleReply}
        onForward={handleForward}
        onShowInfo={handleShowInfo}
        onDelete={handleDelete}
      />

      {/* Input de mensagem */}
      <MessageInput
        message={message}
        setMessage={setMessage}
        replyTo={replyTo}
        setReplyTo={setReplyTo}
        pendingImage={pendingImage}
        setPendingImage={setPendingImage}
        imageCaption={imageCaption}
        setImageCaption={setImageCaption}
        isProcessingImage={isProcessingImage}
        showEmojiPicker={showEmojiPicker}
        setShowEmojiPicker={setShowEmojiPicker}
        showImageUpload={showImageUpload}
        setShowImageUpload={setShowImageUpload}
        onSendMessage={handleSendMessage}
        onSendPendingImage={handleSendPendingImage}
        onEmojiSelect={handleEmojiSelect}
        onAudioSelect={() => setShowAudioModal(true)}
      />

      {/* Modal de informações do contato */}
      <ContactInfoModal
        open={showContactInfo}
        onOpenChange={setShowContactInfo}
        contactInfo={stableContactInfo}
        onClose={handleCloseContactInfo}
        chat={chat}
        setShowImageModal={setShowImageModal}
      />

      {/* Modal de informações da mensagem estilo WhatsApp */}
      <MessageInfoModal
        infoModalMessage={infoModalMessage}
        onClose={() => setInfoModalMessage(null)}
      />
      {/* Modal de mensagens fixadas */}
      <PinnedMessagesModal
        open={showPinsModal}
        onOpenChange={setShowPinsModal}
        pinnedMessages={pinnedMessages}
        onScrollToMessage={scrollToMessage}
      />

      {/* Modal de encaminhar mensagem */}
      <ForwardMessageModal
        forwardModalMessage={forwardModalMessage}
        forwardSearch={forwardSearch}
        setForwardSearch={setForwardSearch}
        selectedChats={selectedChats}
        filteredChats={filteredChats}
        onSelectChat={handleSelectChat}
        onConfirmForward={handleConfirmForward}
        onCloseForwardModal={handleCloseForwardModal}
      />

      {/* Modal de mensagens favoritas */}
      <FavoritesModal
        open={showFavoritesModal}
        onOpenChange={setShowFavoritesModal}
        favoritedMessages={favoritedMessages}
        onScrollToMessage={scrollToMessage}
      />

      {/* Componente de upload de imagem */}
      <ImageUpload
        isVisible={showImageUpload}
        onClose={() => setShowImageUpload(false)}
        onImageSelect={handleSendImage}
      />

      {/* Modal de áudio */}
      <Dialog open={showAudioModal} onOpenChange={setShowAudioModal}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-hidden">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Volume2 className="w-5 h-5 text-orange-500" />
              Selecionar Áudios
            </DialogTitle>
            <DialogDescription>
              Selecione e visualize os arquivos de áudio antes de enviar
            </DialogDescription>
          </DialogHeader>

          <div className="flex flex-col gap-4">
            {/* Área de seleção de arquivos */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-orange-400 transition-colors">
              <input
                type="file"
                multiple
                accept="audio/*"
                onChange={(e) => handleAudioFileSelect(e.target.files)}
                className="hidden"
                id="audio-file-input"
              />
              <label
                htmlFor="audio-file-input"
                className="cursor-pointer flex flex-col items-center gap-3"
              >
                <div className="bg-orange-500 text-white rounded-full p-4">
                  <Plus className="w-8 h-8" />
                </div>
                <div>
                  <p className="font-medium text-lg">Adicionar Áudios</p>
                  <p className="text-sm text-gray-500">
                    Clique para selecionar arquivos de áudio
                  </p>
                </div>
              </label>
            </div>

            {/* Lista de áudios selecionados */}
            {selectedAudioFiles.length > 0 && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">Áudios Selecionados ({selectedAudioFiles.length})</h3>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={previousAudio}
                      disabled={currentAudioIndex === 0}
                    >
                      <SkipBack className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={nextAudio}
                      disabled={currentAudioIndex === selectedAudioFiles.length - 1}
                    >
                      <SkipForward className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                {/* Visualização do áudio atual */}
                <div className="flex flex-col items-center justify-center p-8 bg-accent rounded-lg w-full max-w-md mx-auto">
                  <Volume2 className="w-16 h-16 text-orange-500 mb-4" />
                  <p className="text-lg font-medium mb-2 text-center">
                    {selectedAudioFiles[currentAudioIndex]?.name}
                  </p>
                  <p className="text-sm text-muted-foreground mb-4">
                    {(selectedAudioFiles[currentAudioIndex]?.file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                  
                  {/* Player HTML5 com controles nativos */}
                  <audio 
                    src={selectedAudioFiles[currentAudioIndex]?.url} 
                    controls
                    className="w-full"
                    onPlay={() => handleAudioPlayback(selectedAudioFiles[currentAudioIndex]?.id, { isPlaying: true })}
                    onPause={() => handleAudioPlayback(selectedAudioFiles[currentAudioIndex]?.id, { isPlaying: false })}
                    onEnded={() => handleAudioPlayback(selectedAudioFiles[currentAudioIndex]?.id, { isPlaying: false, isCompleted: true })}
                  />
                </div>

                {/* Thumbnails dos áudios */}
                <div className="grid grid-cols-4 gap-2 max-h-32 overflow-y-auto">
                  {selectedAudioFiles.map((item, index) => (
                    <div
                      key={item.id}
                      className={`relative cursor-pointer rounded-lg border-2 transition-all ${
                        index === currentAudioIndex
                          ? 'border-orange-500 bg-orange-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => setCurrentAudioIndex(index)}
                    >
                      <div className="w-full h-20 bg-accent flex items-center justify-center">
                        <Volume2 className="w-6 h-6 text-muted-foreground" />
                      </div>
                      <div className="p-2 text-center">
                        <p className="text-xs font-medium truncate">{item.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {(item.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                      
                      {/* Botão de remover */}
                      <Button
                        variant="destructive"
                        size="sm"
                        className="absolute -top-2 -right-2 h-6 w-6 p-0 rounded-full"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeAudioFile(item.id);
                        }}
                      >
                        <X className="w-3 h-3" />
                      </Button>

                      {/* Indicador de progresso */}
                      {audioUploadProgress[item.id] !== undefined && (
                        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-200 rounded-b-lg overflow-hidden">
                          <div 
                            className="h-full bg-green-500 transition-all duration-300"
                            style={{ width: `${audioUploadProgress[item.id]}%` }}
                          />
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Botões de ação */}
                <div className="flex items-center justify-between pt-4 border-t">
                  <Button
                    variant="outline"
                    onClick={() => setShowAudioModal(false)}
                  >
                    Cancelar
                  </Button>
                  <Button
                    onClick={handleAudioUpload}
                    disabled={selectedAudioFiles.length === 0}
                    className="bg-orange-500 hover:bg-orange-600"
                  >
                    Enviar {selectedAudioFiles.length} Áudio{selectedAudioFiles.length !== 1 ? 's' : ''}
                  </Button>
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

ChatView.propTypes = {
  chat: PropTypes.object.isRequired,
  instances: PropTypes.array,
  clients: PropTypes.array
};

export default ChatView
