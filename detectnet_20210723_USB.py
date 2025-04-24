#!/usr/bin/python3
#
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import jetson.inference
import jetson.utils

import argparse
import sys
from os import path
import serial
import time

import os
import subprocess

# 全局变量记录当前播放进程
current_audio_process = None
wait=0
file_path=''

AUDIO_FOLDER = '/home/nvidia/Desktop/audio/'  # All audio files here


def play_audio(Find_flag,Target_ID):    
    global wait
    global current_audio_process
    file_path='/home/nvidia/Desktop/audio/wait.wav'
   
    # 如果已有音频在播放，终止它
    if current_audio_process is not None and wait == 1:
        return
    if current_audio_process is not None:
        current_audio_process.terminate()
        current_audio_process.wait()
    time.sleep(0.1)
    if Target_ID==0 and wait == 0:
        file_path=os.path.join(AUDIO_FOLDER,'wait.wav')
        wait = 1
    elif Target_ID==1:
        if Find_flag == 1:
            file_path=os.path.join(AUDIO_FOLDER,'key_founded.wav')
        else:
            file_path=os.path.join(AUDIO_FOLDER,'key_notfounded.wav')			
    elif Target_ID==2:
        if Find_flag == 1:
            file_path=os.path.join(AUDIO_FOLDER,'mouse_founded.wav')
        else:
            file_path=os.path.join(AUDIO_FOLDER,'mouse_notfounded.wav')
    elif Target_ID==3:
        if Find_flag == 1:
            file_path=os.path.join(AUDIO_FOLDER,'keyboard_founded.wav')
        else:
            file_path=os.path.join(AUDIO_FOLDER,'keyboard_notfounded.wav')
    elif Target_ID==4:
        if Find_flag == 1:
            file_path=os.path.join(AUDIO_FOLDER,'cellphone_founded.wav')
        else:
            file_path=os.path.join(AUDIO_FOLDER,'cellphone_notfounded.wav')	
    elif Target_ID==5:#laptop
        if Find_flag == 1:
            file_path=os.path.join(AUDIO_FOLDER,'key_founded.wav')
        else:
            file_path=os.path.join(AUDIO_FOLDER,'key_notfounded.wav')
    elif Target_ID==6:
        if Find_flag == 1:
            file_path=os.path.join(AUDIO_FOLDER,'pen_founded.wav')
        else:
            file_path=os.path.join(AUDIO_FOLDER,'pen_notfounded.wav')
    elif Target_ID==7:
        if Find_flag == 1:
            file_path=os.path.join(AUDIO_FOLDER,'earphone_founded.wav')
        else:
            file_path=os.path.join(AUDIO_FOLDER,'earphone_notfounded.wav')
    elif Target_ID==8:
        if Find_flag == 1:
            file_path=os.path.join(AUDIO_FOLDER,'glass_founded.wav')
        else:
            file_path=os.path.join(AUDIO_FOLDER,'glass_notfounded.wav')
    elif Target_ID==9:
        if Find_flag == 1:
            file_path=os.path.join(AUDIO_FOLDER,'Nailong_founded.wav')
        else:
            file_path=os.path.join(AUDIO_FOLDER,'Nailong_notfounded.wav')
    elif Target_ID==10:
        if Find_flag == 1:
            file_path=os.path.join(AUDIO_FOLDER,'wallet_founded.wav')
        else:
            file_path=os.path.join(AUDIO_FOLDER,'wallet_notfounded.wav')
    current_audio_process = subprocess.Popen(["aplay", file_path])
	

#Detect arduino serial path (Cater for different USB-Serial)
if path.exists("/dev/ttyACM0"):
	arduino = serial.Serial(port = '/dev/ttyACM0',baudrate = 115200, timeout = 1 )
elif path.exists("/dev/ttyUSB0"):
	arduino = serial.Serial(port = '/dev/ttyUSB0',baudrate = 115200, timeout = 1 )
else:
	print("Please plug in the Arduino")
	exit()
if not(arduino.isOpen()):
    arduino.open()

#Variables for command and control
pan =90
tilt = 90
tilt_offset = 30
pan_prev =90
tilt_prev = 90
pan_max = 100
pan_min = 80
tilt_max = 100
tilt_min = 80
width = 1280
height = 720
objX = width/2
objY = height/2
error_tolerance = 100
move_cmd = 0
# 1=right 2=left 3=str 4=back
deadband = 200
Target_Area = 70000
Target_ID = 0
Find_flag = 0


# parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", \
    formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage() +\
    jetson.utils.videoSource.Usage() + jetson.utils.videoOutput.Usage() + jetson.utils.logUsage())

#More arguments (For commandline arguments)
parser.add_argument("input_URI", type=str, default="", nargs='?', help="URI of the input stream")
parser.add_argument("output_URI", type=str, default="", nargs='?', help="URI of the output stream")
parser.add_argument("--network", type=str, default="ssd-mobilenet-v2", help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.8, help="minimum detection threshold to use") 

