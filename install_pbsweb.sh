#!/bin/bash

# This installs or updates the application from the git directory
# to the test or production website application destination.
#
# Usage: 
#
#   $ ./install_pbsweb.sh test | prod

###############
# Configuration
###############

confs='/var/www/wsgi/confs'

###########
# Functions
###########

function will_install {
    # Show the user what will be installed by this script.
    echo "This script will install the following:"
    echo "  Configuration files to $confs"
    echo "  Python code to $dest"
    echo "  Templates to ${dest}/views"
    echo ""
}

echo ""
echo "------------------------"
echo "Install or Update PBSWeb"
echo "------------------------"
echo ""

# Check number of args is one.
if [ $# -lt 1 ]; then
    echo "Usage:  $0 test | prod"
    echo ""
    echo "You need to specify either test or prod (for production)."
    echo ""
    exit 0;
fi

# Check user has entered a valid option.
if [ $1 == 'test' ]; then
    dest='/var/www/wsgi/apps/pbsweb_test'
elif [ $1 == 'prod' ]; then
    dest='/var/www/wsgi/apps/pbsweb'
else
    echo "Error, unknown option: $1"
    echo "Exiting."
    exit 0
fi

# Exit if these files are not found.
if [ ! \( -f pbs.py -a -f _pbs.so \) ]; then
    echo "Error: missing pbs.py or _pbs.so"
    echo "Perhaps you forgot to run the SWIG script?"
    echo "Exiting."
    exit 0
fi

will_install

# Check user really wants to install.
# The variable ${1^^} just uppercases the first arg i.e. it will show TEST or PROD. 
echo "This will install to ${1^^}"
read -r -p "Type \"y\" to install. Any other key will exit: " REPLY
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "exiting"
    exit 0
fi

################
# Do the install
################

if [ ! -d $confs ]; then
    mkdir -p $confs
fi

if [ ! -d $dest ]; then
    mkdir -p $dest
fi

# Copy the configuration files.
cp confs/emperor.ini /var/www/wsgi/

if [ $1 == 'test' ]; then
    cp confs/pbsweb_test.ini $confs
elif [ $1 == 'prod' ]; then
    cp confs/pbsweb.ini $confs
else
    echo "Error, unknown option: $1"
    exit 0
fi

# Copy the python code.
cp pbsweb.py $dest
cp pbsutils.py $dest
cp pbs.py $dest
cp _pbs.so $dest

# Copy the HTML templates.
cp -r views $dest
cp -r static $dest

# Touch the wsgi conf as this install may have updated any of the above files.
touch $confs/pbsweb.ini
touch $confs/pbsweb_test.ini

echo ""
echo "You may have to do this:"
echo "sudo systemctl restart nginx.service"

