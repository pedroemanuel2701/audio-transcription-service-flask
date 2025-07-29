# audio-transcription-service-flask
Este é um projeto de backend em Python que oferece um serviço de transcrição de áudio para texto (Speech-to-Text) utilizando o microframework Flask e a biblioteca SpeechRecognition. Ele permite o upload de arquivos de áudio (como MP3, WAV, M4A) e retorna o texto transcrito.
🚀 Funcionalidades

    Recebe arquivos de áudio via requisições POST.

    Converte automaticamente diversos formatos de áudio para WAV para processamento.

    Transcreve áudio para texto utilizando a API de reconhecimento de fala do Google (Web Speech API).

    Remove arquivos temporários após a transcrição.

    Tratamento de erros para áudios ininteligíveis ou problemas de serviço.

🛠️ Tecnologias Utilizadas

    Python 3.x

    Flask: Microframework web para Python.

    SpeechRecognition: Biblioteca Python para reconhecimento de fala, atuando como interface para diversas APIs de ASR.

    Pydub: Biblioteca Python para manipulação de áudio, utilizada para conversão de formatos.

    FFmpeg: Ferramenta externa essencial para a pydub lidar com diferentes formatos de áudio.

⚙️ Instalação e Configuração

Siga os passos abaixo para configurar e executar o projeto localmente.
1. Pré-requisitos

    Python 3.8+: Certifique-se de ter o Python instalado e configurado no seu PATH.

    FFmpeg: O pydub requer o FFmpeg instalado no seu sistema e acessível via PATH.

        Windows: Baixe a versão full ou essentials em formato .zip ou .7z de gyan.dev/ffmpeg/builds/ (ou BtbN). Descompacte a pasta bin em um local fixo (ex: C:\ffmpeg\bin) e adicione este caminho às variáveis de ambiente do sistema (Path). Lembre-se de reiniciar o terminal após adicionar ao PATH.

        macOS: brew install ffmpeg

        Linux: sudo apt-get install ffmpeg (Debian/Ubuntu)

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

pip install Flask SpeechRecognition pydub PyAudio ffmpeg-python

🚀 Como Usar
1. Iniciar o Servidor Flask

Com o ambiente virtual ativado e dentro da pasta raiz do projeto, execute:

python app.py

O servidor será iniciado e você verá uma mensagem indicando que ele está rodando em http://127.0.0.1:5000/. Mantenha este terminal aberto.
2. Testar a API de Transcrição

Você pode usar ferramentas como Postman ou curl para enviar arquivos de áudio para a API.

    Endpoint: http://127.0.0.1:5000/transcrever

    Método: POST

    Corpo da Requisição (Body): form-data

    Chave (Key): arquivo_audio

    Valor (Value): Selecione o arquivo de áudio (tipo File).

Exemplo com Postman

    Crie uma nova requisição POST.

    Defina a URL como http://127.0.0.1:5000/transcrever.

    Vá para a aba Body e selecione form-data.

    Adicione uma Key chamada arquivo_audio.

    Mude o tipo do Value para File e selecione seu arquivo de áudio (.mp3, .wav, .m4a, etc.).

    Clique em Send.

Exemplo com cURL

Abra um novo terminal e execute (substitua seu_audio.mp3 pelo caminho e nome do seu arquivo de áudio):

curl -X POST -F "arquivo_audio=@seu_audio.mp3" http://127.0.0.1:5000/transcrever

3. Resposta da API

A API retornará uma resposta JSON com o texto transcrito ou uma mensagem de erro:

Sucesso (Status 200 OK):

{
    "transcription": "Olá, isso é um teste de transcrição de áudio."
}

Erro (Status 400 Bad Request ou 500 Internal Server Error):

{
    "error": "Não foi possível entender o áudio."
}

ou

{
    "error": "Erro de serviço: [detalhes do erro]"
}

📄 API Endpoints

    GET /

        Descrição: Retorna uma mensagem de boas-vindas para verificar se o servidor está ativo.

        Resposta: Bem-vindo ao serviço de transcrição de áudio!

    POST /transcrever

        Descrição: Recebe um arquivo de áudio e retorna sua transcrição textual.

        Parâmetros da Requisição (form-data):

            arquivo_audio (File): O arquivo de áudio a ser transcrito.

        Respostas:

            200 OK: {"transcription": "texto transcrito"}

            400 Bad Request: {"error": "Nenhum arquivo de áudio enviado."} ou {"error": "Nome do arquivo inválido."} ou {"error": "Não foi possível entender o áudio."}

            500 Internal Server Error: {"error": "Erro de serviço: [detalhes]"} ou {"error": "Ocorreu um erro inesperado: [detalhes]"}

⚠️ Tratamento de Erros

O serviço inclui tratamento de erros para:

    sr.UnknownValueError: Quando a API de reconhecimento de fala não consegue entender o áudio.

    sr.RequestError: Problemas de comunicação com a API do Google (ex: sem internet, limites de requisição).

    Exception: Quaisquer outros erros inesperados durante o processamento.

Em caso de erro, os arquivos temporários são limpos e uma mensagem JSON com o erro é retornada.
📜 Licença

Este projeto está licenciado sob a Licença MIT. Veja o arquivo LICENSE para mais detalhes.
🤝 Contribuição

Contribuições são bem-vindas! Se você tiver sugestões, melhorias ou encontrar bugs, sinta-se à vontade para abrir uma issue ou enviar um pull request.
📞 Contato

Para dúvidas ou sugestões, entre em contato:

    Pedro Emanuel

    GitHub: pedroemanuel2701
