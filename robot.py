#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 12:13:35 2019

@author: stan
"""
import json
import time
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
            #action_now = '{} {} {} MOVE'.format(x, y, z)
            #self.is_safe_cartesian(action_now)
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
            
            
    def run_trajectory(self, traj):
        """ Accepts length 15 array, traj
         Assume each point consists of values for [WAIST, SHOULDER, ELBOW, L-HAND, WRIST] in this order""" 
        assert len(traj) == 15
        
        # Extracts the three points
        first_point = traj[0:5]
        second_point = traj[5:10]
        third_point = traj[10:]
        points = [first_point, second_point, third_point]
    
        # Print out for debugging
        print("First point:", first_point)
        print("Second point:", second_point)
        print("Third point:", third_point)
        
        position_log = []
        
        # Get robot to move to the 3 points
        for n in range (len(points)):
            print("Point {}".format(n+1))
            # Wait 3 seconds between moving between the two points for 
            # human to be able to observe transitions
            time.sleep(3)
            # Select the point
            point = points[n]
            x = int(point[0]) # Assume first three values represent the xyz coordinate
            y = int(point[1])
            z = int(point[2])
            l_hand_value = int(point[3]) # Assume 4th value is the amount to move L_HAND by
            wrist_value = int(point[4]) # Assume 5th value is the amount to move WRIST by
            
            position_log.append(self.get_cart_pos_time())
            
            # Move to cartesian position
            # Check if safe first
            #cartesian_roboforth_command = '{} {} {} MOVETO'.format(x, y, z)
            #self.is_safe_cartesian(cartesian_roboforth_command)
            # Now move if safe
            self.move_to_cart(x, y, z)
    
            position_log.append(self.get_cart_pos_time())
    
            # Move L_HAND, have to move WRIST as well - the two are not independent
            # Check if safe first
            #l_hand_roboforth_command = 'TELL L-HAND {} MOVETO'.format(l_hand_value)
            #self.is_safe_joint(l_hand_roboforth_command)
            # Now move if safe
            self.move_to_joint('L-HAND', l_hand_value)
            
            position_log.append(self.get_cart_pos_time())
            
            # Move WRIST
            # Check if safe first
            #wrist_roboforth_command = 'TELL WRIST {} MOVETO'.format(wrist_value)
            #self.is_safe_joint(wrist_roboforth_command)
            # Now move if safe
            self.move_to_joint('WRIST', wrist_value)
            
            position_log.append(self.get_cart_pos_time())
            
        return position_log
    
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

    def move_to_joint(self, joint, deg):
        # dirn is 1 or -1 moves joint in opposite directions
        if self.mode == 'j':
            # move arm
            if joint == 'L-HAND':            
                self.arm.write('TELL L-HAND WRIST {} {} MOVETO'.format(deg, deg))
            else:
                self.arm.write('TELL {} {} MOVETO'.format(joint, deg))
            # wait for return message
            return_msg = self.arm.read()
            # reset to original position if encountered a problem
            if return_msg.split()[-2] != 'OK':
                self.reset()
        else:
            self.to_joint()
            self.move_to_joint(joint, deg=deg)
    
    def is_safe_joint(self, action, hand_min=-2000, hand_max=6800):
        """ Checks whether the action passed to the robot is safe
        action is a string of ROBOFORTH command to robot"""
        # TODO Fix get_position such that cartesian would not cause bug

        self.to_joint() # TODO fix this
        hand_coords = self.get_joint_pos()
        print("joint coords", hand_coords)

        if (action.split()[0] == "TELL") and (action.split()[1] == "L-HAND"):
            # TODO add differentiation for relative and absolute commands (MOVE/MOVETO)
            hand_movement = int(action.split()[2])

        if (hand_coords[0] + hand_movement < hand_min) or (hand_coords[0] + hand_movement > hand_max):
            raise Exception('Motion is not safe!')

    def is_safe_cartesian(self, action, x_min = -2000, x_max = 2000, 
            y_min = 2000, y_max = 4500, z_min = -1500, z_max = 2000):
        """ Checks whether the action passed to the robot is safe
        action is a string of ROBOFORTH command to robot"""
        # TODO Fix get_position such that cartesian would not cause bug

        self.to_cartesian()
        hand_coords = self.get_cart_pos()

        if (action.split()[3] == "MOVETO"):
            x_movement = int(action.split()[0])
            y_movement = int(action.split2000()[1])
            z_movement = int(action.split()[2])
            pitch = int(action.split()[3])

            if (x_movement < x_min) or (x_movement > x_max):
                    raise Exception('Motion is not safe!')
            if (z_movement < z_min) or (z_movement > z_max):
                    raise Exception('Motion is not safe!')
            if (hand_coords[2]== 0):
                if (y_movement < y_min ) or (y_movement > y_max):
                    raise Exception('Motion is not safe!')
            elif (hand_coords[2] < 0) and (hand_coords[2] > -1000):
                pass #check pitch
            elif (hand_coords[2] <= -1000) and (hand_coords[2] > -1500):
                pass #check pitch
            
        if (action.split()[3] == "MOVE"):
            x_movement = int(action.split()[0])
            y_movement = int(action.split()[1])
            z_movement = int(action.split()[2])

            if (x_movement + hand_coords[0] < x_min) or (x_movement + hand_coords[0] > x_max):
                    raise Exception('Motion is not safe!')
            if (z_movement + hand_coords[2]< z_min) or (z_movement + hand_coords[2] > z_max):
                raise Exception('Motion is not safe!')
            if (hand_coords[2]== 0):
                if (y_movement + hand_coords[1] < y_min ) or (y_movement + hand_coords[1] > y_max):
                    print(y_movement + hand_coords[1])
                    raise Exception('Motion is not safe!')
            elif (hand_coords[2] < 0) and (hand_coords[2] > -1000):
                pass #check pitch
            elif (hand_coords[2] <= -1000) and (hand_coords[2] > -1500):
                pass #check pitch
    
    def get_cart_pos_time(self):
        return self.get_cart_pos()+[time.time()]
    
    def reset(self):
        self.move_home()
        self.to_joint(print_read=False)
        self.arm.write('TELL WAIST -127 MOVETO')
        print(self.arm.read())
        self.arm.write('TELL SHOULDER 2394 MOVETO')
        print(self.arm.read())
        self.arm.write('TELL L-HAND 1722 MOVETO')
        print(self.arm.read())
        self.arm.write('TELL WRIST -1768 MOVETO')
        print(self.arm.read())
        self.arm.write('TELL ELBOW 5308 MOVETO')
        print(self.arm.read())
        self.to_cartesian(print_read=False)
        
    def run_encoded_pickup(self):
        inp = input('Start')
        trial_name = input('Enter trial number or name: ')
        log = []
        
        log.append(self.get_cart_pos_time())
        # GET TO POSITION 1
        self.to_joint(print_read=False)
        self.arm.write('TELL WAIST -127 MOVETO')
        print(self.arm.read())
        self.arm.write('TELL SHOULDER 3437 MOVETO')
        print(self.arm.read())
        self.arm.write('TELL L-HAND 757 MOVETO')
        print(self.arm.read())
        self.arm.write('TELL WRIST -2854 MOVETO')
        print(self.arm.read())
        self.arm.write('TELL ELBOW 6011 MOVETO')
        print(self.arm.read())
        self.to_cartesian(print_read=False)
        log.append(self.get_cart_pos_time())
        
        inp = input('Position 1 achieved, proceed?')
        
        log.append(self.get_cart_pos_time())
        self.move_by_cart(100, -800, -500, print_read=False)
        self.to_joint(print_read=False)
        self.arm.write('TELL WRIST -2000 MOVE')
        self.arm.read()
        log.append(self.get_cart_pos_time())
        self.to_cartesian(print_read=False)        
        log.append(self.get_cart_pos_time())
        
        inp = input('Position 2 achieved, proceed?')
        
        log.append(self.get_cart_pos_time())
        self.move_by_cart(100, 400, -100, print_read=False)
        self.to_joint(print_read=False)
        self.arm.write('TELL L-HAND WRIST -1000 MOVE')
        self.arm.read()
        self.to_cartesian(print_read=False)        
        log.append(self.get_cart_pos_time())
        
        inp = input('Position 3 achieved, proceed?')        
        
        log.append(self.get_cart_pos_time())
        self.move_by_cart(0, 0, 1500, print_read=False)        
        log.append(self.get_cart_pos_time())
        
        fname = trial_name+'robot.json'
        with open(fname, 'w+') as f:
            json.dump({'log': log}, f)
            
    def __del__(self):
        self.de_energise()
        self.disconnect()
    
    # OLD FUNCTIONS

    def rotate_by_old(self, joint, dirn=1, deg=120):
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
    	hand_coords = self.get_joint_pos()

    	if (action.split()[0] == "TELL") and (action.split()[1] == "HAND"):
    		# TODO add differentiation for relative and absolute commands (MOVE/MOVETO)
    		hand_movement = int(action.split()[2])


    		if (hand_coords[0] + hand_movement < hand_min) or (hand_coords[0] + hand_movement > hand_max):
    			raise Exception('Motion is not safe!')
    
        


