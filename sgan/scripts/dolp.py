import tkinter
import PySimpleGUI as sg
from timeit import default_timer as timer
import time
import subprocess
import cv2
import time
from datetime import datetime
from arena_api.__future__.save import Recorder
from arena_api.buffer import BufferFactory
from arena_api.enums import PixelFormat
from arena_api.system import system
import numpy as np
import pause
import os
import threading  
#import imageio
import RPi.GPIO as GPIO
from PIL import Image as PIL_Image
from math import atan
from math import atan2
from math import pi

count=0
led_pin = 12  # LED pin for feedback of shutter signal
refresh_rate_txt=0
multi_img_trig_count=0
multi_cap_flag=False
prev_time=0
but_pin = 18  #Input pin 18 for shutter signal
stop_threads= False

#Processing of image to form AOP and DOLP images

def process_image(im_raw):

    print("started processing image")
    im_raw=im_raw.astype(np.uint8)
    im_I = im_raw
    x=len(im_I)-1
    y=len(im_I[0])-1


    # 4 gratings

    I90deg=im_I[0:x+1:2,0:y+1:2]
    I0deg=im_I[1:x+2:2,1:y+2:2]
    I45deg=im_I[0:x+1:2,1:y+2:2]
    I135deg=im_I[1:x+2:2,0:y+1:2]



    # demosaicing

    im_temp=np.zeros(np.shape(im_I))

    I90 = np.zeros(np.shape(im_temp))

    I0 = np.zeros(np.shape(im_temp))

    I45 = np.zeros(np.shape(im_temp))

    I135 = np.zeros(np.shape(im_temp))

    # at location (1,1) etc. (row,column)

    I90[0:x+1:2,0:y+1:2]=im_I[0:x+1:2,0:y+1:2]

    I0[0:x+1:2,0:y+1:2]=im_I[1:x+2:2,1:y+2:2]
    I45[0:x+1:2,0:y+1:2]=im_I[0:x+1:2,1:y+2:2]
    I135[0:x+1:2,0:y+1:2]=im_I[1:x+2:2,0:y+1:2]

    # at location (2,2) etc.
    I90[1:x:2,1:y:2]=im_I[2:x+1:2,2:y+1:2]

    I0[1:x:2,1:y:2]=im_I[1:x:2,1:y:2]

    I45[1:x:2,1:y:2]=im_I[2:x+1:2,1:y:2]
    I135[1:x:2,1:y:2]=im_I[1:x:2,2:y+1:2]




    # at location (2,1) etc.
    I90[1:x:2,0:y+1:2]=im_I[2:x+1:2,0:y+1:2]
    I0[1:x:2,0:y+1:2]=im_I[1:x:2,1:y+2:2]
    I45[1:x:2,0:y+1:2]=im_I[2:x+1:2,1:y+2:2]

    I135[1:x:2,0:y+1:2]=im_I[1:x:2,0:y+1:2]

    # at location (1,2) etc.
    I90[0:x+1:2,1:y:2]=im_I[0:x+1:2,2:y+1:2]
    I0[0:x+1:2,1:y:2]=im_I[1:x+2:2,1:y:2]

    I45[0:x+1:2,1:y:2]=im_I[0:x+1:2,1:y:2]

    I135[0:x+1:2,1:y:2]=im_I[1:x+2:2,2:y+1:2]


    # calibration
    factor_0deg = 0.8710
    factor_45deg = 0.8500
    factor_90deg = 0.8690
    factor_135deg =  0.8580




    # calculating stokes parameters
    S0_temp = ((factor_0deg * I0) + (factor_90deg * I90)+(factor_45deg * I45) + (factor_135deg * I135))/2
    S1_cali = (factor_0deg * I0) - (factor_90deg * I90)
    S2_cali = (factor_45deg * I45) - (factor_135deg * I135)

    S0_cali = S0_temp*1.18

    # deleting last row/col all zeros
    S1=np.delete(S1_cali, -1, axis=1)
    S1=np.delete(S1, -1, axis=0)

    S2=np.delete(S2_cali, -1, axis=1)
    S2=np.delete(S2, -1, axis=0)

    S0=np.delete(S0_cali, -1, axis=1)
    S0=np.delete(S0, -1, axis=0)

    S0_temp=np.delete(S0_temp, -1, axis=1)
    S0_temp=np.delete(S0_temp, -1, axis=0)

    S0_temp=np.maximum(S0_temp , 0.00000001)
    S0_temp=np.minimum(S0_temp , 2)
    # calculating DOLP
    DOLP_temp=np.sqrt(S1**2 + S2**2) 
    DOLP = np.divide(DOLP_temp, S0_temp)
    #DOLP=DOLP_temp / S0

    DOLP=np.maximum(DOLP,0)
    DOLP=np.minimum(DOLP,1)


    ##### save the DOLP image


    # calculating AOP
    AOP_2 = np.zeros(np.shape(S1_cali))
    AOP = np.zeros(np.shape(S1_cali))
    for i in range(0,2047):
        for j in range(0,2447):
            if (S1_cali[i,j]==0) or (S2_cali[i,j]==0):
                AOP_2[i,j] =0
            else:
                #AOP_2[i,j]=atan2(S2_cali[i,j] , S1_cali[i,j])/pi*180
                AOP_2[i,j]=atan(S2_cali[i,j]/S1_cali[i,j])/pi*180
                
                #if AOP_2[i,j]<0:
                #    AOP_2[i,j]+=180
                    
                
                if S1_cali[i,j]<0:
                    AOP_2[i,j]=AOP_2[i,j]+180
                if AOP_2[i,j]<0:
                   AOP_2[i,j]=360+AOP_2[i,j]
            
            AOP[i,j] = 0.5*AOP_2[i,j]
            if AOP[i,j]>180:
                AOP[i,j]=AOP[i,j]-180
                
    AOP=np.maximum(AOP,0)
    AOP=np.minimum(AOP,180)            

    AOP = AOP/180

    AOP=np.array(AOP*255, dtype=(np.uint8))
    DOLP=np.array(DOLP*255, dtype=(np.uint8))

    AOP= cv2.applyColorMap(AOP, cv2.COLORMAP_JET)
    DOLP= cv2.applyColorMap(DOLP, cv2.COLORMAP_JET)



    return AOP, DOLP
