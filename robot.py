#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 12:13:35 2019

@author: stan
"""

import sys
# Import the arm module
from r12 import arm


class Robot():
    """ Class for high level control of the r12 arm """


    def __init__(self):
        self.arm = arm.Arm()
        self.connected = False
        # The mode attribute keeps track of last mode chosen j=JOINT, c=CARTESIAN
        self.mode = 'j'
        self.energised = True
        self.calibrated = False

    def check_connection(self):
        if self.arm.is_connected():
            self.connected = True
        else:
            self.connected = False

    def connect(self):
        # Connect arm and check connection
        self.arm.connect()

        if self.arm.is_connected():
            print(self.arm.get_info())
        else:
            raise Exception('Failed to connect')
        
        # Start ROBOFORTH
        self.arm.write('ROBOFORTH')
        print(self.arm.read())
        self.arm.write('START')
        print(self.arm.read())
        self.connected = True
        
        print('Robot connected!')


    def disconnect(self):
        """ Disconnect arm """
        self.arm.disconnect()
        if not self.arm.is_connected():
            print('Robot disconnected!')


    def de_energise(self, print_read=True):
        """ De-energise the robot """
        self.arm.write('DE-ENERGISE')
        reading = self.arm.read()
        if print_read:
            print(reading)

        self.energised = False

    def energise(self, print_read=True):
        """ Energises robot"""
        self.arm.write('ENERGISE')
        reading = self.arm.read()
        if print_read:
            print(reading)

        self.energised = True


    def calibrate(self):
        # Calibration - make sure the robot is vertical!
        self.arm.write('CALIBRATE')
        reading = self.arm.read()
        # Check if calibration successful
        if reading.split()[-2] == 'OK':
            self.calibrated = True
            print('Robot calibrated!')
        else:
            self.calibrated = False
            raise Exception('Failed to calibrate')


    def to_joint(self, print_read=True):
        """ Changes movement mode to joint mode and displays reading"""
        self.arm.write('JOINT')
        reading = self.arm.read()
        if print_read:
            print(reading)

        self.mode = 'j'


    def to_cartesian(self, print_read=True):
        """ Changes movement mode to cartesian mode and displays reading"""
        self.arm.write('CARTESIAN')
        reading = self.arm.read()
        if print_read:
            print(reading)
        self.mode = 'c'


    def get_joint_pos(self):
        """ Returns JOINT position as a 5 dimensional vector, 
        correspondng to [WAIST, SHOULDER, ELBOW, HAND, WRIST] coordinates"""
        
        if self.mode == 'j':
            self.arm.write('WHERE')
            reading = self.arm.read()
            # TEMP
            print(reading)
            reading_split = reading.split()

            coords = [int(reading_split[7]), int(reading_split[8]),
            int(reading_split[9]), int(reading_split[10]), int(reading_split[11])]

        else:
            self.to_joint(print_read=False)
            coords = self.get_joint_pos()
            self.to_cartesian(print_read=False)


        return coords

    def get_cart_pos(self):
        """ Returns CARTESIAN position as a 5 dimensional vector, 
        correspondng to [X, Y, Z, PITCH, ROLL] coordinates"""

        
        if self.mode == 'c':
            self.arm.write('WHERE')
            reading = self.arm.read()
            # TEMP
            print(reading)
            reading_split = reading.split()

            coords = [int(float(reading_split[8])*10), int(float(reading_split[9])*10),
            int(float(reading_split[10])*10), int(float(reading_split[11])), int(float(reading_split[12]))]

        else:
            self.to_cartesian(print_read=False)
            coords = self.get_cart_pos()
            self.to_joint(print_read=False)


        return coords

    def move_home(self, print_read=True):
        """ Moves robot to HOME position"""
        self.arm.write('HOME')
        reading = self.arm.read()
        if print_read:
            print(reading)


    def get_ready(self, print_read=True):
        """ Send the robot to "READY" position and displays reading (used after being in HOME position)"""
        self.arm.write('READY')
        reading = self.arm.read()
        if print_read:
            print(reading)


    def move_by_cart(self, x, y, z, print_read=True):
        """ Moves BY a specified number in x, y, z directions"""
        if self.mode == 'c':
            self.arm.write('{} {} {} MOVE'.format(x, y, z))
            reading = self.arm.read()
            if print_read:
                print(reading)
        else:
            self.to_cartesian(print_read=False)
            self.move_by_cart(x,y,z)
            self.to_joint(print_read=False)


    def move_to_cart(self, x, y, z, print_read=True):
        """ Moves TO a specified number in x, y, z directions"""
        if self.mode == 'c':
            self.arm.write('{} {} {} MOVETO'.format(x, y, z))
            reading = self.arm.read()
            if print_read:
                print(reading)
        else:
            self.to_cartesian(print_read=False)
            self.move_to_cart(x,y,z)
            self.to_joint(print_read=False)

    def write_command(self, command, print_read=True):
        """ Writes a passed command argument to the robot arm,
        expects ROBOFORTH language
        Results in setting mode, energised and calibrated attributes to None
        hence try to avoid using"""
        self.arm.write(command)
        reading = self.arm.read()
        if print_read:
            print(reading)
        
        self.mode = None
        self.energised = None
        self.calibrated = None


    def write_command_loop(self, print_read=True):
        """ Go into a manual command loop where input is asked
        for each action (in ROBOFORTH language)
        Results in setting mode, energised and calibrated attributes to None
        hence try to avoid using"""
        command=None
        while command!='y':
            command = input('Write a command for the Robot or write "y" if ready:')
            if command!='y':
                self.arm.write(command)
                reading = self.arm.read()
                if print_read:
                    print(reading)

        self.mode = None
        self.energised = None
        self.calibrated = None


    # OLD FUNCTIONS

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



