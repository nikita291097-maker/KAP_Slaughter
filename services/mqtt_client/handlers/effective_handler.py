import json
import time

from datetime import datetime

from core.logger import log
from core.spool import append_to_spool
from core.config import MAX_BUFFER_SIZE, EVENT_MIN_INTERVAL_MS, DEBOUNCE_MS, DEBOUNCE_EVENTS

from core import state

from models.event import Event


#
# Локальное состояние rate-limit и debounce.
# Хранится в модуле, сбрасывается при рестарте сервиса.
# При рестарте не критично — MQTT QoS=1 + ON CONFLICT в БД добьют дубли.
#
_last_emit_ms: dict = {}        # event_id -> epoch ms последней записи
_last_transition_ms: dict = {}  # event_id -> epoch ms последнего фронта (для debounce)


def _passes_rate_limit(event_id: int) -> bool:
    """
    True, если событие можно записать (не слишком часто).
    Для event_id без лимита возвращает True.
    """
    min_interval = EVENT_MIN_INTERVAL_MS.get(event_id, 0)
    if min_interval <= 0:
        return True

    now_ms = time.time() * 1000.0
    last_ms = _last_emit_ms.get(event_id, 0.0)

    if now_ms - last_ms < min_interval:
        return False

    _last_emit_ms[event_id] = now_ms
    return True


def _passes_debounce(event_id: int, value: int) -> bool:
    """
    Отсекает дребезг счётчиков: повторный приход того же значения
    в пределах DEBOUNCE_MS считается шумом.
    Применяется только к event_id из DEBOUNCE_EVENTS.
    """
    if event_id not in DEBOUNCE_EVENTS:
        return True

    now_ms = time.time() * 1000.0
    prev = state.last_states.get(event_id)
    last_ms = _last_transition_ms.get(event_id, 0.0)

    if prev == value and now_ms - last_ms < DEBOUNCE_MS:
        return False

    _last_transition_ms[event_id] = now_ms
    return True


def handle_effective(msg):

    try:

        payload = msg.payload.decode()

        if payload.endswith("e"):
            payload = payload[:-1]

        data = json.loads(payload)

        event = Event(
            event_id=data["id"],
            timestamp=datetime.fromisoformat(
                data["timestamp"]
            ),
            value=int(data["value"])
        )

        #
        # RATE LIMIT
        # Для "шумных" event_id (640, датчики, такты) — не чаще N мс.
        # Отсекает 62 сообщения/сек по одному и тому же коду.
        #
        if not _passes_rate_limit(event.event_id):
            log.debug(
                f"Rate-limited: id={event.event_id}, "
                f"value={event.value}"
            )
            return

        #
        # DEDUPLICATION по value
        # Если значение не изменилось — пропускаем.
        # Работает для дискретных сигналов (0/1), не работает для счётчиков.
        #
        prev_value = state.last_states.get(
            event.event_id
        )

        if prev_value == event.value:
            log.debug(
                f"Duplicate skipped: "
                f"id={event.event_id}, "
                f"value={event.value}"
            )
            return

        #
        # DEBOUNCE
        # Для счётчиков из DEBOUNCE_EVENTS: игнорируем повторный фронт
        # того же значения в пределах DEBOUNCE_MS.
        # Спасает от дребезга датчика "Туша проехала".
        #
        if not _passes_debounce(event.event_id, event.value):
            log.debug(
                f"Debounced: id={event.event_id}, "
                f"value={event.value}"
            )
            return

        #
        # UPDATE LAST STATE
        #
        state.last_states[
            event.event_id
        ] = event.value

        #
        # SPOOL
        #
        append_to_spool(
            event.to_json()
        )

        #
        # BUFFER
        #
        with state.buffer_lock:

            state.buffer.append(
                event.to_tuple()
            )

            if len(state.buffer) > MAX_BUFFER_SIZE:

                overflow = (
                    len(state.buffer)
                    - MAX_BUFFER_SIZE
                )

                del state.buffer[:overflow]

                log.warning(
                    f"Buffer overflow: "
                    f"dropped {overflow}"
                )

    except Exception as e:

        log.error(
            f"Effective parse error: {e}"
        )