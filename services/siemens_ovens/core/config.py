import os

LOG_DIR = "/app/logs"
SPOOL_DIR = "/app/spool"
SPOOL_FILE = f"{SPOOL_DIR}/events.log"

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

BATCH_SIZE = int(os.getenv("BATCH_SIZE", 50))
FLUSH_INTERVAL = int(os.getenv("FLUSH_INTERVAL", 5))
MAX_BUFFER_SIZE = int(os.getenv("MAX_BUFFER_SIZE", 10000))

SOURCE_NAME = os.getenv("SOURCE_NAME", "Обезволаш")   # переопределяется в compose

PLC_IP = os.getenv("PLC_IP", "172.18.48.161")
PLC_RACK = int(os.getenv("PLC_RACK", 0))
PLC_SLOT = int(os.getenv("PLC_SLOT", 1))
PLC_DB_NUMBER = int(os.getenv("PLC_DB_NUMBER", 23))
PLC_POLL_INTERVAL = int(os.getenv("PLC_POLL_INTERVAL", 1))
PLC_ERROR_THRESHOLD = int(os.getenv("PLC_ERROR_THRESHOLD", 3))
PLC_ID = int(os.getenv("PLC_ID", 1))   # 1 или 2