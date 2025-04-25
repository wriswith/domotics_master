from threading import Thread

import serial
import time

from config import DISCOVERY_MODE, DISCOVERY_OUTPUT_FILE, SERIAL_PORT, BAUD_RATE, ACTIVE_PINS
from one_wire_message import OneWireMessage, MT_INVALID, MT_CIRCUIT_ID, MT_HEARTBEAT


def serial_reader_thread(message_queues: dict):

    active_pins = list(message_queues.keys())
    try:
        # Open serial connection
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            buffer = ""
            print(f"Listening on {SERIAL_PORT} at {BAUD_RATE} baud...")
            time.sleep(2)  # Wait for Pico to reset after opening port (important for some boards)

            while True:

                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    buffer += line
                    if "###" in buffer:
                        parts = buffer.split("###")
                        buffer = parts.pop()  # add last empty of incomplete message to buffer.
                        for raw_message in parts:
                            message = OneWireMessage(raw_message)
                            if message.pin in active_pins:
                                message_queues[message.pin].append(message)
                            else:
                                raise Exception(f"Received message from unexpected pin. ({raw_message})")

                time.sleep(0.01)

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("Interrupted by user.")


def circuit_id_released(button_down_message: OneWireMessage, release_message: OneWireMessage):
    if (DISCOVERY_MODE and button_down_message.circuit_id_is_unknown and
            (release_message.frame_number - button_down_message.frame_number) * 0.05 > 3):
        button_name = input("Enter the name for the released button and press enter.")
        if len(button_name) > 0:
            with open(DISCOVERY_OUTPUT_FILE, 'at') as discovery_file:
                discovery_file.write(f'"{button_down_message.circuit_id}": "{button_name}",\r\n')
    print(f"Released button {button_down_message.get_button_label()}")


def button_pressed(message: OneWireMessage):
    print(f"Button pressed ({message.get_button_label()})")

def button_held(button_down_message: OneWireMessage, current_message: OneWireMessage):
    print(f"Button held ({current_message.get_button_label()})")

def is_divergent_message(messages, message):
    divergent_message = False
    for previous_message in messages:
        if previous_message.message_type != message.message_type:
            divergent_message = True
        elif message.message_type == MT_CIRCUIT_ID and message.circuit_id != previous_message.circuit_id:
            divergent_message = True
    return divergent_message


def parse_message(message: OneWireMessage, button_down_message: OneWireMessage):
    if message.message_type == MT_HEARTBEAT:
        if button_down_message is not None:
            circuit_id_released(button_down_message, message)
            return None
    elif message.message_type == MT_CIRCUIT_ID:
        if button_down_message is None:
                button_pressed(message)
                return message
        elif message.circuit_id != button_down_message.circuit_id:
            circuit_id_released(button_down_message, message)
            button_pressed(message)
            return message
        else:
            button_held(button_down_message, message)
            return button_down_message
    else:
        raise Exception(f"This message type is not implemented: {message.message_type}. ({message})")


def message_handler(message_queue: list):
    button_down_message = None
    min_identical_msg = 2
    previous_loop = []
    while True:
        while len(message_queue) > 0:
            message = message_queue.pop(0)
            if message.message_type == MT_INVALID:
                print(f"invalid_msg ({message.pin}_{message.circuit_id})")
                pass  # Drop invalid messages
            else:
                if is_divergent_message(previous_loop, message):
                    previous_loop = []
                else:
                    previous_loop.append(message)

                if len(previous_loop) >= min_identical_msg:
                    button_down_message = parse_message(message, button_down_message)
                    previous_loop = []

        time.sleep(0.02)


def one_wire_reader(active_pins: list):
    # Start reading messages from the pi pico
    message_queues = {}
    message_handler_threads = {}
    for pin in active_pins:
        message_queues[pin] = []
        message_handler_threads[pin] = Thread(target=message_handler, args=(message_queues[pin], ))
        message_handler_threads[pin].start()

    serial_thread = Thread(target=serial_reader_thread, args=(message_queues, ))
    serial_thread.start()


if __name__ == '__main__':
    one_wire_reader(ACTIVE_PINS)
