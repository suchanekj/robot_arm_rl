#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:23:17 2020

@author: stan
"""
import cv2
from frame_loader import CameraFrameLoader
import imutils
from vis import Detector

class GraspingEnv(object):
    def __init__(self, visualise_vision=False):
        self.fl = CameraFrameLoader(source=4)
        self.det = Detector(visualise=visualise_vision)
        self.hue_min = 25.0
        self.last_frame = None
        
    def calibrate_env(self):
        self.det.calibrate(self.fl)
        
    def get_frame(self):
        # Resize and blur for detection
        frame= self.fl._get_frame() 
        frame = imutils.resize(frame, width=900)
        self.last_frame = cv2.GaussianBlur(frame, (11, 11), 0)
        
    def get_object_z_coord(self):
        x,y,w,h = self.det.detect_rect_from_hue(self.last_frame, self.hue_min)
        if y:
            return self.last_frame.shape[0]-y
        else:
            return None
        
    def get_reward(self, reward_idx):
        # Normalised height
        if reward_idx == 1:
            z = self.get_object_z_coord()
            if z:
                return self.get_object_z_coord()/self.last_frame.shape[0]
            else:
                return 0
    
graspingEnv = GraspingEnv(visualise_vision=True)
while True:
    graspingEnv.get_frame()
    print(graspingEnv.get_reward(1))
    key = cv2.waitKey(1) & 0xFF
    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

# Run action 1
# Run action 2
# Run action 3
# Get reward


# close all windows
cv2.destroyAllWindows()