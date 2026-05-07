import os
import logging

from logging.handlers import TimedRotatingFileHandler

from core.config import LOG_DIR

os.makedirs(LOG_DIR, exist_ok=True)

log = logging.getLogger("mqtt_client")

log.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s"
)

file_handler = TimedRotatingFileHandler(
    f"{LOG_DIR}/app.log",
    when="midnight",
    backupCount=7,
    encoding="utf-8"
)

file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

log.addHandler(file_handler)
log.addHandler(console_handler)