# -*- coding: utf-8 -*-
"""
Created on Sat May 31 15:06:18 2025

@author: ashka
"""

import serial
import socket

SERIAL_PORT = 'COM6'
BAUD_RATE = 115200

UDP_IP = '127.0.0.1'
DASHBOARD_PORT = 5005
VPYTHON_PORT = 5006

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Forwarding serial data...")
while True:
    line = ser.readline()
    if line:
        sock.sendto(line, (UDP_IP, DASHBOARD_PORT))
        sock.sendto(line, (UDP_IP, VPYTHON_PORT))
