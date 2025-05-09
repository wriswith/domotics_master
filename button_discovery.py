from threading import Thread

from one_wire_reader import serial_reader_thread


def button_discovery():
    messages_received = []
    serial_thread = Thread(target=serial_reader_thread, args=(messages_received,))
    serial_thread.start()


if __name__ == '__main__':
    button_discovery()
