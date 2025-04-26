
import can

from config import CAN_CHANNEL, CAN_INTERFACE
from dobiss_entity import DobissEntity
from dobiss_entity_config import DOBISS_LIGHTS_CONFIG

"""
I made use of the  DSD TECH USB to CAN-bus SH-C30A.
I set the bitrate to 125000 at device detection with a udev rule.
    - Create script /opt/setup_can.sh
    - Create udev rule /etc/udev/rules.d/90-can0.rules
    - Reload the rules 'sudo udevadm control --reload'
"""


def can_bus_control():
    bus = can.interface.Bus(channel=CAN_CHANNEL, interface=CAN_INTERFACE)

    dobiss_entity = DobissEntity.config_to_dobiss_entity(DOBISS_LIGHTS_CONFIG["Trap"], "Trap")

    # Prepare the message
    msg = can.Message(
        arbitration_id=dobiss_entity.module_id,
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


def test_send_msg():
    # Set up the CAN bus
    bus = can.interface.Bus(channel='can0', interface='socketcan')

    # Prepare the message
    msg = can.Message(
        arbitration_id=0x00400102,  # 4194562 decimal
        data=bytes.fromhex('010101FFFF64FFFF'),
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


if __name__ == '__main__':
    test_send_msg()
