import os
import random
import time
from datetime import datetime

import psycopg2

STATUSES = ["RUNNING", "STOPPED", "WARNING", "ERROR", "MAINTENANCE"]


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
            conn.commit()


def update_state() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM conveyors ORDER BY position;")
            conveyor_ids = [row[0] for row in cur.fetchall()]

            for conveyor_id in conveyor_ids:
                status = random.choices(STATUSES, weights=[55, 15, 15, 10, 5], k=1)[0]
                carcass_count = carcass_count_for_status(status)
                cur.execute(
                    """
                    UPDATE conveyor_state
                    SET status = %s,
                        carcass_count = %s,
                        updated_at = %s
                    WHERE conveyor_id = %s;
                    """,
                    (status, carcass_count, datetime.utcnow(), conveyor_id),
                )
            conn.commit()


def main() -> None:
    while True:
        try:
            ensure_rows()
            update_state()
            sleep_seconds = random.randint(2, 5)
            time.sleep(sleep_seconds)
        except Exception as exc:  # noqa: BLE001
            print(f"Simulator error: {exc}")
            time.sleep(3)


if __name__ == "__main__":
    main()
