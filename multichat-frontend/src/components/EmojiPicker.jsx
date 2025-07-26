import React, { useState, useMemo, useEffect } from 'react'
import Emoji from './Emoji'
import emojiData from '../data/emoji-whatsapp.json'

// Mapeamento de nomes de categoria para ícones e rótulos amigáveis
const categoryMeta = [
  { key: 'recent', icon: '🕒', label: 'Recentes' },
  { key: 'Smileys & Emotion', icon: '😃', label: 'Emoção' },
  { key: 'People & Body', icon: '🧑', label: 'Pessoas' },
  { key: 'Animals & Nature', icon: '🌱', label: 'Natureza' },
  { key: 'Food & Drink', icon: '🍔', label: 'Comida' },
  { key: 'Travel & Places', icon: '🌍', label: 'Lugares' },
  { key: 'Activities', icon: '⚽', label: 'Atividades' },
  { key: 'Objects', icon: '💡', label: 'Objetos' },
  { key: 'Symbols', icon: '🔣', label: 'Símbolos' },
  { key: 'Flags', icon: '🏳️', label: 'Bandeiras' },
]

const RECENT_KEY = 'emoji_recent'
const RECENT_LIMIT = 32

function getRecentEmojis() {
  try {
    const data = localStorage.getItem(RECENT_KEY)
    if (!data) return []
    return JSON.parse(data)
  } catch {
    return []
  }
}
function addRecentEmoji(emoji) {
  try {
    let rec = getRecentEmojis()
    rec = rec.filter(e => e !== emoji)
    rec.unshift(emoji)
    if (rec.length > RECENT_LIMIT) rec = rec.slice(0, RECENT_LIMIT)
    localStorage.setItem(RECENT_KEY, JSON.stringify(rec))
  } catch {}
}

export default function EmojiPicker({ onSelect, onClose, searchEnabled = true }) {
  const [search, setSearch] = useState('')
  const [activeCategory, setActiveCategory] = useState(categoryMeta[0].key)
  const [page, setPage] = useState(0)
  const [recent, setRecent] = useState([])
  const EMOJIS_PER_PAGE = 72 // 8x9 grid para aproveitar melhor o espaço reduzido

  // Carregar recentes ao abrir
  useEffect(() => {
    setRecent(getRecentEmojis())
  }, [])
  // Atualizar recentes ao trocar aba para recentes
  useEffect(() => {
    if (activeCategory === 'recent') setRecent(getRecentEmojis())
  }, [activeCategory])

  // Lista de emojis da categoria ativa
  const emojis = useMemo(() => {
    if (activeCategory === 'recent') {
      // Buscar detalhes dos emojis recentes
      const all = Object.values(emojiData).flat()
      return recent
        .map(e => all.find(obj => obj.emoji === e))
        .filter(Boolean)
    }
    let list = emojiData[activeCategory] || []
    if (search.trim()) {
      const q = search.trim().toLowerCase()
      list = list.filter(e =>
        e.emoji.includes(q) ||
        (e.name && e.name.toLowerCase().includes(q)) ||
        (e.slug && e.slug.toLowerCase().includes(q))
      )
    }
    return list
  }, [activeCategory, search, recent])

  // Paginação
  const paginated = useMemo(() => {
    const start = page * EMOJIS_PER_PAGE
    return emojis.slice(start, start + EMOJIS_PER_PAGE)
  }, [emojis, page])

  // Resetar página ao trocar categoria ou busca
  useEffect(() => { setPage(0) }, [activeCategory, search])

  // Handler de seleção
  function handleSelect(emoji) {
    if (activeCategory !== 'recent') addRecentEmoji(emoji)
    onSelect?.(emoji)
    // Não fechar automaticamente para permitir múltiplos cliques
  }

  return (
    <div className="w-96 h-96 bg-background text-foreground border border-border rounded-xl shadow-2xl p-4 flex flex-col gap-3 animate-in fade-in-0 zoom-in-95 backdrop-blur-sm">
      {/* Barra de categorias */}
      <div className="flex gap-1 mb-3 overflow-x-auto border-b border-border/50 pb-3">
        {categoryMeta.map(cat => (
          <button
            key={cat.key}
            className={`flex-1 flex flex-col items-center justify-center p-2 rounded-lg hover:bg-accent/50 transition-all duration-200 text-lg ${activeCategory === cat.key ? 'bg-primary/10 text-primary border border-primary/20' : 'text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveCategory(cat.key)}
            title={cat.label}
            type="button"
          >
            <span>{cat.icon}</span>
          </button>
        ))}
      </div>
      {/* Busca */}
      {searchEnabled && activeCategory !== 'recent' && (
        <div className="relative mb-3">
          <input
            type="text"
            className="w-full px-3 py-2 pl-9 rounded-lg border border-border/50 bg-input/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-200"
            placeholder="Buscar emoji..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            aria-label="Buscar emoji"
          />
          <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">🔍</span>
        </div>
      )}
      {/* Grid de emojis */}
      <div className="grid grid-cols-8 gap-1 flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-accent/40 scrollbar-track-transparent p-1">
        {paginated.length === 0 && (
          <span className="col-span-8 text-center text-muted-foreground text-sm py-8">
            {activeCategory === 'recent' ? 'Nenhum emoji recente' : 'Nenhum emoji encontrado'}
          </span>
        )}
        {paginated.map((emoji, i) => (
          <button
            key={i}
            className="text-lg p-1 rounded-md hover:bg-accent/60 focus:bg-accent/60 transition-all duration-200 hover:scale-105 transform active:scale-95"
            onClick={() => handleSelect(emoji.emoji)}
            type="button"
            tabIndex={0}
            title={emoji.name}
          >
            <Emoji>{emoji.emoji}</Emoji>
          </button>
        ))}
      </div>
      {/* Paginação */}
      {emojis.length > EMOJIS_PER_PAGE && (
        <div className="flex justify-center gap-2 mt-3 pt-3 border-t border-border/50">
          <button
            className="px-2 py-1 rounded-md bg-accent/50 text-xs disabled:opacity-30 hover:bg-accent/70 transition-all duration-200 disabled:cursor-not-allowed"
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
          >
            ←
          </button>
          <span className="text-xs text-muted-foreground self-center px-2 py-1 bg-muted/50 rounded-md">
            {page + 1} / {Math.ceil(emojis.length / EMOJIS_PER_PAGE)}
          </span>
          <button
            className="px-2 py-1 rounded-md bg-accent/50 text-xs disabled:opacity-30 hover:bg-accent/70 transition-all duration-200 disabled:cursor-not-allowed"
            onClick={() => setPage(p => Math.min(Math.ceil(emojis.length / EMOJIS_PER_PAGE) - 1, p + 1))}
            disabled={page >= Math.ceil(emojis.length / EMOJIS_PER_PAGE) - 1}
          >
            →
          </button>
        </div>
      )}
    </div>
  )
} 