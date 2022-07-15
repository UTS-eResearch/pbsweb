#!/bin/bash

# Remove intermediate files created by SWIG or Python tests,
# and which are not needed at runtime.

rm -f pbs.pyc
rm -f pbsutils.pyc
rm -f pbs_wrap.c
rm -f pbs_wrap.o
rm -fr __pycache__

