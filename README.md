# Запуск
## Запуск проекта локально
```shell
    docker compose up -d
```

```shell
    uvicorn app.main:app
```

## Запуск проекта на проде
```shell
    docker compose -f compose-prod.yml up -d
```

## Подготовка dev окружения
- Перед тем как запускать проект нужно создать .env file из
.env-example (там прописаны значения по умолчанию для локальной разработки)
- Создать python venv и активировать его
```shell
   python -m venv .venv
```
- Установить зависимости
```shell
    pip install -r requirements.txt
```
- Запустить dev compose
- Запустить uvicorn

Dev версия сайта доступна по адресу:
http://localhost:8000


ДЛЯ ПРОДАКШНА!!!
Переставить database host в переменных окружения на db (адрес сервиса в докер сети).