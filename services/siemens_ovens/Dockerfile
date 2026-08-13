FROM python:3.11-slim

# Установка системных зависимостей для Snap7
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsnap7-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем и устанавливаем Python-пакеты из локальной папки
COPY packages/ /tmp/packages/
RUN pip install --no-cache-dir --no-index --find-links /tmp/packages \
    paho-mqtt \
    psycopg2-binary \
    python-snap7

COPY . .

CMD ["python", "main.py"]