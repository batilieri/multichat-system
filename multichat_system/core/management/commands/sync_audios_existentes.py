from django.core.management.base import BaseCommand
from django.utils import timezone
from pathlib import Path
import json
from core.models import Chat, Mensagem


class Command(BaseCommand):
    help = 'Sincroniza áudios já baixados com chats existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cliente-id',
            type=int,
            default=2,
            help='ID do cliente para sincronizar (padrão: 2)'
        )
        parser.add_argument(
            '--instance-id',
            type=str,
            default='3B6XIW-ZTS923-GEAY6V',
            help='ID da instância WhatsApp (padrão: 3B6XIW-ZTS923-GEAY6V)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem fazer alterações no banco'
        )

    def handle(self, *args, **options):
        cliente_id = options['cliente_id']
        instance_id = options['instance_id']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'🎵 SINCRONIZANDO ÁUDIOS EXISTENTES PARA CLIENTE {cliente_id}'
            )
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 MODO DRY-RUN: Nenhuma alteração será feita')
            )
        
        # Construir caminho base
        base_path = Path(__file__).parent.parent.parent.parent / "media_storage" / f"cliente_{cliente_id}" / f"instance_{instance_id}" / "chats"
        
        if not base_path.exists():
            self.stdout.write(
                self.style.ERROR(f'❌ Diretório não encontrado: {base_path}')
            )
            return
        
        # Analisar estrutura de áudios
        estrutura_audios = self.analisar_estrutura_audios(base_path)
        
        if not estrutura_audios:
            self.stdout.write(
                self.style.WARNING('⚠️ Nenhum áudio encontrado para sincronizar')
            )
            return
        
        # Buscar chats existentes
        chats_info = self.buscar_chats_existentes()
        
        # Mapear áudios com chats
        mapeamentos = self.mapear_audios_com_chats(estrutura_audios, chats_info)
        
        # Atualizar URLs de mídia
        if not dry_run:
            atualizacoes = self.atualizar_urls_midias(mapeamentos)
        else:
            atualizacoes = len([m for m in mapeamentos.values() if m['estrategia'] == 'timestamp_proximo'])
        
        # Relatório final
        self.criar_relatorio_final(estrutura_audios, chats_info, mapeamentos, atualizacoes, dry_run)

    def analisar_estrutura_audios(self, base_path):
        """Analisa a estrutura de áudios armazenados"""
        self.stdout.write('🔍 Analisando estrutura de áudios...')
        
        estrutura_audios = {}
        
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
                                'modified': timezone.make_aware(
                                    timezone.datetime.fromtimestamp(audio_file.stat().st_mtime)
                                ),
                                'full_path': str(audio_file)
                            }
                            
                            # Extrair informações do nome do arquivo
                            if "msg_" in audio_file.name:
                                parts = audio_file.name.replace(".ogg", "").replace(".mp3", "").replace(".m4a", "").split("_")
                                if len(parts) >= 3:
                                    file_info['hash'] = parts[1]
                                    file_info['timestamp'] = parts[2]
                            
                            estrutura_audios[chat_id]['files'].append(file_info)
                            
                            self.stdout.write(
                                f'   📁 Chat {chat_id}: {audio_file.name} ({file_info["size"]} bytes)'
                            )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Total de chats com áudios: {len(estrutura_audios)}')
        )
        return estrutura_audios

    def buscar_chats_existentes(self):
        """Busca chats existentes no banco de dados"""
        self.stdout.write('📱 Buscando chats existentes no banco...')
        
        chats = Chat.objects.all()
        self.stdout.write(f'✅ {chats.count()} chats encontrados no banco')
        
        chats_info = {}
        for chat in chats:
            mensagens_audio_count = chat.mensagens.filter(tipo='audio').count()
            
            chats_info[chat.chat_id] = {
                'id': chat.id,
                'chat_name': chat.chat_name,
                'cliente': chat.cliente.nome,
                'mensagens_count': chat.mensagens.count(),
                'mensagens_audio': mensagens_audio_count
            }
            
            self.stdout.write(
                f'   📱 Chat {chat.chat_id}: {chat.chat_name or "Sem nome"} ({mensagens_audio_count} áudios)'
            )
        
        return chats_info

    def mapear_audios_com_chats(self, estrutura_audios, chats_info):
        """Mapeia áudios com chats baseado em diferentes estratégias"""
        self.stdout.write('🔗 Mapeando áudios com chats...')
        
        mapeamentos = {}
        
        for chat_id, audio_info in estrutura_audios.items():
            self.stdout.write(f'\n🔍 Analisando chat {chat_id}:')
            
            if chat_id in chats_info:
                chat_db = chats_info[chat_id]
                self.stdout.write(
                    f'   ✅ Chat encontrado no banco: {chat_db["chat_name"] or chat_id}'
                )
                self.stdout.write(
                    f'   📊 Mensagens: {chat_db["mensagens_count"]} total, {chat_db["mensagens_audio"]} áudios'
                )
                
                # Buscar mensagens de áudio existentes
                mensagens_audio = Mensagem.objects.filter(chat__chat_id=chat_id, tipo='audio')
                
                if mensagens_audio.exists():
                    self.stdout.write(f'   🎵 {mensagens_audio.count()} mensagens de áudio encontradas')
                    
                    # Mapear arquivos com mensagens baseado em timestamp
                    for audio_file in audio_info['files']:
                        if 'timestamp' in audio_file:
                            # Buscar mensagens do mesmo dia
                            file_date = audio_file['modified'].date()
                            mensagens_mesmo_dia = mensagens_audio.filter(
                                data_envio__date=file_date
                            )
                            
                            if mensagens_mesmo_dia.exists():
                                # Usar a mensagem mais próxima do timestamp do arquivo
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
                                
                                self.stdout.write(
                                    f'      🎯 Arquivo {audio_file["name"]} → Mensagem ID {mensagem_mais_proxima.id}'
                                )
                            else:
                                self.stdout.write(
                                    f'      ⚠️ Arquivo {audio_file["name"]}: nenhuma mensagem do mesmo dia'
                                )
                else:
                    self.stdout.write(f'   ⚠️ Nenhuma mensagem de áudio encontrada para este chat')
            else:
                self.stdout.write(f'   ❌ Chat {chat_id} não encontrado no banco')
        
        return mapeamentos

    def atualizar_urls_midias(self, mapeamentos):
        """Atualiza URLs de mídia nas mensagens existentes"""
        self.stdout.write('🔗 Atualizando URLs de mídia...')
        
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
                        self.stdout.write(
                            f'   ✅ Mensagem {mensagem.id} atualizada com URL local'
                        )
                
            except Mensagem.DoesNotExist:
                self.stdout.write(
                    f'   ❌ Mensagem {mapeamento["mensagem_id"]} não encontrada'
                )
            except Exception as e:
                self.stdout.write(
                    f'   ❌ Erro ao atualizar mensagem {mapeamento["mensagem_id"]}: {e}'
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Total de mensagens atualizadas: {atualizacoes}')
        )
        return atualizacoes

    def criar_relatorio_final(self, estrutura_audios, chats_info, mapeamentos, atualizacoes, dry_run):
        """Cria relatório final da operação"""
        self.stdout.write('\n📊 RELATÓRIO FINAL')
        self.stdout.write('=' * 80)
        
        total_arquivos = sum(len(info['files']) for info in estrutura_audios.values())
        total_mapeados = len(mapeamentos)
        
        self.stdout.write(f'📁 TOTAL DE ARQUIVOS DE ÁUDIO: {total_arquivos}')
        self.stdout.write(f'🔗 TOTAL MAPEADO: {total_mapeados}')
        self.stdout.write(f'📱 CHATS COM ÁUDIOS: {len(estrutura_audios)}')
        self.stdout.write(f'💾 CHATS NO BANCO: {len(chats_info)}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'🔍 MODO DRY-RUN: {atualizacoes} mensagens seriam atualizadas')
            )
        else:
            self.stdout.write(f'✅ MENSAGENS ATUALIZADAS: {atualizacoes}')
        
        self.stdout.write(f'\n🎯 ESTRATÉGIAS UTILIZADAS:')
        estrategias = {}
        for mapeamento in mapeamentos.values():
            estrategia = mapeamento['estrategia']
            estrategias[estrategia] = estrategias.get(estrategia, 0) + 1
        
        for estrategia, count in estrategias.items():
            self.stdout.write(f'   - {estrategia}: {count} arquivos')
        
        self.stdout.write(f'\n📋 CHATS ATUALIZADOS:')
        for chat_id, audio_info in estrutura_audios.items():
            arquivos_chat = len(audio_info['files'])
            mapeados_chat = len([m for m in mapeamentos.values() if m['chat_id'] == chat_id])
            
            self.stdout.write(
                f'   - Chat {chat_id}: {arquivos_chat} arquivos, {mapeados_chat} mapeados'
            )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS('\n🚀 OPERAÇÃO CONCLUÍDA COM SUCESSO!')
            )
            self.stdout.write('=' * 80)
            self.stdout.write(f'✅ {total_mapeados}/{total_arquivos} arquivos mapeados')
            self.stdout.write(f'✅ {len(estrutura_audios)} chats atualizados com áudios')
            self.stdout.write(f'✅ {atualizacoes} mensagens atualizadas com URLs locais')
            
            self.stdout.write('\n💡 PRÓXIMOS PASSOS:')
            self.stdout.write('1. 🔄 Reiniciar servidor Django')
            self.stdout.write('2. 🌐 Testar frontend - áudios devem aparecer automaticamente')
            self.stdout.write('3. 🔍 Verificar logs para confirmar funcionamento')
            self.stdout.write('4. 📱 Testar reprodução de áudios nos chats')
        else:
            self.stdout.write(
                self.style.WARNING('\n🔍 DRY-RUN CONCLUÍDO - Nenhuma alteração foi feita')
            ) 