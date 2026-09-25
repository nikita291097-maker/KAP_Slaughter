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

    # Аварийные сигналы
    # DB_Meldungen.Meldung[0]
    705: ('bool_word', 0, 1),   # SS01-1F1 RM Защита от перенапряжения
    # 706 — SS01-17F1 MSS главный вал — НЕ ИСПОЛЬЗУЕТСЯ
    707: ('bool_word', 0, 3),   # SS01-17F2 MSS Отключен защитный автомат двигателя
    708: ('bool_word', 0, 4),   # SS01-17Q1 Ошибка плавного пуска двигателя
    # 709 — SS01-18F1 MSS Конвейер щетины — НЕ ИСПОЛЬЗУЕТСЯ
    710: ('bool_word', 0, 6),   # Нажат аварийный выключатель на линии убоя
    711: ('bool_word', 0, 7),   # NH01-1A1-1S1 NH-Нажата аварийная кнопка 1
    712: ('bool_word', 0, 8),   # NH02-1A1-1S1 NH-Нажата аварийная кнопка 2
    713: ('bool_word', 0, 9),   # Старт заблокирован механическим ключом
    714: ('bool_word', 0, 10),  # Шпарчан не готов
    715: ('bool_word', 0, 11),  # Обезволашивающая машина 2 не готова
    # 716 — MA-3B1 роликовый стол — НЕ ИСПОЛЬЗУЕТСЯ
    # 717 — MA-3B1 роликовый стол — НЕ ИСПОЛЬЗУЕТСЯ
    718: ('bool_word', 0, 14),  # Открыта дверь машины
    719: ('bool_word', 0, 15),  # Открыта защитная дверь между машинами

    # DB_Meldungen.Meldung[1]
    # 720 — не используется
    # 721 — не используется
    722: ('bool_word', 2, 3),   # Обезволашивающая машина в ручном режиме
    723: ('bool_word', 2, 4),   # Отсутствие сжатого воздуха
    724: ('bool_word', 2, 6),   # Нет готовности работы в цикле с обезволашивающей машиной 2
}
LOST_CONNECTION_ID_1 = 700

# ---------- Маппинг для PLC 2 (ID 750..774) ----------
SIGNAL_MAP_2 = {
    # Информационные
    751: ('bool', 35, 2),   # Automatik/manual
    752: ('bool', 35, 3),   # ReadyToWork
    753: ('bool', 35, 4),   # Starting
    754: ('bool', 110, 0),  # ConnectLost

    # DB_Meldungen.Meldung[0]
    755: ('bool_word', 0, 1),   # SS01-1F1 RM Защита от перенапряжения
    # 756 — не используется
    757: ('bool_word', 0, 3),   # SS01-17F2 MSS Отключен защитный автомат двигателя
    758: ('bool_word', 0, 4),   # SS01-17Q1 Ошибка плавного пуска двигателя
    # 759 — не используется
    760: ('bool_word', 0, 6),   # Нажат аварийный выключатель на линии убоя
    761: ('bool_word', 0, 7),   # NH01-1A1-1S1 NH-Нажата аварийная кнопка 1
    762: ('bool_word', 0, 8),   # NH02-1A1-1S1 NH-Нажата аварийная кнопка 2
    763: ('bool_word', 0, 9),   # Старт заблокирован механическим ключом
    764: ('bool_word', 0, 10),  # Шпарчан не готов
    765: ('bool_word', 0, 11),  # Обезволашивающая машина 1 не готова
    # 766 — не используется
    # 767 — не используется
    768: ('bool_word', 0, 14),  # Открыта защитная дверь между машинами

    # DB_Meldungen.Meldung[1]
    # 769 — не используется
    # 770 — не используется
    771: ('bool_word', 2, 2),   # Обезволашивающая машина в ручном режиме
    772: ('bool_word', 2, 3),   # Отсутствие сжатого воздуха
    773: ('bool_word', 2, 5),   # Нет готовности работы в цикле с обезволашивающей машиной 1
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