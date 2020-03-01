#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

# Write your program here

import ubinascii, ujson, urequests, utime
import math
ev3 = EV3Brick()
ev3.speaker.beep()

# Initializing section
disSen = UltrasonicSensor(Port.S3)
resetSen = UltrasonicSensor(Port.S4)
motor1 = Motor(Port.B)
motor2 = Motor(Port.C)

theta, height, armLength = math.pi/10, 0.150, 0.09 #trajectory angle, ball height (launched), arm length

#Pre-Function, Function :)
def zeroListMaker(n):
     zeroList = [0]*n
     return zeroList

n = 3 #sampling runs
trainingData = zeroListMaker(n)
buttonNiceShot = TouchSensor(Port.S2)
buttonFoul = TouchSensor(Port.S1)
index, record, throw = 0, [0,0], ''



key = 'q2-v7Aq2fJ00VfOSN0lD1zjmvv9NEOTTAgHPrEqxWE'

# Functions

def SL_setup():
     urlBase = "https://api.systemlinkcloud.com/nitag/v2/tags/"
     headers = {"Accept":"application/json","x-ni-api-key":key}
     return urlBase, headers

def Get_SL(Tag):
     urlBase, headers = SL_setup()
     urlValue = urlBase + Tag + "/values/current"
     try:
          value = urequests.get(urlValue,headers=headers).text
          data = ujson.loads(value)
          #print(data)
          result = data.get("value").get("value")
     except Exception as e:
          print(e)
          result = 'failed'
     return result

def Put_SL(Tag, Type, Value):
     urlBase, headers = SL_setup()
     urlValue = urlBase + Tag + "/values/current"
     propValue = {"value":{"type":Type,"value":Value}}
     try:
          reply = urequests.put(urlValue,headers=headers,json=propValue).text
     except Exception as e:
          print(e)         
          reply = 'failed'
     return reply


def resetArm():
     if resetSen.distance()/10 > 30:
          while (resetSen.distance()/10) > 30:
               motor1.run_target(70, 5, wait=False)
               motor2.run_target(70, 5)
               motor1.reset_angle(0)
               motor2.reset_angle(0)
          #motor1.run_target(-80, -40,wait=False)
          #motor2.run_target(-80, -40)
          print('reset')

def checkShot(index, omega, distance, throw):
     throw = 'Ref!'
     while throw == 'Ref!':
          if buttonNiceShot.pressed():
               record = [omega, round(distance,2)]
               throw = 'Nice Shot Glass Cannon!'
               index = index + 1
          if buttonFoul.pressed():
               throw = 'Foul Ball!'
               record = ['Bad']
     print(throw)
     return index, record, throw

          

def Newton_Model(theta, height, armLength):
    velocity = (((math.sqrt(2))*((disSen.distance()+30)/1000)*math.sqrt(9.8)*math.sqrt(1/math.sin(2*theta)))
    /math.sqrt(2*(disSen.distance()+30)/1000+height*math.sin(2*theta)*(1/math.sin(2*theta)**2)))
    omega = ((velocity/armLength)*180/math.pi)/2.5
    return omega

def saving(trainingData):
     with open("trainingData.txt",'w+') as outFile:
                  for line in trainingData:
                       outFile.write(str(line) + '\n')
                  outFile.close
                  ev3.speaker.say("Ready for the majors")


# Main Code

while True:
    print('Suggested Omega:', str(Newton_Model(theta, height, armLength)))
    if Get_SL('trigger') == 'false': #Hold, Hold, Hold....
        omega = Newton_Model(theta, height, armLength)
        Put_SL('aim', 'STRING', str(disSen.distance()/10))
    if Get_SL('trigger') == 'true': #Fire!
        omega = Newton_Model(theta, height, armLength)
        motor1.run_target(omega, 400, wait=False)
        motor2.run_target(omega, 400)
        motor1.reset_angle(0)
        motor2.reset_angle(0)
        wait(200)
        index, record, throw = checkShot(index, omega, disSen.distance(), throw)
        if index == n:
             saving(trainingData)
             print(trainingData)
             break
        if throw == 'Nice Shot Glass Cannon!':
             trainingData[index-1] = record
             print(trainingData)
        resetArm()
     
     
        #print(disSen.distance()/10+12) #8 cm offset actual and minus another 2
        #print(resetSen.distance()/10)



    


