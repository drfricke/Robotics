#!/usr/bin/env pybricks-micropython

from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color,
                                 SoundFile, ImageFile, Align)
from pybricks.tools import print, wait, StopWatch
from pybricks.robotics import DriveBase
from math import *

import utime, ujson
from pybricks.iodevices import UARTDevice

resetAngle = TouchSensor(Port.S1)
xMotor = Motor(Port.A)
yMotor = Motor(Port.D)
hapticMotor = Motor(Port.B)
uartComm = UARTDevice(Port.S2, 9600)
dZone = 15


def moveEncode(x, y):
    coords = {'x' : x, 'y' : y}
    moveCMD =  ujson.dumps(coords)
    wait(100)
    return moveCMD + ''.join(['B' for i in range(24-len(moveCMD))])

#Main Function
def main():
    reflection = 100
    #main loop
    while True:
        #initial angle reading (correcting signs of angles)
        x = - xMotor.angle()
        y = yMotor.angle()
        
        if abs(y) < dZone:
            y = 0

        #Encode the values in a json object
        #deadzone
        moveCMD = moveEncode(x, y)
        #try to read values from serial
        try:
            data_raw = uartComm.read(24).decode().replace('B', '')
            data = ujson.loads(data_raw)
            reflection = data['signal']

        except Exception as e:
            print(e)
            uartComm.clear()
            print("Read Failed")
        
        #try to write values to serial    
        try:
            uartComm.write(moveCMD) 
        except Exception as e:
            print(e)
            print("Write Failed")

        if resetAngle.pressed():
            xMotor.reset_angle(0)
            yMotor.reset_angle(0)
            print('Angle Reset')

        
        if reflection < 70:
            hapticMotor.dc(100)
        else: 
            hapticMotor.dc(0)
        

main()
        




