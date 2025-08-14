import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Volume2, Play, Pause, Download, Heart, Share2, MoreVertical } from 'lucide-react';
import { Button } from './ui/button';
import SimpleAudioPlayer from './SimpleAudioPlayer';

const AudioTest = () => {
  const [testMessages, setTestMessages] = useState([
    {
      id: 1,
      tipo: 'audio',
      conteudo: '[Áudio]',
      chat_id: '556999267344',
      cliente_id: 2,
      instance_id: 'DTBDM1-YC2NM5-79C0T4',
      message_id: 'msg_83228A0F_20250814_092821',
      isOwn: false,
      timestamp: new Date().toISOString()
    },
    {
      id: 2,
      tipo: 'audio',
      conteudo: '[Áudio]',
      chat_id: '556999872433',
      cliente_id: 2,
      instance_id: 'DTBDM1-YC2NM5-79C0T4',
      message_id: 'msg_328F544F_20250814_092946',
      isOwn: true,
      timestamp: new Date().toISOString()
    },
    {
      id: 3,
      tipo: 'audio',
      conteudo: '[Áudio]',
      chat_id: '556999267344',
      cliente_id: 2,
      instance_id: 'DTBDM1-YC2NM5-79C0T4',
      message_id: 'msg_8DF20434_20250814_092709',
      isOwn: false,
      timestamp: new Date().toISOString()
    }
  ]);

  const addTestMessage = () => {
    const newMessage = {
      id: Date.now(),
      tipo: 'audio',
      conteudo: '[Áudio]',
      chat_id: '556999267344',
      cliente_id: 2,
      instance_id: 'DTBDM1-YC2NM5-79C0T4',
      message_id: `msg_${Math.random().toString(36).substr(2, 8)}_${Date.now()}`,
      isOwn: Math.random() > 0.5,
      timestamp: new Date().toISOString()
    };
    setTestMessages(prev => [...prev, newMessage]);
  };

  const clearMessages = () => {
    setTestMessages([]);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">🎵 Teste do Sistema de Áudio</h1>
        <p className="text-muted-foreground">
          Teste o player de áudio com mensagens simuladas
        </p>
      </div>

      {/* Controles de teste */}
      <div className="flex items-center justify-center gap-4">
        <Button onClick={addTestMessage} className="bg-orange-500 hover:bg-orange-600">
          <Volume2 className="w-4 h-4 mr-2" />
          Adicionar Mensagem de Áudio
        </Button>
        <Button onClick={clearMessages} variant="outline">
          Limpar Mensagens
        </Button>
      </div>

      {/* Estatísticas */}
      <div className="bg-accent rounded-lg p-4 text-center">
        <h3 className="font-medium mb-2">Estatísticas do Teste</h3>
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-muted-foreground">Total de mensagens</p>
            <p className="font-medium">{testMessages.length}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Mensagens próprias</p>
            <p className="font-medium">
              {testMessages.filter(m => m.isOwn).length}
            </p>
          </div>
          <div>
            <p className="text-muted-foreground">Mensagens recebidas</p>
            <p className="font-medium">
              {testMessages.filter(m => !m.isOwn).length}
            </p>
          </div>
        </div>
      </div>

      {/* Lista de mensagens de teste */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold">Mensagens de Áudio de Teste</h2>
        
        {testMessages.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Volume2 className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p>Nenhuma mensagem de áudio para testar</p>
            <p className="text-sm">Clique em "Adicionar Mensagem de Áudio" para começar</p>
          </div>
        ) : (
          <div className="space-y-4">
            {testMessages.map((message, index) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border border-border rounded-lg p-4 bg-card"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">
                      {message.isOwn ? 'Você' : 'Contato'}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      ID: {message.message_id}
                    </span>
                    <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                      Chat: {message.chat_id}
                    </span>
                  </div>
                </div>
                
                {/* Renderizar o player de áudio */}
                <SimpleAudioPlayer 
                  message={message} 
                  isOwnMessage={message.isOwn}
                />
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Instruções */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-medium text-blue-800 mb-2">Como testar:</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Clique em "Adicionar Mensagem de Áudio" para criar mensagens de teste</li>
          <li>• Cada mensagem simula uma mensagem de áudio real do chat</li>
          <li>• Teste os controles de play/pause em cada player</li>
          <li>• Verifique se as URLs estão sendo construídas corretamente</li>
          <li>• Teste mensagens próprias vs. recebidas</li>
          <li>• Use o console do navegador para ver logs detalhados</li>
        </ul>
      </div>

      {/* Logs de debug */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h3 className="font-medium text-gray-800 mb-2">Logs de Debug</h3>
        <p className="text-sm text-gray-600">
          Abra o console do navegador (F12) para ver logs detalhados sobre:
        </p>
        <ul className="text-sm text-gray-600 mt-2 space-y-1">
          <li>• Detecção de tipo de mensagem</li>
          <li>• Construção de URLs de áudio</li>
          <li>• Estados de carregamento e erro</li>
          <li>• Eventos de reprodução</li>
        </ul>
      </div>
    </div>
  );
};

export default AudioTest; 