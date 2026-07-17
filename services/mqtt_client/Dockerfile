FROM python:3.11-slim

WORKDIR /app

# Копируем скачанные пакеты
COPY packages/ /tmp/packages/

# Устанавливаем из локальной директории
RUN pip install --no-cache-dir --no-index --find-links /tmp/packages paho-mqtt psycopg2-binary

COPY . .

CMD ["python", "main.py"]