import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Volume2, Play, Pause, SkipBack, SkipForward, Plus, X, CheckCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { useToast } from './ui/use-toast';

const AudioSystemDemo = () => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackStatus, setPlaybackStatus] = useState({});
  const { toast } = useToast();

  const handleFileSelect = (files) => {
    const audioFiles = Array.from(files).filter(file => file.type.startsWith('audio/'));
    
    if (audioFiles.length === 0) {
      toast({
        title: "Erro",
        description: "Nenhum arquivo de áudio válido selecionado",
        variant: "destructive"
      });
      return;
    }

    const processedFiles = audioFiles.map(file => ({
      file,
      name: file.name,
      size: file.size,
      type: 'audio',
      url: URL.createObjectURL(file),
      id: Date.now() + Math.random()
    }));

    setSelectedFiles(prev => [...prev, ...processedFiles]);
    setCurrentIndex(0);
    
    toast({
      title: "Sucesso",
      description: `${audioFiles.length} arquivo(s) de áudio selecionado(s)`,
    });
  };

  const handlePlayback = (fileId, status) => {
    setPlaybackStatus(prev => ({
      ...prev,
      [fileId]: {
        ...prev[fileId],
        ...status,
        reproduzidaEm: new Date().toLocaleTimeString()
      }
    }));
  };

  const removeFile = (fileId) => {
    setSelectedFiles(prev => prev.filter(f => f.id !== fileId));
    if (selectedFiles.length === 1) {
      setCurrentIndex(0);
    } else if (currentIndex >= selectedFiles.length - 1) {
      setCurrentIndex(prev => prev - 1);
    }
  };

  const nextFile = () => {
    if (currentIndex < selectedFiles.length - 1) {
      setCurrentIndex(prev => prev + 1);
    }
  };

  const previousFile = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  };

  const currentFile = selectedFiles[currentIndex];

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">🎵 Sistema de Áudio MultiChat</h1>
        <p className="text-muted-foreground">
          Demonstração completa do sistema de áudio com todas as funcionalidades
        </p>
      </div>

      {/* Área de seleção de arquivos */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-orange-400 transition-colors"
      >
        <input
          type="file"
          multiple
          accept="audio/*"
          onChange={(e) => handleFileSelect(e.target.files)}
          className="hidden"
          id="demo-audio-input"
        />
        <label
          htmlFor="demo-audio-input"
          className="cursor-pointer flex flex-col items-center gap-4"
        >
          <div className="bg-orange-500 text-white rounded-full p-6">
            <Plus className="w-12 h-12" />
          </div>
          <div>
            <p className="text-xl font-medium">Adicionar Áudios</p>
            <p className="text-muted-foreground">
              Clique para selecionar arquivos de áudio
            </p>
          </div>
        </label>
      </motion.div>

      {/* Lista de arquivos selecionados */}
      {selectedFiles.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">
              Áudios Selecionados ({selectedFiles.length})
            </h2>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={previousFile}
                disabled={currentIndex === 0}
              >
                <SkipBack className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={nextFile}
                disabled={currentIndex === selectedFiles.length - 1}
              >
                <SkipForward className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Visualização do áudio atual */}
          <div className="flex flex-col items-center justify-center p-8 bg-accent rounded-lg w-full max-w-md mx-auto">
            <Volume2 className="w-16 h-16 text-orange-500 mb-4" />
            <p className="text-lg font-medium mb-2 text-center">
              {currentFile?.name}
            </p>
            <p className="text-sm text-muted-foreground mb-4">
              {(currentFile?.file.size / 1024 / 1024).toFixed(2)} MB
            </p>
            
            {/* Player HTML5 com controles nativos */}
            <audio 
              src={currentFile?.url} 
              controls
              className="w-full"
              onPlay={() => {
                setIsPlaying(true);
                handlePlayback(currentFile?.id, { isPlaying: true });
              }}
              onPause={() => {
                setIsPlaying(false);
                handlePlayback(currentFile?.id, { isPlaying: false });
              }}
              onEnded={() => {
                setIsPlaying(false);
                handlePlayback(currentFile?.id, { isPlaying: false, isCompleted: true });
              }}
            />

            {/* Status de reprodução */}
            {playbackStatus[currentFile?.id] && (
              <div className="mt-4 text-center">
                <Badge variant="secondary" className="mb-2">
                  {playbackStatus[currentFile?.id].isPlaying ? '🎵 Tocando' : '⏸️ Pausado'}
                </Badge>
                {playbackStatus[currentFile?.id].reproduzidaEm && (
                  <p className="text-xs text-muted-foreground">
                    Reproduzido às {playbackStatus[currentFile?.id].reproduzidaEm}
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Thumbnails dos áudios */}
          <div className="grid grid-cols-4 gap-3 max-h-40 overflow-y-auto">
            {selectedFiles.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className={`relative cursor-pointer rounded-lg border-2 transition-all ${
                  index === currentIndex
                    ? 'border-orange-500 bg-orange-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setCurrentIndex(index)}
              >
                <div className="w-full h-24 bg-accent flex items-center justify-center">
                  <Volume2 className="w-8 h-8 text-muted-foreground" />
                </div>
                <div className="p-2 text-center">
                  <p className="text-xs font-medium truncate">{item.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {(item.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                
                {/* Botão de remover */}
                <Button
                  variant="destructive"
                  size="sm"
                  className="absolute -top-2 -right-2 h-6 w-6 p-0 rounded-full"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(item.id);
                  }}
                >
                  <X className="w-3 h-3" />
                </Button>

                {/* Indicador de status */}
                {playbackStatus[item.id] && (
                  <div className="absolute top-1 left-1">
                    {playbackStatus[item.id].isCompleted ? (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : playbackStatus[item.id].isPlaying ? (
                      <Play className="w-4 h-4 text-blue-500" />
                    ) : (
                      <Pause className="w-4 h-4 text-gray-500" />
                    )}
                  </div>
                )}
              </motion.div>
            ))}
          </div>

          {/* Estatísticas */}
          <div className="bg-accent rounded-lg p-4">
            <h3 className="font-medium mb-2">Estatísticas de Reprodução</h3>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Total de arquivos</p>
                <p className="font-medium">{selectedFiles.length}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Reproduzidos</p>
                <p className="font-medium">
                  {Object.values(playbackStatus).filter(s => s.isCompleted).length}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Em reprodução</p>
                <p className="font-medium">
                  {Object.values(playbackStatus).filter(s => s.isPlaying).length}
                </p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Instruções */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-blue-50 border border-blue-200 rounded-lg p-4"
      >
        <h3 className="font-medium text-blue-800 mb-2">Como usar:</h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Clique em "Adicionar Áudios" para selecionar arquivos de áudio</li>
          <li>• Use os controles de navegação para alternar entre áudios</li>
          <li>• O player HTML5 permite reproduzir, pausar e controlar o volume</li>
          <li>• Clique nos thumbnails para selecionar um áudio específico</li>
          <li>• Use o botão X para remover arquivos indesejados</li>
          <li>• O sistema rastreia o status de reprodução de cada áudio</li>
        </ul>
      </motion.div>
    </div>
  );
};

export default AudioSystemDemo; 