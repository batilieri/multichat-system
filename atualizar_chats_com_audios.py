#!/usr/bin/env python3
"""
🎵 ATUALIZADOR AUTOMÁTICO DE CHATS COM ÁUDIOS
Mapeia automaticamente áudios já baixados com chats existentes
"""

import os
import sys
import django
from pathlib import Path
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multichat_system.multichat.settings')
sys.path.append('multichat_system')
django.setup()

def analisar_estrutura_audios():
    """Analisa a estrutura de áudios armazenados"""
    print("🔍 ANALISANDO ESTRUTURA DE ÁUDIOS")
    print("=" * 60)
    
    base_path = Path("multichat_system/media_storage/Elizeu_Batiliere_Dos_Santos/instance_3B6XIW-ZTS923-GEAY6V/chats")
    
    if not base_path.exists():
        print("❌ Diretório base não encontrado")
        return {}
    
    estrutura_audios = {}
    
    # Percorrer todos os chats
    for chat_dir in base_path.iterdir():
        if chat_dir.is_dir():
            chat_id = chat_dir.name
            audio_dir = chat_dir / "audio"
            
            if audio_dir.exists():
                audio_files = list(audio_dir.glob("*.ogg")) + list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.m4a"))
                
                if audio_files:
                    estrutura_audios[chat_id] = {
                        'path': str(audio_dir),
                        'files': []
                    }
                    
                    for audio_file in audio_files:
                        file_info = {
                            'name': audio_file.name,
                            'size': audio_file.stat().st_size,
                            'modified': datetime.fromtimestamp(audio_file.stat().st_mtime),
                            'full_path': str(audio_file)
                        }
                        
                        # Extrair informações do nome do arquivo
                        if "msg_" in audio_file.name:
                            parts = audio_file.name.replace(".ogg", "").replace(".mp3", "").replace(".m4a", "").split("_")
                            if len(parts) >= 3:
                                file_info['hash'] = parts[1]
                                file_info['timestamp'] = parts[2]
                        
                        estrutura_audios[chat_id]['files'].append(file_info)
                        
                        print(f"   📁 Chat {chat_id}: {audio_file.name} ({file_info['size']} bytes)")
    
    print(f"\n✅ Total de chats com áudios: {len(estrutura_audios)}")
    return estrutura_audios

def buscar_chats_existentes():
    """Busca chats existentes no banco de dados"""
    print("\n📱 BUSCANDO CHATS EXISTENTES NO BANCO")
    print("=" * 60)
    
    from core.models import Chat
    
    chats = Chat.objects.all()
    print(f"✅ {chats.count()} chats encontrados no banco")
    
    chats_info = {}
    for chat in chats:
        # Contar mensagens de áudio manualmente
        mensagens_audio_count = chat.mensagens.filter(tipo='audio').count()
        
        chats_info[chat.chat_id] = {
            'id': chat.id,
            'chat_name': chat.chat_name,
            'cliente': chat.cliente.nome,
            'mensagens_count': chat.mensagens.count(),
            'mensagens_audio': mensagens_audio_count
        }
        
        print(f"   📱 Chat {chat.chat_id}: {chat.chat_name or 'Sem nome'} ({mensagens_audio_count} áudios)")
    
    return chats_info

