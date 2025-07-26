import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Settings as SettingsIcon, Save, Bell, Shield, Palette, Globe } from 'lucide-react'

const Settings = () => {
  const [settings, setSettings] = useState({
    notifications: {
      email: true,
      push: true,
      sound: false
    },
    appearance: {
      theme: 'auto',
      language: 'pt-BR'
    },
    security: {
      twoFactor: false,
      sessionTimeout: 30
    }
  })

  const handleSave = () => {
    console.log('Salvando configurações:', settings)
  }

  return (
    <div className="min-h-full bg-background">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Configurações</h1>
            <p className="text-muted-foreground">Personalize sua experiência</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleSave}
            className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            <Save className="h-4 w-4" />
            <span>Salvar</span>
          </motion.button>
        </div>
      </div>

      {/* Conteúdo com scroll */}
      <div className="p-6 space-y-6 overflow-y-auto">
        {/* Notificações */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-card border border-border rounded-lg p-6"
        >
          <div className="flex items-center space-x-3 mb-4">
            <Bell className="h-5 w-5 text-primary" />
            <h3 className="text-lg font-semibold text-foreground">Notificações</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-foreground">Notificações por email</span>
              <input
                type="checkbox"
                checked={settings.notifications.email}
                onChange={(e) => setSettings({
                  ...settings,
                  notifications: { ...settings.notifications, email: e.target.checked }
                })}
                className="rounded"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-foreground">Notificações push</span>
              <input
                type="checkbox"
                checked={settings.notifications.push}
                onChange={(e) => setSettings({
                  ...settings,
                  notifications: { ...settings.notifications, push: e.target.checked }
                })}
                className="rounded"
              />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-foreground">Som das notificações</span>
              <input
                type="checkbox"
                checked={settings.notifications.sound}
                onChange={(e) => setSettings({
                  ...settings,
                  notifications: { ...settings.notifications, sound: e.target.checked }
                })}
                className="rounded"
              />
            </div>
          </div>
        </motion.div>

        {/* Aparência */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-card border border-border rounded-lg p-6"
        >
          <div className="flex items-center space-x-3 mb-4">
            <Palette className="h-5 w-5 text-primary" />
            <h3 className="text-lg font-semibold text-foreground">Aparência</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-foreground mb-2">Tema</label>
              <select
                value={settings.appearance.theme}
                onChange={(e) => setSettings({
                  ...settings,
                  appearance: { ...settings.appearance, theme: e.target.value }
                })}
                className="w-full p-2 border border-input rounded-lg bg-background text-foreground"
              >
                <option value="light">Claro</option>
                <option value="dark">Escuro</option>
                <option value="auto">Automático</option>
              </select>
            </div>
            <div>
              <label className="block text-foreground mb-2">Idioma</label>
              <select
                value={settings.appearance.language}
                onChange={(e) => setSettings({
                  ...settings,
                  appearance: { ...settings.appearance, language: e.target.value }
                })}
                className="w-full p-2 border border-input rounded-lg bg-background text-foreground"
              >
                <option value="pt-BR">Português (Brasil)</option>
                <option value="en-US">English (US)</option>
                <option value="es-ES">Español</option>
              </select>
            </div>
          </div>
        </motion.div>

        {/* Segurança */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-card border border-border rounded-lg p-6"
        >
          <div className="flex items-center space-x-3 mb-4">
            <Shield className="h-5 w-5 text-primary" />
            <h3 className="text-lg font-semibold text-foreground">Segurança</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-foreground">Autenticação de dois fatores</span>
              <input
                type="checkbox"
                checked={settings.security.twoFactor}
                onChange={(e) => setSettings({
                  ...settings,
                  security: { ...settings.security, twoFactor: e.target.checked }
                })}
                className="rounded"
              />
            </div>
            <div>
              <label className="block text-foreground mb-2">Timeout da sessão (minutos)</label>
              <input
                type="number"
                value={settings.security.sessionTimeout}
                onChange={(e) => setSettings({
                  ...settings,
                  security: { ...settings.security, sessionTimeout: parseInt(e.target.value) }
                })}
                className="w-full p-2 border border-input rounded-lg bg-background text-foreground"
              />
            </div>
          </div>
        </motion.div>

        {/* Sistema */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-card border border-border rounded-lg p-6"
        >
          <div className="flex items-center space-x-3 mb-4">
            <Globe className="h-5 w-5 text-primary" />
            <h3 className="text-lg font-semibold text-foreground">Sistema</h3>
          </div>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-foreground">Versão</span>
              <span className="text-muted-foreground">1.0.0</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-foreground">Última atualização</span>
              <span className="text-muted-foreground">10/07/2025</span>
            </div>
            <button className="w-full p-2 border border-input rounded-lg hover:bg-accent transition-colors text-foreground">
              Verificar atualizações
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default Settings

