import logging

ALLOW_NEW_CIRCUIT_IDS = False
DISCOVERY_MODE = False  # After 3+ seconds button press, you will be prompted for name.
DISCOVERY_OUTPUT_FILE = "../button_discovery.txt"

SERIAL_PORT = 'COM8'

SERIAL_BAUD_RATE = 115200
ACTIVE_PICO_PINS = [13, 14, 15]

CAN_INTERFACE = "socketcan"
CAN_CHANNEL = "can0"

SHORT_PRESS_CUTOFF = 1.000  # number of seconds before a button press stops being a short

CONSOLE_LOG_LEVEL = logging.DEBUG
