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

# Uvicorn знает, где находится объект FastAPI «app» – он объявлен
# в файле app/main.py как `app = FastAPI(...)`  :contentReference[oaicite:0]{index=0}:contentReference[oaicite:1]{index=1}
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    