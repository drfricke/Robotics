#!/usr/bin/env pybricks-micropython
#David Fricke including some code from Chris Rogers


#Import files
from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color,
                                 SoundFile, ImageFile, Align)
from pybricks.tools import print, wait, StopWatch
from pybricks.robotics import DriveBase

from pybricks.ev3devio import Ev3devSensor 
import utime
import ev3dev2
from ev3dev2.port import LegoPort


from pybricks.parameters import Port
from pybricks.ev3devio import Ev3devSensor

#Initializing

left_motor = Motor(Port.A)
right_motor = Motor(Port.D)
front = DriveBase(left_motor, right_motor, 57, 121)
kp = .45 #adjustable kp and kd
kd = .41
oldDiffError = 0
speed = -260

class MySensor(Ev3devSensor):  #Define Class 
    _ev3dev_driver_name="ev3-analog-01" #do not forget to set port mode to EV3-Analog 
    def readvalue(self):
        self._mode('ANALOG')
        return self._value(0)


# Before running the code go to Device Browser and Sensors. Make sure you can see ev3-analog-01, otherwise you will get an error.

#more initialzing code

sens = LegoPort(address ='ev3-ports:in1')
sens2 = LegoPort(address ='ev3-ports:in4')# which port?? 1,2,3, or 4
sens.mode = 'ev3-analog'
sens2.mod = 'ev3-analog'
utime.sleep(0.5)
sensor_left=MySensor(Port.S1)
sensor_right=MySensor(Port.S4)# same port as above
reffLeft = sensor_left.readvalue()
reffRight = sensor_right.readvalue()

#Drive code
# Uncomment print lines to get readings for tuning or troubleshooting

# A note to readers or furture self - earlier iterations failed because I had two seprate errors feeding into
# motors which fought each other instead of working together. It's important to have one error and 
# use the single error to control both motors  - using that error to assit both motors. Past iterations
# had a hard time with only one motor attempting to turn and the other driving normal - both actively working
# together for turns is NEEDED. Important lesson for future control systems :) 

while True:
    #print('Left' + str(sensor_left.readvalue()) + '    Right' + str(sensor_right.readvalue()))
    diffError = ((reffLeft - sensor_left.readvalue()) - ((reffRight - sensor_right.readvalue()))) #errorLeft - errorRight
    diffCorrection = kp*diffError
    corrDdiff = kd*(diffError - oldDiffError)
    oldDiffError = diffError
    #print(str(round((speed + corrDdiff + diffCorrection),2)))
    left_motor.run(speed + (corrDdiff + diffCorrection))
    right_motor.run(speed - (corrDdiff + diffCorrection))
    
    
    

