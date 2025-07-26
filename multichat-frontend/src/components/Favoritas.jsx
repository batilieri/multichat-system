import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Heart, Star, Search, Filter, Calendar, User, MessageCircle, Trash2 } from 'lucide-react'
import { clearAllFavorites } from '../data/mock/messages'
import { useFavorites } from '../hooks/use-favorites'
import Message from './Message'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'
import { useToast } from './ui/use-toast'

const Favoritas = () => {
  const [filteredMessages, setFilteredMessages] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [sortBy, setSortBy] = useState('date')
  const { toast } = useToast()
  
  const { 
    favoritedMessages, 
    isLoading, 
    searchFavorites, 
    getFavoritesByType 
  } = useFavorites()

  // Filtrar e ordenar mensagens
  useEffect(() => {
    let filtered = searchFavorites(searchTerm)

    // Filtrar por tipo
    if (filterType !== 'all') {
      filtered = getFavoritesByType(filterType)
    }

    // Ordenar
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.timestamp) - new Date(a.timestamp)
        case 'sender':
          return (a.sender || '').localeCompare(b.sender || '')
        case 'type':
          return (a.tipo || '').localeCompare(b.tipo || '')
        default:
          return 0
      }
    })

    setFilteredMessages(filtered)
  }, [favoritedMessages, searchTerm, filterType, sortBy, searchFavorites, getFavoritesByType])

  const handleClearAll = () => {
    if (window.confirm('Tem certeza que deseja remover todas as mensagens favoritas?')) {
      clearAllFavorites()
      setFilteredMessages([])
      toast({
        title: "Favoritas removidas",
        description: "Todas as mensagens favoritas foram removidas",
        duration: 3000,
      })
    }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'imagem':
        return '🖼️'
      case 'video':
        return '🎥'
      case 'audio':
        return '🎵'
      case 'documento':
        return '📄'
      case 'sticker':
        return '😀'
      default:
        return '💬'
    }
  }

  const getTypeLabel = (type) => {
    switch (type) {
      case 'imagem':
        return 'Imagem'
      case 'video':
        return 'Vídeo'
      case 'audio':
        return 'Áudio'
      case 'documento':
        return 'Documento'
      case 'sticker':
        return 'Sticker'
      default:
        return 'Texto'
    }
  }

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <div className="p-6 border-b border-border bg-card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="h-12 w-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
              <Heart className="h-6 w-6 text-yellow-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-foreground">Mensagens Favoritas</h1>
              <p className="text-muted-foreground">
                {favoritedMessages.length} mensagem{favoritedMessages.length !== 1 ? 's' : ''} favorita{favoritedMessages.length !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
          
          {favoritedMessages.length > 0 && (
            <Button 
              variant="outline" 
              onClick={handleClearAll}
              className="text-destructive hover:text-destructive"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Limpar todas
            </Button>
          )}
        </div>

        {/* Filtros */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Busca */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar mensagens..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Filtro por tipo */}
          <Select value={filterType} onValueChange={setFilterType}>
            <SelectTrigger>
              <SelectValue placeholder="Tipo de mensagem" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos os tipos</SelectItem>
              <SelectItem value="texto">Texto</SelectItem>
              <SelectItem value="imagem">Imagem</SelectItem>
              <SelectItem value="video">Vídeo</SelectItem>
              <SelectItem value="audio">Áudio</SelectItem>
              <SelectItem value="documento">Documento</SelectItem>
              <SelectItem value="sticker">Sticker</SelectItem>
            </SelectContent>
          </Select>

          {/* Ordenação */}
          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger>
              <SelectValue placeholder="Ordenar por" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="date">Data (mais recente)</SelectItem>
              <SelectItem value="sender">Remetente</SelectItem>
              <SelectItem value="type">Tipo</SelectItem>
            </SelectContent>
          </Select>

          {/* Estatísticas */}
          <div className="flex items-center justify-center p-2 bg-accent rounded-lg">
            <span className="text-sm text-muted-foreground">
              {filteredMessages.length} de {favoritedMessages.length}
            </span>
          </div>
        </div>
      </div>

      {/* Lista de mensagens */}
      <div className="flex-1 overflow-y-auto p-6">
        {isLoading ? (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12"
          >
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500 mx-auto mb-4"></div>
            <p className="text-muted-foreground">Carregando favoritas...</p>
          </motion.div>
        ) : favoritedMessages.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12"
          >
            <Heart className="w-24 h-24 text-muted-foreground/30 mx-auto mb-6" />
            <h3 className="text-xl font-semibold text-foreground mb-2">
              Nenhuma mensagem favorita
            </h3>
            <p className="text-muted-foreground max-w-md mx-auto">
              Você ainda não favoritou nenhuma mensagem. Toque na estrela ⭐ em qualquer mensagem para adicioná-la aos seus favoritos.
            </p>
          </motion.div>
        ) : filteredMessages.length === 0 ? (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12"
          >
            <Search className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Nenhuma mensagem encontrada
            </h3>
            <p className="text-muted-foreground">
              Tente ajustar os filtros de busca
            </p>
          </motion.div>
        ) : (
          <div className="space-y-4">
            {filteredMessages.map((msg, index) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-card border border-border rounded-lg p-4 hover:bg-accent/50 transition-colors"
              >
                {/* Header da mensagem */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{getTypeIcon(msg.tipo)}</span>
                      <span className="text-sm font-medium text-foreground">
                        {getTypeLabel(msg.tipo)}
                      </span>
                    </div>
                    <span className="text-muted-foreground">•</span>
                    <div className="flex items-center space-x-1">
                      <User className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">
                        {msg.sender || 'Remetente'}
                      </span>
                    </div>
                    <span className="text-muted-foreground">•</span>
                    <div className="flex items-center space-x-1">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">
                        {new Date(msg.timestamp).toLocaleDateString('pt-BR', {
                          day: '2-digit',
                          month: '2-digit',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </span>
                    </div>
                  </div>
                  <Star className="h-5 w-5 text-yellow-500" />
                </div>

                {/* Conteúdo da mensagem */}
                <div className="pl-6 border-l-2 border-yellow-500/30">
                  <Message message={msg} hideMenu />
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Favoritas 