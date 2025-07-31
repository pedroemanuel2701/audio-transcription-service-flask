# audio-transcription-service-flask
Este é um projeto de backend em Python que oferece um serviço de transcrição de áudio para texto (Speech-to-Text) utilizando o microframework Flask e a biblioteca SpeechRecognition. A principal melhoria desta versão é a implementação de processamento assíncrono para lidar com áudios longos sem bloquear o servidor, utilizando Celery como fila de tarefas e Redis como broker/backend.
🚀 Funcionalidades

    Recebe arquivos de áudio via requisições POST.

    Processamento Assíncrono: Descarrega a tarefa de transcrição para workers Celery, respondendo imediatamente ao cliente.

    Consulta de Status: Permite que o cliente verifique o progresso e o resultado da transcrição através de um ID de tarefa.

    Suporte a Múltiplos Formatos de Áudio/Vídeo: Converte automaticamente diversos formatos de áudio (e extrai áudio de vídeo) para WAV para processamento, incluindo .wav, .mp3, .m4a, .ogg, .mp4, .flac, .aiff, .webm.

    Transcreve áudio para texto utilizando a API de reconhecimento de fala do Google (Web Speech API).

    Remove arquivos temporários após a transcrição.

    Tratamento de erros robusto para áudios ininteligíveis ou problemas de serviço, com mensagens de erro detalhadas.

    Logs detalhados para depuração e monitoramento (salvos em app.log e exibidos no console).

🛠️ Tecnologias Utilizadas

    Python 3.8+

    Flask: Microframework web para Python.

    Celery: Sistema de fila de tarefas para processamento assíncrono.

    Redis: Banco de dados em memória, utilizado como broker de mensagens e backend de resultados para o Celery.

    SpeechRecognition: Biblioteca Python para reconhecimento de fala, atuando como interface para diversas APIs de ASR.

    Pydub: Biblioteca Python para manipulação de áudio, utilizada para conversão de formatos.

    FFmpeg: Ferramenta externa essencial para a pydub lidar com diferentes formatos de áudio/vídeo.

    Greenlet (via eventlet): Biblioteca de concorrência utilizada pelo Celery worker no Windows, com o pool threads para estabilidade.

⚙️ Instalação e Configuração

Siga os passos abaixo para configurar e executar o projeto localmente.
1. Pré-requisitos

    Python 3.8+: Certifique-se de ter o Python instalado e configurado no seu PATH.

    FFmpeg: O pydub requer o FFmpeg instalado no seu sistema e acessível via PATH.

        Windows: Baixe a versão full ou essentials em formato .zip ou .7z de gyan.dev/ffmpeg/builds/. Descompacte a pasta bin em um local fixo (ex: C:\ffmpeg\bin) e adicione este caminho às variáveis de ambiente do sistema (Path). Lembre-se de reiniciar o terminal após adicionar ao PATH.

        macOS: brew install ffmpeg

        Linux: sudo apt-get install ffmpeg (Debian/Ubuntu)

    Redis Server: O Celery precisa de um servidor Redis rodando.

        Windows: Baixe o instalador .msi de github.com/microsoftarchive/redis/releases. Durante a instalação, marque as opções para "Add Redis to your PATH" e "Install Redis as a Windows Service" e mantenha a porta padrão 6379.

        macOS: brew install redis && brew services start redis

        Linux: sudo apt update && sudo apt install redis-server && sudo systemctl enable redis-server && sudo systemctl start redis-server

        Verificação: Abra um novo terminal e digite redis-cli ping. A resposta deve ser PONG.

2. Clonar o Repositório

Abra seu terminal e clone o repositório para o seu computador:

git clone https://github.com/pedroemanuel2701/audio-transcription-service-flask.git
cd audio-transcription-service-flask

3. Criar e Ativar o Ambiente Virtual

É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto:

python -m venv venv

Ative o ambiente virtual:

    Windows (Prompt de Comando/PowerShell):

    .\venv\Scripts\activate

    macOS/Linux/Git Bash:

    source venv/bin/activate

    Você verá (venv) no início da linha do seu terminal, indicando que o ambiente virtual está ativo.

4. Instalar Dependências Python

Com o ambiente virtual ativado, instale as bibliotecas Python necessárias:

pip install Flask SpeechRecognition pydub PyAudio ffmpeg-python celery redis eventlet

🚀 Como Usar (Fluxo Assíncrono)

Para usar o serviço, você precisará de dois terminais abertos simultaneamente (no VS Code, por exemplo): um para o servidor Flask e outro para o worker Celery.
1. Iniciar o Servidor Flask (Terminal 1)

Com o ambiente virtual ativado e dentro da pasta raiz do projeto, execute:

set FLASK_APP=tasks.py # Para Windows CMD/PowerShell
# export FLASK_APP=tasks.py # Para macOS/Linux/Git Bash
flask run --host=127.0.0.1 --port=5000 --debug

O servidor será iniciado e você verá uma mensagem indicando que ele está rodando em http://127.0.0.1:5000/. Mantenha este terminal aberto.
2. Iniciar o Celery Worker (Terminal 2)

