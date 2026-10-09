import time

from core.logger import log
from core.config import DEBOUNCE_MS, STABLE_TICK_MS, MAX_PENDING_AGE_MS
from core import state
from handlers.effective_handler import emit_stable


def start_stable_worker():
    """
    Раз в STABLE_TICK_MS проверяет pending.
    Если значение не менялось >= DEBOUNCE_MS — эмитит его.
    """
    log.info(f"Stable worker started (debounce={DEBOUNCE_MS}ms, tick={STABLE_TICK_MS}ms)")

    while True:
        time.sleep(STABLE_TICK_MS / 1000.0)
        now = time.monotonic()

        ready = []
        for event_id, p in list(state.pending.items()):
            age_stable = (now - p["last_change"]) * 1000.0
            age_total  = (now - p["first_seen"])  * 1000.0

            # стабильно достаточно ИЛИ висит слишком долго (защита от утечки)
            if age_stable >= DEBOUNCE_MS or age_total >= MAX_PENDING_AGE_MS:
                ready.append((event_id, p))
                del state.pending[event_id]

        for event_id, p in ready:
            emit_stable(event_id, p["candidate"], p["timestamp"])
            log.debug(
                f"Emitted stable: id={event_id}, value={p['candidate']}, "
                f"stable_for={int((now - p['last_change']) * 1000)}ms"
            )