#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 14:38:47 2020

@author: stan
"""
from datetime import datetime
import glob
import json
import numpy as np
import serial
import time

BAUD_RATE=38400
TIMEOUT=1

def arduino_serial_port(port):
    ''' Create a serial connect to the Arduino. '''
    return serial.Serial(port, baudrate=BAUD_RATE, timeout=TIMEOUT)

def find_port(port_name='/dev/ttyACM0'):
    ''' Find a port to connect to '''
    # Find ports matching the supplied glob.
    ports = glob.glob(port_name)
    print(ports)
    if len(ports) == 0:
        return None

    for port in ports:
        with arduino_serial_port(port) as ser:
            if not ser.isOpen():
                ser.open()
        return port
    
    raise Exception('Connection found, but is not responsive.')
    return None

class ForceSensor(object):
    def __init__(self):
        self.ser = None
        self.port = None
        self.connect()
        
    def connect(self):
        port = find_port()
        if port:
            self.port = port
        else:
            manual_port = input("Enter port Arduino is connected to (e.g. COM4): ")
            print("Selected port", manual_port)
            self.port = manual_port
        try:
            self.ser = arduino_serial_port(self.port)
        except:
            raise Exception("Port not found")
    
    """ Flushes the input buffer and returns the start of the logging time """
    def start_logging_forces(self):
        self.ser.flushInput()
        ts=time.time()
        return ts
    
    """ Reads the whole buffer, returns the list of forces between start and end
     of the trial and the end time"""
    def end_logging_forces(self):
        lines = self.ser.read(self.ser.in_waiting).split(b'\r\n')
        tf = time.time()
        force_readings = []
        for line in lines:
            if len(line)>=14:
                fv, fh1, fh2 = self.get_forces_from_reading(line)
                force_readings.append([fv, fh1, fh2])
        force_readings = np.array(force_readings)
        force_log = {'fv':list(force_readings[:, 0]),'fh1':list(force_readings[:, 1]),
                       'fh2':list(force_readings[:, 2])}
        return force_log, tf
    
    def get_forces_from_reading(self, line):
        if len(line)>=14:
            fv = float(line.split(b' ')[0])
            fh1 = float(line.split(b' ')[1])
            fh2 = float(line.split(b' ')[2])
            return fv, fh1, fh2
        
    def test_connection(self):
        self.ser.flushInput()
        ts = time.time()
        while time.time()-ts<5: 
            line = self.ser.readline()[:-2]
            print(self.get_forces_from_reading(line))
        #print(self.ser.read(self.ser.in_waiting).split(b'\n'))
        
    
    def log_pickup(self):
        trial_name = input('Enter trial number or name: ')
        force_readings = []
        ts = time.time()
        while time.time()-ts<20:
            line = self.ser.readline()[:-2]
            if len(line)>=14:
                fv, fh1, fh2 = self.get_forces_from_reading(line)
                force_readings.append([fv, fh1, fh2])
        tf = time.time()
        force_readings = np.array(force_readings)
        result_dict = {'fv':list(force_readings[:, 0]),'fh1':list(force_readings[:, 1]),
                       'fh2':list(force_readings[:, 2]), 't':[ts, tf]}
        fname = trial_name+'fsensor'+'.json'
        with open(fname, 'w+') as f:
            json.dump(result_dict, f)
        print(fname, result_dict)
    def __del__(self):
        self.ser.close()
        
#forceSensor = ForceSensor()
#forceSensor.test_connection()
#forceSensor.test_connection()