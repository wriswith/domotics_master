# dobiss_one_wire
Software to replace the Dobiss master that drives the lighting buttons.

The dobiss domotics solution uses a parasitic one wire bus to connect the lighting switches to the domotic modules. This one wire consists of a twisted pair in a UTP cable that passes every lighting switch in the bus. Behind every lighting button there is a circuit board that is connected to both the twisted pair and the lighting switch. When the lighting button is pressed, the circuit board will broadcast its unique ID on the bus.

## Communication protocol
The protocol works with one master and many slave devices. The master initiates communication by pulling the bus down for 600 micro seconds. This is the reset pulse.
If no slave responds, the master will sleep for 50 milliseconds and send another reset pulse.
If there is a slave that wants to communicate (ie if there is a button in the house being pressed), the slave will respond by pulling the bus down for 50 microseconds.
The master will respond with the command 11001100. To send this it will pull the bus down before every bit. A 1 is send by pulling the bus down for 7 microseconds (between 1 and 15 microseconds according to the one-wire spec). A 0 is send by pulling the bus down for 63 microseconds.
The slave will respond to this command by sending its 8 byte unique ID. The master needs to request every bit of the response by pulling the bus down for 7 microseconds. If the slave wants to send a 1, it will do nothing. If the slave wants to send a 0, it will keep the bus down for another 50 microseconds.
