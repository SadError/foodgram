# Foodgram - продуктовый помощник

Проект доступен по адресу: http://62.113.106.188/
Логин: admin2@bk.ru
Пароль: qwerty45

Cайт, на котором посетители могут публиковать рецепты, добавлять интересные рецепты в избранное и подписываться на публикации других авторов. Раздел «Список покупок» позволяет скачать список продуктов для приготовления выбранных блюд.

### Технологии
- React
- Python
- Django REST Framework
- Postgres
- Docker

### Установка
- Склонировать репозиторий
```commandline
git clone https://github.com/SadError/foodgram-project-react.git
```
- В директории infra переименовать файл env.example -> .env и изменить переменные окружения. 
- Для работы с проектом необходимо установить Docker и Docker-compose и выполнить команды для сборки контейнеров:

```commandline
cd infra
docker-compose up -d --build
```
- Внутри контейнера необходимо выполнить миграции, собрать статику приложения, при необходимости создать суперюзера:
```commandline
docker-compose exec <container_id> python manage.py makemigrations
docker-compose exec <container_id> python manage.py migrate
docker-compose exec <container_id> python manage.py createsuperuser
docker-compose exec <container_id> python manage.py collectstatic --no-input
```
### Документация
Документация доступна по адресу: http://62.113.106.188/api/docs/redoc/
