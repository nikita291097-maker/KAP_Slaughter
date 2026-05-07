import time
import paho.mqtt.client as mqtt

from core.logger import log
from core.config import *

from handlers.effective_handler import handle_effective


def on_connect(client, userdata, flags, rc):

    from core import state

    state.mqtt_ok = (rc == 0)

    log.info(f"Connected to MQTT: {rc}")

    client.subscribe(
        "event/+/effective",
        qos=1
    )


def on_disconnect(client, userdata, rc):

    from core import state

    state.mqtt_ok = False

    log.warning(f"MQTT disconnected: {rc}")


def on_message(client, userdata, msg):

    topic = msg.topic

    if "/effective" in topic:
        handle_effective(msg)


def start_mqtt():

    client = mqtt.Client()

    client.username_pw_set(
        MQTT_USER,
        MQTT_PASSWORD
    )

    client.reconnect_delay_set(
        min_delay=1,
        max_delay=30
    )

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    while True:

        try:

            client.connect(
                MQTT_HOST,
                MQTT_PORT,
                60
            )

            log.info("Service started")

            client.loop_forever()

        except Exception as e:

            log.error(f"MQTT error: {e}")

            time.sleep(5)