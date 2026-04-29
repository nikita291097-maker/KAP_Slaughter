import json
import psycopg2
import paho.mqtt.client as mqtt
from datetime import datetime

# =========================
# DB CONNECTION
# =========================
conn = psycopg2.connect(
    host="172.17.0.1",
    port=5432,
    dbname="kap_slaughter",
    user="postgres",
    password="postgres"
)
conn.autocommit = True

print("DB connected", flush=True)


# =========================
# HELPERS
# =========================
def save_raw(topic, payload):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO mqtt_raw (topic, payload, ts)
                VALUES (%s, %s, %s)
            """, (topic, json.dumps(payload), datetime.utcnow()))
    except Exception as e:
        print("RAW INSERT ERROR:", e, flush=True)


def ensure_line_exists(line_id):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO lines (line_id)
                VALUES (%s)
                ON CONFLICT (line_id) DO NOTHING
            """, (line_id,))
    except Exception as e:
        print("LINE UPSERT ERROR:", e, flush=True)


def ensure_event_exists(event_id):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO event_dictionary (event_id)
                VALUES (%s)
                ON CONFLICT (event_id) DO NOTHING
            """, (event_id,))
    except Exception as e:
        print("EVENT UPSERT ERROR:", e, flush=True)


def handle_factory_state(data):
    try:
        ts = data["timestamp"]

        for line in data["payload"]:
            line_id = line["id"]
            state = line["state"]
            speed = line["speed"]

            ensure_line_exists(line_id)

            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO line_state_current (line_id, state, speed, ts)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (line_id)
                    DO UPDATE SET
                        state = EXCLUDED.state,
                        speed = EXCLUDED.speed,
                        ts = EXCLUDED.ts,
                        updated_at = now()
                """, (line_id, state, speed, ts))

        print(f"[LINES] updated {len(data['payload'])} lines", flush=True)

    except Exception as e:
        print("LINE STATE ERROR:", e, flush=True)


def decode_events(arr):
    active = set()
    for word_index, word in enumerate(arr):
        for bit in range(16):
            if word & (1 << bit):
                event_id = word_index * 16 + bit + 1
                active.add(event_id)
    return active


prev_events = set()


def handle_events(data):
    global prev_events

    try:
        ts = data["timestamp"]
        current = decode_events(data["events_actual"])

        raised = current - prev_events
        cleared = prev_events - current

        with conn.cursor() as cur:
            for eid in raised:
                ensure_event_exists(eid)

                # история
                cur.execute("""
                    INSERT INTO event_log (event_id, event_phase, ts, source)
                    VALUES (%s, 'RAISED', %s, 'snapshot')
                """, (eid, ts))

                # текущее состояние
                cur.execute("""
                    INSERT INTO event_state_current (event_id, is_active, ts)
                    VALUES (%s, TRUE, %s)
                    ON CONFLICT (event_id)
                    DO UPDATE SET
                        is_active = TRUE,
                        ts = EXCLUDED.ts,
                        updated_at = now()
                """, (eid, ts))

            for eid in cleared:
                ensure_event_exists(eid)

                cur.execute("""
                    INSERT INTO event_log (event_id, event_phase, ts, source)
                    VALUES (%s, 'CLEARED', %s, 'snapshot')
                """, (eid, ts))

                cur.execute("""
                    INSERT INTO event_state_current (event_id, is_active, ts)
                    VALUES (%s, FALSE, %s)
                    ON CONFLICT (event_id)
                    DO UPDATE SET
                        is_active = FALSE,
                        ts = EXCLUDED.ts,
                        updated_at = now()
                """, (eid, ts))

        print(f"[EVENTS] active={len(current)} raised={len(raised)} cleared={len(cleared)}", flush=True)

        prev_events = current

    except Exception as e:
        print("EVENT ERROR:", e, flush=True)


# =========================
# MQTT CALLBACKS
# =========================
def on_connect(client, userdata, flags, rc):
    print(f"MQTT connected, code={rc}", flush=True)
    client.subscribe("#")
    print("Subscribed to #", flush=True)


def on_message(client, userdata, msg):
    print("RECEIVED:", msg.topic, flush=True)

    try:
        payload = msg.payload.decode()

        # фикс бага подрядчика
        if payload.endswith("e"):
            payload = payload[:-1]

        data = json.loads(payload)

        save_raw(msg.topic, data)

        if msg.topic == "factory/state":
            handle_factory_state(data)

        elif msg.topic in ["factory/events", "events/state"]:
            handle_events(data)

    except Exception as e:
        print("MESSAGE ERROR:", e, flush=True)


# =========================
# MQTT CLIENT
# =========================
print("Connecting to MQTT...", flush=True)

client = mqtt.Client(protocol=mqtt.MQTTv311)
client.username_pw_set("apk-asu", "DemPassWd")

client.on_connect = on_connect
client.on_message = on_message

client.connect("10.47.156.240", 1883)

client.loop_forever()