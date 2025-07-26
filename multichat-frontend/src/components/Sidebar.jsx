import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  MessageCircle,
  Users,
  Settings,
  ChevronLeft,
  ChevronRight,
  BarChart3,
  UserCheck,
  Bell,
  HelpCircle,
  Smartphone
} from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const Sidebar = ({ collapsed, onToggle }) => {
  const location = useLocation()
  const { isAdmin, isCliente, isColaborador, canCreateUsers, canAccessReports, canAccessSettings, canAccessWhatsApp, canAccessUsers } = useAuth()

  console.log('🔍 Sidebar - isAdmin():', isAdmin());
  console.log('🔍 Sidebar - canAccessReports():', canAccessReports());
  console.log('🔍 Sidebar - canAccessSettings():', canAccessSettings());
  console.log('🔍 Sidebar - canAccessWhatsApp():', canAccessWhatsApp());
  console.log('🔍 Sidebar - canAccessUsers():', canAccessUsers());

  const menuItems = [
    {
      title: 'Dashboard',
      icon: LayoutDashboard,
      path: '/dashboard',
      description: 'Visão geral do sistema',
      show: true // Todos podem ver o dashboard
    },
    {
      title: 'Chats',
      icon: MessageCircle,
      path: '/chats',
      description: 'Conversas ativas',
      show: true // Todos podem ver os chats
    },
    {
      title: 'WhatsApp',
      icon: Smartphone,
      path: '/whatsapp',
      description: 'Instâncias WhatsApp',
      show: canAccessWhatsApp()
    },
    {
      title: 'Usuários',
      icon: Users,
      path: '/usuarios',
      description: 'Gerenciar equipe',
      show: canAccessUsers()
    },
    {
      title: 'Relatórios',
      icon: BarChart3,
      path: '/relatorios',
      description: 'Análises e métricas',
      show: canAccessReports()
    },
    {
      title: 'Configurações',
      icon: Settings,
      path: '/configuracoes',
      description: 'Configurações do sistema',
      show: canAccessSettings()
    }
  ].filter(item => item.show)

  const isActive = (path) => location.pathname === path

  return (
    <motion.div
      initial={false}
      animate={{
        width: collapsed ? 80 : 280
      }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
      className="bg-sidebar border-r border-sidebar-border flex flex-col h-full relative"
    >
      {/* Header da sidebar */}
      <div className="p-4 border-b border-sidebar-border">
        <div className="flex items-center justify-between">
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center space-x-3"
            >
              <div className="h-8 w-8 bg-sidebar-primary rounded-lg flex items-center justify-center">
                <MessageCircle className="h-5 w-5 text-sidebar-primary-foreground" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-sidebar-foreground">
                  MultiChat
                </h1>
                <p className="text-xs text-sidebar-foreground/60">
                  Sistema de Atendimento
                </p>
              </div>
            </motion.div>
          )}
          
          <button
            onClick={onToggle}
            className="p-1.5 rounded-lg hover:bg-sidebar-accent transition-colors"
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4 text-sidebar-foreground" />
            ) : (
              <ChevronLeft className="h-4 w-4 text-sidebar-foreground" />
            )}
          </button>
        </div>
      </div>

      {/* Menu principal */}
      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const active = isActive(item.path)
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className="block"
            >
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`
                  flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all duration-200
                  ${active 
                    ? 'bg-sidebar-primary text-sidebar-primary-foreground shadow-sm' 
                    : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                  }
                `}
              >
                <Icon className={`h-5 w-5 ${collapsed ? 'mx-auto' : ''}`} />
                
                {!collapsed && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex-1"
                  >
                    <div className="font-medium">{item.title}</div>
                    <div className="text-xs opacity-60">{item.description}</div>
                  </motion.div>
                )}
              </motion.div>
            </Link>
          )
        })}
      </nav>

      {/* Seção inferior */}
      <div className="p-4 border-t border-sidebar-border space-y-2">
        {/* Notificações */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="flex items-center space-x-3 px-3 py-2 rounded-lg text-sidebar-foreground hover:bg-sidebar-accent transition-colors cursor-pointer"
        >
          <Bell className={`h-5 w-5 ${collapsed ? 'mx-auto' : ''}`} />
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex-1"
            >
              <div className="font-medium">Notificações</div>
              <div className="text-xs opacity-60">3 novas</div>
            </motion.div>
          )}
          {!collapsed && (
            <div className="h-2 w-2 bg-red-500 rounded-full"></div>
          )}
        </motion.div>

        {/* Ajuda */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          className="flex items-center space-x-3 px-3 py-2 rounded-lg text-sidebar-foreground hover:bg-sidebar-accent transition-colors cursor-pointer"
        >
          <HelpCircle className={`h-5 w-5 ${collapsed ? 'mx-auto' : ''}`} />
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex-1"
            >
              <div className="font-medium">Ajuda</div>
              <div className="text-xs opacity-60">Suporte e docs</div>
            </motion.div>
          )}
        </motion.div>
      </div>

      {/* Status de conexão */}
      <div className="p-4 border-t border-sidebar-border">
        <div className={`flex items-center ${collapsed ? 'justify-center' : 'space-x-3'}`}>
          <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-xs text-sidebar-foreground/60"
            >
              Sistema online
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export default Sidebar

