#!/bin/bash

# Remove files created by SWIG or Python tests.

rm -f pbs.py
rm -f pbs.pyc
rm -f pbsutils.pyc
rm -f pbs_wrap.c
rm -f *.so
rm -fr __pycache__

