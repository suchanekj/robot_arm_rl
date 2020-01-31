#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 10:23:19 2020

@author: stan
"""
import cv2
import imutils
import numpy as np

class Detector(object):
    def __init__(self, visualise=False):
        self.blurSize=3
        self.visualise=visualise
        
    def calibrate(self, frameLoader):
        hue_min = 0.0
        
        while True and hue_min<180.0:
            print(hue_min)
            colourLower = (int(hue_min), 70, 10)
            colourUpper = (int(hue_min) + 30, 255, 255)
            frame = frameLoader._get_frame()
            hue_min+=0.1
            
            # if we are vframeiewing a video and we did not grab a frame,
            # then we have reached the end of the video
            if frame is None:
                break
            # resize the frame, blur it, and convert it to the HSV
            # color space
            frame = imutils.resize(frame, width=900)
            blurred = cv2.GaussianBlur(frame, (11, 11), 0)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        
            # construct a mask for the color "green", then perform
            # a series of dilations and erosions to remove any small
            # blobs left in the mask
            mask = cv2.inRange(hsv, colourLower, colourUpper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
                
            display = np.concatenate((frame, np.stack((mask, mask, mask), 2)), 1)
            cv2.imshow("Frame", display)
            key = cv2.waitKey(1) & 0xFF
            
            # if the 'q' key is pressed, stop the loop
            if key == ord("q"):
                break
            
    def detect_contours_from_hue(self, frame, hue_min):
        colourLower = (int(hue_min), 70, 10)
        colourUpper = (int(hue_min) + 30, 255, 255)
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, colourLower, colourUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        return cnts, mask
    
    def detect_rect_from_hue(self, frame, hue_min):
        
        cnts, mask = self.detect_contours_from_hue(frame, hue_min)
        x,y,w,h=None,None,None,None
        
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the enclosing rectangle and
            # centroid
            
            # TODO: change this so that it takes a large contour with highest 
            # vertical coordinate
            c = max(cnts, key=cv2.contourArea)

            x,y,w,h = cv2.boundingRect(c)
            if self.visualise:
                cv2.rectangle(frame,(x,y,w,h),(0, 0, 255), 2)
                display = np.concatenate((frame, np.stack((mask, mask, mask), 2)), 1)
                cv2.imshow("Frame", display)
        return x,y,w,h
    
    def detect_markers_from_hue(self, frame, hue_min):
        cnts, mask = self.detect_contours_from_hue(frame, hue_min)
        # only proceed if both contours were found
        centers = [None] * 2
        radius = [None] * 2
        if len(cnts) > 1:
            cnts.sort(key=cv2.contourArea, reverse=True)
            marker_c = cnts[:2]
            for i, c in enumerate(marker_c):
                centers[i], radius[i] = cv2.minEnclosingCircle(c)
                
            if self.visualise:
                cv2.circle(frame,(int(centers[0][0]),int(centers[0][1])),int(radius[0]),(0, 0, 255), 2)
                cv2.circle(frame,(int(centers[1][0]),int(centers[1][1])),int(radius[1]),(0, 0, 255), 2)
                display = np.concatenate((frame, np.stack((mask, mask, mask), 2)), 1)
                cv2.imshow("Frame", display)
        return centers, radius