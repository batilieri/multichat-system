#!/usr/bin/env python3
"""
🔍 MONITOR WEBHOOK TEMPO REAL
Monitora webhooks em tempo real para verificar se download automático está funcionando
"""

import os
import sys
import django
import time
from datetime import datetime, timedelta
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

from webhook.models import WebhookEvent

class MonitorWebhookTempoReal:
    def __init__(self):
        self.ultimo_webhook_verificado = None
        self.arquivos_conhecidos = set()
        self.inicializar_estado()
    
    def inicializar_estado(self):
        """Inicializa o estado atual do monitor"""
        print("🔄 INICIALIZANDO MONITOR WEBHOOK TEMPO REAL")
        print("=" * 60)
        
        # Obter último webhook
        ultimo = WebhookEvent.objects.all().order_by('-timestamp').first()
        if ultimo:
            self.ultimo_webhook_verificado = ultimo.timestamp
            print(f"📅 Último webhook conhecido: {ultimo.timestamp}")
            print(f"🆔 Event ID: {ultimo.event_id}")
        else:
            print("❌ Nenhum webhook encontrado")
        
        # Mapear arquivos existentes
        media_path = Path("multichat_system/media_storage")
        if media_path.exists():
            for arquivo in media_path.rglob("*.mp3"):
                self.arquivos_conhecidos.add(str(arquivo))
            print(f"📁 Arquivos existentes mapeados: {len(self.arquivos_conhecidos)}")
        
        print("✅ Monitor inicializado! Aguardando novos webhooks...")
    
    def verificar_novos_webhooks(self):
        """Verifica se há novos webhooks desde a última verificação"""
        if not self.ultimo_webhook_verificado:
            return []
        
        novos_webhooks = WebhookEvent.objects.filter(
            timestamp__gt=self.ultimo_webhook_verificado
        ).order_by('timestamp')
        
        if novos_webhooks.exists():
            # Atualizar último webhook verificado
            self.ultimo_webhook_verificado = novos_webhooks.last().timestamp
        
        return list(novos_webhooks)
    
    def verificar_novos_arquivos(self):
        """Verifica se há novos arquivos de mídia"""
        novos_arquivos = []
        
        media_path = Path("multichat_system/media_storage")
        if media_path.exists():
            for arquivo in media_path.rglob("*.mp3"):
                if str(arquivo) not in self.arquivos_conhecidos:
                    novos_arquivos.append(arquivo)
                    self.arquivos_conhecidos.add(str(arquivo))
        
        return novos_arquivos
    
    def analisar_webhook(self, webhook):
        """Analisa um webhook específico"""
        try:
            data = webhook.raw_data
            msg_content = data.get('msgContent', {})
            
            tem_audio = 'audioMessage' in msg_content
            tem_imagem = 'imageMessage' in msg_content
            tem_video = 'videoMessage' in msg_content
            tem_documento = 'documentMessage' in msg_content
            
            tipos_midia = []
            if tem_audio: tipos_midia.append('🎵 audio')
            if tem_imagem: tipos_midia.append('🖼️ imagem')
            if tem_video: tipos_midia.append('🎬 video')
            if tem_documento: tipos_midia.append('📄 documento')
            
            return {
                'tem_midia': bool(tipos_midia),
                'tipos': tipos_midia,
                'message_id': data.get('messageId', 'N/A'),
                'from_me': data.get('fromMe', False),
                'event_type': webhook.event_type,
                'processed': webhook.processed
            }
        
        except Exception as e:
            return {
                'tem_midia': False,
                'tipos': [],
                'erro': str(e)
            }
    
    def monitorar_tempo_real(self, duracao_segundos=300):
        """Monitora webhooks em tempo real por X segundos"""
        print(f"\n🚀 INICIANDO MONITORAMENTO EM TEMPO REAL")
        print(f"⏱️ Duração: {duracao_segundos} segundos")
        print("📱 Envie um áudio pelo WhatsApp agora!")
        print("=" * 60)
        
        inicio = datetime.now()
        ultimo_relatorio = inicio
        
        while (datetime.now() - inicio).seconds < duracao_segundos:
            # Verificar novos webhooks
            novos_webhooks = self.verificar_novos_webhooks()
            
            # Verificar novos arquivos
            novos_arquivos = self.verificar_novos_arquivos()
            
            # Processar novos webhooks
            for webhook in novos_webhooks:
                analise = self.analisar_webhook(webhook)
                
                print(f"\n🆕 NOVO WEBHOOK: {webhook.timestamp}")
                print(f"   🆔 ID: {webhook.event_id}")
                print(f"   👤 Cliente: {webhook.cliente.nome}")
                print(f"   📧 Message ID: {analise.get('message_id', 'N/A')}")
                print(f"   📤 From Me: {analise.get('from_me', False)}")
                print(f"   🏷️ Event Type: {analise.get('event_type', 'N/A')}")
                print(f"   ✅ Processed: {analise.get('processed', False)}")
                
                if analise['tem_midia']:
                    print(f"   📎 MÍDIA DETECTADA: {', '.join(analise['tipos'])}")
                    print(f"   🔄 AGUARDANDO DOWNLOAD AUTOMÁTICO...")
                else:
                    print(f"   💬 Mensagem de texto (sem mídia)")
            
            # Processar novos arquivos
            for arquivo in novos_arquivos:
                mod_time = datetime.fromtimestamp(arquivo.stat().st_mtime)
                tamanho = arquivo.stat().st_size
                
                print(f"\n📁 NOVO ARQUIVO BAIXADO:")
                print(f"   📄 Nome: {arquivo.name}")
                print(f"   📂 Pasta: {arquivo.parent}")
                print(f"   📏 Tamanho: {tamanho} bytes")
                print(f"   🕒 Criado: {mod_time}")
                print(f"   ✅ DOWNLOAD AUTOMÁTICO FUNCIONOU!")
            
            # Relatório periódico
            agora = datetime.now()
            if (agora - ultimo_relatorio).seconds >= 30:
                tempo_decorrido = (agora - inicio).seconds
                restante = duracao_segundos - tempo_decorrido
                print(f"\n⏱️ {tempo_decorrido}s decorridos, {restante}s restantes...")
                ultimo_relatorio = agora
            
            # Pequena pausa para não sobrecarregar
            time.sleep(2)
        
        # Relatório final
        self.gerar_relatorio_final(inicio)
    
    def gerar_relatorio_final(self, inicio):
        """Gera relatório final do monitoramento"""
        print(f"\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DO MONITORAMENTO")
        print("=" * 60)
        
        total_webhooks = WebhookEvent.objects.filter(
            timestamp__gte=inicio
        ).count()
        
        total_arquivos_novos = 0
        media_path = Path("multichat_system/media_storage")
        if media_path.exists():
            for arquivo in media_path.rglob("*.mp3"):
                mod_time = datetime.fromtimestamp(arquivo.stat().st_mtime)
                if mod_time >= inicio:
                    total_arquivos_novos += 1
        
        print(f"📈 Estatísticas do período:")
        print(f"   📨 Webhooks recebidos: {total_webhooks}")
        print(f"   📁 Arquivos baixados: {total_arquivos_novos}")
        
        if total_webhooks > 0 and total_arquivos_novos > 0:
            print(f"\n🎉 SUCESSO! Download automático está funcionando!")
        elif total_webhooks > 0 and total_arquivos_novos == 0:
            print(f"\n⚠️ Webhooks recebidos mas nenhum arquivo baixado")
            print(f"   🔧 Verificar se eram mensagens com mídia")
        else:
            print(f"\n📭 Nenhum webhook recebido durante o monitoramento")
            print(f"   💡 Envie uma mensagem de áudio pelo WhatsApp")
    
    def status_atual(self):
        """Mostra status atual do sistema"""
        print(f"\n📊 STATUS ATUAL DO SISTEMA")
        print("=" * 60)
        
        # Últimos webhooks
        ultimos = WebhookEvent.objects.all().order_by('-timestamp')[:5]
        print(f"📨 Últimos 5 webhooks:")
        for webhook in ultimos:
            print(f"   🕒 {webhook.timestamp} - {webhook.event_type} - {webhook.cliente.nome}")
        
        # Últimos arquivos
        media_path = Path("multichat_system/media_storage")
        arquivos_recentes = []
        
        if media_path.exists():
            for arquivo in media_path.rglob("*.mp3"):
                mod_time = datetime.fromtimestamp(arquivo.stat().st_mtime)
                arquivos_recentes.append((arquivo, mod_time))
        
        # Ordenar por data de modificação
        arquivos_recentes.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n📁 Últimos 5 arquivos baixados:")
        for arquivo, mod_time in arquivos_recentes[:5]:
            print(f"   🕒 {mod_time} - {arquivo.name}")

def main():
    """Função principal"""
    monitor = MonitorWebhookTempoReal()
    
    print("🔍 MONITOR WEBHOOK TEMPO REAL")
    print("=" * 80)
    print("OBJETIVO: Verificar se download automático funciona para novos áudios")
    print("=" * 80)
    
    # Mostrar status atual
    monitor.status_atual()
    
    # Perguntar se quer monitorar
    print(f"\n💡 INSTRUÇÕES:")
    print("1. Mantenha este script rodando")
    print("2. Envie um áudio pelo WhatsApp")
    print("3. Observe se aparece 'NOVO WEBHOOK' e 'NOVO ARQUIVO BAIXADO'")
    
    try:
        # Monitorar por 5 minutos
        monitor.monitorar_tempo_real(300)
    except KeyboardInterrupt:
        print(f"\n⏹️ Monitoramento interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante monitoramento: {e}")

if __name__ == "__main__":
    main() 