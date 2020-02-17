#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 14:38:47 2020

@author: stan
"""
import glob
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
            raise Exception('Port not found')
        self.ser = arduino_serial_port(self.port)
        
    def test_connection(self):
        ts = time.time()
        while time.time()-ts<15:
            line = self.ser.readline()[:-2]
            if len(line)>=13:
                fv = float(line.split(b' ')[0])
                fh1 = float(line.split(b' ')[1])
                print(fv, fh1)
    """
    def log_pickup(self, success):
        # success indicates if the pickup was successful or not
        # s means successful
        # u means unsuccessful
        # p means partially successful
        ts = time.time()
    """    
    def __del__(self):
        self.ser.close()
        
forceSensor = ForceSensor()
forceSensor.test_connection()