from threading import Lock

buffer = []

buffer_lock = Lock()

mqtt_ok = False

last_flush = 0

last_live_write = 0

current_error_id = 0

current_live_id = 0