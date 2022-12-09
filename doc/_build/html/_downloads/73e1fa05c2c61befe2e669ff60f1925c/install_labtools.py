#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 11:32:45 2020

install/update the labtools package

@author: boeglinw
"""

import subprocess
import sys


#%%
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
# install("LabTools3")

#%%
def uninstall(package):
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package])
# uninstall("LabTools3")

#%%
def update(package):
    uninstall(package)
    install(package)

update("LabTools3")
