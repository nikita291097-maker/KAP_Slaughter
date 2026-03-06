import os
import random
import time
import logging
from datetime import datetime

import psycopg2

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    """
    Минимальная проверка/инициализация:
    - добавляет колонку carcass_count в conveyor_state, если её нет
    - гарантирует наличие записи для каждого конвейера в conveyor_state
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Добавление колонки, если её нет
            cur.execute("""
                ALTER TABLE conveyor_state
                ADD COLUMN IF NOT EXISTS carcass_count INTEGER DEFAULT 0;
            """)
            # Инициализация записей для всех конвейеров, если их нет
            cur.execute("""
                INSERT INTO conveyor_state (conveyor_id, status, carcass_count, updated_at)
                SELECT id, 'STOPPED', 0, now()
                FROM conveyors
                ON CONFLICT (conveyor_id) DO NOTHING;
            """)
            conn.commit()


def close_event(cur, conveyor_id: int, event_class: str) -> None:
    """Закрыть активное событие указанного класса для конвейера."""
    cur.execute("""
        UPDATE system_events
        SET event_state = 'CLEARED', cleared_at = NOW()
        WHERE conveyor_id = %s
          AND event_class = %s
          AND event_state = 'ACTIVE';
    """, (conveyor_id, event_class))


def create_event(cur, conveyor_id: int, event_class: str, message: str) -> None:
    """Создать новое активное событие, если нет активного с таким же классом."""
    cur.execute("""
        SELECT id FROM system_events
        WHERE conveyor_id = %s
          AND event_class = %s
          AND event_state = 'ACTIVE';
    """, (conveyor_id, event_class))
    if cur.fetchone() is None:
        cur.execute("""
            INSERT INTO system_events (conveyor_id, event_class, event_state, message, created_at)
            VALUES (%s, %s, 'ACTIVE', %s, NOW());
        """, (conveyor_id, event_class, message))


def update_state() -> None:
    """Обновляет состояние конвейеров и генерирует события при изменении статуса."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Получаем все конвейеры с их именами
            cur.execute("SELECT id, name FROM conveyors ORDER BY position;")
            conveyors = cur.fetchall()  # (id, name)

            for conveyor_id, conveyor_name in conveyors:
                # Получаем текущий статус из таблицы состояний
                cur.execute("SELECT status FROM conveyor_state WHERE conveyor_id = %s;", (conveyor_id,))
                row = cur.fetchone()
                old_status = row[0] if row else None

                # Генерируем новый статус случайным образом
                new_status = random.choices(STATUSES, weights=[55, 15, 15, 10, 5], k=1)[0]
                carcass_count = carcass_count_for_status(new_status)

                # Если статус изменился — обрабатываем события
                if old_status != new_status:
                    logger.info(f"Конвейер {conveyor_name}: {old_status} -> {new_status}")

                    # Закрываем событие, соответствующее старому проблемному статусу
                    if old_status == "ERROR":
                        close_event(cur, conveyor_id, "ALARM")
                    elif old_status == "WARNING":
                        close_event(cur, conveyor_id, "DEVIATION")
                    elif old_status == "STOPPED":
                        close_event(cur, conveyor_id, "EVENT")

                    # Создаём событие для нового проблемного статуса
                    if new_status == "ERROR":
                        create_event(cur, conveyor_id, "ALARM", f"Авария: {conveyor_name}")
                    elif new_status == "WARNING":
                        create_event(cur, conveyor_id, "DEVIATION", f"Отклонение: {conveyor_name}")
                    elif new_status == "STOPPED":
                        create_event(cur, conveyor_id, "EVENT", "Конвейер остановлен")

                # Обновляем состояние конвейера
                cur.execute("""
                    UPDATE conveyor_state
                    SET status = %s,
                        carcass_count = %s,
                        updated_at = %s
                    WHERE conveyor_id = %s;
                """, (new_status, carcass_count, datetime.utcnow(), conveyor_id))

            conn.commit()


def main() -> None:
    while True:
        try:
            ensure_rows()          # теперь функция определена
            update_state()
            sleep_seconds = random.randint(2, 5)
            time.sleep(sleep_seconds)
        except Exception as exc:
            logger.exception(f"Simulator error: {exc}")
            time.sleep(3)


if __name__ == "__main__":
    main()