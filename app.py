from flask import Flask, request, jsonify
import speech_recognition as sr
from pydub import AudioSegment
import os

app = Flask(__name__)

# Configuração para onde os arquivos de áudio serão salvos de forma temporária
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return "Bem-vindo ao serviço de transcrição de áudio!"

@app.route('/transcrever', methods=['POST'])
def transcreverAudio():
    print(f"Requisição recebida. Método: {request.method}")
    print(f"Cabeçalhos da Requisição: {request.headers}")
    print(f"Arquivos na Requisição (request.files): {request.files}")

    if 'arquivo_audio' not in request.files:
        print("Erro: 'arquivo_audio' não encontrado em request.files.") # Debug
        return jsonify({'error': 'Nenhum arquivo de áudio enviado.'}), 400
    
    arquivo_audio = request.files['arquivo_audio']
    if arquivo_audio.filename == '':
        print("Erro: Nome do arquivo vazio.") # Debug
        return jsonify({'error': 'Nome do arquivo inválido.'}), 400
    
    if arquivo_audio:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], arquivo_audio.filename)
        arquivo_audio.save(filepath)
        print(f"Arquivo '{arquivo_audio.filename}' salvo em '{filepath}'") # Debug

        recognizer = sr.Recognizer()
        transcribed_text = ""

        # Caminho para o arquivo WAV temporário
        wav_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_audio.wav')

        try:
            print(f"Tentando converter {filepath} para WAV em {wav_filepath}") # Debug
            audio = AudioSegment.from_file(filepath)
            audio.export(wav_filepath, format='wav')
            print("Conversão para WAV bem-sucedida.") # Debug

            with sr.AudioFile(wav_filepath) as source:
                print("Lendo dados de áudio para reconhecimento.") # Debug
                audio_data = recognizer.record(source)
                print("Dados de áudio lidos. Enviando para o Google Speech Recognition.") # Debug
                transcribed_text = recognizer.recognize_google(audio_data, language='pt-BR')
                print(f"Transcrição recebida: '{transcribed_text}'") # Debug

            # Limpa os arquivos temporários
            os.remove(filepath)
            os.remove(wav_filepath)
            print("Arquivos temporários removidos.") # Debug

            return jsonify({'transcription': transcribed_text}), 200
        
        except sr.UnknownValueError:
            print("Erro: sr.UnknownValueError - Não foi possível entender o áudio.") # Debug
            if os.path.exists(filepath): os.remove(filepath)
            if os.path.exists(wav_filepath): os.remove(wav_filepath)
            return jsonify({'error': 'Não foi possível entender o áudio.'}), 400
        
        except sr.RequestError as e:
            print(f"Erro: sr.RequestError - {e}") # Debug
            if os.path.exists(filepath): os.remove(filepath)
            if os.path.exists(wav_filepath): os.remove(wav_filepath)
            return jsonify({'error': f'Erro de serviço: {e}'}), 500
        
        except Exception as e:
            print(f"Erro: Exception inesperada - {e}") # Debug
            if os.path.exists(filepath): os.remove(filepath)
            if os.path.exists(wav_filepath): os.remove(wav_filepath)
            return jsonify({'error': f'Ocorreu um erro inesperado: {e}'}), 500

if __name__ == '__main__': 
    app.run(debug=True)