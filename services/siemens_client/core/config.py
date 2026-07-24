import os

# -------- Общие настройки ----------
LOG_DIR = "/app/logs"
SPOOL_DIR = "/app/spool"
SPOOL_FILE = f"{SPOOL_DIR}/events.log"

# -------- База данных ----------
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# -------- Параметры буфера и флашей ----------
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 50))
FLUSH_INTERVAL = int(os.getenv("FLUSH_INTERVAL", 5))
MAX_BUFFER_SIZE = int(os.getenv("MAX_BUFFER_SIZE", 10000))

# -------- Источник данных ----------
SOURCE_NAME = os.getenv("SOURCE_NAME", "ПЛК Шпарчан")  # переопределяется в docker-compose

# -------- Настройки PLC ----------
PLC_IP = os.getenv("PLC_IP", "172.18.48.160")
PLC_RACK = int(os.getenv("PLC_RACK", 0))
PLC_SLOT = int(os.getenv("PLC_SLOT", 1))
PLC_DB_NUMBER = int(os.getenv("PLC_DB_NUMBER", 49))
PLC_POLL_INTERVAL = int(os.getenv("PLC_POLL_INTERVAL", 1))        # секунды
PLC_ERROR_THRESHOLD = int(os.getenv("PLC_ERROR_THRESHOLD", 3))    # число ошибок до потери связи

# (если нужны другие настройки MQTT – они не используются, но оставлены для совместимости)
MQTT_HOST = os.getenv("MQTT_HOST", "")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USER = os.getenv("MQTT_USER", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")