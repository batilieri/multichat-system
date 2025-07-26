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
  const EMOJIS_PER_PAGE = 81 // 9x9 grid para aproveitar melhor o espaço

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
    <div className="w-96 h-96 bg-background text-foreground border border-border rounded-lg shadow-2xl p-4 flex flex-col gap-3 animate-in fade-in-0 zoom-in-95">
      {/* Barra de categorias */}
      <div className="flex gap-1 mb-3 overflow-x-auto border-b border-border pb-2">
        {categoryMeta.map(cat => (
          <button
            key={cat.key}
            className={`flex-1 flex flex-col items-center justify-center p-2 rounded-lg hover:bg-accent transition-colors text-xl ${activeCategory === cat.key ? 'bg-accent text-primary' : 'text-muted-foreground'}`}
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
          className="w-full px-3 py-2 rounded-lg border border-border bg-input text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
          placeholder="🔍 Buscar emoji..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          aria-label="Buscar emoji"
        />
      )}
      {/* Grid de emojis */}
      <div className="grid grid-cols-9 gap-2 flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-accent/40 scrollbar-track-transparent">
        {paginated.length === 0 && (
          <span className="col-span-9 text-center text-muted-foreground text-sm py-8">
            {activeCategory === 'recent' ? 'Nenhum emoji recente' : 'Nenhum emoji encontrado'}
          </span>
        )}
        {paginated.map((emoji, i) => (
          <button
            key={i}
            className="text-2xl p-2 rounded-lg hover:bg-accent focus:bg-accent transition-colors hover:scale-110 transform"
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
        <div className="flex justify-center gap-3 mt-3 pt-2 border-t border-border">
          <button
            className="px-3 py-1 rounded-lg bg-accent text-sm disabled:opacity-50 hover:bg-accent/80 transition-colors"
            onClick={() => setPage(p => Math.max(0, p - 1))}
            disabled={page === 0}
          >
            ← Anterior
          </button>
          <span className="text-sm text-muted-foreground self-center px-3 py-1 bg-muted rounded-lg">
            {page + 1} / {Math.ceil(emojis.length / EMOJIS_PER_PAGE)}
          </span>
          <button
            className="px-3 py-1 rounded-lg bg-accent text-sm disabled:opacity-50 hover:bg-accent/80 transition-colors"
            onClick={() => setPage(p => Math.min(Math.ceil(emojis.length / EMOJIS_PER_PAGE) - 1, p + 1))}
            disabled={page >= Math.ceil(emojis.length / EMOJIS_PER_PAGE) - 1}
          >
            Próxima →
          </button>
        </div>
      )}
    </div>
  )
} 