#!/usr/bin/env python3
"""
🔍 MONITOR LOGS WEBHOOK
Monitora logs do webhook em tempo real
"""

import time
import os
from pathlib import Path
from datetime import datetime

def monitor_webhook_logs():
    """Monitora logs do webhook"""
    log_file = Path("webhook_debug.log")
    
    print("🔍 MONITOR LOGS WEBHOOK INICIADO")
    print("=" * 60)
    print("💡 Envie um áudio pelo WhatsApp agora!")
    print("🔍 Monitorando arquivo: webhook_debug.log")
    print("=" * 60)
    
    # Posição inicial do arquivo
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            f.seek(0, 2)  # Ir para o final
            last_position = f.tell()
    else:
        last_position = 0
        print("⚠️ Arquivo de log não existe ainda")
    
    try:
        while True:
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    f.seek(last_position)
                    new_lines = f.readlines()
                    last_position = f.tell()
                    
                    for line in new_lines:
                        line = line.strip()
                        if any(keyword in line for keyword in ['🔄', '📎', '✅', '❌', '🔍']):
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            print(f"[{timestamp}] {line}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Monitor interrompido")

if __name__ == "__main__":
    monitor_webhook_logs()
