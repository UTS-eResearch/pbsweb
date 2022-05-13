#!/bin/bash

# This script uses the PBS supplied include file pbs_ifl.h (and pbs.i) 
# to create pbs.py, pbs_wrap.c and _pbs.so.
#
# Notes:
# 1. The package "openssl-devel" provides the libs to link with, 
#    i.e. "... -lcrypto -lssl".
#    $ rpmquery -ql openssl-devel | grep lib
#      /usr/lib64/libcrypto.so
#      /usr/lib64/libssl.so

#############################
# Set your configuration here
#############################

conf="/etc/pbs.conf"  # PBS configuration file

# Specify here where the include files are for the version of Python that you are using.
# If you are using a Python in a virtual environment then use the include location that 
# the virtual env was derived from.
PYTHON_INCL="/usr/include/python3.8"

SWIG_EXEC="/usr/bin/swig"

# You should not need to change anything below here.

# Make sure we have a PBS config file.
if [ ! -f $conf ]; then
   echo "Error: missing PBS configuration file $conf"
   exit 0
fi 

# The PBS config file must be sourced to provide $PBS_EXEC.
. $conf

# Set LD_RUN_PATH here so users should not need to export LD_LIBRARY_PATH at run time.
# If you link with libpbs.so below you will need to export LD_RUN_PATH.
# If you link with libpbs.a then LD_RUN_PATH will not be needed.
export LD_RUN_PATH=$PBS_EXEC/lib

# Running swig creates pbs.py and pbs_wrap.c
$SWIG_EXEC -I$PBS_EXEC/include -python pbs.i

if [ $? -ne 0 ]; then
    echo 'Error: You are probably missing the file: /opt/pbs/include/pbs_ifl.h'
    exit 0
fi

# Running gcc creates _pbs.so
# Note: This is what I had before, compile and link in one step. 
# But I have commented out this and separated the compile and link
# as its then easier to debug errors during build.
#gcc -shared -fPIC -I$PYTHON_INCL -I$PBS_EXEC/include pbs_wrap.c \
#    $PBS_EXEC/lib/libpbs.a \
#    -L/lib -lpthread -lcrypto -lssl \
#    -o _pbs.so 

# Compiling
gcc -c -shared -fpic -I$PYTHON_INCL -I$PBS_EXEC/include pbs_wrap.c # -o tmp.so 

# Linking
#gcc -shared -fpic -L/lib -L/opt/pbs/lib \
gcc -shared -fpic -L/opt/pbs/lib \
    $PBS_EXEC/lib/libpbs.so pbs_wrap.o \
    -lpthread -lcrypto -lssl -lsec \
    -o _pbs.so 

# It does not need to be executable.
chmod ugo-x _pbs.so

