from queue import Queue
from threading import Thread

import time

from serial import Serial, SerialException

from config.config import DISCOVERY_MODE, DISCOVERY_OUTPUT_FILE, SERIAL_PORT, SERIAL_BAUD_RATE, ACTIVE_PICO_PINS, \
    MIN_IDENTICAL_ONE_WIRE_MESSAGES
from config.constants import SWITCH_ACTION_PRESS, SWITCH_ACTION_HOLD, SWITCH_ACTION_RELEASE
from logger import logger
from objects.one_wire_message import OneWireMessage, MT_INVALID, MT_CIRCUIT_ID, MT_HEARTBEAT
from objects.switch_event import SwitchEvent


def serial_reader_thread(message_queues: dict):
    """
    Receive the messages from the pico pi and put them into the "queue" for handling.
    :param message_queues:
    :return:
    """
    active_pins = list(message_queues.keys())
    try:
        # Open serial connection
        with Serial(SERIAL_PORT, SERIAL_BAUD_RATE, timeout=1) as ser:
            buffer = ""
            logger.info(f"Listening on {SERIAL_PORT} at {SERIAL_BAUD_RATE} baud...")
            time.sleep(2)  # Wait for Pico to reset after opening port (important for some boards)

            while True:
                if ser.in_waiting > 0:
                    try:
                        line = ser.readline().decode('utf-8').strip()
                    except UnicodeDecodeError as e:
                        logger.error(f"Read error on UART ({e})")
                        continue
                    buffer += line

                    # every message ends with '###'. If this pattern is detected, there should be a message in the buffer.
                    if "###" in buffer:
                        parts = buffer.split("###")
                        buffer = parts.pop()  # add last empty or incomplete message back into buffer.
                        for raw_message in parts:
                            message = OneWireMessage(raw_message)  # parse the raw message to a message object.
                            if message.pin in active_pins:
                                message_queues[message.pin].append(message)
                            else:
                                raise Exception(f"Received message from unexpected pin. ({raw_message})")

                time.sleep(0.01)

    except SerialException as e:
        logger.error(f"Serial error: {e}")
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")


def button_released(button_down_message: OneWireMessage, release_message: OneWireMessage, switch_event_queue: Queue):
    switch_event_queue.put(SwitchEvent(circuit_id=button_down_message.circuit_id,
                                       action=SWITCH_ACTION_RELEASE,
                                       duration=(release_message.frame_number - button_down_message.frame_number) * 0.05))
    if DISCOVERY_MODE:
        discovery_mode(button_down_message, release_message)

    logger.debug(f"Released button {button_down_message.get_button_label()}")


def discovery_mode(button_down_message, release_message):
    """
    Execution will block after long press on new button to allow logging the new circuit_id with a user-friendly name
    to a log file
    """
    if (button_down_message.circuit_id_is_unknown and
            (release_message.frame_number - button_down_message.frame_number) * 0.05 > 3):
        button_name = input("Enter the name for the released button and press enter.")
        if len(button_name) > 0:
            with open(DISCOVERY_OUTPUT_FILE, 'at') as discovery_file:
                discovery_file.write(f'"{button_down_message.circuit_id}": "{button_name}",\r\n')
    logger.debug(f"Released button {button_down_message.get_button_label()}")


def button_pressed(message: OneWireMessage, switch_event_queue: Queue):
    switch_event_queue.put(SwitchEvent(circuit_id=message.circuit_id,
                                       action=SWITCH_ACTION_PRESS,
                                       duration=0))
    logger.debug(f"Button pressed ({message.get_button_label()})")


def button_held(button_down_message: OneWireMessage, current_message: OneWireMessage, switch_event_queue: Queue):
    switch_event_queue.put(SwitchEvent(circuit_id=button_down_message.circuit_id,
                                       action=SWITCH_ACTION_HOLD,
                                       duration=(current_message.frame_number - button_down_message.frame_number) * 0.07))
    logger.debug(f"Button held ({button_down_message.get_button_label()})")


def is_divergent_message(messages, message):
    divergent_message = False
    for previous_message in messages:
        if previous_message.message_type != message.message_type:
            divergent_message = True
        elif message.message_type == MT_CIRCUIT_ID and message.circuit_id != previous_message.circuit_id:
            divergent_message = True
    return divergent_message


def parse_message(message: OneWireMessage, button_down_message: OneWireMessage, switch_event_queue: Queue):
    if message.message_type == MT_HEARTBEAT:
        if button_down_message is not None:
            button_released(button_down_message, message, switch_event_queue)
        return None
    elif message.message_type == MT_CIRCUIT_ID:
        if button_down_message is None:
            button_pressed(message, switch_event_queue)
            return message
        elif message.circuit_id != button_down_message.circuit_id:
            button_released(button_down_message, message, switch_event_queue)
            button_pressed(message, switch_event_queue)
            return message
        else:
            button_held(button_down_message, message, switch_event_queue)
            return button_down_message
    else:
        raise Exception(f"This message type is not implemented: {message.message_type}. ({message})")


def message_handler(message_queue: list, switch_event_queue: Queue):
    button_down_message = None
    previous_loop = []
    while True:
        while len(message_queue) > 0:
            message = message_queue.pop(0)
            if message.message_type == MT_INVALID:
                logger.debug(f"invalid_msg ({message.pin}_{message.circuit_id})")
                pass  # Drop invalid messages
            else:
                if is_divergent_message(previous_loop, message):
                    previous_loop = []
                else:
                    previous_loop.append(message)

                if len(previous_loop) >= MIN_IDENTICAL_ONE_WIRE_MESSAGES:
                    button_down_message = parse_message(message, button_down_message, switch_event_queue)
                    previous_loop = []

        time.sleep(0.02)


def one_wire_reader(active_pins: list, switch_event_queue: Queue):
    logger.debug(f"Starting receiver thread for msgs from microcontroller.")
    # Start reading messages from the pi pico
    message_queues = {}
    message_handler_threads = {}
    for pin in active_pins:
        message_queues[pin] = []
        message_handler_threads[pin] = Thread(target=message_handler, args=(message_queues[pin], switch_event_queue, ))
        message_handler_threads[pin].start()

    serial_thread = Thread(target=serial_reader_thread, args=(message_queues, ))
    serial_thread.start()


if __name__ == '__main__':
    one_wire_reader(ACTIVE_PICO_PINS, Queue())
