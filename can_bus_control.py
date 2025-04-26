
import can

from config import CAN_CHANNEL, CAN_INTERFACE

"""
I made use of the  DSD TECH USB to CAN-bus SH-C30A.
I set the bitrate to 125000 at device detection with a udev rule.
    - Create script /opt/setup_can.sh
    - Create udev rule /etc/udev/rules.d/90-can0.rules
    - Reload the rules 'sudo udevadm control --reload'
"""


def can_bus_control():
    bus = can.interface.Bus(channel=CAN_CHANNEL, interface=CAN_INTERFACE, bitrate=125000,
                            receive_own_messages=True,can_filters=[
        {"can_id": 0x0002FF01, "can_mask": 0x1FFFFFFF, "extended": True},  # Reply to SET
        {"can_id": 0x01FDFF01, "can_mask": 0x1FFFFFFF, "extended": True},  # Reply to GET
    ])
    notifier = can.Notifier(bus)


def test_send_msg():
    # Set up the CAN bus
    bus = can.interface.Bus(channel='can0', interface='socketcan')

    # Prepare the message
    msg = can.Message(
        arbitration_id=0x00400102,  # 4194562 decimal
        data=bytes.fromhex('010101FFFF64FFFF'),
        is_extended_id=True  # important! your ID is 29 bits (extended frame)
    )

    # Send the message
    try:
        bus.send(msg)
        print("Message sent successfully!")
    except can.CanError as e:
        print(f"Message NOT sent: {e}")


if __name__ == '__main__':
    test_send_msg()