def mapear_audios_com_chats(estrutura_audios, chats_info):
    """Mapeia áudios com chats baseado em diferentes estratégias"""
    print("\n🔗 MAPEANDO ÁUDIOS COM CHATS")
    print("=" * 60)
    
    mapeamentos = {}
    
    for chat_id, audio_info in estrutura_audios.items():
        print(f"\n🔍 Analisando chat {chat_id}:")
        
        if chat_id in chats_info:
            chat_db = chats_info[chat_id]
            print(f"   ✅ Chat encontrado no banco: {chat_db['chat_name'] or chat_id}")
            print(f"   📊 Mensagens: {chat_db['mensagens_count']} total, {chat_db['mensagens_audio']} áudios")
            
            # Estratégia 1: Buscar mensagens de áudio existentes
            from core.models import Mensagem
            mensagens_audio = Mensagem.objects.filter(chat__chat_id=chat_id, tipo='audio')
            
            if mensagens_audio.exists():
                print(f"   🎵 {mensagens_audio.count()} mensagens de áudio encontradas")
                
                # Mapear arquivos com mensagens baseado em timestamp
                for audio_file in audio_info['files']:
                    if 'timestamp' in audio_file:
                        # Buscar mensagem com timestamp próximo
                        file_date = audio_file['modified'].date()
                        
                        # Buscar mensagens do mesmo dia
                        mensagens_mesmo_dia = mensagens_audio.filter(
                            data_envio__date=file_date
                        )
                        
                        if mensagens_mesmo_dia.exists():
                            # Usar a mensagem mais próxima do timestamp do arquivo
                            # Converter para timezone-aware se necessário
                            from django.utils import timezone
                            
                            def get_timestamp_diff(mensagem):
                                msg_time = mensagem.data_envio
                                if timezone.is_naive(msg_time):
                                    msg_time = timezone.make_aware(msg_time)
                                
                                file_time = audio_file['modified']
                                if timezone.is_naive(file_time):
                                    file_time = timezone.make_aware(file_time)
                                
                                return abs((msg_time - file_time).total_seconds())
                            
                            mensagem_mais_proxima = min(
                                mensagens_mesmo_dia,
                                key=get_timestamp_diff
                            )
                            
                            mapeamentos[audio_file['full_path']] = {
                                'chat_id': chat_id,
                                'mensagem_id': mensagem_mais_proxima.id,
                                'message_id': mensagem_mais_proxima.message_id,
                                'timestamp_mensagem': mensagem_mais_proxima.data_envio,
                                'timestamp_arquivo': audio_file['modified'],
                                'estrategia': 'timestamp_proximo'
                            }
                            
                            print(f"      🎯 Arquivo {audio_file['name']} → Mensagem ID {mensagem_mais_proxima.id}")
                        else:
                            print(f"      ⚠️ Arquivo {audio_file['name']}: nenhuma mensagem do mesmo dia")
            else:
                print(f"   ⚠️ Nenhuma mensagem de áudio encontrada para este chat")
                
                # Estratégia 2: Criar mensagem de áudio para arquivo não mapeado
                for audio_file in audio_info['files']:
                    print(f"      🔄 Criando mensagem para arquivo {audio_file['name']}")
                    
                    # Criar mensagem de áudio
                    nova_mensagem = Mensagem.objects.create(
                        chat_id=chat_db['id'],
                        remetente="Sistema",
                        conteudo=json.dumps({
                            "audioMessage": {
                                "url": f"/media/whatsapp_media/{chat_id}/audio/{audio_file['name']}",
                                "fileName": audio_file['name'],
                                "fileSize": audio_file['size'],
                                "timestamp": audio_file['modified'].isoformat(),
                                "mimetype": "audio/ogg" if audio_file['name'].endswith('.ogg') else "audio/mpeg"
                            }
                        }),
                        tipo='audio',
                        lida=False,
                        from_me=False,
                        message_id=f"auto_{audio_file['hash']}_{int(audio_file['modified'].timestamp())}",
                        data_envio=audio_file['modified']
                    )
                    
                    mapeamentos[audio_file['full_path']] = {
                        'chat_id': chat_id,
                        'mensagem_id': nova_mensagem.id,
                        'message_id': nova_mensagem.message_id,
                        'timestamp_mensagem': nova_mensagem.data_envio,
                        'timestamp_arquivo': audio_file['modified'],
                        'estrategia': 'criada_automaticamente'
                    }
                    
                    print(f"         ✅ Mensagem criada: ID {nova_mensagem.id}")
        else:
            print(f"   ❌ Chat {chat_id} não encontrado no banco")
    
    return mapeamentos

