# Проект команды 2 "Онлайн кинотатр"

Общая структура проекта "Онлайн кинотеатр"

**Модульная схема:**

![alt text](srs/attachements/image-2.png)

**Диаграма контейнеров приложения C2**

![alt text](srs/attachements/image-1.png)


## [Auth service - Sprint 6](srs/auth.md)

Пояснения по docker compose
- Порты остаются открытыми, поскольку данный docker compose предназначен для разработки, а не для продакшен среды
- postgres запускается на 30001 порту
- для nginx прокинут 82 порт 


## Запуск приложения

### Docker-compose

1. Выполнить команды:
```bash
dc up [--build] -d
```

### Локальный запуск

1. Активировать venv и создать .env по образцу
2. Установить зависимости

```bash
pip install --upgrade pip && pip install -r requirements.txt
```
3. Используйте docker-compose.yml 
Так же поднятие контейнеров с сервисами для локальной работы доступны через 

```bash
dc up [--build] -d auth_postgres auth_redis
```

4. Запуск приложения

```bash
cd src && python main.py
```

## Tests

### Локальный запуск

1. Выполнить команды:

```bash
cd tests/functional && make up-dev
```
2. Запустить командой:

```bash
pytest src
```

### Запуск в docker-compose

1. Выполнить команды:

```bash
cd tests/functional && make up
```


## Docs

Наш сервис поддерживает документацию OpenAPI Swagger по адресу:

http://127.0.0.1/api/openapi

## Состав команды

- TeamLead developer: [Maria Letunenko](https://github.com/mletunenko)


## Change log

- 2024-12-09: Создали базовую структуру проекта, документацию
- ...
- 2025-01-25: Социальная авторизация через Yandex OAuth 
- 2025-01-25: Подключение трассировки запросов с помощью Jaeger

## Связанные репозитории

Сервис выдачи контента
- https://github.com/mletunenko/Async_API_sprint_1_team

Сервис административной панели 
- https://github.com/mletunenko/new_admin_panel_sprint_3

Сервис авторизации
- https://github.com/mletunenko/Auth_sprint_1
