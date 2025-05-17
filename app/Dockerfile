# syntax=docker/dockerfile:1
# --------------------------
# Базовый слой
# --------------------------
FROM python:3.12-slim AS base

# ── Системные оптимизации ───────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ── Системные зависимости (необходимы для psycopg2-binary и cryptography) ─
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# --------------------------
# Установка зависимостей
# --------------------------
WORKDIR /app

# Зависимости отделены от кода – слой кэширующийся
COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --------------------------
# Копируем исходный код
# --------------------------
COPY . /app

# --------------------------
# Конфигурация запуска
# --------------------------
EXPOSE 8000

# Проверяем структуру файлов после копирования
RUN ls -la /app && \
    ls -la /app/app && \
    ls -la /app/app/routes || echo "Директория routes не найдена"

# Uvicorn запускается только после инициализации сервисов
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]