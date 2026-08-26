import time
from datetime import datetime
from core.logger import log
from core import state
from core.config import (
    PLC_IP, PLC_RACK, PLC_SLOT, PLC_DB_NUMBER,
    PLC_POLL_INTERVAL, PLC_ERROR_THRESHOLD, PLC_ID
)
from core.plc_reader import read_plc, SIGNAL_MAP, LOST_CONNECTION_ID, parse_all_signals
from core.spool import append_to_spool
from models.event import Event

def generate_event(event_id, status, timestamp=None):
    if timestamp is None:
        timestamp = datetime.utcnow()
    event = Event(event_id, timestamp, status)
    append_to_spool(event.to_json())
    with state.buffer_lock:
        state.buffer.append(event.to_tuple())

def reader_loop():
    log.info(f"PLC reader started for Опалочная печь {PLC_ID} ({PLC_IP})")

    event_ids = list(SIGNAL_MAP.keys())
    # Инициализация состояний
    state.plc_last_values = {}
    state.plc_stable_values = {}
    state.plc_state_start = {}
    state.plc_last_confirmed = {}
    state.plc_active_events = {}
    for eid in event_ids:
        state.plc_active_events[eid] = False
        state.plc_last_values[eid] = None
        state.plc_stable_values[eid] = None
        state.plc_state_start[eid] = datetime.utcnow()
        state.plc_last_confirmed[eid] = None

    state.plc_connection_lost = False
    state.plc_error_count = 0
    state.plc_connection_event_generated = False  # используем глобальную переменную из state

    # При старте: закрываем все активные события и потерю связи
    generate_event(LOST_CONNECTION_ID, 0)
    for eid in event_ids:
        generate_event(eid, 0)
        state.plc_active_events[eid] = False

    error_counter = 0
    LOG_ERROR_INTERVAL = 5

    while True:
        try:
            data = read_plc(PLC_IP, PLC_RACK, PLC_SLOT, PLC_DB_NUMBER)
            state.plc_error_count = 0
            error_counter = 0
            state.plc_connection_event_generated = False  # сброс после успешного чтения

            # Восстановление после потери
            if state.plc_connection_lost:
                log.info(f"PLC connection restored (Опалочная печь {PLC_ID})")
                state.plc_connection_lost = False
                generate_event(LOST_CONNECTION_ID, 0)

                now = datetime.utcnow()
                current_bools = parse_all_signals(data)
                for eid in event_ids:
                    val = current_bools.get(eid, 0)
                    state.plc_last_values[eid] = val
                    state.plc_stable_values[eid] = None
                    state.plc_state_start[eid] = now
                    state.plc_last_confirmed[eid] = None
                    state.plc_active_events[eid] = False
                    if val == 1:
                        generate_event(eid, 1)
                        state.plc_active_events[eid] = True
                time.sleep(PLC_POLL_INTERVAL)
                continue

            # Обработка булевых сигналов с антидребезгом 3 сек
            current_bools = parse_all_signals(data)
            now = datetime.utcnow()

            for eid in event_ids:
                raw_val = current_bools.get(eid)
                if raw_val is None:
                    continue

                if state.plc_last_values.get(eid) != raw_val:
                    state.plc_last_values[eid] = raw_val
                    state.plc_state_start[eid] = now
                    state.plc_stable_values[eid] = None
                    continue

                if state.plc_stable_values.get(eid) is None:
                    elapsed = (now - state.plc_state_start[eid]).total_seconds()
                    if elapsed >= state.DEBOUNCE_TIME:
                        state.plc_stable_values[eid] = raw_val
                        prev = state.plc_last_confirmed.get(eid)
                        if prev != raw_val:
                            if raw_val == 1:
                                if not state.plc_active_events.get(eid, False):
                                    generate_event(eid, 1)
                                    state.plc_active_events[eid] = True
                            else:
                                if state.plc_active_events.get(eid, False):
                                    generate_event(eid, 0)
                                    state.plc_active_events[eid] = False
                            state.plc_last_confirmed[eid] = raw_val

        except Exception as e:
            state.plc_error_count += 1
            error_counter += 1
            if error_counter % LOG_ERROR_INTERVAL == 0:
                log.error(f"PLC read failed ({state.plc_error_count} errors): {e}")

            # Генерируем потерю связи, если порог достигнут и событие ещё не создано
            if state.plc_error_count >= PLC_ERROR_THRESHOLD and not state.plc_connection_event_generated:
                log.warning(f"PLC connection lost (Опалочная печь {PLC_ID})")
                state.plc_connection_lost = True
                state.plc_connection_event_generated = True
                generate_event(LOST_CONNECTION_ID, 1)

                # Закрываем все активные сигналы
                for eid in event_ids:
                    if state.plc_active_events.get(eid, False):
                        generate_event(eid, 0)
                        state.plc_active_events[eid] = False

        time.sleep(PLC_POLL_INTERVAL)

def start_reader_worker():
    from threading import Thread
    t = Thread(target=reader_loop, daemon=True)
    t.start()                                            