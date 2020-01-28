#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 12:13:35 2019

@author: stan
"""
import sys
# Import the arm module
sys.path.insert(1, '/home/stan/Documents/ML_projects/RL_robotics/r12_python_shell/r12')
import arm

# robot commands functions - communicates with the robot
class Robot():
    def __init__(self):
        self.arm = arm.Arm()
        self.arm.connect()
        if self.arm.is_connected():
            print(self.arm.get_info())
        else:
            raise Exception('Failed to connect')
        self.arm.write('ROBOFORTH')
        print(self.arm.read())
        self.arm.write('START')
        print(self.arm.read())
        # de-energise
        input('De-Energise?')
        self.arm.write('DE-ENERGISE')
        print(self.arm.read())
        # energise
        input('Press ENTER when in home position')
        self.arm.write('ENERGISE')
        print(self.arm.read())
        # calibrate
        self.arm.write('CALIBRATE')
        print(self.arm.read())
        # FIND COORDINATES
        self.arm.write('JOINT')
        print(self.arm.read())
        # Bring to approximately horizontal position
        self.reset()
        
        command=None
        while command!='DONE':
            command = input('Write a command for the Robot or DONE if ready: ')
            if command!='DONE':
                self.arm.write(command)
                print(self.arm.read())    
        
    def rotate_by(self, joint, dirn=1, deg=120):
        # dirn is 1 or -1 moves joint in opposite directions
        deg = deg*dirn
        # move arm
        if joint == 'L-HAND':            
            self.arm.write('TELL L-HAND WRIST {} {} MOVE'.format(deg, deg))
        else:
            self.arm.write('TELL {} {} MOVE'.format(joint, deg))
        # wait for return message
        return_msg = self.arm.read()
        # reset to original position if encountered a problem
        if return_msg.split()[-2] != 'OK':
            self.reset()
            
    def rotate_return(self, joint, dirn, deg=120):
        self.rotate(joint, dirn, deg=deg)
        self.rotate(joint, -dirn, deg=deg)      
        
    def rotate_to(self, lhand_dest, wrist_dest):
        self.arm.write('TELL L_HAND WRIST {} {} MOVETO'.format(lhand_dest, wrist_dest))
        return_msg = self.arm.read()
        if return_msg.split()[-2] != 'OK':
            self.reset()
            
    def get_position(self):
        # returns the position of the l-hand joint and the wrist
        # does not return the rest because it should stay constant
        self.arm.write('WHERE')
        return_msg = self.arm.read().split()
        lhand_pos = return_msg[-4]
        wrist_pos = return_msg[-3]
        return lhand_pos, wrist_pos
    
    def reset(self):
        # Approximately horizontal maze position is
        # WAIST SHOULDER ELBOW L-HAND WRIST
        # 0 2800 9000 -1240 10512
        
        self.arm.write('TELL SHOULDER 2800 MOVETO')
        print(self.arm.read())
        self.arm.write('TELL ELBOW 9000 MOVETO')
        print(self.arm.read())
        self.arm.write('TELL L-HAND -1240 MOVETO')
        print(self.arm.read())
        self.arm.write('TELL WRIST 10510 MOVETO')
        print(self.arm.read())
        
    def reset_home(self):
        self.arm.write('HOME')
        
        