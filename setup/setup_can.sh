#!/bin/bash

sleep 1

ip link set can0 down
ip link set can0 type can bitrate 125000
ip link set can0 up
