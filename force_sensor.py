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
        
    def get_forces_from_reading(self, line):
        if len(line)>=14:
            fv = float(line.split(b' ')[0])
            fh1 = float(line.split(b' ')[1])
            fh2 = float(line.split(b' ')[2])
            return fv, fh1, fh2
        
    def test_connection(self):
        ts = time.time()
        while time.time()-ts<20:
            line = self.ser.readline()[:-2]
            print(line)
            print(self.get_forces_from_reading(line))
    
    def log_pickup(self):
        force_readings = []
        ts = time.time()
        while time.time()-ts<15:
            line = self.ser.readline()[:-2]
            if len(line)>=14:
                fv, fh1, fh2 = self.get_forces_from_reading(line)
                force_readings.append([fv, fh1, fh2])
        force_readings = np.array(force_readings)
        result_dict = {'fv':list(force_readings[:, 0]),'fh1':list(force_readings[:, 1]),
                       'fh2':list(force_readings[:, 2])}
        success = input('Success?')
        fname = str(datetime.now().strftime('%Y%m-%d%H-%M%S-'))+success+'.json'
        with open(fname, 'w+') as f:
            json.dump(result_dict, f)
        print(success, fname, result_dict)
    
    def __del__(self):
        self.ser.close()
        
forceSensor = ForceSensor()
#forceSensor.test_connection()
forceSensor.log_pickup()