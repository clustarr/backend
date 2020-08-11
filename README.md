# clustarr-backend

## Usage
Adjust the volumes of the celery and flask service inside the file `docker-compose.yml`.

### development
To enable live reload during development and enable flask debugging, run the following command.
```console
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### production
The production mode uses gunicorn to run the flask app.
```console
docker-compose up
```