is_headless = ["--headless"] if sys.argv[0].find('console.py') != -1 else [""]

#Print help when no arguments given
try:
    opt = parser.parse_known_args()[0]
except:
    print("")
    parser.print_help()
    sys.exit(0)

# load the object detection network
net = jetson.inference.detectNet(opt.network, sys.argv, opt.threshold)

# create video sources & outputs
input = jetson.utils.videoSource(opt.input_URI, argv=sys.argv)
output = jetson.utils.videoOutput(opt.output_URI, argv=sys.argv+is_headless)

# process frames until the user exits
last_flag=0#
last_move_cmd=0#
num_of_audio=0#
while True:

    # capture the next image
    img = input.Capture()

    # detect objects in the image (with overlay)
    detections = net.Detect(img, overlay=opt.overlay)

    # print the detections
    # print("detected {:d} objects in image".format(len(detections)))
    
    #Initialize the object coordinates and area
    objX = width/2
    objY = height/2
    Area = 0

    
    temp_data = arduino.readline().decode('utf-8', errors='ignore').strip()
    if temp_data == '0':
        play_audio(0,0)
    if ( temp_data >= '0' and temp_data <= '9' ):  
        Target_ID = int(temp_data)
        print( Target_ID )
        # print(Target_ID)
#Find largest detected objects (in case of deep learning confusion)
    for detection in detections:
        # print(type(detection.ID))
        print(detection)
        # print((detection.ClassID))
        if( detection.ClassID == Target_ID and Target_ID != 0 ):
            Find_flag = 1
            if(int(detection.Area)>Area):
                objX =int(detection.Center[0])
                objY = int(detection.Center[1])
                Area = int(detection.Area)
            if( abs( width / 2 - objX ) < deadband ):
                if( Area <= Target_Area ):
                    move_cmd = 3
                else:
                    move_cmd = 0
            elif( width / 2 > objX ):
                move_cmd  = 1
            else:
                move_cmd = 2
        #elif (detection.ClassID != Target_ID and Target_ID != 0):
            #if(int(detection.Area)>Area):
                #objX =int(detection.Center[0])
                #objY = int(detection.Center[1])
                #Area = int(detection.Area)
            #if( abs( width / 2 - objX ) < deadband ):
                #if( Area <= Target_Area ):
                   #Find_flag = 2
        else:
            Find_flag = 0
            move_cmd = 0
            
    if(len(detections) == 0 ):
        Find_flag = 0
        move_cmd =0
   
    if Find_flag != last_flag: #0->1
        if Find_flag == 1 and move_cmd == 0:
            play_audio(1,Target_ID)
            wait=0
        elif Find_flag == 0:
            pass

    last_flag = Find_flag
    if move_cmd == 0 and last_move_cmd != 0 and Find_flag == 1:
        play_audio(1,Target_ID)
        wait=0
#         print(move_cmd)
    #Determine the adjustments needed to make to the cmaera
    
    # temp_data = arduino.readline().decode('utf-8', errors='ignore').strip()
    # temp_data = arduino.readline()
    # print(temp_data)

    panOffset = objX - (width/2)
    tiltOffset = objY - (height/2)
    
    #Puting the values in margins
    if (abs(panOffset)>error_tolerance):
        pan = pan-panOffset/100
    if (abs(tiltOffset)>error_tolerance):
        tilt = tilt+tiltOffset/100
    if pan>pan_max:
        pan = pan_max
    if pan<pan_min:
        pan=pan_min
    if tilt>tilt_max:
        tilt=tilt_max
    if tilt<tilt_min:
        tilt=tilt_min
    #Rounding them off
    pan = int(pan)
    tilt = int(tilt) + tilt_offset
    Area = int(Area)
    #Setting up command string
    myString = '(' +  str(Find_flag) + ',' + str(move_cmd) + ')'
    # myString = '(1,3)'
    print("myString = %s" %myString)
    
    #Print strings sent by arduino, if there's any
    if arduino.inWaiting():
        # print("From Arduino serial: %s" %arduino.readline().decode('utf-8'))
        arduino.flushInput()
        arduino.flushOutput()
    
    #Determine if sending signals is necessary (trival adjustsments wastes time)
    #if (abs(pan - pan_prev) > 5 or abs(tilt - tilt_prev)> 5):
    #    pan_prev = pan
    #    tilt_prev = tilt
        #Send it if area is reasonable
       # if (Area > 0 and Area < 300000):
    arduino.write(myString.encode())

    # render the image
    smallImg = jetson.utils.cudaAllocMapped(width=img.width*0.5, height=img.height*0.5, format=img.format)
    jetson.utils.cudaResize(img, smallImg)
    output.Render(smallImg)


    # update the title bar
    output.SetStatus("{:s} | Network {:.0f} FPS".format(opt.network, net.GetNetworkFPS()))
    
    # print out performance info
    net.PrintProfilerTimes()

    # exit on input/output EOS
    if not input.IsStreaming() or not output.IsStreaming():
        break


