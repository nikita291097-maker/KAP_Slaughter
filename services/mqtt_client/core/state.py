from threading import Lock

last_emit_time: dict[int, float] = {}   # event_id -> ms epoch

buffer = []
buffer_lock = Lock()

mqtt_ok = False
last_flush = 0
last_live_write = 0

current_live_id = 0   # используется для kap_live
last_states = {}

# Pending: event_id -> {"candidate": int, "last_change": float, "first_seen": float, "timestamp": datetime}
pending: dict = {}
