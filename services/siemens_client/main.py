from threading import Thread
from core.logger import log
from core.db import init_db
from core.spool import load_spool
from workers.flush_worker import start_flush_worker
from workers.reader_worker import start_reader_worker

def main():
    log.info("Siemens PLC service starting")
    init_db()
    load_spool()
    Thread(target=start_flush_worker, daemon=True).start()
    Thread(target=start_reader_worker, daemon=True).start()
    # Бесконечное ожидание, т.к. воркеры работают в фоне
    while True:
        import time
        time.sleep(10)

if __name__ == "__main__":
    main()