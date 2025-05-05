# dobiss_one_wire
This repository is a solution to replace the Dobiss master that forms the heart of the domotics system.
It has a hardware component to drive communicate with the lighting buttons, as well as a software side to configure the system (without using the proprietary Dobiss software). 

## Parasitic One Wire
Dobiss uses a parasitic one wire bus to connect the lighting switches to the control modules. This one wire bus consists 
of a single twisted pair in a shielded UTP cable that passes every lighting button in the bus. Behind every lighting button 
there is a circuit board that is connected to both the twisted pair and the lighting button. When the lighting button is 
pressed, the circuit board will broadcast its unique ID on the bus.

The 'parasitic' part of the one wire bus means that the slaves are connected only with 2 wires, being a ground wire and 
a wire that handles both data and the connection to the powersupply.

## Communication protocol
The protocol works with one master and many slave devices. The master initiates communication by pulling the bus down for 
600 µs. This is the reset pulse. If no slave responds, the master will sleep for 50 ms and send another reset pulse.
If there is a slave that wants to communicate (ie if there is a button in the house being pressed), a slave will respond 
by pulling the bus down for 50 µs. This is called the presence pulse.

The master will respond with the command 11001100. To send this byte it will pull the bus down before every bit. 
A 1 is send by pulling the bus down for 7 microseconds (between 1 and 15 microseconds according to the one-wire spec). 
A 0 is send by pulling the bus down for 63 microseconds. The slave will respond to this command by sending its 8 byte 
unique ID. The master needs to request every bit of the response by pulling the bus down for 7 microseconds. If the 
slave wants to send a 1, it will do nothing and the bus returns to the high state. If the slave wants to send a 0, it 
will keep the bus down for another 50 microseconds.

## Custom Dobiss master hardware
This solution to replace the master of this Dobiss lighting switch bus consists of:
* A Raspberry Pi 5 4GB
* A Raspberry Pi Pico
* A logic level shifter (Adafruit 4-channel I2C-safe Bi-directional Logic Level Converter - BSS138)
* A 1k Ohm resistor

  The Pi 5 acts as powersupply and processes the messages which are sent on the bus.

  The Pi Pico handles the low level communication. It generates the reset pulse and requests the unique ID if a presence pulse is detected. THe unique ID is communicated to the Pi 5 by using serial over USB.

  The low side of the logic level shifter is connected the 3.3 V pin (pin 1) and a ground pin (pin 9) of the Pi 5. One of its low side pins (A4) is connected to a GPIO pin (pin 20) of the Pi Pico.

  The high side of the logic level shifter is connected to the 5V pin (pin 2) and a ground pin of the Pi 5. Finally a high side pin (B4) is connected to the data wire of the bus (D).

  The bus itself (the D wire) is connected to the 5V pin with a 1K Ohm pullup resistor.
