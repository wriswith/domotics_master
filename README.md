# dobiss_one_wire
Software to replace the Dobiss master that drives the lighting buttons.

The dobiss domotics solution uses a parasitic one wire bus to connect the lighting switches to the domotic modules. This one wire consists of a twisted pair in a UTP cable that passes every lighting switch in the bus. Behind every lighting button there is a circuit board that is connected to both the twisted pair and the lighting switch. When the lighting button is pressed, the circuit board will broadcast its unique ID on the bus.
