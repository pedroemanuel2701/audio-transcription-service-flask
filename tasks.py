from flask import Flask, request, jsonify, url_for  # Importando Flask e módulos necessários
import speech_recognition as sr                     # Importando o módulo de reconhecimento de fala
from pydub import AudioSegment                      # Importando o módulo para manipulação de áudio
import os                                           # Importando módulo para manipulação de arquivos e diretórios
from celery import Celery                           # Importando Celery para tarefas assíncronas 
from celery.result import AsyncResult               # Importando AsyncResult para verificar o status das tarefas
from celery.utils.log import get_logger             # Importando get_logger para logging do Celery
import logging                                      # Importando módulo de logging para registrar eventos

app = Flask(__name__)

# arquivos de áudio serão salvos de forma temporária
PASTA_UPLOADS = 'uploads'
if not os.path.exists(PASTA_UPLOADS): 
    os.makedirs(PASTA_UPLOADS)

app.config['UPLOAD_FOLDER'] = PASTA_UPLOADS
app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:6379/0'

# --- Configuração do Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
app.logger.info("Servidor Flask iniciando...")

logger_celery = get_logger(__name__)
logger_celery.setLevel(logging.INFO)

# --- Configuração do Celery ---
def criar_celery(aplicacao):
    celery = Celery(
        aplicacao.import_name,
        broker=aplicacao.config['CELERY_BROKER_URL'],
        backend=aplicacao.config['CELERY_RESULT_BACKEND']
    )
    # Não adicione handlers manualmente!
    # O logging.basicConfig já garante que todos os logs vão para o arquivo e console.
    return celery

celery = criar_celery(app)

# --- Tarefa Celery para Transcrição ---
@celery.task(bind=True)
def tarefa_transcrever_audio(self, caminho_arquivo):
    id_tarefa = self.request.id
    app.logger.info(f"[{id_tarefa}] Tarefa de transcrição iniciada para o arquivo: {caminho_arquivo}")

    reconhecedor = sr.Recognizer()
    texto_transcrito = ""
    caminho_wav = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_audio_{id_tarefa}.wav")

    try:
        self.update_state(state='PROGRESS', meta={'status': 'Processando áudio...'})
        app.logger.info(f"[{id_tarefa}] Processando áudio: {caminho_arquivo}")

        audio = AudioSegment.from_file(caminho_arquivo)
        audio.export(caminho_wav, format='wav')
        app.logger.info(f"[{id_tarefa}] Áudio convertido para WAV: {caminho_wav}")

        self.update_state(state='PROGRESS', meta={'status': 'Transcrevendo...'})
        app.logger.info(f"[{id_tarefa}] Iniciando reconhecimento de fala...")

        with sr.AudioFile(caminho_wav) as fonte:
            dados_audio = reconhecedor.record(fonte)
            texto_transcrito = reconhecedor.recognize_google(dados_audio, language='pt-BR')

        app.logger.info(f"[{id_tarefa}] Transcrição concluída: '{texto_transcrito}'")
        return {'status': 'Concluído', 'transcricao': texto_transcrito}

    except sr.UnknownValueError as erro:
        app.logger.warning(f"[{id_tarefa}] Erro de reconhecimento: Não foi possível entender o áudio. Detalhes: {erro}")
        raise ValueError('Não foi possível entender o áudio.') from erro
    except sr.RequestError as erro:
        app.logger.error(f"[{id_tarefa}] Erro de serviço com a API do Google: {erro}")
        raise RuntimeError(f'Erro de serviço da API do Google: {erro}') from erro
    except Exception as erro:
        app.logger.exception(f"[{id_tarefa}] Ocorreu um erro inesperado durante a transcrição.")
        raise RuntimeError(f'Ocorreu um erro inesperado: {erro}') from erro
    finally:
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
            app.logger.info(f"[{id_tarefa}] Arquivo original removido: {caminho_arquivo}")
        if os.path.exists(caminho_wav):
            os.remove(caminho_wav)
            app.logger.info(f"[{id_tarefa}] Arquivo WAV temporário removido: {caminho_wav}")

