from threading import Lock
from datetime import datetime

buffer = []
buffer_lock = Lock()
current_live_id = 0
mqtt_ok = False

# PLC states
plc_raw_values = {}
plc_stable_values = {}
plc_state_start = {}
plc_last_confirmed = {}
plc_active_events = {}          # для обычных сигналов (без режима)
plc_last_total = None
plc_connection_lost = False
plc_error_count = 0

DEBOUNCE_TIME = 3  # секунды