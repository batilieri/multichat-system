import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search,
  User,
  LogOut,
  ChevronDown,
  Settings,
  Moon,
  Sun
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'

const Header = ({ user, isMinimized = false }) => {
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  
  const { logout } = useAuth()
  const { theme, toggleTheme } = useTheme()

  const handleLogout = async () => {
    await logout()
    setShowUserMenu(false)
  }

  return (
    <header className="bg-background border-b border-border px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Lado esquerdo - Busca (visível quando não minimizado) */}
        {!isMinimized && (
          <div className="flex items-center space-x-4 flex-1">
            <div className="relative max-w-md w-full">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Buscar chats, usuários..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-input rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all duration-200"
              />
            </div>
          </div>
        )}

        {/* Lado direito - Controles */}
        <div className="flex items-center space-x-4">
          {/* Toggle de tema (visível quando não minimizado) */}
          {!isMinimized && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-accent transition-colors"
            >
              {theme === 'light' ? (
                <Moon className="h-5 w-5 text-foreground" />
              ) : (
                <Sun className="h-5 w-5 text-foreground" />
              )}
            </motion.button>
          )}

          {/* Menu do usuário - Visível apenas quando não minimizado */}
          {!isMinimized && (
            <div className="relative">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 p-2 rounded-lg hover:bg-accent transition-colors"
              >
                <div className="h-8 w-8 bg-primary rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-primary-foreground" />
                </div>
                <div className="text-left hidden sm:block">
                  <p className="font-medium text-foreground text-sm">
                    {user?.nome || user?.email}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {user?.tipo_usuario}
                  </p>
                </div>
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              </motion.button>

            {/* Menu dropdown do usuário */}
            <AnimatePresence>
              {showUserMenu && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                  className="absolute right-0 mt-2 w-64 bg-popover border border-border rounded-lg shadow-lg z-50"
                >
                  <div className="p-4 border-b border-border">
                    <div className="flex items-center space-x-3">
                      <div className="h-12 w-12 bg-primary rounded-full flex items-center justify-center">
                        <User className="h-6 w-6 text-primary-foreground" />
                      </div>
                      <div>
                        <p className="font-medium text-foreground">
                          {user?.nome || user?.email}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {user?.cliente?.nome_empresa}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Plano: {user?.cliente?.plano}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="p-2">
                    <motion.button
                      whileHover={{ backgroundColor: 'var(--accent)' }}
                      className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors"
                    >
                      <User className="h-4 w-4 text-muted-foreground" />
                      <span className="text-foreground">Meu Perfil</span>
                    </motion.button>

                    <motion.button
                      whileHover={{ backgroundColor: 'var(--accent)' }}
                      className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors"
                    >
                      <Settings className="h-4 w-4 text-muted-foreground" />
                      <span className="text-foreground">Configurações</span>
                    </motion.button>

                    <div className="border-t border-border my-2"></div>

                    <motion.button
                      whileHover={{ backgroundColor: 'var(--destructive)' }}
                      onClick={handleLogout}
                      className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors text-destructive hover:text-destructive-foreground"
                    >
                      <LogOut className="h-4 w-4" />
                      <span>Sair</span>
                    </motion.button>
                  </div>
                </motion.div>
                          )}
          </AnimatePresence>
        </div>
        )}
      </div>
      </div>

      {/* Overlay para fechar menus */}
      {showUserMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => {
            setShowUserMenu(false)
          }}
        />
      )}
    </header>
  )
}

export default Header

