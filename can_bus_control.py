
import can
from can import Message

from config.config import CAN_CHANNEL, CAN_INTERFACE
from objects.dobiss_entity import DobissEntity
from config.dobiss_entity_config import DOBISS_MODULES, DOBISS_DIMMER
from objects.dobiss_module import DobissModule

"""
I made use of the  DSD TECH USB to CAN-bus SH-C30A.
I set the bitrate to 125000 at device detection with a udev rule.
    - Create script /opt/setup_can.sh
    - Create udev rule /etc/udev/rules.d/90-can0.rules
    - Reload the rules 'sudo udevadm control --reload'
"""


def get_can_bus():
    return can.interface.Bus(channel=CAN_CHANNEL, interface=CAN_INTERFACE)


def switch_dobiss_entity(entity: DobissEntity):
    """
    Switch the status of the entity (reverse on or off)
    :param entity:
    :return:
    """
    bus = get_can_bus()
    msg = create_can_message(entity.module_id, entity.get_msg_to_switch_status())
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
        return True
    except can.CanError as e:
        print(f"Message NOT sent: {e}")
        raise e
    finally:
        bus.shutdown()


def update_status_of_entities(dobiss_entities):
    """
    Get the status of all outputs of every object and update the entity objects accordingly.
    :param dobiss_entities:
    :return:
    """
    dobiss_entities = pivot_entity_dict(dobiss_entities)
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
            # print(f"Received packet: ID=0x{response.arbitration_id:X}, Data={response.data.hex()}")
        # print(f"Complete response: {complete_response.hex()}")
        parse_status_response(complete_response, dobiss_entities, module.module_number)

    bus.shutdown()


def parse_status_response(response: bytes, dobiss_entities, module_number: int):
    """
    Parse the response of a module to the status of the individual outputs.
    :param response:
    :param dobiss_entities:
    :param module_number:
    :return:
    """
    output_number = 0
    for response_byte in response:
        if response_byte == 0xff:
            break  # no more outputs
        else:
            output_number += 1
            if output_number in dobiss_entities[module_number]:
                entity = dobiss_entities[module_number][output_number]
                if entity.dobiss_type == DOBISS_DIMMER:
                    if response_byte == 0:
                        entity.current_status = 0
                        entity.current_brightness = 0
                    else:
                        entity.current_status = 1
                        entity.current_brightness = response_byte
                else:
                    dobiss_entities[module_number][output_number].current_status = response_byte


def pivot_entity_dict(dobiss_entities):
    """
    Return a dict with module and output as key instead of entity_name.
    :param dobiss_entities:
    :return:
    """
    module_output_dict = {}
    for name in dobiss_entities:
        entity = dobiss_entities[name]
        if entity.module_number not in module_output_dict:
            module_output_dict[entity.module_number] = {}
        module_output_dict[entity.module_number][entity.output] = entity
    return module_output_dict
