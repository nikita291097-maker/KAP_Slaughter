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
# DEBOUNCE — антидребезг для всех дискретных сигналов
# ============================================================

# Время стабильности (мс): сигнал должен не меняться столько,
# чтобы считаться реальным событием и быть записанным в БД.
# Для механических контактов и кнопок — 200–500 мс.
DEBOUNCE_MS = 300

# Частота опроса pending stable_worker'ом (мс).
STABLE_TICK_MS = 100

# Максимальное время удержания pending (мс) — защита от утечки.
# Если сигнал флэппит бесконечно, всё равно эмитим последнее значение.
MAX_PENDING_AGE_MS = 60000

# Event_id, для которых debounce НЕ применяется.
# Это счётчики и события с чередующейся парой 1→0 за миллисекунды,
# где важен именно фронт 1, а не итоговое значение.
DEBOUNCE_EXCLUDE = {640, 508, 509, 510, 511}