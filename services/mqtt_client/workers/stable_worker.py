import time

from core.logger import log
from core.config import DEBOUNCE_MS, STABLE_TICK_MS, MAX_PENDING_AGE_MS
from core import state
from handlers.effective_handler import emit_stable


def start_stable_worker():
    """
    Раз в STABLE_TICK_MS проверяет pending.

    Если значение сигнала не менялось >= DEBOUNCE_MS — эмитит его
    в spool + буфер. Если сигнал флэппит дольше MAX_PENDING_AGE_MS —
    эмитит последнее значение принудительно (защита от утечки).
    """
    log.info(
        f"Stable worker started "
        f"(debounce={DEBOUNCE_MS}ms, tick={STABLE_TICK_MS}ms)"
    )

    while True:
        time.sleep(STABLE_TICK_MS / 1000.0)
        now = time.monotonic()

        # Собираем «созревшие» pending, чтобы не мутировать dict в цикле
        ready = []
        for event_id, p in list(state.pending.items()):
            age_stable = (now - p["last_change"]) * 1000.0
            age_total  = (now - p["first_seen"])  * 1000.0

            if age_stable >= DEBOUNCE_MS or age_total >= MAX_PENDING_AGE_MS:
                ready.append((event_id, p))

        for event_id, p in ready:
            try:
                emit_stable(event_id, p["candidate"], p["timestamp"])
                log.debug(
                    f"Emitted stable: id={event_id}, "
                    f"value={p['candidate']}"
                )
            except Exception as e:
                log.error(f"Emit stable error for id={event_id}: {e}")

            state.pending.pop(event_id, None)