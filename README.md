# Foodgram - продуктовый помощник

## Описание проекта
Онлайн-сервис Foodgram («Продуктовый помощник») - сервис для публикции любимых рецептов. Пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в «Избранное», а также удобно скачивать список необходимых ингредиентов для приготовления желаемых блюд в формате .txt.


## Основные модули
- Recipes - модуль предостовляющий функционал для создания и редактирования рецептов, добавления(удаления) рецептов в(из) избранное(ого) и(или) в список покупок для формирования и возможности скачать список необходимых ингредиентов для приготовления блюд.
- Subscriptions - позволяет подписываться(отписываться) на(от) других пользователей для удобного отслеживания их опубликованных рецептов.

## Инструкция по загрузке и запуску проекта:
Клонируйте репозиторий:
```
git clone https://github.com/NikitaPetrovich1/foodgram-project-react
```
Создайте файл .env и заполните его необходимыми данными по примеру файла .env.example.

Замените строки "image:..." в файле docker-compose.production.yml в блоке backend на "build: ./backend/" и блоках frontend и gateway аналогично
Заустите docker на вашем устройстве и запустите файл docker-compose.production.yml командой:
```
docker compose -f docker-compose.production.yml up
```
Выполните миграции и загрузку необходимых данных из scv файлов командами:
```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
```
docker compose -f docker-compose.production.yml exec backend python manage.py load ingredients
```
```
docker compose -f docker-compose.production.yml exec backend python manage.py load tags
```
Соберите коллекцию бэкенд статики командой:
```
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```
