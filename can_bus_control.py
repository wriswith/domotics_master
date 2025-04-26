
import can

from config import CAN_CHANNEL, CAN_INTERFACE
from dobiss_entity import DobissEntity
from dobiss_entity_config import DOBISS_LIGHTS_CONFIG, DOBISS_MODULES
from dobiss_module import DobissModule

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
    bus = get_can_bus()
    for module_number in DOBISS_MODULES:
        if module_number == 1:
            module = DobissModule.config_to_dobiss_module(DOBISS_MODULES[module_number])
            msg = can.Message(arbitration_id=module.get_status_can_id(),
                              data=module.get_status_msg(),
                              is_extended_id=True)
            bus.send(msg)
            break



    # for name in dobiss_entities:

    bus.shutdown()


def test_send_msg():
    # Set up the CAN bus
    bus = can.interface.Bus(channel='can0', interface='socketcan')

    # Prepare the message
    msg = can.Message(
        arbitration_id=0x00200401,  # 4194562 decimal
        data=bytes.fromhex('04ff'),
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
