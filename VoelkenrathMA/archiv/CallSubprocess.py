# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 10:33:27 2023

@author: mvoel
"""

import subprocess

def call_subprocess(compounds):
    command = ['python', 'DWSIMWork.py', "create_compound"]
    
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    input_data = compounds
    
    stdout, stderr = process.communicate(input=input_data)
    
    # print output
    print("Standard Output: stdout")
    print("Standard Error: stderr")
    