import json

from datetime import datetime

from core.logger import log
from core.spool import append_to_spool
from core.config import MAX_BUFFER_SIZE

from core import state

from models.event import Event


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
        # DEDUPLICATION
        #

        prev_value = state.last_states.get(
            event.event_id
        )

        if prev_value == event.value:

            log.info(
                f"Duplicate skipped: "
                f"id={event.event_id}, "
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