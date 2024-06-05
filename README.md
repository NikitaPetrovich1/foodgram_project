# Foodgram_project_react

## Назначение

Проект создан для размещения размещения различных рецептов пользователями. Позволяет добавлять рецепты в избранное, подписываться на других пользователей, создавать свои рецепты и даже скачивать список необходимых покупок для приготовления по рецепту.

## Стек проекта

- Языки программирования
    - *Backend* [Python 3.11.7](https://www.python.org/downloads/release/python-3117/)
    - *Frontend* [NodeJS 13.12](https://nodejs.org/en/blog/release/v13.12.0)

- Фреймворки
    - [Django 4.2.11](https://docs.djangoproject.com/en/5.0/releases/4.2.11/)
    - [DRF 3.14](https://www.django-rest-framework.org/community/3.14-announcement/)
    - [React 17.0.1](https://github.com/facebook/react/blob/main/CHANGELOG.md#1701-october-22-2020)

- СУБД
    - [PostgreSQL 16](https://www.postgresql.org/about/news/postgresql-16-released-2715/)



## Как запустить проект локально:

Клонировать репозиторий:

```
git clone git@github.com:NikitaPetrovich1/foodgram_project
```

Перейти в него в командной строке:

```
cd foodgram-project-react
```

Обязательно создать файл `.env` и указать секреты. 
Если работа ведется в терминале, то сделать это можно через командую строку, например, через `nano`:

```
nano .env
```
Если работа ведется через IDE, то можно внести изменения как в самом файле `.env`, так и в файле `settings.py`, который находится в папке `./backend/foodgram_backend/`.

Запустить сборку проекта Через docker compose можно через команду:

```
docker compose up
```

Если запуск не происходит по причине недостаточности прав, то в начале команды нужно добавить `sudo` (при наличии такого доступа).

## Ссылки
- Локальные эндпоинты проекта:
    - [Главная страница](http://localhost:8000/)
    - [Админ-зона](http://localhost:8000/admin/)
    - [API](http://localhost:8000/api/)