Abra um novo terminal, ative o ambiente virtual (Passo 3) e execute o worker Celery.

# Navegue para a pasta do projeto e ative o ambiente virtual
cd audio-transcription-service-flask
.\venv\Scripts\activate # ou source venv/bin/activate para macOS/Linux/Git Bash

# Inicie o Celery Worker (usando --pool=threads para estabilidade no Windows)
python -m celery -A tasks.celery worker --loglevel=info --pool=threads

Mantenha este terminal aberto também. Você verá mensagens do Celery indicando que ele está pronto para receber tarefas.
3. Testar a API de Transcrição

Você pode usar ferramentas como Postman ou curl para enviar arquivos de áudio para a API.

    Endpoint de Início da Transcrição: http://127.0.0.1:5000/transcrever

    Método: POST

    Corpo da Requisição (Body): form-data

    Chave (Key): arquivo_audio

    Valor (Value): Selecione o arquivo de áudio (tipo File).

Exemplo de Fluxo com Postman

    Enviar Áudio (Requisição POST):

        Crie uma nova requisição POST para http://127.0.0.1:5000/transcrever.

        Vá para a aba Body, selecione form-data.

        Adicione a Key arquivo_audio, mude o tipo do Value para File e selecione seu arquivo de áudio.

        Clique em Send.

        Resposta (Status 202 Accepted): Você receberá imediatamente um id_tarefa e uma url_status.

        {
            "mensagem": "Transcrição iniciada. Consulte o status com o ID da tarefa.",
            "id_tarefa": "SEU_ID_DA_TAREFA_AQUI",
            "url_status": "http://127.0.0.1:5000/status/SEU_ID_DA_TAREFA_AQUI"
        }

        No terminal do Celery Worker, você verá mensagens indicando o recebimento e processamento da tarefa.

    Consultar Status da Transcrição (Requisição GET):

        Crie uma nova requisição GET.

        Defina a URL como a url_status que você recebeu (ex: http://127.0.0.1:5000/status/SEU_ID_DA_TAREFA_AQUI).

        Clique em Send repetidamente para ver o status mudar.

4. Respostas da API
Endpoint POST /transcrever

    Sucesso (Status 202 Accepted):

    {
        "mensagem": "...",
        "id_tarefa": "...",
        "url_status": "..."
    }

    Erro (Status 400 Bad Request):

    {
        "erro": "..."
    }

Endpoint GET /status/<task_id>

    Pendente ou Em Progresso (Status 200 OK):

    {
        "estado": "PENDING",
        "status": "Tarefa pendente ou não encontrada."
    }

    ou

    {
        "estado": "PROGRESS",
        "status": "Processando áudio..."
    }

    Concluído com Sucesso (Status 200 OK):

    {
        "estado": "SUCCESS",
        "resultado": {
            "status": "Concluído",
            "transcricao": "Seu texto transcrito aqui."
        }
    }

    Falha (Status 200 OK - erro retornado dentro do JSON):

    {
        "estado": "FAILURE",
        "status": "Tarefa falhou.",
        "erro": "Mensagem de erro detalhada da exceção."
    }

📄 API Endpoints

    GET /

        Descrição: Retorna uma mensagem de boas-vindas para verificar se o servidor está ativo.

        Resposta: Bem-vindo ao serviço de transcrição de áudio assíncrona!

    POST /transcrever

        Descrição: Inicia uma tarefa assíncrona para transcrever um arquivo de áudio.

        Parâmetros da Requisição (form-data):

            arquivo_audio (File): O arquivo de áudio a ser transcrito.

        Respostas:

            202 Accepted: {"mensagem": "...", "id_tarefa": "...", "url_status": "..."}

            400 Bad Request: {"erro": "..."}

    GET /status/<task_id>

        Descrição: Consulta o status e o resultado de uma tarefa de transcrição.

        Parâmetros de URL:

            task_id (string): O ID da tarefa retornado pelo endpoint /transcrever.

        Respostas:

            200 OK: {"estado": "PENDING"|"PROGRESS"|"SUCCESS"|"FAILURE", "status": "...", "resultado": {...}|"erro": "..."}

⚠️ Tratamento de Erros

O serviço inclui tratamento de erros para:

    sr.UnknownValueError: Quando a API de reconhecimento de fala não consegue entender o áudio.

    sr.RequestError: Problemas de comunicação com a API do Google (ex: sem internet, limites de requisição).

    Exception: Quaisquer outros erros inesperados durante o processamento.

Em caso de erro, os arquivos temporários são limpos e uma mensagem JSON com o erro é retornada no resultado da tarefa.
📜 Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para mais detalhes.
🤝 Contribuição

Contribuições são bem-vindas! Se você tiver sugestões, melhorias ou encontrar bugs, sinta-se à vontade para abrir uma issue ou enviar um pull request.
📞 Contato

Para dúvidas ou sugestões, entre em contato:

    Pedro Emanuel

    GitHub: pedroemanuel2701