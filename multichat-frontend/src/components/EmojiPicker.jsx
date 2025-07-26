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
  const EMOJIS_PER_PAGE = 56 // 7x8 grid

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
    onClose?.()
  }

  return (
    <div className="w-80 bg-background text-foreground p-3 flex flex-col gap-2 animate-in fade-in-0 zoom-in-95">
      {/* Barra de categorias */}
      <div className="flex gap-1 mb-2 overflow-x-auto">
        {categoryMeta.map(cat => (
          <button
            key={cat.key}
            className={`flex-1 flex flex-col items-center justify-center p-1 rounded-md hover:bg-accent transition-colors text-lg ${activeCategory === cat.key ? 'bg-accent' : ''}`}
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
        <input
          type="text"
          className="w-full px-3 py-2 rounded-md border border-border bg-input text-sm mb-2 focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="Buscar emoji..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          aria-label="Buscar emoji"
        />
      )}
      {/* Grid de emojis */}
      <div className="grid grid-cols-8 gap-1 max-h-56 overflow-y-auto scrollbar-thin scrollbar-thumb-accent/40 scrollbar-track-transparent">
        {paginated.length === 0 && (
          <span className="col-span-8 text-center text-muted-foreground text-xs py-4">
            {activeCategory === 'recent' ? 'Nenhum emoji recente' : 'Nenhum emoji encontrado'}
          </span>
        )}
        {paginated.map((emoji, i) => (
          <button
            key={i}
            className="text-xl p-1 rounded hover:bg-accent focus:bg-accent transition-colors"
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
        <div className="flex justify-center gap-2 mt-2">
          <button
            className="px-2 py-1 rounded bg-accent text-xs disabled:opacity-50"
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
          >
            Anterior
          </button>
          <span className="text-xs text-muted-foreground self-center">{page + 1} / {Math.ceil(emojis.length / EMOJIS_PER_PAGE)}</span>
          <button
            className="px-2 py-1 rounded bg-accent text-xs disabled:opacity-50"
            onClick={() => setPage(p => Math.min(Math.ceil(emojis.length / EMOJIS_PER_PAGE) - 1, p + 1))}
            disabled={page >= Math.ceil(emojis.length / EMOJIS_PER_PAGE) - 1}
          >
            Próxima
          </button>
        </div>
      )}
    </div>
  )
} 