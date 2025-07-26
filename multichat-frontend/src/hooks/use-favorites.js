import { useState, useEffect, useCallback } from 'react'
import { getAllFavoritedMessages, toggleFavoriteMessage } from '../data/mock/messages'

export const useFavorites = () => {
  const [favoritedMessages, setFavoritedMessages] = useState([])
  const [isLoading, setIsLoading] = useState(true)

  // Carregar favoritas
  const loadFavorites = useCallback(() => {
    try {
      const favorites = getAllFavoritedMessages()
      setFavoritedMessages(favorites)
    } catch (error) {
      console.error('Erro ao carregar favoritas:', error)
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Toggle favorita
  const toggleFavorite = useCallback((messageId) => {
    try {
      const updatedMessage = toggleFavoriteMessage(messageId)
      if (updatedMessage) {
        // Atualizar lista local
        setFavoritedMessages(prev => {
          if (updatedMessage.isFavorited) {
            // Adicionar se não existir
            return prev.some(msg => msg.id === messageId) 
              ? prev 
              : [...prev, updatedMessage]
          } else {
            // Remover se existir
            return prev.filter(msg => msg.id !== messageId)
          }
        })
      }
      return updatedMessage
    } catch (error) {
      console.error('Erro ao favoritar mensagem:', error)
      return null
    }
  }, [])

  // Verificar se uma mensagem é favorita
  const isFavorited = useCallback((messageId) => {
    return favoritedMessages.some(msg => msg.id === messageId)
  }, [favoritedMessages])

  // Obter contador de favoritas
  const getFavoritesCount = useCallback(() => {
    return favoritedMessages.length
  }, [favoritedMessages])

  // Filtrar favoritas por chat
  const getFavoritesByChat = useCallback((chatId) => {
    return favoritedMessages.filter(msg => msg.chatId === chatId)
  }, [favoritedMessages])

  // Filtrar favoritas por tipo
  const getFavoritesByType = useCallback((type) => {
    return favoritedMessages.filter(msg => msg.tipo === type)
  }, [favoritedMessages])

  // Buscar favoritas por texto
  const searchFavorites = useCallback((searchTerm) => {
    if (!searchTerm) return favoritedMessages
    
    return favoritedMessages.filter(msg => 
      (msg.conteudo || msg.content || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (msg.sender || '').toLowerCase().includes(searchTerm.toLowerCase())
    )
  }, [favoritedMessages])

  // Carregar favoritas ao montar o hook
  useEffect(() => {
    loadFavorites()
    
    // Atualizar a cada 2 segundos para sincronizar mudanças
    const interval = setInterval(loadFavorites, 2000)
    return () => clearInterval(interval)
  }, [loadFavorites])

  return {
    favoritedMessages,
    isLoading,
    toggleFavorite,
    isFavorited,
    getFavoritesCount,
    getFavoritesByChat,
    getFavoritesByType,
    searchFavorites,
    loadFavorites
  }
} 