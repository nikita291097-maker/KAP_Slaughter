from threading import Lock

buffer = []
buffer_lock = Lock()

mqtt_ok = False
last_flush = 0
last_live_write = 0

current_live_id = 0   # используется для kap_live
last_states = {}

# Переменная current_error_id удалена – она больше не нужна