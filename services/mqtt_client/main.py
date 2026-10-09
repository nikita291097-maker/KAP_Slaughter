from threading import Thread

from core.logger import log
from core.db import init_db
from core.spool import load_spool
from core.mqtt import start_mqtt

from workers.flush_worker import start_flush_worker
from workers.heartbeat_worker import start_heartbeat_worker
from workers.stable_worker import start_stable_worker


def main():

    log.info("Service starting")

    init_db()

    load_spool()

    #
    # stable_worker запускаем ДО mqtt — чтобы pending сразу обрабатывался
    #
    Thread(
        target=start_stable_worker,
        daemon=True
    ).start()

    Thread(
        target=start_flush_worker,
        daemon=True
    ).start()

    Thread(
        target=start_heartbeat_worker,
        daemon=True
    ).start()

    start_mqtt()


if __name__ == "__main__":
    main()