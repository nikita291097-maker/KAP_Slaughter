import os
import json

from datetime import datetime

from core.logger import log
from core.config import *

from core import state

from models.event import Event

os.makedirs(SPOOL_DIR, exist_ok=True)


def append_to_spool(event_json):

    try:

        with open(SPOOL_FILE, "a", encoding="utf-8") as f:

            f.write(
                json.dumps(
                    event_json,
                    ensure_ascii=False
                )
            )

            f.write("\n")

    except Exception as e:

        log.error(f"Spool append error: {e}")


def clear_spool():

    with open(SPOOL_FILE, "w", encoding="utf-8"):
        pass


def load_spool():

    try:

        if not os.path.exists(SPOOL_FILE):
            return

        restored = 0

        with open(SPOOL_FILE, "r", encoding="utf-8") as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                data = json.loads(line)

                event = Event(
                    event_id=data["event_id"],
                    timestamp=datetime.fromisoformat(
                        data["timestamp"]
                    ),
                    value=data["value"]
                )

                state.buffer.append(
                    event.to_tuple()
                )

                restored += 1

        log.warning(
            f"Restored {restored} events from spool"
        )

    except Exception as e:

        log.error(f"Spool load error: {e}")