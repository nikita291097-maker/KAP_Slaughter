import time
from datetime import datetime, timedelta
from core.logger import log
from core import state
from core.config import (
    PLC_IP, PLC_RACK, PLC_SLOT, PLC_DB_NUMBER,
    PLC_POLL_INTERVAL, PLC_ERROR_THRESHOLD
)
from core.plc_reader import read_plc, get_signal_value, parse_all_bool_values
from core.spool import append_to_spool
from models.event import Event

EVENT_LOST_CONNECTION = 600
EVENT_TOTAL = 640

# Булевы сигналы: 601-604, 616-633, 635-638
BOOL_EVENT_IDS = list(range(601, 605)) + list(range(616, 634)) + list(range(635, 639))
# Результат: 601,602,603,604, 616-633, 635,636,637,638

def generate_event(event_id, status, timestamp=None):
    if timestamp is None:
        timestamp = datetime.utcnow()
    event = Event(event_id, timestamp, status)
    append_to_spool(event.to_json())
    with state.buffer_lock:
        state.buffer.append(event.to_tuple())

def reader_loop():
    log.info("PLC reader started")
    state.plc_raw_values = {}
    state.plc_stable_values = {}
    state.plc_state_start = {}
    state.plc_last_confirmed = {}
    state.plc_active_events = {}
    for eid in BOOL_EVENT_IDS:
        state.plc_active_events[eid] = False
    state.plc_last_total = None
    state.plc_connection_lost = False
    state.plc_error_count = 0

    error_counter = 0
    LOG_ERROR_INTERVAL = 10

    while True:
        try:
            data = read_plc(PLC_IP, PLC_RACK, PLC_SLOT, PLC_DB_NUMBER)
            state.plc_error_count = 0
            error_counter = 0

            if state.plc_connection_lost:
                log.info("PLC connection restored")
                state.plc_connection_lost = False
                generate_event(EVENT_LOST_CONNECTION, 0)
                now = datetime.utcnow()
                for eid in BOOL_EVENT_IDS:
                    state.plc_raw_values[eid] = None
                    state.plc_stable_values[eid] = None
                    state.plc_state_start[eid] = now
                    state.plc_last_confirmed[eid] = None
                    state.plc_active_events[eid] = False
                state.plc_last_total = get_signal_value(data, EVENT_TOTAL)
                time.sleep(PLC_POLL_INTERVAL)
                continue

            current_total = get_signal_value(data, EVENT_TOTAL)
            if state.plc_last_total is not None and current_total > state.plc_last_total:
                delta = current_total - state.plc_last_total
                log.info(f"Total increased by {delta} (old={state.plc_last_total}, new={current_total})")
                now = datetime.utcnow()
                for i in range(1, delta + 1):
                    t1 = now + timedelta(milliseconds=(i-1))
                    t0 = now + timedelta(milliseconds=i)
                    generate_event(EVENT_TOTAL, 1, t1)
                    generate_event(EVENT_TOTAL, 0, t0)
                state.plc_last_total = current_total
            elif state.plc_last_total is None:
                state.plc_last_total = current_total

            current_bools = parse_all_bool_values(data)
            now = datetime.utcnow()

            for eid in BOOL_EVENT_IDS:
                raw_val = current_bools.get(eid)
                if raw_val is None:
                    continue

                if state.plc_raw_values.get(eid) != raw_val:
                    state.plc_raw_values[eid] = raw_val
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

            if state.plc_error_count >= PLC_ERROR_THRESHOLD and not state.plc_connection_lost:
                log.warning("PLC connection lost")
                state.plc_connection_lost = True
                generate_event(EVENT_LOST_CONNECTION, 1)

                for eid in BOOL_EVENT_IDS:
                    if state.plc_active_events.get(eid, False):
                        generate_event(eid, 0)
                        state.plc_active_events[eid] = False

        time.sleep(PLC_POLL_INTERVAL)

def start_reader_worker():
    from threading import Thread
    t = Thread(target=reader_loop, daemon=True)
    t.start()