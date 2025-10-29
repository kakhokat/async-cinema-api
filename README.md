# 🎬 Async Cinema API

Асинхронный API для онлайн-кинотеатра, построенный на **FastAPI**, **PostgreSQL** и **Redis**.

## 📄 Техническое задание
[Ссылка на ТЗ](https://github.com/kakhokat/Async_API_sprint_1)  

## ⚙️ Стек технологий
- Python 3.12+
- FastAPI
- PostgreSQL
- Redis
- Docker / Docker Compose
- GitHub Actions

## 🚀 Установка и запуск
```bash
git clone git@github.com:kakhokat/async-cinema-api.git
cd async-cinema-api

Скопировать переменные окружения
cp .env.example .env

Запустить через Docker Compose
docker-compose up --build

Открыть API
http://localhost:8000/docs