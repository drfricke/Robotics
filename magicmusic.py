#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

import serial

ev3 = EV3Brick()

#notes = ['G3/8','G3/8', 'G3/8', 'Eb3/2','R/8','F3/8','F3/8', 'F3/8', 'D3/2']
#ev3.speaker.play_notes(notes, tempo=120)

# Write your program here
#ev3.speaker.beep()

s=serial.Serial("/dev/ttyACM0",9600)

while True:
     try:
          data=s.read(s.inWaiting()).decode("utf-8")
          data = data.splitlines()
          if len(data) == 1:
               imu = data[0].split(',')
               if len(imu) == 6:
                    #print(imu)
                    if float(imu[2]) >= .2:
                         print('z posi or neg')
                    elif float(imu[0]) > .22:
                         if float(imu[1]) > .22:
                              print('+, +')
                              ev3.speaker.beep(440,500)
                              #ev3.speaker.play_notes(notes[0], tempo=120)
                         elif float(imu[1]) < -.22:
                              print('+, -')
                    elif float(imu[0]) < -.22:
                         if float(imu[1]) > .22:
                              print('-, +')
                         elif float(imu[1]) < -.22:
                              print('-, -')
     except Exception as e: print(e)



#old stuff
# for i in range(10):
#      data=s.read(s.inWaiting()).decode("utf-8")
#      #print('size = %d, buffer = %d' % (len(data),s.inWaiting()))
#      data = data.splitlines()
#      imu = data[:-2]
#      print(imu)
