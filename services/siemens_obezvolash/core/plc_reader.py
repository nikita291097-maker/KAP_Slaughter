import struct
import snap7
from snap7 import util
from core.logger import log
from core.config import PLC_ID

DB_NUMBER = 23
DB_SIZE = 112

# ---------- Маппинг для PLC 1 (ID 700..724) ----------
SIGNAL_MAP_1 = {
    # Информационные сигналы
    701: ('bool', 35, 2),   # Automatik/manual
    702: ('bool', 35, 3),   # ReadyToWork
    703: ('bool', 35, 4),   # Starting
    704: ('bool', 110, 0),  # ConnectLost (авария)

    # Аварийные биты из Alarms[0] (смещение 0) и Alarms[1] (смещение 2)
    705: ('bool_word', 0, 1),   # SS01-1F1 RM
    706: ('bool_word', 0, 2),   # SS01-17F1 MSS главный вал
    707: ('bool_word', 0, 3),   # SS01-17F2 MSS вспом. вал
    708: ('bool_word', 0, 4),   # SS01-17Q1 плавный пуск
    709: ('bool_word', 0, 5),   # SS01-18F1 MSS Конвейер щетины
    710: ('bool_word', 0, 6),   # Аварийный выключатель на линии убоя
    711: ('bool_word', 0, 7),   # NH-Кнопка 1
    712: ('bool_word', 0, 8),   # NH-Кнопка 2
    713: ('bool_word', 0, 9),   # Старт заблокирован
    714: ('bool_word', 0, 10),  # Not-Halt bei DBA
    715: ('bool_word', 0, 11),  # Not-Halt Genius 2
    716: ('bool_word', 0, 12),  # MA-3B1 роликовый стол (1)
    717: ('bool_word', 0, 13),  # MA-3B1 роликовый стол (2)
    718: ('bool_word', 0, 14),  # Открыта дверь оборудования
    719: ('bool_word', 0, 15),  # Открыта защитная дверь
    720: ('bool_word', 2, 1),   # Ошибка закрытия решетки
    721: ('bool_word', 2, 2),   # Ошибка открытия решетки
    722: ('bool_word', 2, 3),   # Genius в ручном режиме
    723: ('bool_word', 2, 4),   # Отсутствие сжатого воздуха
    724: ('bool_word', 2, 6),   # Нет выпуска цикла из Genius 2
}
LOST_CONNECTION_ID_1 = 700

# ---------- Маппинг для PLC 2 (ID 750..774) ----------
SIGNAL_MAP_2 = {
    # Информационные
    751: ('bool', 35, 2),   # Automatik/manual
    752: ('bool', 35, 3),   # ReadyToWork
    753: ('bool', 35, 4),   # Starting
    754: ('bool', 110, 0),  # ConnectLost

    # Аварийные биты (сдвиг битов по расшифровке)
    755: ('bool_word', 0, 0),   # SS01-1F1 RM
    756: ('bool_word', 0, 2),   # SS01-17F1 MSS главный вал
    757: ('bool_word', 0, 3),   # SS01-17F2 MSS вспом. вал
    758: ('bool_word', 0, 4),   # SS01-17Q1 плавный пуск
    759: ('bool_word', 0, 5),   # SS01-18F1 MSS Конвейер щетины
    760: ('bool_word', 0, 6),   # Аварийный выключатель на линии убоя
    761: ('bool_word', 0, 7),   # NH-Кнопка 1
    762: ('bool_word', 0, 8),   # NH-Кнопка 2
    763: ('bool_word', 0, 9),   # Старт заблокирован
    764: ('bool_word', 0, 10),  # Not-Halt bei DBA
    765: ('bool_word', 0, 11),  # Not-Halt Genius 1
    766: ('bool_word', 0, 13),  # MA-3B1 роликовый стол (1)
    767: ('bool_word', 0, 14),  # MA-3B1 роликовый стол (2)
    768: ('bool_word', 0, 15),  # Открыта дверь оборудования? (проверить)
    769: ('bool_word', 2, 0),   # Ошибка закрытия решетки
    770: ('bool_word', 2, 1),   # Ошибка открытия решетки
    771: ('bool_word', 2, 2),   # Genius в ручном режиме
    772: ('bool_word', 2, 3),   # Отсутствие сжатого воздуха
    773: ('bool_word', 2, 5),   # Нет выпуска цикла из Genius 1
}
LOST_CONNECTION_ID_2 = 750

# Выбор маппинга по PLC_ID
if PLC_ID == 1:
    SIGNAL_MAP = SIGNAL_MAP_1
    LOST_CONNECTION_ID = LOST_CONNECTION_ID_1
elif PLC_ID == 2:
    SIGNAL_MAP = SIGNAL_MAP_2
    LOST_CONNECTION_ID = LOST_CONNECTION_ID_2
else:
    raise ValueError("PLC_ID must be 1 or 2")

# Функции парсинга (остаются без изменений)
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