![Main Kittygram Workflow](https://github.com/MikeDzhin/foodgram-project-react/actions/workflows/main.yml/badge.svg)



# Социальная сеть "FOOTGRAM - продуктовый помощник"
## _Дипломная работа Яндекс Практикум_

## Проект доступен по адресу: https://footgram.servebeer.com
### Логин администратора: zipperpocket@gmail.com
### Пароль администратора: 29082023a

## Стек технологий:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
---

### Описание проекта
Онлайн сервис Foodgram создан для людей, которые постоянно задаются вопросом - "Что бы приготовить?".
С нашим продуктовым помощником такой вопрос больше никогда не встанет перед Вами!
На сайте представлено огромное количество готовых рецептов от людей для людей!
Делитесь рецептами с другими пользователями, подписывайтесь друг на друга, добавляйте рецепты в избранное, и что самое главное - Вам больше не надо писать на листочке список покупок в магазине! Foodgram сделает всё за вас! Достаточно добавить понравившиеся рецепты в список покупок и скачать его!
---
### __Архитектура проекта__
Проект разворачивается в Docker-контейнерах:
- Backend-приложение API ✨
- Frontend-контейнер ✨
- PostgreSQL База данных ✨
- Nginx-сервер ✨
---
### __Запуск проекта__

#### 1. Для начала надо клонировать проект к себе на компьютер и перейти в него в командной строке.

> git clone https://github.com/MikeDzhin/foodgram-project-react
#### 2. Создаем и активируем виртуальное окружение

> - python -m venv venv
> - source venv/scripts/activate
#### 3. Создаем файл .env c переменными окружения

> Необходимые переменные в файле .env:
> - POSTGRES_USER
> - POSTGRES_PASSWORD
> - POSTGRES_DB
> - DB_HOST
> - DB_PORT
> - SECRET_KEY

#### 4. Установить и запустить приложения в контейнерах (при этом надо находиться в директории infra)
> docker compose up --build

#### 5. Сделать миграции, создать суперпользователя, собрать статику и заполнить в Базе данных таблицу с ингредиентами
> - docker compose exec backend python manage.py migrate
> - docker compose exec backend python manage.py collectstatic --no-input
> - docker compose exec backend python manage.py jsontodb
