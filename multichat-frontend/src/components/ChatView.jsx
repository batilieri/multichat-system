// Este arquivo foi restaurado para a versão original da base.
// Importe novamente a versão padrão do ChatView.jsx do repositório principal.

import React, { useState, useEffect } from 'react'
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
  Heart
} from 'lucide-react'
import Message from './Message'
import { getMessagesByChat, getPinnedMessages, getFavoritedMessages } from '../data/mock/messages'
import { getAllChats } from '../data/mock/chats'
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
import { enviarMensagemWapi } from '../lib/wapi'
import PropTypes from 'prop-types';

const ChatView = ({ chat, instances = [], clients = [] }) => {
  // Estados para dados carregados internamente
  const [internalClients, setInternalClients] = useState([]);
  const [internalInstances, setInternalInstances] = useState([]);
  const [dataLoaded, setDataLoaded] = useState(false);

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
  
  // refs para scroll até mensagem
  const messageRefs = React.useRef({})
  const [infoModalMessage, setInfoModalMessage] = useState(null)

  // Carregar mensagens e favoritas
  useEffect(() => {
    const chatMessages = getMessagesByChat(chat?.id)
    setMessages(chatMessages)
    setFavoritedMessages(getFavoritedMessages())
    setPinnedMessages(getPinnedMessages().sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp)))
  }, [chat?.id])

  // Atualizar favoritas quando mudar
  useEffect(() => {
    const interval = setInterval(() => {
      setFavoritedMessages(getFavoritedMessages())
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  // Função para adicionar nova mensagem em tempo real
  const handleNewMessage = (newMessage) => {
    console.log('🆕 Nova mensagem recebida em tempo real:', newMessage)
    
    // Verificar se a mensagem já existe para evitar duplicação
    const messageExists = messages.some(msg => msg.id === newMessage.id)
    if (messageExists) {
      console.log('⚠️ Mensagem já existe, ignorando:', newMessage.id)
      return
    }
    
    // Transformar mensagem para o formato esperado
    const transformedMessage = {
      id: newMessage.id,
      type: newMessage.type,
      content: newMessage.content,
      timestamp: newMessage.timestamp,
      sender: newMessage.sender,
      isOwn: newMessage.isOwn,
      status: newMessage.status,
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
      pollName: newMessage.pollName,
      pollOptions: newMessage.pollOptions,
      pollSelectableCount: newMessage.pollSelectableCount,
      stickerUrl: newMessage.stickerUrl,
      stickerMimetype: newMessage.stickerMimetype,
      stickerFileLength: newMessage.stickerFileLength,
      stickerIsAnimated: newMessage.stickerIsAnimated,
      stickerIsAvatar: newMessage.stickerIsAvatar,
      stickerIsAi: newMessage.stickerIsAi,
      stickerIsLottie: newMessage.stickerIsLottie,
      thumbnailDirectPath: newMessage.thumbnailDirectPath,
      thumbnailSha256: newMessage.thumbnailSha256,
      thumbnailEncSha256: newMessage.thumbnailEncSha256,
      thumbnailHeight: newMessage.thumbnailHeight,
      thumbnailWidth: newMessage.thumbnailWidth
    }

    // Adicionar mensagem ao estado (no final da lista)
    setMessages(prev => [...prev, transformedMessage])
    
    // Scroll para a última mensagem
    setTimeout(() => {
      const messagesContainer = document.querySelector('.messages-container')
      if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight
      }
    }, 100)
  }

  // Função para atualizar dados do chat
  const handleChatUpdate = (chatData) => {
    console.log('🔄 Chat atualizado em tempo real:', chatData)
    // Aqui você pode atualizar informações do chat se necessário
  }

  // Usar hook de atualizações em tempo real
  const { isConnected } = useChatUpdates(
    chat?.chat_id,
    handleNewMessage,
    handleChatUpdate
  )

  // Scroll automático para o final quando mensagens são carregadas
  useEffect(() => {
    if (messages.length > 0) {
      setTimeout(() => {
        const messagesContainer = document.querySelector('.messages-container')
        if (messagesContainer) {
          messagesContainer.scrollTop = messagesContainer.scrollHeight
        }
      }, 100)
    }
  }, [messages])


  const loadMessages = async (offsetValue = 0, scrollToBottom = false) => {
    if (!chat?.id) return
    try {
      setLoading(true)
      const response = await apiRequest(`/api/mensagens/?chat_id=${chat.chat_id}&limit=${MESSAGES_PAGE_SIZE}&offset=${offsetValue}`)
      if (!response.ok) throw new Error('Erro na resposta da API')
      const data = await response.json()
      
      // Transformar dados do backend para o formato esperado pelo frontend
      const newMessages = (data.results || data).map(msg => ({
        id: msg.id,
        type: msg.tipo,
        content: msg.conteudo,
        timestamp: msg.data_envio,
        sender: msg.remetente,
        isOwn: msg.fromMe, // Corrigido: agora usa o campo correto do backend
        status: msg.lida ? 'read' : 'sent',
        replyTo: null,
        forwarded: false,
        // Campos detalhados de mídia (snake_case -> camelCase)
        mediaUrl: msg.media_url,
        mediaType: msg.media_type,
        mediaSize: msg.media_size,
        mediaCaption: msg.media_caption,
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
      }))
      
      // Remover duplicatas baseado no ID da mensagem
      const uniqueMessages = newMessages.filter((msg, index, self) => 
        index === self.findIndex(m => m.id === msg.id)
      )
      
      // Inverter a ordem para exibir de baixo para cima (mais antigas no topo)
      const reversedMessages = [...uniqueMessages].reverse()
      
      if (offsetValue === 0) {
        setMessages(reversedMessages)
      } else {
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
  const allChats = getAllChats()
  const filteredChats = allChats.filter(chat => {
    const name = chat.is_group ? chat.group_name : chat.contact_name
    return name && name.toLowerCase().includes(forwardSearch.toLowerCase())
  })
  // refs para scroll até mensagem
  const messageRefs = React.useRef({})
  const [infoModalMessage, setInfoModalMessage] = useState(null)

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
        await enviarMensagemWapi({
          chat_id: chat.chat_id,
          instancia: instanciaId,
          token,
          mensagem: mensagemParaEnviar
        });
        setMessages(prev => [...prev, {
          id: Date.now(),
          type: 'text',
          content: mensagemParaEnviar,
          timestamp: new Date().toISOString(),
          sender: 'Você',
          isOwn: true,
          status: 'sent',
          replyTo: null
        }]);
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

  // Função para abrir modal de dados da mensagem
  const handleShowInfo = (msg) => {
    setInfoModalMessage(msg)
  }

  // Dados mock do contato (em um app real viriam da API)
  const contactInfo = {
    name: chat.is_group ? (chat.group_name || 'Grupo') : (chat.contact_name || chat.chat_id || 'Contato'),
    phone: chat.chat_id || 'N/A',
    email: chat.is_group ? null : (chat.contact_name ? `${chat.contact_name.toLowerCase().replace(' ', '.')}@example.com` : null),
    status: chat.atribuicao_atual?.status || 'Online',
    lastSeen: 'Hoje às 14:30',
    location: chat.is_group ? null : 'São Paulo, SP',
    joinedDate: '15 de março de 2024',
    isBlocked: false,
    isMuted: false,
    isStarred: false,
    isArchived: false,
    totalMessages: messages.length,
    mediaShared: 12,
    documentsShared: 3
  }

  const ContactInfoModal = () => (
    <Dialog open={showContactInfo} onOpenChange={setShowContactInfo}>
      <DialogContent className="!fixed !z-50 !w-[80vw] !h-[80vh] !max-w-none !max-h-none !translate-x-[-50%] !translate-y-[-50%] !top-[50%] !left-[50%] p-0 overflow-hidden bg-background rounded-lg border border-border shadow-2xl [&>button]:!absolute [&>button]:!top-6 [&>button]:!right-6 [&>button]:!text-primary-foreground [&>button]:!hover:bg-primary-foreground/20 [&>button]:!bg-transparent [&>button]:!border-none [&>button]:!shadow-none [&>button]:!rounded-lg [&>button]:!p-2 [&>button]:!transition-colors">
        {/* Header do modal */}
        <div className="bg-primary text-primary-foreground p-6 border-b border-primary/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {/* Torna a foto clicável para abrir em destaque */}
              <div
                className="h-16 w-16 bg-primary-foreground/20 rounded-full flex items-center justify-center cursor-pointer overflow-hidden"
                onClick={e => {
                  e.stopPropagation();
                  if (chat.foto_perfil || chat.profile_picture) setShowImageModal(true);
                }}
                title="Clique para ampliar a foto"
              >
                {chat.foto_perfil || chat.profile_picture ? (
                  <img
                    src={chat.foto_perfil || chat.profile_picture}
                    alt={chat.contact_name || chat.sender_name || chat.chat_id}
                    className="h-full w-full object-cover"
                    onError={e => {
                      e.target.style.display = 'none';
                      e.target.nextSibling && (e.target.nextSibling.style.display = 'flex');
                    }}
                  />
                ) : (
                  <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" className="h-5 w-5 text-primary-foreground">
                    <circle cx="12" cy="7" r="4" />
                    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
                  </svg>
                )}
              </div>
              <div>
                <h3 className="text-xl font-semibold text-primary-foreground">
                  {contactInfo.name}
                </h3>
                <p className="text-primary-foreground/80 text-sm">
                  {contactInfo.status}
                </p>
              </div>
            </div>

          </div>
        </div>

        {/* Conteúdo do modal */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
              {/* Coluna 1: Informações básicas */}
              <div className="space-y-6">
                <h4 className="text-lg font-semibold text-foreground border-b border-border pb-2">
                  Informações do Contato
                </h4>
                
                <div className="space-y-4">
                  <div className="flex items-center space-x-4 p-4 bg-accent/50 rounded-lg border border-border">
                    <Phone className="h-5 w-5 text-primary" />
                    <div>
                      <p className="text-sm text-muted-foreground">Telefone</p>
                      <p className="font-medium">{contactInfo.phone}</p>
                    </div>
                  </div>

                  {contactInfo.email && (
                    <div className="flex items-center space-x-4 p-4 bg-accent/50 rounded-lg border border-border">
                      <Mail className="h-5 w-5 text-primary" />
                      <div>
                        <p className="text-sm text-muted-foreground">Email</p>
                        <p className="font-medium">{contactInfo.email}</p>
                      </div>
                    </div>
                  )}

                  {contactInfo.location && (
                    <div className="flex items-center space-x-4 p-4 bg-accent/50 rounded-lg border border-border">
                      <MapPin className="h-5 w-5 text-primary" />
                      <div>
                        <p className="text-sm text-muted-foreground">Localização</p>
                        <p className="font-medium">{contactInfo.location}</p>
                      </div>
                    </div>
                  )}

                  <div className="flex items-center space-x-4 p-4 bg-accent/50 rounded-lg border border-border">
                    <Calendar className="h-5 w-5 text-primary" />
                    <div>
                      <p className="text-sm text-muted-foreground">Visto por último</p>
                      <p className="font-medium">{contactInfo.lastSeen}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Coluna 2: Estatísticas e Ações */}
              <div className="space-y-6">
                <h4 className="text-lg font-semibold text-foreground border-b border-border pb-2">
                  Estatísticas
                </h4>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-6 bg-accent rounded-lg border border-border">
                    <p className="text-4xl font-bold text-primary">{contactInfo.totalMessages}</p>
                    <p className="text-sm text-muted-foreground mt-2">Mensagens</p>
                  </div>
                  <div className="text-center p-6 bg-accent rounded-lg border border-border">
                    <p className="text-4xl font-bold text-primary">{contactInfo.mediaShared}</p>
                    <p className="text-sm text-muted-foreground mt-2">Mídias</p>
                  </div>
                </div>

                <h4 className="text-lg font-semibold text-foreground border-b border-border pb-2 mt-6">
                  Ações Rápidas
                </h4>
                
                <div className="grid grid-cols-1 gap-3">
                  <Button variant="outline" className="w-full justify-start h-14 text-base">
                    <MessageCircle className="h-5 w-5 mr-3" />
                    Enviar mensagem
                  </Button>
                  
                  <Button variant="outline" className="w-full justify-start h-14 text-base">
                    <Phone className="h-5 w-5 mr-3" />
                    Ligar
                  </Button>
                  
                  <Button variant="outline" className="w-full justify-start h-14 text-base">
                    <Video className="h-5 w-5 mr-3" />
                    Videochamada
                  </Button>
                </div>
              </div>

              {/* Coluna 3: Configurações */}
              <div className="space-y-6">
                <h4 className="text-lg font-semibold text-foreground border-b border-border pb-2">
                  Configurações
                </h4>
                
                <div className="space-y-3">
                  <Button variant="ghost" className="w-full justify-start h-14 text-base">
                    <Star className="h-5 w-5 mr-3" />
                    {contactInfo.isStarred ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}
                  </Button>
                  
                  <Button variant="ghost" className="w-full justify-start h-14 text-base">
                    <VolumeX className="h-5 w-5 mr-3" />
                    {contactInfo.isMuted ? 'Ativar notificações' : 'Silenciar notificações'}
                  </Button>
                  
                  <Button variant="ghost" className="w-full justify-start h-14 text-base">
                    <Archive className="h-5 w-5 mr-3" />
                    {contactInfo.isArchived ? 'Desarquivar' : 'Arquivar'}
                  </Button>
                  
                  <Button variant="ghost" className="w-full justify-start h-14 text-base">
                    <Edit className="h-5 w-5 mr-3" />
                    Editar contato
                  </Button>
                  
                  <div className="border-t border-border pt-4 mt-4">
                    <Button variant="ghost" className="w-full justify-start h-14 text-base text-destructive">
                      <Ban className="h-5 w-5 mr-3" />
                      {contactInfo.isBlocked ? 'Desbloquear' : 'Bloquear'}
                    </Button>
                    
                    <Button variant="ghost" className="w-full justify-start h-14 text-base text-destructive">
                      <Trash2 className="h-5 w-5 mr-3" />
                      Excluir conversa
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )

  return (
    <div className="flex flex-col flex-1 w-full max-w-full min-w-0 h-full bg-background overflow-x-auto">
      {/* Header do chat */}
      <div className="flex items-center gap-4 p-4 border-b border-border bg-card sticky top-0 z-10">
        {/* Área clicável para abrir o perfil (exceto imagem) */}
        <div className="flex items-center gap-4 flex-1 cursor-pointer select-none" onClick={() => setShowContactInfo(true)}>
          <div className="h-10 w-10 bg-primary rounded-full flex items-center justify-center overflow-hidden cursor-pointer" onClick={e => { e.stopPropagation(); if (chat.foto_perfil || chat.profile_picture) setShowImageModal(true); }}>
            {chat.foto_perfil || chat.profile_picture ? (
              <img
                src={chat.foto_perfil || chat.profile_picture}
                alt={chat.contact_name || chat.sender_name || chat.chat_id}
                className="h-full w-full object-cover"
                onError={e => {
                  e.target.style.display = 'none';
                  e.target.nextSibling && (e.target.nextSibling.style.display = 'flex');
                }}
              />
            ) : (
              <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24" className="h-5 w-5 text-primary-foreground">
                <circle cx="12" cy="7" r="4" />
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
              </svg>
            )}
          </div>
          <div className="flex flex-col min-w-0">
            <span className="font-semibold truncate text-foreground text-base">
              {chat.contact_name || chat.sender_name || chat.group_name || chat.chat_id}
            </span>
            <span className="text-xs text-muted-foreground truncate">
              {chat.status || chat.phone || chat.chat_id}
            </span>
          </div>
        </div>
        {/* Botões de ação do header */}
        <div className="flex items-center space-x-2">
          <button className="p-2 hover:bg-accent rounded-lg transition-colors">
            <Phone className="h-4 w-4 text-muted-foreground" />
          </button>
          <button className="p-2 hover:bg-accent rounded-lg transition-colors">
            <Video className="h-4 w-4 text-muted-foreground" />
          </button>
          {/* Botão de favoritas */}
          <button 
            className="p-2 hover:bg-yellow-500/20 rounded-lg transition-colors relative" 
            onClick={() => setShowFavoritesModal(true)} 
            title="Mensagens favoritas"
          >
            <Heart className="h-4 w-4 text-yellow-500" />
            {favoritedMessages.length > 0 && (
              <motion.span 
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-1 -right-1 bg-yellow-500 text-white rounded-full text-xs px-1.5 py-0.5 font-medium"
              >
                {favoritedMessages.length}
              </motion.span>
            )}
          </button>
          {/* Botão de pins */}
          <button className="p-2 hover:bg-primary/20 rounded-lg transition-colors relative" onClick={() => setShowPinsModal(true)} title="Mensagens fixadas">
            <Pin className="h-4 w-4 text-primary" />
            {pinnedMessages.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-primary text-primary-foreground rounded-full text-xs px-1.5 py-0.5">{pinnedMessages.length}</span>
            )}
          </button>
          <button className="p-2 hover:bg-accent rounded-lg transition-colors">
            <MoreVertical className="h-4 w-4 text-muted-foreground" />
          </button>
        </div>
      </div>
      {/* Modal para exibir imagem em destaque */}
      {showImageModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80" onClick={() => setShowImageModal(false)}>
          <img
            src={chat.foto_perfil || chat.profile_picture}
            alt="Foto do contato"
            className="max-h-[80vh] max-w-[90vw] rounded-xl shadow-2xl border-4 border-white"
            onClick={e => e.stopPropagation()}
          />
          <button
            className="absolute top-6 right-8 text-white text-3xl font-bold bg-black/60 rounded-full px-3 py-1 hover:bg-black/80 transition"
            onClick={() => setShowImageModal(false)}
            style={{zIndex: 100}}
          >
            ×
          </button>
        </div>
      )}

      {/* Área de mensagens */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 w-full messages-container" onScroll={handleScroll}>
        {!loading && Object.entries(groupMessagesByDate(messages)).map(([date, msgs]) => (
          <div key={date} className="w-full">
            <div className="flex justify-center my-2">
              <span className="bg-muted text-xs px-3 py-1 rounded-full border border-border">{date}</span>
            </div>
            <div className="flex flex-col gap-2"> {/* Espaço entre mensagens */}
              {msgs.map((msg) => (
                <div key={msg.id} className="w-full" ref={el => messageRefs.current[msg.id] = el}>
                  <Message 
                    message={msg} 
                    profilePicture={chat.foto_perfil || chat.profile_picture}
                    onReply={handleReply} 
                    onForward={handleForward} 
                    onShowInfo={handleShowInfo} 
                  />
                </div>
              ))}
            </div>
          </div>
        ))}
        {loading && <div className="text-center text-muted-foreground">Carregando mensagens...</div>}
        {hasMore && !loading && (
          <div className="flex justify-center my-2">
            <button className="text-xs text-primary underline" onClick={() => loadMessages(offset)}>
              Carregar mais mensagens
            </button>
          </div>
        )}
      </div>

      {/* Input de mensagem */}
      <div className="p-4 border-t border-border bg-card">
        {/* Se estiver respondendo, mostrar a mensagem acima do input */}
        {replyTo && (
          <div className="mb-2 p-2 bg-accent/50 border-l-4 border-primary rounded flex items-center justify-between">
            <div>
              <span className="font-semibold text-primary mr-2">Respondendo:</span>
              <span className="text-sm text-muted-foreground">{replyTo.conteudo || 'Mídia'}</span>
            </div>
            <button onClick={() => setReplyTo(null)} className="ml-2 p-1 rounded hover:bg-accent transition-colors">
              <X className="w-4 h-4 text-muted-foreground" />
            </button>
          </div>
        )}
        <div className="flex items-center space-x-2">
          <button className="p-2 hover:bg-accent rounded-lg transition-colors">
            <Paperclip className="h-5 w-5 text-muted-foreground" />
          </button>
          
          <div className="flex-1 relative">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Digite sua mensagem..."
              className="w-full px-4 py-2 border border-input rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
            />
          </div>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleSendMessage}
            disabled={!message.trim()}
            className="p-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="h-5 w-5" />
          </motion.button>

          <button className="p-2 hover:bg-accent rounded-lg transition-colors">
            <Smile className="h-5 w-5 text-muted-foreground" />
          </button>

          {/* Remover o botão tradicional de envio (motion.button) */}
        </div>
      </div>

      {/* Modal de informações do contato */}
      <ContactInfoModal />

      {/* Modal de informações da mensagem estilo WhatsApp */}
      {infoModalMessage && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-background dark:bg-zinc-900 rounded-xl p-6 shadow-xl min-w-[340px] max-w-[90vw]">
            <h2 className="font-bold text-lg mb-4 flex items-center gap-2">
              <Info className="w-5 h-5" /> Dados da mensagem
            </h2>
            <div className="space-y-4">
              {/* Status: Entregue */}
              <div className="flex items-center gap-3">
                <CheckCheck className="w-5 h-5 text-muted-foreground" />
                <div>
                  <div className="font-medium">Entregue</div>
                  <div className="text-xs text-muted-foreground">{infoModalMessage.entregueEm ? `Hoje às ${infoModalMessage.entregueEm}` : '—'}</div>
                </div>
              </div>
              {/* Status: Vista */}
              <div className="flex items-center gap-3">
                <CheckCheck className="w-5 h-5 text-primary" />
                <div>
                  <div className="font-medium">Vista</div>
                  <div className="text-xs text-muted-foreground">{infoModalMessage.vistaEm ? `Hoje às ${infoModalMessage.vistaEm}` : '—'}</div>
                </div>
              </div>
              {/* Status: Reproduzida (apenas para áudio) */}
              {infoModalMessage.tipo === 'audio' && (
                <div className="flex items-center gap-3">
                  <Play className="w-5 h-5 text-blue-500" />
                  <div>
                    <div className="font-medium">Reproduzida</div>
                    <div className="text-xs text-muted-foreground">{infoModalMessage.reproduzidaEm ? `Hoje às ${infoModalMessage.reproduzidaEm}` : '—'}</div>
                  </div>
                </div>
              )}
            </div>
            <button className="mt-6 px-4 py-2 rounded bg-primary text-primary-foreground w-full" onClick={() => setInfoModalMessage(null)}>Fechar</button>
          </div>
        </div>
      )}
      {/* Modal de mensagens fixadas */}
      <Dialog open={showPinsModal} onOpenChange={setShowPinsModal}>
        <DialogContent className="!fixed !z-50 !w-[80vw] !h-[80vh] !max-w-none !max-h-none !translate-x-[-50%] !translate-y-[-50%] !top-[50%] !left-[50%] p-0 overflow-hidden bg-background rounded-lg border border-border shadow-2xl [&>button]:!absolute [&>button]:!top-6 [&>button]:!right-6 [&>button]:!text-primary-foreground [&>button]:!hover:bg-primary-foreground/20 [&>button]:!bg-transparent [&>button]:!border-none [&>button]:!shadow-none [&>button]:!rounded-lg [&>button]:!p-2 [&>button]:!transition-colors">
          <div className="bg-primary text-primary-foreground p-6 border-b border-primary/20">
            <div className="flex items-center gap-2">
              <Pin className="w-6 h-6 text-primary-foreground" />
              <h2 className="text-2xl font-bold">Mensagens fixadas</h2>
            </div>
            <p className="text-primary-foreground/80 text-sm mt-1">Veja todas as mensagens fixadas nesta conversa. Clique em uma para ir até ela no chat.</p>
          </div>
          <div className="flex-1 overflow-y-auto p-6">
            <div className="max-w-7xl mx-auto flex flex-col gap-4">
              {pinnedMessages.length === 0 && (
                <div className="text-muted-foreground text-sm">Nenhuma mensagem fixada.</div>
              )}
              {pinnedMessages.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  whileHover={{ scale: 1.01 }}
                  className="w-full cursor-pointer hover:bg-accent/50 rounded-lg transition-colors"
                  onClick={() => scrollToMessage(msg.id)}
                >
                  <Message message={msg} hideMenu />
                </motion.div>
              ))}
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Modal de encaminhar mensagem */}
      {forwardModalMessage && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="bg-background rounded-xl shadow-2xl w-full max-w-md mx-auto p-0">
            <div className="flex items-center border-b border-border p-4">
              <button onClick={handleCloseForwardModal} className="mr-2 p-1 rounded hover:bg-accent transition-colors">
                <span className="text-xl">×</span>
              </button>
              <h2 className="text-lg font-semibold">Encaminhar mensagem para</h2>
            </div>
            <div className="p-4">
              <div className="mb-4">
                <div className="flex items-center border border-primary rounded-lg px-3 py-2">
                  <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" className="mr-2 text-primary"><circle cx="8" cy="8" r="7"/><line x1="13" y1="13" x2="17" y2="17"/></svg>
                  <input
                    type="text"
                    placeholder="Buscar contato ou grupo"
                    className="flex-1 bg-transparent outline-none text-foreground"
                    value={forwardSearch}
                    onChange={e => setForwardSearch(e.target.value)}
                  />
                </div>
              </div>
              <div className="mb-2 text-sm text-primary font-medium">Conversas recentes</div>
              <div className="max-h-60 overflow-y-auto divide-y divide-border">
                {filteredChats.length === 0 && (
                  <div className="text-muted-foreground text-sm p-4 text-center">Nenhum contato encontrado.</div>
                )}
                {filteredChats.map(chat => {
                  const name = chat.is_group ? (chat.group_name || 'Grupo') : (chat.contact_name || chat.sender_name || chat.chat_id || 'Contato')
                  const selected = selectedChats.includes(chat.id)
                  return (
                    <div
                      key={chat.id}
                      className={`flex items-center px-3 py-2 cursor-pointer hover:bg-accent transition-colors rounded ${selected ? 'bg-primary/10 border-l-4 border-primary' : ''}`}
                      onClick={() => handleSelectChat(chat.id)}
                    >
                      <div className="h-8 w-8 bg-accent rounded-full flex items-center justify-center mr-3">
                        {chat.is_group ? (
                          <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="10" cy="10" r="8"/><path d="M6 14s1-2 4-2 4 2 4 2"/></svg>
                        ) : (
                          <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="10" cy="10" r="8"/><circle cx="10" cy="8" r="3"/><path d="M6 16s1-2 4-2 4 2 4 2"/></svg>
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-foreground">{name}</div>
                        <div className="text-xs text-muted-foreground">{chat.chat_id || 'N/A'}</div>
                      </div>
                      <input
                        type="checkbox"
                        checked={selected}
                        onChange={() => handleSelectChat(chat.id)}
                        className="accent-primary w-4 h-4 ml-2"
                        onClick={e => e.stopPropagation()}
                      />
                    </div>
                  )
                })}
              </div>
              <div className="flex justify-end mt-4">
                <button
                  className="bg-primary text-primary-foreground px-6 py-2 rounded-lg font-semibold disabled:opacity-50"
                  disabled={selectedChats.length === 0}
                  onClick={handleConfirmForward}
                >
                  Encaminhar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de mensagens favoritas */}
      <Dialog open={showFavoritesModal} onOpenChange={setShowFavoritesModal}>
        <DialogContent className="w-full h-[90vh] p-0 md:p-8 flex flex-col justify-center items-center">
          <DialogTitle asChild>
            <h2 className="text-2xl font-bold text-foreground flex items-center gap-2 mb-2">
              <Heart className="w-6 h-6 text-yellow-500" /> Mensagens Favoritas
            </h2>
          </DialogTitle>
          <DialogDescription asChild>
            <p className="text-muted-foreground mb-6">
              Suas mensagens favoritas nesta conversa. Clique em uma para ir até ela no chat.
            </p>
          </DialogDescription>
          <div className="overflow-y-auto h-full w-full flex flex-col gap-4 px-2 md:px-0">
            {favoritedMessages.length === 0 ? (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center py-12"
              >
                <Heart className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" />
                <p className="text-muted-foreground text-lg font-medium">Nenhuma mensagem favorita</p>
                <p className="text-muted-foreground/70 text-sm mt-2">
                  Toque na estrela ⭐ em qualquer mensagem para favoritá-la
                </p>
              </motion.div>
            ) : (
              favoritedMessages.map((msg, index) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ scale: 1.01 }}
                  className="w-full cursor-pointer hover:bg-accent/50 rounded-lg transition-colors border border-border/50"
                  onClick={() => scrollToMessage(msg.id)}
                >
                  <div className="p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-muted-foreground">
                        {new Date(msg.timestamp).toLocaleDateString('pt-BR', {
                          day: '2-digit',
                          month: '2-digit',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                      <Star className="w-4 h-4 text-yellow-500" />
                    </div>
                    <Message message={msg} hideMenu />
                  </div>
                </motion.div>
              ))
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
