import time
import psycopg2

from core.logger import log
from core.config import *

conn = None


def get_conn():

    global conn

    while True:

        try:

            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )

            conn.autocommit = True

            log.info("DB connected")

            return conn

        except Exception as e:

            log.error(f"DB connect error: {e}")

            time.sleep(5)


def ensure_connection():

    global conn

    try:

        with conn.cursor() as cur:
            cur.execute("SELECT 1")

    except Exception:

        log.warning("DB reconnecting")

        conn = get_conn()


def init_db():

    from core import state

    ensure_connection()

    with conn.cursor() as cur:

        cur.execute(
            "SELECT COALESCE(MAX(id),0) FROM kap_error"
        )

        state.current_error_id = cur.fetchone()[0]

        cur.execute(
            "SELECT COALESCE(MAX(id),0) FROM kap_live"
        )

        state.current_live_id = cur.fetchone()[0]

    log.info(
        f"Init counters: "
        f"kap_error={state.current_error_id}, "
        f"kap_live={state.current_live_id}"
    )