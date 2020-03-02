#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

# Write your program here
#Additional imports&
import ubinascii, ujson, urequests, utime
import math
EV3Brick().speaker.beep()

# Initializing section
disSen = UltrasonicSensor(Port.S3)
resetSen = UltrasonicSensor(Port.S4)
motor1 = Motor(Port.B)
motor2 = Motor(Port.C)

#Newton start up
#trajectory angle, ball height (launched), arm length
theta, height, armLength = math.pi/10, 0.150, 0.09 

#Pre-Function, Function :)
def zeroListMaker(n):
     zeroList = [0]*n
     return zeroList

#training and catch start up
n = 2 #sampling runs
trainingData = zeroListMaker(n)
buttonNiceShot = TouchSensor(Port.S2)
buttonFoul = TouchSensor(Port.S1)
index, record, throw, strike = 0, [0,0], '', 0

#API!
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
          print('reset')

def checkShot(index, omega, distance, throw):
     throw = 'Ref!'
     while throw == 'Ref!':
          if buttonNiceShot.pressed():
               record = [round(omega, 2), round(distance)]
               throw = 'Nice Shot Glass Cannon!'
               index = index + 1
          if buttonFoul.pressed():
               throw = 'Foul Ball!'
               record = ['Bad']
     print(throw)
     return index, record, throw


def Newton_Model(theta, height, armLength):
    velocity = (((math.sqrt(2))*((disSen.distance()+40)/1000)*math.sqrt(9.8)*math.sqrt(1/math.sin(2*theta)))
    /math.sqrt(2*(disSen.distance()+40)/1000+height*math.sin(2*theta)*(1/math.sin(2*theta)**2)))
    omega = ((velocity/armLength)*180/math.pi)/2.5
    return omega

def saving(trainingData):
     with open("trainingData.txt",'a+') as outFile:
                  for line in trainingData:
                       outFile.write(str(line) + '\n')
                  outFile.close
                  ev3.speaker.say("I am ready for the majors")

def linerRegressionOfTrainingData(distance):
     #Sxx = (Avg(X)-X)^2
     #Sxy = (Avg(X)-X) * (Avg(Y)-Y)
     SumX, SumY, lineCount = 0, 0, 0
     fin = open('trainingData.txt')
     for line in fin:
          lineCount = lineCount + 1
          #print('omega:',line[1:7],'dis:',line[9:12]) #works, poorly
          line = line[1:-2]
          line = line.split(", ")
          SumX = float(line[1]) + SumX
          SumY = float(line[0]) + SumY
     AveX, AveY = (SumX/lineCount), (SumY/lineCount)
     XYList, indexer, indexer2 = zeroListMaker(lineCount), 0, 0
     for zero in XYList:
          XYList[indexer2] = [0,0,0]
          indexer2 = indexer2 + 1
     fin = open('trainingData.txt') #Beter way of doing this??
     for line in fin:
          line = line[1:-2]
          line = line.split(", ")
          XYList[indexer][1]= (float(line[1]) - AveX)
          XYList[indexer][2]= (float(line[1]) - AveX)**2
          XYList[indexer][0]= (float(line[0]) - AveY)
          indexer = indexer + 1
     SSxx, SSyy, SSxy = 0, 0, 0
     for item in XYList:
          SSxx = SSxx + item[2]
          SSyy = SSyy + item[0]
          SSxy = SSxy + item[0]*item[1]
     slope = SSxy/SSxx
     #Intercept = AVG(Y) – Slope * AVG(X)
     intercept = AveY - AveX*slope
     bestOmegaEstimate = slope*distance+intercept
     #print('slope: ', slope, 'intercept:' , intercept) #check
     #R^2 Value - would be cool... Haha
     return bestOmegaEstimate

#print(linerRegressionOfTrainingData(disSen.distance()))

# Main Code
while True:
     #print('Suggested Omega:', str(Newton_Model(theta, height, armLength))) #Newton's Suggestion
     last_distance = disSen.distance()
     if Get_SL('trigger') == 'false': #Hold, Hold, Hold....
          omega = linerRegressionOfTrainingData(disSen.distance())
          Put_SL('aim', 'STRING', str(disSen.distance()/10)+' cm')
     if Get_SL('trigger') == 'true': #Fire!
          Put_SL('aim', 'STRING', str(disSen.distance()/10)+' cm')
          if Get_SL('model') == '0':
               omega = Newton_Model(theta, height, armLength)
               print('Newton at Bat!')
          if Get_SL('model') == '1':
               omega = linerRegressionOfTrainingData(disSen.distance())
               print('Glass Cannon at Bat!')
          #wind up if far!
          if omega > 600:
               motor1.run_target(-80, -70,wait=False)
               motor2.run_target(-80, -70)
          correction = int(Get_SL('speed'))
          omega = omega + correction
          print('omega:', omega, 'correction:', correction)
          motor1.run_target(omega, 400, wait=False)
          motor2.run_target(omega, 400)
          motor1.reset_angle(0)
          motor2.reset_angle(0)
          wait(200)
          last_distance = disSen.distance()
          index, record, throw = checkShot(index, omega, disSen.distance(), throw)
     #Playing Catch with a Robot! It's for learning & science!
     if 20 < abs(last_distance - disSen.distance()):
          strike = 0
          correction = 0
     if throw == 'Foul Ball!':
          strike = strike + 1
     if strike >= 2:
          correction = correction + 15     
     if throw == 'Nice Shot Glass Cannon!':
          trainingData[index-1] = record
          print(trainingData[index-1])
     if index == n:
          saving(trainingData)
          print('Good Game!')
          break
     resetArm()