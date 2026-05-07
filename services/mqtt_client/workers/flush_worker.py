import time

from psycopg2.extras import execute_batch

from core.logger import log
from core.spool import clear_spool

from core import state

import core.db as db


def flush():

    with state.buffer_lock:

        if not state.buffer:
            return

        batch_data = state.buffer[:]

    try:

        db.ensure_connection()

        batch = []

        for eid, ts, val in batch_data:

            state.current_error_id += 1

            batch.append(
                (
                    state.current_error_id,
                    eid,
                    eid,
                    ts,
                    val
                )
            )

        with db.conn.cursor() as cur:

            execute_batch(cur, """
                INSERT INTO kap_error
                (
                    id,
                    num,
                    iderror,
                    mydate,
                    status
                )
                VALUES (%s,%s,%s,%s,%s)
            """, batch)

        with state.buffer_lock:

            del state.buffer[:len(batch_data)]

        clear_spool()

        log.info(
            f"Flushed {len(batch)} events "
            f"(last_id={state.current_error_id})"
        )

    except Exception as e:

        log.error(f"Batch insert error: {e}")


def start_flush_worker():

    while True:

        time.sleep(5)

        flush()