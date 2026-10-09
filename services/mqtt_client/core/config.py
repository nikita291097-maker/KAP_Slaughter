import os

MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

BATCH_SIZE = int(os.getenv("BATCH_SIZE", 50))
FLUSH_INTERVAL = int(os.getenv("FLUSH_INTERVAL", 5))

MAX_BUFFER_SIZE = int(os.getenv("MAX_BUFFER_SIZE", 10000))

LOG_DIR = "/app/logs"
SPOOL_DIR = "/app/spool"

SPOOL_FILE = f"{SPOOL_DIR}/events.log"

# Новая переменная – источник данных
SOURCE_NAME = os.getenv("SOURCE_NAME", "ЗИВИЛ")

# ============================================================
# АНТИ-ФЛУД
# ============================================================

# Минимальный интервал между записями per event_id, мс.
# 0 или отсутствие = без ограничения.
# Для счётчиков/датчиков — не чаще 1 записи в N мс.
EVENT_MIN_INTERVAL_MS = {
    640: 1000,   # Туша проехала — макс 1/сек
    605: 1000,   # Такт 1
    606: 1000,   # Такт 2
    607: 1000,   # Режим "свинья"
    608: 1000,   # Режим "свиноматка"
    508: 500,    # Датчик продукта линии 42
    509: 500,    # Датчик продукта линии 33
    510: 500,    # Счётчик продукта линии 42
    511: 500,    # Счётчик продукта линии 33
}

# Окно debounce для дребезга, мс.
# Применяется только к DEBOUNCE_EVENTS.
DEBOUNCE_MS = 300

# event_id, для которых отсекаем повторный фронт того же значения
# в пределах DEBOUNCE_MS.
DEBOUNCE_EVENTS = {
    640,   # Туша проехала
}