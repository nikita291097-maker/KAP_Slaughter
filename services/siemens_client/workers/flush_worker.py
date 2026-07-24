import time
from psycopg2.extras import execute_batch
from core.logger import log
from core.spool import clear_spool
from core.config import SOURCE_NAME
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
            batch.append((eid, eid, ts, val, SOURCE_NAME))

        with db.conn.cursor() as cur:
            execute_batch(cur, """
                INSERT INTO kap_error (num, iderror, mydate, status, source)
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT (iderror, mydate) DO NOTHING
            """, batch)

        with state.buffer_lock:
            del state.buffer[:len(batch_data)]

        clear_spool()
        log.info(f"Flushed {len(batch)} events (source={SOURCE_NAME})")

    except Exception as e:
        log.error(f"Batch insert error: {e}")

def start_flush_worker():
    while True:
        time.sleep(5)
        flush()