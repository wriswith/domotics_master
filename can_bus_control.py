
import can
from can import Message

from config.config import CAN_CHANNEL, CAN_INTERFACE, TEST_RUN
from config.dobiss_entity_config import DOBISS_MODULES
from logger import logger
from objects.dobiss_module import DobissModule

# from objects.dobiss_entity import DobissEntity
# from config.dobiss_entity_config import DOBISS_MODULES, DOBISS_DIMMER
# from objects.dobiss_module import DobissModule

"""
I made use of the  DSD TECH USB to CAN-bus SH-C30A.
I set the bitrate to 125000 at device detection with a udev rule.
    - Create script /opt/setup_can.sh
    - Create udev rule /etc/udev/rules.d/90-can0.rules
    - Reload the rules 'sudo udevadm control --reload'
"""

_bus = None


def get_can_bus():
    global _bus
    if _bus is None:
        return can.interface.Bus(channel=CAN_CHANNEL, interface=CAN_INTERFACE)
    else:
        return _bus


def send_dobiss_command(module_id, msg_data):
    if not TEST_RUN:
        bus = get_can_bus()
        msg = create_can_message(module_id, msg_data)
        send_can_message(msg, bus)


def create_can_message(arbitration_id: int, data: bytes):
    return can.Message(
        arbitration_id=arbitration_id,
        data=data,
        is_extended_id=True
    )


def send_can_message(message: Message, bus: can.interface.Bus):
    """
    Send a CAN message onto the bus. Responses are not supported by this function.
    :param message:
    :param bus:
    :return:
    """
    try:
        bus.send(message)
    except can.CanError as e:
        logger.error(f"Message NOT sent: {e}")
        raise e
    finally:
        bus.shutdown()


def get_modules_statuses():
    """
    Get the status of all outputs of every object and update the entity objects accordingly.
    :return:
    """
    result = {}
    bus = get_can_bus()
    for module_number in DOBISS_MODULES:
        module = DobissModule.config_to_dobiss_module(DOBISS_MODULES[module_number])
        msg = can.Message(arbitration_id=module.get_status_can_id(),
                          data=module.get_status_msg(),
                          is_extended_id=True)
        bus.send(msg)
        complete_response = b''
        for i in range(module.nr_response_messages):
            response = bus.recv(timeout=0.4)  # small timeout per recv
            if response is None:
                raise Exception(f"Failed to get a response when requesting status from module {module.module_number}.")

            complete_response += response.data
            logger.debug(f"Received packet: ID=0x{response.arbitration_id:X}, Data={response.data.hex()}")
        logger.debug(f"Complete response: {complete_response.hex()}")
        result[module.module_number] = complete_response
    return result

if __name__ == '__main__':
    bus = get_can_bus()
    bus.send(create_can_message(0x00400102, b'\x01\x01\x01\xff\xff\x00\xff\xff'))
    bus.shutdown()
