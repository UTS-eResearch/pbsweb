#!/bin/bash

# This script customises PBSWeb for the University of Technology Sydney.
# PBSWeb must have already been installed via the normal install script. 
# This script overwrites the standard templates with UTS specific templates.
#
# sudo is not needed to run the script.
#
# Usage: ./install_pbsweb_UTS.sh test | prod

confs='/var/www/wsgi/confs'

echo ""
echo "---------------------------------------"
echo "Update PBSWeb with UTS Specific Changes"
echo "---------------------------------------"
echo ""

# Check number of args is one.
if [ $# -lt 1 ]; then
    echo "Usage:  $0 test | prod"
    echo ""
    echo "You need to specify either test or prod (for production)."
    echo ""
    exit 1;
fi

# Check user has entered a valid option.
if [ $1 == 'test' ]; then
    dest='/var/www/wsgi/apps/pbsweb_test'
elif [ $1 == 'prod' ]; then
    dest='/var/www/wsgi/apps/pbsweb'
else
    echo "Error, unknown option: $1"
    exit 0
fi

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

# Copy the HTML templates.
cp src/views/head_UTS.html $dest/views/head.html
cp src/views/jobs_UTS.j2 $dest/views/jobs.j2

# Copy the javascript which enables us to sort columns.
cp src/static/sorttable.js $dest/static/
 
# Touch the wsgi confs to get wsgi to reload the templates.
touch $confs/pbsweb.ini
touch $confs/pbsweb_test.ini

echo ""
echo "You probably do not need to do this:"
echo "sudo systemctl restart nginx.service"

