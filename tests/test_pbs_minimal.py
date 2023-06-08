#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Just test if the pbs module can be loaded without errors.
This script should not produce any output if pbs can be loaded OK.
'''

import os,sys
try:
    # Running from above the tests directory.
    sys.path.append(os.path.abspath("./src"))
    import pbs 
except:
    # Running from within the tests directory.
    sys.path.append(os.path.abspath("../src"))
    import pbs 