# --- Rotas do Flask ---
@app.route('/')
def pagina_inicial():
    app.logger.info("Requisição GET recebida na rota /")
    return "Bem-vindo ao serviço de transcrição de áudio assíncrona!"

@app.route('/transcrever', methods=['POST'])
def endpoint_transcrever_audio():
    app.logger.info("Requisição POST recebida na rota /transcrever")
    if 'arquivo_audio' not in request.files:
        app.logger.warning("Nenhum arquivo de áudio enviado na requisição.")
        return jsonify({'erro': 'Nenhum arquivo de áudio enviado.'}), 400

    arquivo_audio = request.files['arquivo_audio']
    if arquivo_audio.filename == '':
        app.logger.warning("Nome do arquivo de áudio inválido (vazio).")
        return jsonify({'erro': 'Nome do arquivo inválido.'}), 400

    if not arquivo_audio.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.ogg')):
        app.logger.warning(f"Formato de arquivo não suportado: {arquivo_audio.filename}")
        return jsonify({'erro': 'Formato de arquivo não suportado. Use .wav, .mp3, .m4a ou .ogg.'}), 400

    caminho_arquivo = os.path.join(app.config['UPLOAD_FOLDER'], arquivo_audio.filename)
    try:
        arquivo_audio.save(caminho_arquivo)
        app.logger.info(f"Arquivo '{arquivo_audio.filename}' salvo temporariamente em '{caminho_arquivo}'")
    except Exception as erro:
        app.logger.error(f"Erro ao salvar o arquivo: {erro}")
        return jsonify({'erro': f"Erro ao salvar o arquivo: {erro}"}), 500

    tarefa = tarefa_transcrever_audio.delay(caminho_arquivo)
    app.logger.info(f"Tarefa de transcrição enviada para o Celery. Task ID: {tarefa.id}")
    return jsonify({
        'mensagem': 'Transcrição iniciada. Consulte o status com o ID da tarefa.',
        'id_tarefa': tarefa.id,
        'url_status': url_for('obter_status_tarefa', task_id=tarefa.id, _external=True)
    }), 202

@app.route('/status/<task_id>')
def obter_status_tarefa(task_id):
    app.logger.info(f"Requisição GET recebida para status da tarefa: {task_id}")
    tarefa = AsyncResult(task_id, app=celery)

    resposta = {}
    if tarefa.state == 'PENDING':
        resposta = {
            'estado': tarefa.state,
            'status': 'Tarefa pendente ou não encontrada.'
        }
        app.logger.info(f"Status da tarefa {task_id}: PENDING")
    elif tarefa.state == 'PROGRESS':
        resposta = {
            'estado': tarefa.state,
            'status': tarefa.info.get('status', 'Processando...')
        }
        app.logger.info(f"Status da tarefa {task_id}: PROGRESS - {tarefa.info.get('status', 'Processando...')}")
    elif tarefa.state == 'SUCCESS':
        resposta = {
            'estado': tarefa.state,
            'resultado': tarefa.info
        }
        app.logger.info(f"Status da tarefa {task_id}: SUCCESS - Resultado: {tarefa.info}")
    elif tarefa.state == 'FAILURE':
        # Mostra a mensagem da exceção levantada na tarefa
        resposta = {
            'estado': tarefa.state,
            'status': 'Tarefa falhou.',
            'erro': str(tarefa.info)  # Agora mostra a mensagem específica do erro
        }
        app.logger.error(f"Status da tarefa {task_id}: FAILURE - Erro: {tarefa.info}")
    else:
        resposta = {
            'estado': tarefa.state,
            'status': 'Estado desconhecido.'
        }
        app.logger.warning(f"Status da tarefa {task_id}: Estado desconhecido - {tarefa.state}")

    return jsonify(resposta)

if __name__ == '__main__':
    app.run(debug=True)