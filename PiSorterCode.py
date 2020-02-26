#Final

import cv2
import PIL.Image
from io import BytesIO
import IPython.display

from IPython.display import clear_output

import serial #need for ev3 talk
import imutils
print('hi')
import numpy as np #useful math/array stuff
import matplotlib.pyplot as plt
import time

def array_to_image(a, fmt='jpeg'): #jpeg vs png???
    #Create binary stream object
    f = BytesIO()
    #Convert array to binary stream object
    PIL.Image.fromarray(a).save(f, fmt)
    
    return IPython.display.Image(data=f.getvalue())

# Function to read the frame form camera
def get_frame(cam):
    # Capture frame-by-frame
    ret, frame = cam.read()
    crop = frame[150:400,170:370]
    #crop = vis[y1:y2,x1:x2] cropping image
    return crop

# Display the image
d1 = IPython.display.display("Your image displayed here!", display_id=1)

for i in range(300):
    # Start video capture 
    cam = cv2.VideoCapture(0)
    # Grab the frame
    frame = get_frame(cam)
    # Release the camera resource
    cam.release()
    
    # Change the color to RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    #need masking! Bounds.
    lower = np.array([180, 60, 50], dtype = "uint8")
    upper = np.array([220, 151, 155], dtype = "uint8")
    mask = cv2.inRange(frame, lower, upper)
    #print(np.sum(mask)) #check mask
    
    if np.sum(mask) >= 80000:
        s=serial.Serial("/dev/serial0",9600,timeout=2)  #This send info the EV3
        s.write("y".encode()) #to yes write to EV3
        print(np.sum(mask))
    
    if np.sum(mask) < 80000:
        s=serial.Serial("/dev/serial0",9600,timeout=2)
        s.write("n".encode()) #to no write to EV3
        #print('NOT')

    # Resize the image to 200px
    frame = imutils.resize(frame, width=200, inter=cv2.INTER_LINEAR)

    #Call the function to convert array data to image
    frame = array_to_image(frame)
    
    #Let's see the image below
    d1.update(frame)
    
print('Code Over')