#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 19:10:45 2020

@author: stan
"""

import json
from matplotlib import pyplot as plt
import os



for root, dirs, files in os.walk('.'):
    for name in files:
        fname = os.path.join(root, name)
        
        if fname.endswith('fsensor.json'):
            trial_name = name.split('fsensor')[0]
            with open(fname) as f:
                sensor_readings = json.load(f)
            with open(os.path.join(root, trial_name+'robot.json')) as f:
                robot_positions = json.load(f)
                
            [ts, tf] = sensor_readings['t']
            log_times = [int(len(sensor_readings['fv'])*(log_entry[-1]-ts)/(tf-ts)) 
                        for log_entry in robot_positions['log']]
            fig, ax = plt.subplots()
            ax.plot(log_times, [log_entry[0] for log_entry in robot_positions['log']],
                    label='x')
            ax.plot(log_times, [log_entry[1] for log_entry in robot_positions['log']],
                    label='y')
            ax.plot(log_times, [log_entry[2] for log_entry in robot_positions['log']],
                    label='z')
            ax.plot(log_times, [log_entry[3] for log_entry in robot_positions['log']], 
                    label='roll')
            ax.plot(log_times, [log_entry[4] for log_entry in robot_positions['log']],
                    label='pitch')
            ax.plot(range(len(sensor_readings['fv'])), sensor_readings['fv'], label='vertical')
            ax.plot(range(len(sensor_readings['fh1'])), sensor_readings['fh1'], label='horizontal1')
            ax.plot(range(len(sensor_readings['fh2'])), sensor_readings['fh2'], label='horizontal2')
            ax.title.set_text(trial_name)
            ax.legend()
            plt.show()