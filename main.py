#!/usr/bin/env pybricks-micropython

from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import (Port, Stop, Direction, Button, Color,
                                 SoundFile, ImageFile, Align)
from pybricks.tools import print, wait, StopWatch
from pybricks.robotics import DriveBase

# Write your program here
# This is your AP Key mUZCBzFc_r4W48or6mAWmdXEf8KHuZYq6yOdTpgBWM

import ubinascii, ujson, urequests, utime, random

#for later information and possible further study, putting the API Key 
# elsewhere (not public) might make this easier to protect it. 
#import passwords
#key = passwords.ni

Key = replace me

## Setting up

def SL_setup():
    #SL_setup() creates the link between SystemLinkCloud and the ev3
    urlBase = "https://api.systemlinkcloud.com/nitag/v2/tags/"
    headers = {"Accept":"application/json","x-ni-api-key":Key}
    return urlBase, headers
     
def Put_SL(Tag, Type, Value):
    #Put_SL() takes the tag, type, and value of the tag and writes it to the website (SLC)
    urlBase, headers = SL_setup()
    urlValue = urlBase + Tag + "/values/current"
    propValue = {"value":{"type":Type,"value":Value}}
    try:
        reply = urequests.put(urlValue,headers=headers,json=propValue).text
    except Exception as e:
        print(e)         
        reply = 'failed'
    return reply

def Get_SL(Tag):
    #Get_SL() takes the tag and retrieves the value from SystemLink
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
     
def Create_SL(Tag, Type):
    # Create_SL() creates a new tag on SystemLink
    urlBase, headers = SL_setup()
    urlTag = urlBase + Tag
    propName={"type":Type,"path":Tag}
    try:
        urequests.put(urlTag,headers=headers,json=propName).text
    except Exception as e:
        print(e)

# # Blank Functions: ignore
# # Create_SL('Bill','STRING')
# # Get_SL('Bill')
# Put_SL('gauge','STRING','done')

#int
base = Motor(Port.D)
fore = Motor(Port.A)
button = TouchSensor(Port.S1)
pressed = Button.CENTER in brick.buttons()

while True:
    print('Base  ' + str(base.angle()), 'Fore  ' + str(fore.angle()))
    base_number = str(base.angle()) #updating angles
    fore_number = str(fore.angle())
    Put_SL('base_number','STRING', base_number) #constantly sending angles
    Put_SL('fore_number','STRING', fore_number)
    isLine = True if Get_SL('line') == 'true' else False #neat line - constantly Get_SL and setting isLine to = true or false
    if button.pressed():
        base.reset_angle(0) #reset angle in case of drift
        fore.reset_angle(0)
    if isLine:
        base.run_time(-10*int(str(base.angle())),150) #run_time gives a little bump
    else: 
        base.stop(Stop.COAST) #reset to coast


#Furture Work
#setting up a deadzone on the joystick so the bot doesn't drifts
#Psuedo Code would be if -5 < deadzone < 5 than put 0 to system link.

#pretty much done with system link here (since the lag is soooooo painful)
#Next thing to is get them work off UART
#Then setting up bot moving off angle inputs (scaling?)
#Refine the haptic response
