#!/bin/bash

# This installs or updates the application from the git directory 
# to the website applications destination.

confs='/var/www/wsgi/confs'
dest='/var/www/wsgi/apps/pbsweb'

# Check user really wants to install.
echo "This will install to $confs and $dest "
read -r -p "Type \"yes\" to install. Any other key will exit: " REPLY
if [[ $REPLY != "yes" ]]; then
    echo "exiting"
    exit 0
fi

# Do the install. 
if [ ! -d $confs ]; then
    mkdir -p $confs
fi

if [ ! -d $dest ]; then
    mkdir -p $dest
fi

cp emperor.ini /var/www/wsgi/
cp pbsweb.ini $confs
cp pbsweb.py $dest
cp pbsutils.py $dest
cp pbs.py $dest
cp _pbs.so $dest
cp -r views $dest
cp -r static $dest

# Touch the wsgi conf if this install has just updated any of the above files.
touch $confs/pbsweb.ini

