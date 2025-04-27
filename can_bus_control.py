
import can

from config import CAN_CHANNEL, CAN_INTERFACE
from objects.dobiss_entity import DobissEntity
from config.dobiss_entity_config import DOBISS_LIGHTS_CONFIG, DOBISS_MODULES
from objects.dobiss_module import DobissModule

"""
I made use of the  DSD TECH USB to CAN-bus SH-C30A.
I set the bitrate to 125000 at device detection with a udev rule.
    - Create script /opt/setup_can.sh
    - Create udev rule /etc/udev/rules.d/90-can0.rules
    - Reload the rules 'sudo udevadm control --reload'
"""


# Create a dict of all dobiss entities
# Read the status of all doviss entities
# create a switch option to flip the status
# create dimmer support


def get_can_bus():
    return can.interface.Bus(channel=CAN_CHANNEL, interface=CAN_INTERFACE)

def can_bus_control():
    bus = can.interface.Bus(channel=CAN_CHANNEL, interface=CAN_INTERFACE)

    dobiss_entity = DobissEntity.config_to_dobiss_entity(DOBISS_LIGHTS_CONFIG["Trap"], "Trap")

    # Prepare the message
    msg = can.Message(
        arbitration_id=dobiss_entity.module_can_id,
        data=dobiss_entity.get_msg_to_set_status(1),
        is_extended_id=True  # important! your ID is 29 bits (extended frame)
    )

    # Send the message
    try:
        bus.send(msg)
        print("Message sent successfully!")
    except can.CanError as e:
        print(f"Message NOT sent: {e}")
    finally:
        bus.shutdown()

    try:
        # Wait for a message (timeout in seconds)
        response = bus.recv(timeout=1.0)

        if response is None:
            print("No response received within timeout.")
        else:
            print(f"Received message: ID=0x{response.arbitration_id:X}, Data={response.data.hex()}, ExtendedID={response.is_extended_id}")

    except can.CanError as e:
        print(f"Error receiving message: {e}")


def update_status_of_entities(dobiss_entities):
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
            print(f"Received packet: ID=0x{response.arbitration_id:X}, Data={response.data.hex()}")
        print(complete_response.hex())
        parse_status_response(complete_response, dobiss_entities, module.module_number)

    bus.shutdown()


def parse_status_response(response: bytes, dobiss_entities, module_number: int):
    output_number = 0
    for response_byte in response:
        if response_byte == 0xff:
            break  # no more outputs
        else:
            output_number += 1
            if output_number in dobiss_entities[module_number]:
                dobiss_entities[module_number][output_number].current_brightness = response_byte


def pivot_entity_dict(dobiss_entities):
    module_output_dict = {}
    for name in dobiss_entities:
        entity = dobiss_entities[name]
        if entity.module_number not in module_output_dict:
            module_output_dict[entity.module_number] = {}
        module_output_dict[entity.module_number][entity.output] = entity
    return module_output_dict


def test_send_msg():
    # Set up the CAN bus
    bus = can.interface.Bus(channel='can0', interface='socketcan')

    # Prepare the message
    msg = can.Message(
        arbitration_id=0x00400101,  # 4194562 decimal
        data=bytes.fromhex('01ff'),
        # 010100ffff64ffff
        # 010101FFFF64FFFF
        # AABBCCDDEEFFGGHH
        # AA: Module
        # BB: Relay (tellen vanaf 0, dus -1)
        # CC: 00 for off, 01 for on
        # DD: Steeds FF
        # EE: Steeds FF
        # FF: Steeds 64
        # GG: Steeds FF
        # HH: Steeds FF
        is_extended_id=True
    )

    # Send the message
    try:
        bus.send(msg)
        print("Message sent successfully!")
    except can.CanError as e:
        print(f"Message NOT sent: {e}")
    finally:
        bus.shutdown()


if __name__ == '__main__':
    test_send_msg()
    # update_status_of_entities(None)
    # c_resp = b'\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\xff\xff\xff\xff'
    # dobiss_entities = {}
    # for name in DOBISS_LIGHTS_CONFIG:
    #     dobiss_entities[name] = DobissEntity.config_to_dobiss_entity(DOBISS_LIGHTS_CONFIG[name], name)
    # dobiss_entities = pivot_entity_dict(dobiss_entities)
    # parse_status_response(c_resp, dobiss_entities, 4)

