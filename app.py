from flask import Flask, request, jsonify, url_for
import speech_recognition as sr
from pydub import AudioSegment
import os
from celery import Celery
from celery.result import AsyncResult

app = Flask(__name__)

# Configuração para onde os arquivos de áudio serão salvos de forma temporária
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6379/0' # Mude 'localhost' para '127.0.0.1'
app.config['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:6379/0' #

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    # Removido celery.conf.update(app.config) para evitar erro ImproperlyConfigured
    return celery

celery = make_celery(app)

@celery.task(bind=True)
def transcribe_audio_task(self, filepath):
    recognizer = sr.Recognizer()
    transcribed_text = ""
    wav_filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_audio_{self.request.id}.wav")

    try:
        self.update_state(state='PROGRESS', meta={'status': 'Processando áudio...'})

        audio = AudioSegment.from_file(filepath)
        audio.export(wav_filepath, format='wav')

        self.update_state(state='PROGRESS', meta={'status': 'Transcrevendo...'})

        with sr.AudioFile(wav_filepath) as source:
            audio_data = recognizer.record(source)
            transcribed_text = recognizer.recognize_google(audio_data, language='pt-BR')

        return {'status': 'Concluído', 'transcription': transcribed_text}

    except sr.UnknownValueError:
        return {'status': 'Erro', 'error': 'Não foi possível entender o áudio.'}
    except sr.RequestError as e:
        return {'status': 'Erro', 'error': f'Erro de serviço: {e}'}
    except Exception as e:
        return {'status': 'Erro', 'error': f'Ocorreu um erro inesperado: {e}'}
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
        if os.path.exists(wav_filepath):
            os.remove(wav_filepath)

@app.route('/')
def home():
    return "Bem-vindo ao serviço de transcrição de áudio assíncrona!"

@app.route('/transcrever', methods=['POST'])
def transcrever_audio_endpoint():
    if 'arquivo_audio' not in request.files:
        return jsonify({'error': 'Nenhum arquivo de áudio enviado.'}), 400
    
    arquivo_audio = request.files['arquivo_audio']
    if arquivo_audio.filename == '':
        return jsonify({'error': 'Nome do arquivo inválido.'}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], arquivo_audio.filename)
    arquivo_audio.save(filepath)

    task = transcribe_audio_task.delay(filepath)
    return jsonify({
        'message': 'Transcrição iniciada. Consulte o status com o ID da tarefa.',
        'task_id': task.id,
        'status_url': url_for('get_task_status', task_id=task.id, _external=True)
    }), 202

@app.route('/status/<task_id>')
def get_task_status(task_id):
    task = result.AsyncResult(task_id, app=celery)

    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Tarefa pendente ou não encontrada.'
        }
    elif task.state == 'PROGRESS':
        response = {
            'state': task.state,
            'status': task.info.get('status', 'Processando...')
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'result': task.info
        }
    elif task.state == 'FAILURE':
        response = {
            'state': task.state,
            'status': 'Tarefa falhou.',
            'error': str(task.info)
        }
    else:
        response = {
            'state': task.state,
            'status': 'Estado desconhecido.'
        }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)