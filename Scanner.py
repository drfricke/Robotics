#!/usr/bin/env pybricks-micropython

from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color,
                                 SoundFile, ImageFile, Align)
from pybricks.tools import print, wait, StopWatch
from pybricks.robotics import DriveBase

from pybricks.iodevices import UARTDevice

import ujson

# Write your program here

left = Motor(Port.A)
right = Motor(Port.D)
light = ColorSensor(Port.S1)
horz = Motor(Port.B)
robot = DriveBase(left, right, 56, 152)

def reading(reflection):
    reflect = {'signal':reflection}
    signal = ujson.dumps(reflect)
    wait(100)
    return signal + ''.join(['B' for i in range(24-len(signal))])

def constrain(value, range):
    if value > range[1]:
        value = range[1]
    elif value < range[0]:
        value = range[0]

def main():
     uartComm = UARTDevice(Port.S2, 9600, 100)
     uartComm.clear()
     xlimits = [-310, 310]

     while True:
        reflection = light.reflection()
        try:
            data_raw = uartComm.read(24).decode().replace('B', '')
            data = ujson.loads(data_raw)
        except Exception as e:
            uartComm.clear()
            print(e)
            print('Read Failed')
            data = {'x':0, 'y':0} #need this or robot.drive throws an error
        
        try:
            signal = reading(reflection)
            uartComm.write(signal)
            print(signal) #prints json signal
        except Exception as e:
            print(e)
            print("Write Failed")
        #print(data['x'], data['y'])
        robot.drive(data['y']/2, 0)
        print(horz.angle())
        horiz_dist = data['x'] * (360/90)
        constrain(horiz_dist, xlimits)
        horz.run_target(100,horiz_dist)
    


main()
