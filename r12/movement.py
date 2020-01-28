# import the necessary packages
from collections import deque
# from imutils.video import VideoStream
import numpy as np
import argparse
#import cv2
#import imutils
import time
import sys
# Import the arm module



import arm
# Connect the arm
robot_arm = arm.Arm()
robot_arm.connect()
if robot_arm.is_connected():
    print(robot_arm.get_info())
else:
    raise Exception('Failed to connect')
command=None
while command!='RUN':
    command = input('Please write the command for the Robot: ')
    if command=='q':
        robot_arm.disconnect()
    else:
        robot_arm.write(command)
        print(robot_arm.read())


"""
import arm
# Connect the arm
robot_arm = arm.Arm()
robot_arm.connect()
if robot_arm.is_connected():
    print(robot_arm.get_info())
else:
    raise Exception('Failed to connect')
command=None
while command!='RUN':
    command = input('Please write the command for the Robot: ')
    if command=='q':
        robot_arm.disconnect()
        break
    else:
        robot_arm.write(command)
        print(robot_arm.read())

"""
robot_arm.disconnect()