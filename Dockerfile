FROM python:3.11-slim

WORKDIR /app

# Создаем не-root пользователя для безопасности
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Копируем только requirements.txt сначала для лучшего кеширования
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY app/ ./app/

# Создаем директорию для кэша и даем права
RUN mkdir -p /app/.pytest_cache && chown -R appuser:appuser /app

# Переключаемся на не-root пользователя
USER appuser

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
