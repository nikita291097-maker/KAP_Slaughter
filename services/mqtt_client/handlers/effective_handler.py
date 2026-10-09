import json
import time

from datetime import datetime

from core.logger import log
from core.spool import append_to_spool
from core.config import MAX_BUFFER_SIZE, DEBOUNCE_EXCLUDE
from core import state

from models.event import Event


def handle_effective(msg):
    """
    Обработчик MQTT-сообщения event/<id>/effective.

    Логика:
      - Если event_id в DEBOUNCE_EXCLUDE → пишем сразу (без debounce).
      - Иначе кладём в state.pending и ждём стабилизации.
        stable_worker через DEBOUNCE_MS эмитит последнее стабильное значение.
    """

    try:

        payload = msg.payload.decode()

        if payload.endswith("e"):
            payload = payload[:-1]

        data = json.loads(payload)

        event = Event(
            event_id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            value=int(data["value"])
        )

        #
        # DEBOUNCE EXCLUDE — пишем сразу
        #
        if event.event_id in DEBOUNCE_EXCLUDE:
            _emit(event)
            return

        #
        # DEBOUNCE через pending
        #
        now = time.monotonic()
        last_emitted = state.last_states.get(event.event_id)
        pending = state.pending.get(event.event_id)

        if pending is None:
            #
            # Нет pending-записи.
            #
            # Если пришедшее значение совпадает с последним отправленным —
            # это дедупликация, игнорируем.
            #
            if last_emitted == event.value:
                log.debug(
                    f"Duplicate skipped: "
                    f"id={event.event_id}, value={event.value}"
                )
                return

            #
            # Новое значение — начинаем ждать стабильности.
            #
            state.pending[event.event_id] = {
                "candidate":   event.value,
                "last_change": now,
                "first_seen":  now,
                "timestamp":   event.timestamp,
            }
            log.debug(
                f"Pending new: "
                f"id={event.event_id}, value={event.value}"
            )
        else:
            #
            # Pending уже есть.
            #
            if pending["candidate"] != event.value:
                #
                # Значение изменилось — сбрасываем таймер стабилизации.
                #
                pending["candidate"]   = event.value
                pending["last_change"] = now
                pending["timestamp"]   = event.timestamp
                log.debug(
                    f"Pending reset: "
                    f"id={event.event_id}, value={event.value}"
                )
            else:
                #
                # То же значение — обновляем только timestamp
                # (для точности event_time в БД). Таймер НЕ сбрасываем.
                #
                pending["timestamp"] = event.timestamp

    except Exception as e:

        log.error(
            f"Effective parse error: {e}"
        )


def _emit(event: Event):
    """
    Немедленная запись в spool + буфер.
    Вызывается либо для DEBOUNCE_EXCLUDE, либо stable_worker'ом.
    """
    append_to_spool(event.to_json())

    with state.buffer_lock:

        state.buffer.append(event.to_tuple())

        if len(state.buffer) > MAX_BUFFER_SIZE:

            overflow = len(state.buffer) - MAX_BUFFER_SIZE

            del state.buffer[:overflow]

            log.warning(
                f"Buffer overflow: dropped {overflow}"
            )


def emit_stable(event_id: int, value: int, timestamp: datetime):
    """
    Публичный API для stable_worker.
    Обновляет last_states и вызывает _emit.
    """
    state.last_states[event_id] = value
    _emit(Event(event_id=event_id, timestamp=timestamp, value=value))