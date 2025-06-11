# -*- coding: utf-8 -*-
"""
Created on Sat May 31 15:15:09 2025

@author: ashka
"""

import socket
import re

from vpython import canvas, vector, color, arrow, cylinder, cone, box, compound, rate
import math
import numpy as np

UDP_IP = '127.0.0.1'
UDP_PORT = 5006

# UDP socket setup
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)

def parse_telemetry_line(line):
    if line.startswith("Received:"):
        line = line[len("Received:"):].strip()
    pattern = r"([A-Za-z0-9_]+)\s*:\s*(-?\d*\.\d+|-?\d+)"
    matches = re.findall(pattern, line)
    result = {}
    for key, val in matches:
        try:
            result[key] = float(val)
        except ValueError:
            result[key] = val
    return result

scene = canvas(title="🚀 Real-Time Rocket Orientation", width=800, height=800, background=color.blue)
scene.forward = vector(-1, -1, -1)
scene.range = 5

xarrow = arrow(length=2, shaftwidth=0.1, color=color.red, axis=vector(1, 0, 0))
yarrow = arrow(length=2, shaftwidth=0.1, color=color.green, axis=vector(0, 1, 0))
zarrow = arrow(length=4, shaftwidth=0.1, color=color.red, axis=vector(0, 0, 1))
frontArrow = arrow(length=4, shaftwidth=0.1, color=color.purple)
upArrow = arrow(length=1, shaftwidth=0.1, color=color.magenta)
sideArrow = arrow(length=2, shaftwidth=0.1, color=color.orange)

stage1 = cylinder(radius=0.5, length=4, color=color.red, axis=vector(0, 1, 0), pos=vector(0, 0, 0))
stage2 = cylinder(radius=0.4, length=3, color=color.white, axis=vector(0, 1, 0), pos=vector(0, 4, 0))
nose = cone(radius=0.4, length=1, color=color.gray(0.5), axis=vector(0, 1, 0), pos=vector(0, 7, 0))
fin1 = box(length=0.1, height=1, width=1, color=color.white, pos=vector(0.5, -0.5, 0))
fin2 = box(length=0.1, height=1, width=1, color=color.white, pos=vector(-0.5, -0.5, 0))
fin3 = box(length=1, height=1, width=0.1, color=color.white, pos=vector(0, -0.5, 0.5))
fin4 = box(length=1, height=1, width=0.1, color=color.white, pos=vector(0, -0.5, -0.5))
myObj = compound([stage1, stage2, nose, fin1, fin2, fin3, fin4])

while True:
    rate(60)
    try:
        data, addr = sock.recvfrom(1024)
        line = data.decode('utf-8', errors='ignore').strip()
        parsed = parse_telemetry_line(line)
        if all(k in parsed for k in ("qw", "qx", "qy", "qz")):
            q0 = parsed['qw']
            q1 = parsed['qx']
            q2 = parsed['qy']
            q3 = parsed['qz']
            norm = math.sqrt(q0*q0 + q1*q1 + q2*q2 + q3*q3)
            if norm == 0:
                continue
            q0, q1, q2, q3 = q0 / norm, q1 / norm, q2 / norm, q3 / norm

            roll = -math.atan2(2*(q0*q1 + q2*q3), 1 - 2*(q1*q1 + q2*q2))
            pitch = math.asin(2*(q0*q2 - q3*q1))
            yaw = -math.atan2(2*(q0*q3 + q1*q2), 1 - 2*(q2*q2 + q3*q3)) - np.pi/2

            k = vector(math.cos(yaw)*math.cos(pitch), math.sin(pitch), math.sin(yaw)*math.cos(pitch))
            y_ref = vector(0, 1, 0)
            s = k.cross(y_ref)
            v = s.cross(k)
            vrot = v * math.cos(roll) + k.cross(v) * math.sin(roll)

            frontArrow.axis = k
            sideArrow.axis = k.cross(vrot)
            upArrow.axis = vrot
            myObj.axis = k
            myObj.up = vrot
    except BlockingIOError:
        pass
