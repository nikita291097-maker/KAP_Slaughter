import os
from datetime import datetime
from typing import Any

import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="KAP API", version="0.4")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "host.docker.internal"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "test"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )


def ensure_schema() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS conveyors (
                    id SERIAL PRIMARY KEY,
                    code TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    position INTEGER,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT now()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS conveyor_state (
                    conveyor_id INTEGER PRIMARY KEY REFERENCES conveyors(id),
                    status TEXT NOT NULL,
                    load_percent INTEGER DEFAULT 0,
                    speed REAL DEFAULT 0,
                    temperature REAL,
                    alarm BOOLEAN DEFAULT FALSE,
                    updated_at TIMESTAMP DEFAULT now()
                );
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
                ALTER TABLE conveyor_state
                ADD COLUMN IF NOT EXISTS carcass_count INTEGER DEFAULT 0;
                """
            )
            cur.execute(
                """
                INSERT INTO conveyors (id, code, name, position, description)
                VALUES
                    (1, 'C1', 'Конвейер обескровливания', 1, NULL),
                    (2, 'C2', 'Элеватор опуска в шпарильную установку', 2, NULL),
                    (3, 'C3', 'Конвейер разделочный', 3, NULL),
                    (4, 'C4', 'Конвейер для органов', 4, NULL),
                    (5, 'C5', 'Конвейер шокового туннеля', 5, NULL)
                ON CONFLICT (id) DO NOTHING;
                """
            )
            conn.commit()


@app.on_event("startup")
def on_startup() -> None:
    ensure_schema()


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/conveyors")
def get_conveyors() -> list[dict[str, Any]]:
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        c.id,
                        c.name,
                        COALESCE(s.status, 'STOPPED') AS status,
                        COALESCE(s.carcass_count, 0) AS carcass_count,
                        s.updated_at
                    FROM conveyors c
                    LEFT JOIN conveyor_state s
                    ON c.id = s.conveyor_id
                    ORDER BY c.position;
                    """
                )
                rows = cur.fetchall()

        response: list[dict[str, Any]] = []
        for conveyor_id, name, status, carcass_count, updated_at in rows:
            response.append(
                {
                    "id": conveyor_id,
                    "name": name,
                    "status": status,
                    "carcass_count": carcass_count,
                    "updated_at": updated_at.isoformat() if updated_at else None,
                }
            )
        return response
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Database error: {exc}") from exc


@app.get("/api/events")
def get_events() -> list[dict[str, Any]]:
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        e.id,
                        c.name,
                        e.event_class,
                        e.event_state,
                        e.message,
                        e.created_at,
                        e.cleared_at
                    FROM system_events e
                    LEFT JOIN conveyors c
                    ON e.conveyor_id = c.id
                    ORDER BY e.id DESC
                    LIMIT 500;
                    """
                )
                rows = cur.fetchall()

        response: list[dict[str, Any]] = []
        for event_id, name, event_class, event_state, message, created_at, cleared_at in rows:
            response.append(
                {
                    "id": event_id,
                    "name": name,
                    "event_class": event_class,
                    "event_state": event_state,
                    "message": message,
                    "created_at": created_at.isoformat() if created_at else None,
                    "cleared_at": cleared_at.isoformat() if cleared_at else None,
                }
            )

        return response
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Database error: {exc}") from exc
