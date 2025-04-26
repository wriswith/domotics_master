
ALLOW_NEW_CIRCUIT_IDS = True
DISCOVERY_MODE = True  # After 3+ seconds button press, you will be prompted for name.
DISCOVERY_OUTPUT_FILE = "button_discovery.txt"

SERIAL_PORT = 'COM8'

SERIAL_BAUD_RATE = 115200
ACTIVE_PICO_PINS = [13, 14, 15]

CAN_INTERFACE = "socketcan"
CAN_CHANNEL = "can0"
