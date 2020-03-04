#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 19:10:45 2020

@author: stan
"""

import json
from matplotlib import pyplot as plt
import os



for root, dirs, files in os.walk('./results_robot'):
    for name in files:
        fname = os.path.join(root, name)
        
        if fname.endswith('fsensor.json'):
            trial_name = name.split('fsensor')[0]
            with open(fname) as f:
                results = json.load(f)
            with open(os.path.join(root, trial_name+'robot.json')) as f:
                log = json.load(f)
                
            [ts, tf] = results['t']
            log_times = [int(len(results['fv'])*(log_entry[-1]-ts)/(tf-ts)) for log_entry in log]
            fig, ax = plt.subplots()
            ax.plot(log_times, [log_entry[0] for log_entry in log], label='x')
            ax.plot(log_times, [log_entry[0] for log_entry in log], label='y')
            ax.plot(log_times, [log_entry[0] for log_entry in log], label='z')
            ax.plot(log_times, [log_entry[0] for log_entry in log], label='roll')
            ax.plot(log_times, [log_entry[0] for log_entry in log], label='pitch')
            ax.plot(range(len(results['fv'])), results['fv'], label='vertical')
            ax.plot(range(len(results['fh1'])), results['fh1'], label='horizontal1')
            ax.plot(range(len(results['fh2'])), results['fh2'], label='horizontal2')
            ax.title.set_text(trial_name)
            ax.legend()
            plt.show()