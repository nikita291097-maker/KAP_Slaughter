import logging
import os
import random
import time
from datetime import datetime

import psycopg2

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

STATUSES = ["RUNNING", "STOPPED", "WARNING", "ERROR", "MAINTENANCE"]
EVENT_RULES = {
    "RUNNING": ("EVENT", "Конвейер в работе"),
    "STOPPED": ("EVENT", "Конвейер остановлен"),
    "MAINTENANCE": ("EVENT", "Конвейер переведен в сервисный режим"),
    "WARNING": ("DEVIATION", "Произошло отклонение, конвейер остановлен"),
    "ERROR": ("ALARM", "Произошла авария"),
}


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "host.docker.internal"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "test"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )


def carcass_count_for_status(status: str) -> int:
    if status == "RUNNING":
        return random.randint(40, 120)
    if status == "WARNING":
        return random.randint(10, 60)
    if status == "STOPPED":
        return 0
    if status == "ERROR":
        return random.randint(0, 5)
    return random.randint(0, 20)


def ensure_rows() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                ALTER TABLE conveyor_state
                ADD COLUMN IF NOT EXISTS carcass_count INTEGER DEFAULT 0;
                """
            )
            cur.execute(
                """
                INSERT INTO conveyor_state (conveyor_id, status, carcass_count, updated_at)
                SELECT id, 'STOPPED', 0, now()
                FROM conveyors
                ON CONFLICT (conveyor_id) DO NOTHING;
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS system_events (
                    id BIGSERIAL PRIMARY KEY,
                    conveyor_id INTEGER REFERENCES conveyors(id),
                    event_class TEXT NOT NULL,
                    event_state TEXT NOT NULL,
                    message TEXT NOT NULL,
                    severity INTEGER DEFAULT 1,
                    created_at TIMESTAMP NOT NULL DEFAULT now(),
                    cleared_at TIMESTAMP NULL
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS conveyor_telemetry (
                    id BIGSERIAL PRIMARY KEY,
                    conveyor_id INTEGER REFERENCES conveyors(id),
                    carcass_count INTEGER,
                    created_at TIMESTAMP DEFAULT now()
                );
                """
            )
            conn.commit()


def clear_active_events(cur, conveyor_id: int) -> None:
    cur.execute(
        """
        UPDATE system_events
        SET event_state = 'CLEARED', cleared_at = NOW()
        WHERE conveyor_id = %s
          AND event_state = 'ACTIVE';
        """,
        (conveyor_id,),
    )


def create_event(cur, conveyor_id: int, conveyor_name: str, status: str) -> None:
    event_class, event_text = EVENT_RULES[status]
    cur.execute(
        """
        INSERT INTO system_events (conveyor_id, event_class, event_state, message, created_at)
        VALUES (%s, %s, 'ACTIVE', %s, NOW());
        """,
        (conveyor_id, event_class, f"{conveyor_name}: {event_text}"),
    )


def process_transition(cur, conveyor_id: int, conveyor_name: str, old_status: str | None, new_status: str) -> None:
    if old_status == new_status:
        return

    clear_active_events(cur, conveyor_id)
    create_event(cur, conveyor_id, conveyor_name, new_status)


def update_state() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM conveyors ORDER BY position;")
            conveyors = cur.fetchall()

            for conveyor_id, conveyor_name in conveyors:
                cur.execute("SELECT status FROM conveyor_state WHERE conveyor_id = %s;", (conveyor_id,))
                row = cur.fetchone()
                old_status = row[0] if row else None

                new_status = random.choices(STATUSES, weights=[55, 15, 15, 10, 5], k=1)[0]
                carcass_count = carcass_count_for_status(new_status)

                if old_status != new_status:
                    logger.info("Конвейер %s: %s -> %s", conveyor_name, old_status, new_status)
                    process_transition(cur, conveyor_id, conveyor_name, old_status, new_status)

                cur.execute(
                    """
                    UPDATE conveyor_state
                    SET status = %s,
                        carcass_count = %s,
                        updated_at = %s
                    WHERE conveyor_id = %s;
                    """,
                    (new_status, carcass_count, datetime.utcnow(), conveyor_id),
                )

                cur.execute(
                    """
                    INSERT INTO conveyor_telemetry (conveyor_id, carcass_count, created_at)
                    VALUES (%s, %s, NOW());
                    """,
                    (conveyor_id, carcass_count),
                )

            conn.commit()


def main() -> None:
    while True:
        try:
            ensure_rows()
            update_state()
            time.sleep(10)
        except Exception as exc:
            logger.exception("Simulator error: %s", exc)
            time.sleep(3)


if __name__ == "__main__":
    main()
