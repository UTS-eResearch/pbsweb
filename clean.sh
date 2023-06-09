#!/bin/bash

# Remove intermediate files created by SWIG or Python tests,
# and which are not needed at runtime.

rm -f src/pbs.pyc
rm -f src/pbsutils.pyc
rm -f src/pbs_wrap.c
rm -f src/pbs_wrap.o
rm -fr src/__pycache__

