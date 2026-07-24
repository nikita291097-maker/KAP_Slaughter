import struct
import snap7
from snap7 import util
from core.logger import log

SIGNAL_MAP = {
    601: ('bool', 0, 2),
    602: ('bool', 0, 5),
    603: ('bool', 0, 6),
    604: ('bool', 1, 3),
    # 605-615 исключены
    616: ('bool', 3, 3),
    617: ('bool', 3, 4),
    618: ('bool', 4, 1),
    619: ('bool', 4, 2),
    620: ('bool', 4, 3),
    621: ('bool', 4, 4),
    # Alarms[0]
    622: ('bool_word', 484, 1),
    623: ('bool_word', 484, 2),
    624: ('bool_word', 484, 4),
    625: ('bool_word', 484, 5),
    626: ('bool_word', 484, 6),
    627: ('bool_word', 484, 7),
    628: ('bool_word', 484, 8),
    629: ('bool_word', 484, 9),
    630: ('bool_word', 484, 10),
    631: ('bool_word', 484, 11),
    632: ('bool_word', 484, 12),
    633: ('bool_word', 484, 14),
    # 634 исключён
    # Alarms[1]
    635: ('bool_word', 486, 0),
    636: ('bool_word', 486, 1),
    637: ('bool_word', 486, 4),
    638: ('bool_word', 486, 5),
    # 639 исключён
    # 640 – отдельно (Total)
}

def read_plc(ip, rack, slot, db_number):
    client = snap7.client.Client()
    try:
        client.connect(ip, rack, slot)
        data = client.db_read(db_number, 0, 550)
        client.disconnect()
        return data
    except Exception as e:
        raise

def parse_bool(data, byte_offset, bit_offset):
    return util.get_bool(data, byte_offset, bit_offset)

def parse_udint(data, byte_offset):
    return struct.unpack_from('>I', data, byte_offset)[0]

def parse_word(data, byte_offset):
    return struct.unpack_from('>H', data, byte_offset)[0]

def get_signal_value(data, event_id):
    if event_id == 640:
        return parse_udint(data, 12)
    sig = SIGNAL_MAP.get(event_id)
    if not sig:
        return None
    typ = sig[0]
    if typ == 'bool':
        return parse_bool(data, sig[1], sig[2])
    elif typ == 'bool_word':
        word = parse_word(data, sig[1])
        return (word >> sig[2]) & 1
    return None

def parse_all_bool_values(data):
    result = {}
    for eid in SIGNAL_MAP:
        result[eid] = get_signal_value(data, eid)
    return result