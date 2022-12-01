# CrushOnU API
API para a utilizar no jogo da CrushOnU

## Requerimentos (Usando Linux)
- Python 3.10.4
- Postgres
- Conta na AWS
- Conta na Google
- Redis

## Instalação
- Clonar o repositório: ```git clone git@github.com:fernandogfleite/crushonu-api.git```
- Entrar no repositório: ```cd crushonu-api```
- Instalar a virtualenv: ```python -m venv venv```
- Ativar a virtualenv: ```source venv/bin/activate```
- Instalar as bibliotecas: ```pip install -r requirements.txt```
- Configurar a .env (use o arquivo .env-example como base)
- Rodar as migrations: ```python manage.py migrate```


## Rodar o projeto
- Para rodar execute o seguinte comando: ```python manage.py runserver```
- Para executar o celery execute o seguinte comando: ```celery -A crushonu worker -l INFO```
