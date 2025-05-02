#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/uart.h"
#include "hardware/gpio.h"


void send_bit(uint PIN, uint bit) {
    gpio_set_dir(PIN, GPIO_OUT);
    if (bit == 1){
        // To send a binary number "1", the bus master sends a very brief (1–15 μs) low pulse.
        gpio_put(PIN, 0);
        sleep_us(7);
        gpio_put(PIN, 1);
        sleep_us(63);
    } else {
        // To send a binary number "0", the master sends a 60 μs low pulse.
        gpio_put(PIN, 0);
        sleep_us(63);
        gpio_put(PIN, 1);
        sleep_us(7);
    }
}


uint receive_bit(uint PIN) {
    // send short pulse to initiate bit
    gpio_set_dir(PIN, GPIO_OUT);
    gpio_put(PIN, 0);
    sleep_us(7);
    gpio_put(PIN, 1);

    // set PIN to reading mode
    gpio_set_dir(PIN, GPIO_IN);

    // give slave time to respond
    sleep_us(20);

    //return state of PIN
    uint bit = gpio_get(PIN);

    // wait for slave to "release" the bus
    sleep_us(50);

    return bit;
}


void receive_byte(uint PIN){
    // Receive 8 bits and print them to UART

    uint byte[8];
    int i;

    for (i = 0; i < 8; i++) {
        byte[i] = receive_bit(PIN);
    }

    for (int j = 0; j < 8; j++) {
        printf("%d", byte[j]);
    }

    printf(" ");
}




int communication_cycle(uint PIN, long counter){
    // send a reset pulse and handle communication with slave if present

    // Start communication with 607 microseconds drop of bus
    gpio_set_dir(PIN, GPIO_OUT);
    gpio_put(PIN, 0);
    sleep_us(607);
    gpio_put(PIN, 1);


    // listen for >60 microseconds presence pulse by slave within 100 microseconds
    gpio_set_dir(PIN, GPIO_IN);
    sleep_us(50);
    uint presence_pulse = 0;
    presence_pulse = gpio_get(PIN);
    if (presence_pulse == 1){
        // no presence of slave received. Skip to next cycle.
        printf("--- Heartbeat %d_%d: ###\r\n", PIN, counter);
        return false;
    }

    // print header of packet to UART
    printf("--- Start frame %d_%d: ", PIN, counter);


    // sleep as detected on logic analyzer. Not in spec.
    sleep_us(580);


    // send command
    send_bit(PIN, 1);
    send_bit(PIN, 1);
    send_bit(PIN, 0);
    send_bit(PIN, 0);
    send_bit(PIN, 1);
    send_bit(PIN, 1);
    send_bit(PIN, 0);
    send_bit(PIN, 0);


    // wait between bytes
    sleep_us(140);


    // Drop for 7 microseconds to trigger a read bit


    // receive response
    const uint number_of_bytes = 8;
    uint response_bytes[8*number_of_bytes];

    int i;
    for (i = 0; i < number_of_bytes; i++) {
        receive_byte(PIN);
        sleep_us(320);
    }


    printf("###\r\n");
    return true;
    // communication ended
}


int main()
{
    stdio_uart_init();  // <--- Use UART0 (GP0 TX, GP1 RX)

    long counters[] = {0, 0, 0};
    // stdio_init_all();
    int ms_passed = 0;
    bool last_pulse_was_command = false;

    // Initialize pins connected to one wire buses
    const uint number_of_pins = 3;
    uint PINS[] = {13, 14, 15};
    int i;
    for (i = 0; i < number_of_pins; i++) {
        gpio_init(PINS[i]);
    }

    // Optional: use the status led to show the pico pi code is running
    int status_led_pin = 25;
    gpio_init(status_led_pin); // Initialize the GPIO pin
    gpio_set_dir(status_led_pin, GPIO_OUT); // Set the GPIO pin as output
    gpio_put(status_led_pin, 0);


    while (true) {
        if (counters[0] % 100 == 0){
            gpio_put(status_led_pin, 1);
        } else if (counters[0] % 100 == 5){
            gpio_put(status_led_pin, 0);
        }

        for (i = 0; i < number_of_pins; i++) {
            counters[i] = counters[i] + 1;
            last_pulse_was_command = communication_cycle(PINS[i], counters[i]);
            if (last_pulse_was_command){
                ms_passed = ms_passed + 9;
            } else {
                ms_passed = ms_passed + 1;
            }
        }


        // Ensure 50 ms between reset pulses. Important for ensuring the power supply to the slaves.
        if (ms_passed < 50){
            sleep_ms(50 - ms_passed);
        }

        ms_passed = 0;

    }
}
