import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Eye, EyeOff, MessageCircle, Loader2, AlertCircle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  const { login } = useAuth()
  const { theme, toggleTheme } = useTheme()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    const result = await login(email, password)
    
    if (!result.success) {
      setError(result.error)
    }
    
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex">
      {/* Lado esquerdo - Formulário */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 bg-background">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-md w-full space-y-8"
        >
          {/* Logo e título */}
          <div className="text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="mx-auto h-16 w-16 bg-primary rounded-2xl flex items-center justify-center mb-6"
            >
              <MessageCircle className="h-8 w-8 text-primary-foreground" />
            </motion.div>
            
            <h2 className="text-3xl font-bold text-foreground">
              MultiChat System
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Faça login para acessar seu painel de atendimento
            </p>
          </div>

          {/* Formulário */}
          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            {error && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 flex items-center space-x-2"
              >
                <AlertCircle className="h-5 w-5 text-destructive" />
                <span className="text-sm text-destructive">{error}</span>
              </motion.div>
            )}

            <div className="space-y-4">
              {/* Campo Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-foreground mb-2">
                  Email
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-3 border border-input rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all duration-200"
                  placeholder="seu@email.com"
                />
              </div>

              {/* Campo Senha */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-foreground mb-2">
                  Senha
                </label>
                <div className="relative">
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-3 py-3 pr-10 border border-input rounded-lg bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all duration-200"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Botão de login */}
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-primary-foreground bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-ring disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Entrando...</span>
                </div>
              ) : (
                'Entrar'
              )}
            </motion.button>

            {/* Links adicionais */}
            <div className="text-center">
              <a
                href="#"
                className="text-sm text-primary hover:text-primary/80 transition-colors"
              >
                Esqueceu sua senha?
              </a>
            </div>
          </form>

          {/* Toggle de tema */}
          <div className="text-center">
            <button
              onClick={toggleTheme}
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              {theme === 'light' ? '🌙 Modo escuro' : '☀️ Modo claro'}
            </button>
          </div>
        </motion.div>
      </div>

      {/* Lado direito - Imagem/Ilustração */}
      <div className="hidden lg:block lg:flex-1 bg-gradient-to-br from-primary/10 via-primary/5 to-transparent">
        <div className="flex items-center justify-center h-full p-12">
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="text-center max-w-lg"
          >
            <div className="mb-8">
              <div className="grid grid-cols-3 gap-4 mb-6">
                {[...Array(9)].map((_, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.5 + i * 0.1 }}
                    className="h-12 w-12 bg-primary/20 rounded-lg flex items-center justify-center"
                  >
                    <MessageCircle className="h-6 w-6 text-primary" />
                  </motion.div>
                ))}
              </div>
            </div>
            
            <h3 className="text-2xl font-bold text-foreground mb-4">
              Gerencie todos os seus atendimentos
            </h3>
            <p className="text-muted-foreground text-lg leading-relaxed">
              Centralize conversas do WhatsApp, organize sua equipe e ofereça 
              um atendimento excepcional aos seus clientes.
            </p>
            
            <div className="mt-8 space-y-4">
              <div className="flex items-center space-x-3 text-left">
                <div className="h-2 w-2 bg-primary rounded-full"></div>
                <span className="text-muted-foreground">Chat em tempo real</span>
              </div>
              <div className="flex items-center space-x-3 text-left">
                <div className="h-2 w-2 bg-primary rounded-full"></div>
                <span className="text-muted-foreground">Gestão de equipe</span>
              </div>
              <div className="flex items-center space-x-3 text-left">
                <div className="h-2 w-2 bg-primary rounded-full"></div>
                <span className="text-muted-foreground">Relatórios detalhados</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default Login

