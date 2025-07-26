import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import './App.css'

// Componentes
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './components/Dashboard'
import ChatList from './components/ChatList'
import ChatView from './components/ChatView'
import UserManagement from './components/UserManagement'
import WhatsappInstances from './components/WhatsappInstances'
import Settings from './components/Settings'
import Login from './components/Login'
import Relatorios from './components/Relatorios'

// Context
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'

// Componente para rotas protegidas
const ProtectedRoute = ({ children, requiredPermission }) => {
  const { user, isAuthenticated } = useAuth()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  if (requiredPermission && !requiredPermission()) {
    return <Navigate to="/dashboard" replace />
  }
  
  return children
}

// Layout principal da aplicação
function AppLayout() {
  const { user, isAuthenticated, canCreateUsers, canAccessReports, canAccessSettings, canAccessWhatsApp, canAccessUsers } = useAuth()
  const [selectedChat, setSelectedChat] = useState(null)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const location = useLocation()
  
  // Verificar se está na rota de chats para minimizar o header
  const isInChats = location.pathname === '/chats'

  if (!isAuthenticated) {
    return <Login />
  }

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar - Fixa na lateral */}
      <div className="fixed left-0 top-0 h-full z-30">
        <Sidebar 
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
      </div>
      
      {/* Conteúdo principal - Com margem para a sidebar */}
      <div 
        className={`flex-1 flex flex-col transition-all duration-300 ${
          sidebarCollapsed ? 'ml-20' : 'ml-70'
        }`}
      >
        {/* Header - Fixo no topo */}
        <div className="sticky top-0 z-20 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <Header user={user} isMinimized={isInChats} />
        </div>
        
        {/* Área de conteúdo - Com scroll natural */}
        <main className="flex-1 min-h-0">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route 
              path="/chats" 
              element={
                <div className="flex h-[calc(100vh-4rem)] w-full max-w-full overflow-hidden">
                  <div className="w-[340px] min-w-[260px] max-w-[400px] border-r border-border overflow-y-auto">
                    <ChatList 
                      selectedChat={selectedChat}
                      onSelectChat={setSelectedChat}
                    />
                  </div>
                  <div className="flex-1 min-w-0 overflow-y-auto">
                    {selectedChat ? (
                      <ChatView chat={selectedChat} />
                    ) : (
                      <div className="flex items-center justify-center h-full text-muted-foreground">
                        Selecione um chat para começar
                      </div>
                    )}
                  </div>
                </div>
              } 
            />
            <Route 
              path="/usuarios" 
              element={
                <ProtectedRoute requiredPermission={canAccessUsers}>
                  <UserManagement />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/whatsapp" 
              element={
                <ProtectedRoute requiredPermission={canAccessWhatsApp}>
                  <WhatsappInstances />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/relatorios" 
              element={
                <ProtectedRoute requiredPermission={canAccessReports}>
                  <Relatorios />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/configuracoes" 
              element={
                <ProtectedRoute requiredPermission={canAccessSettings}>
                  <Settings />
                </ProtectedRoute>
              } 
            />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <AppLayout />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App

