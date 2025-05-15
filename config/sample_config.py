import logging

ALLOW_NEW_CIRCUIT_IDS = False
DISCOVERY_MODE = False  # After 3+ seconds button press, you will be prompted for name.
DISCOVERY_OUTPUT_FILE = "../button_discovery.txt"

SERIAL_PORT = 'COM8'

SERIAL_BAUD_RATE = 115200
ACTIVE_PICO_PINS = [13, 14, 15]

CAN_INTERFACE = "socketcan"
CAN_CHANNEL = "can0"

MIN_IDENTICAL_ONE_WIRE_MESSAGES = 1  # Depending on the slaves and the bus, there can be frequent invalid messages. This variable can be used to filter noise at the cost of responsiveness.

BUTTON_LOCKOUT_PERIOD = 0.4  # Ignore buttons after release to avoid double click.

SHORT_PRESS_CUTOFF = 1.000  # number of seconds before a button press stops being a short

CONSOLE_LOG_LEVEL = logging.DEBUG

MQTT_BROKER = "example.com"
MQTT_PORT = 8883
MQTT_USERNAME = ""
MQTT_PASSWORD = ""

TEST_RUN = False  # Disable Can output for testing