def atualizar_urls_midias(mapeamentos):
    """Atualiza URLs de mídia nas mensagens existentes"""
    print("\n🔗 ATUALIZANDO URLS DE MÍDIA")
    print("=" * 60)
    
    from core.models import Mensagem
    
    atualizacoes = 0
    
    for arquivo_path, mapeamento in mapeamentos.items():
        try:
            mensagem = Mensagem.objects.get(id=mapeamento['mensagem_id'])
            
            # Verificar se já tem URL de mídia
            if not mensagem.conteudo or not mensagem.conteudo.startswith('{'):
                continue
            
            try:
                conteudo_json = json.loads(mensagem.conteudo)
            except json.JSONDecodeError:
                continue
            
            # Atualizar ou adicionar URL de mídia
            if 'audioMessage' in conteudo_json:
                audio_message = conteudo_json['audioMessage']
                
                # Adicionar URL local se não existir
                if 'localPath' not in audio_message:
                    audio_message['localPath'] = arquivo_path
                    audio_message['localUrl'] = f"/api/audio/hash-mapping/{mensagem.id}/"
                    
                    # Atualizar mensagem
                    mensagem.conteudo = json.dumps(conteudo_json, ensure_ascii=False)
                    mensagem.save()
                    
                    atualizacoes += 1
                    print(f"   ✅ Mensagem {mensagem.id} atualizada com URL local")
            
        except Mensagem.DoesNotExist:
            print(f"   ❌ Mensagem {mapeamento['mensagem_id']} não encontrada")
        except Exception as e:
            print(f"   ❌ Erro ao atualizar mensagem {mapeamento['mensagem_id']}: {e}")
    
    print(f"\n✅ Total de mensagens atualizadas: {atualizacoes}")
    return atualizacoes

def criar_relatorio_final(estrutura_audios, chats_info, mapeamentos):
    """Cria relatório final da operação"""
    print("\n📊 RELATÓRIO FINAL")
    print("=" * 80)
    
    total_arquivos = sum(len(info['files']) for info in estrutura_audios.values())
    total_mapeados = len(mapeamentos)
    
    print(f"📁 TOTAL DE ARQUIVOS DE ÁUDIO: {total_arquivos}")
    print(f"🔗 TOTAL MAPEADO: {total_mapeados}")
    print(f"📱 CHATS COM ÁUDIOS: {len(estrutura_audios)}")
    print(f"💾 CHATS NO BANCO: {len(chats_info)}")
    
    print(f"\n🎯 ESTRATÉGIAS UTILIZADAS:")
    estrategias = {}
    for mapeamento in mapeamentos.values():
        estrategia = mapeamento['estrategia']
        estrategias[estrategia] = estrategias.get(estrategia, 0) + 1
    
    for estrategia, count in estrategias.items():
        print(f"   - {estrategia}: {count} arquivos")
    
    print(f"\n📋 CHATS ATUALIZADOS:")
    for chat_id, audio_info in estrutura_audios.items():
        arquivos_chat = len(audio_info['files'])
        mapeados_chat = len([m for m in mapeamentos.values() if m['chat_id'] == chat_id])
        
        print(f"   - Chat {chat_id}: {arquivos_chat} arquivos, {mapeados_chat} mapeados")
    
    return {
        'total_arquivos': total_arquivos,
        'total_mapeados': total_mapeados,
        'chats_com_audios': len(estrutura_audios),
        'chats_no_banco': len(chats_info),
        'estrategias': estrategias
    }

def main():
    """Função principal"""
    print("🎵 ATUALIZADOR AUTOMÁTICO DE CHATS COM ÁUDIOS")
    print("=" * 80)
    print("Mapeia automaticamente áudios já baixados com chats existentes")
    print("=" * 80)
    
    # 1. Analisar estrutura de áudios
    estrutura_audios = analisar_estrutura_audios()
    if not estrutura_audios:
        print("❌ Nenhum áudio encontrado para processar")
        return
    
    # 2. Buscar chats existentes
    chats_info = buscar_chats_existentes()
    
    # 3. Mapear áudios com chats
    mapeamentos = mapear_audios_com_chats(estrutura_audios, chats_info)
    
    # 4. Atualizar URLs de mídia
    atualizacoes = atualizar_urls_midias(mapeamentos)
    
    # 5. Relatório final
    relatorio = criar_relatorio_final(estrutura_audios, chats_info, mapeamentos)
    
    print("\n" + "=" * 80)
    print("🚀 OPERAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 80)
    
    print(f"✅ {relatorio['total_mapeados']}/{relatorio['total_arquivos']} arquivos mapeados")
    print(f"✅ {relatorio['chats_com_audios']} chats atualizados com áudios")
    print(f"✅ {atualizacoes} mensagens atualizadas com URLs locais")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. 🔄 Reiniciar servidor Django")
    print("2. 🌐 Testar frontend - áudios devem aparecer automaticamente")
    print("3. 🔍 Verificar logs para confirmar funcionamento")
    print("4. 📱 Testar reprodução de áudios nos chats")

if __name__ == "__main__":
    main() 