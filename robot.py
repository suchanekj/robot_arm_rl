#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 12:13:35 2019

@author: stan
"""
import sys
# Import the arm module
from r12 import arm

# robot commands functions - communicates with the robot
class Robot():
    def __init__(self):
        # Connect arm and start Roboforth
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
        self.mode = None # TODO keep last chosen mode (JOINT or CARTESIAN) as attribute
        # TODO maybe move the following out of initialization and into
        # individual methods

        # De-energisation and energisation
        command = input('Do you want to de-energise the robot? [y/n]: ')
        if command == 'y':
            self.arm.write('DE-ENERGISE')
            print(self.arm.read())
            input('Please move the robot to completely vertical position if calibration is intended and press ENTER!')

        elif command == 'n':
            pass
        else:
            raise Exception('Unknown command')
        
        # Energise
        self.arm.write('ENERGISE')
        print(self.arm.read())


        # Calibration
        command = input('Do you want to calibrate the robot? If yes, make sure it is vertical! [y/n]: ')
        if command == 'y':
            self.arm.write('CALIBRATE')
            print(self.arm.read())

            # TODO add check if calibration successful
        elif command == 'n':
            pass
        else:
            raise Exception('Unknown command')

        # Deprecated
        # Bring to approximately horizontal position
        # self.reset()
        
        command=None
        while command!='y':
            command = input('Write a command for the Robot or write "y" if ready:')
            if command!='y':
                self.arm.write(command)
                print(self.arm.read())

    def move_home(self):
        """Moves robot to HOME position"""
        self.arm.write('HOME')
        print(self.arm.read())

    def to_joint(self):
        """ Changes movement mode to joint mode and displays reading"""
        self.arm.write('JOINT')
        print(self.arm.read())

    def to_cartesian(self):
        """ Changes movement mode to cartesian mode and displays reading"""
        self.arm.write('CARTESIAN')
        print(self.arm.read())


    def give_command(self, command):
        """ Writes command and displays reading"""
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
        lhand_pos = int(return_msg[-4])
        wrist_pos = int(return_msg[-3])
        return lhand_pos, wrist_pos

    def get_ready(self):
        """ Send the robot to "READY" position and displays reading (used after being in HOME position)"""
        self.arm.write('READY')
        print(self.arm.read())
    
    def level_hand(self):
        # Rotates hand into leveled position

        # Approximately horizontal arm position is
        # WAIST SHOULDER ELBOW L-HAND WRIST
        # 0 2800 8000 -500 -1600
        
        # Get hand out of the way (don't use if hand too far backwards)
        self.arm.write('TELL HAND -1500 MOVETO')
        print(self.arm.read())

        self.arm.write('TELL SHOULDER 2800 MOVETO')
        print(self.arm.read())
        self.arm.write('TELL ELBOW 8000 MOVETO')
        print(self.arm.read())
        self.arm.write('TELL HAND -500 MOVETO')
        print(self.arm.read())
        self.arm.write('TELL WRIST -1600 MOVETO')
        print(self.arm.read())

    def is_safe(self, action, hand_min=-2000, hand_max=6800):
    	""" Checks whether the action passed to the robot is safe
    	action is a string of ROBOFORTH command to robot"""
    	# TODO Fix get_position such that cartesian would not cause bug

    	self.to_joint() # TODO fix this
    	hand_coords = self.get_position()

    	if (action.split()[0] == "TELL") and (action.split()[1] == "HAND"):
    		# TODO add differentiation for relative and absolute commands (MOVE/MOVETO)
    		hand_movement = int(action.split()[2])


    		if (hand_coords[0] + hand_movement < hand_min) or (hand_coords[0] + hand_movement > hand_max):
    			raise Exception('Motion is not safe!')



