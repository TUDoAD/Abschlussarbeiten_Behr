# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 10:33:27 2023

@author: mvoel
"""

import subprocess

command = ['python', 'CreateSubstanceJSON.py']

process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

stdout, stderr = process.communicate()

# print output
"""
print("Standard Output:")
print(stdout.decode())
print("Standard Error:")
print(stderr.decode())
"""