import time

from datetime import datetime, timedelta

from core.logger import log

from core import state

import core.db as db


def write_live():

    try:

        db.ensure_connection()

        state.current_live_id += 1

        status = 0 if state.mqtt_ok else 1

        ts = (
            datetime.utcnow()
            + timedelta(hours=3)
        )

        with db.conn.cursor() as cur:

            cur.execute("""
                INSERT INTO kap_live
                (
                    id,
                    typeerror,
                    livetime
                )
                VALUES (%s,%s,%s)
            """, (
                state.current_live_id,
                status,
                ts
            ))

        log.info(
            f"Live written: "
            f"id={state.current_live_id}, "
            f"status={status}"
        )

    except Exception as e:

        log.error(f"Live insert error: {e}")


def start_heartbeat_worker():

    while True:

        write_live()

        time.sleep(60)