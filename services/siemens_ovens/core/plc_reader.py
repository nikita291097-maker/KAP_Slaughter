import struct
import snap7
from snap7 import util
from core.logger import log
from core.config import PLC_ID

DB_NUMBER = 10
DB_SIZE = 100   # достаточно для смещений до 35.4

# ---------- Маппинг для печи 1 (ID 800..823) ----------
SIGNAL_MAP_1 = {
    # Информационные сигналы (801-810)
    801: ('bool', 34, 0),   # VoltageOk
    802: ('bool', 34, 1),   # PowerOn24V
    803: ('bool', 34, 2),   # DeblockFO
    804: ('bool', 34, 4),   # FOReady
    805: ('bool', 34, 5),   # HermesityOk
    806: ('bool', 34, 6),   # PressureGas_Ok
    807: ('bool', 34, 7),   # PressureAir_Ok
    808: ('bool', 35, 0),   # GasBurnerReady
    809: ('bool', 35, 3),   # SensorFlowReply
    810: ('bool', 35, 4),   # PowerOn

    # Аварийные биты (812-823) из Alarms[0]
    812: ('bool_word', 0, 1),
    813: ('bool_word', 0, 2),
    814: ('bool_word', 0, 3),
    815: ('bool_word', 0, 4),
    816: ('bool_word', 0, 5),   # Warning
    817: ('bool_word', 0, 6),
    818: ('bool_word', 0, 7),
    819: ('bool_word', 0, 8),
    820: ('bool_word', 0, 9),
    821: ('bool_word', 0, 10),
    822: ('bool_word', 0, 11),  # Warning
    823: ('bool_word', 0, 12),
}
LOST_CONNECTION_ID_1 = 800

# ---------- Маппинг для печи 2 (ID 850..873) ----------
SIGNAL_MAP_2 = {
    # Информационные (851-860)
    851: ('bool', 34, 0),
    852: ('bool', 34, 1),
    853: ('bool', 34, 2),
    854: ('bool', 34, 4),
    855: ('bool', 34, 5),
    856: ('bool', 34, 6),
    857: ('bool', 34, 7),
    858: ('bool', 35, 0),
    859: ('bool', 35, 3),
    860: ('bool', 35, 4),

    # Аварийные (862-873)
    862: ('bool_word', 0, 1),
    863: ('bool_word', 0, 2),
    864: ('bool_word', 0, 3),
    865: ('bool_word', 0, 4),
    866: ('bool_word', 0, 5),
    867: ('bool_word', 0, 6),
    868: ('bool_word', 0, 7),
    869: ('bool_word', 0, 8),
    870: ('bool_word', 0, 9),
    871: ('bool_word', 0, 10),
    872: ('bool_word', 0, 11),
    873: ('bool_word', 0, 12),
}
LOST_CONNECTION_ID_2 = 850

# Выбор маппинга по PLC_ID
if PLC_ID == 1:
    SIGNAL_MAP = SIGNAL_MAP_1
    LOST_CONNECTION_ID = LOST_CONNECTION_ID_1
elif PLC_ID == 2:
    SIGNAL_MAP = SIGNAL_MAP_2
    LOST_CONNECTION_ID = LOST_CONNECTION_ID_2
else:
    raise ValueError("PLC_ID must be 1 or 2")

# Функции чтения и парсинга (без изменений)
def read_plc(ip, rack, slot, db_number):
    client = snap7.client.Client()
    try:
        client.connect(ip, rack, slot)
        data = client.db_read(db_number, 0, DB_SIZE)
        client.disconnect()
        return data
    except Exception as e:
        raise

def parse_bool(data, byte_offset, bit_offset):
    return util.get_bool(data, byte_offset, bit_offset)

def parse_word(data, byte_offset):
    return struct.unpack_from('>H', data, byte_offset)[0]

def get_signal_value(data, sig_def):
    typ = sig_def[0]
    if typ == 'bool':
        return parse_bool(data, sig_def[1], sig_def[2])
    elif typ == 'bool_word':
        word = parse_word(data, sig_def[1])
        return (word >> sig_def[2]) & 1
    return None

def parse_all_signals(data):
    result = {}
    for eid, sig_def in SIGNAL_MAP.items():
        result[eid] = get_signal_value(data, sig_def)
    return result