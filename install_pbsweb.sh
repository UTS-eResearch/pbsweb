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
    echo "  PBSWeb $version_string to $dest"
    echo "  Templates to ${dest}/views"
    echo ""
}

function update_version {
    # If this repo is checked out at a tagged release version then just use the
    # tag number only for the displayed version, like 2.0.0. If this repo is not
    # at a tagged release then we wish to know the exact patch that a user might
    # be using so use the long "git describe" string like 2.0.0-6-g382c9e0.
    # The command "git describe" string format is:
    #   'tag' - 'number of commits' - 'abbreviated commit name'
    # e.g. git describe v2.0.0 --long
    #      v2.0.0-0-g7ef3b13  <== The middle number is zero.
    #
    # ie.g. git describe --long
    #      v2.0.0-6-g382c9e0  <== The middle number is not zero.
    #
    description=$(git describe --long)

    version_num=$(echo $description | cut -d '-' -f1)  # e.g. v2.0.0
    num_commits=$(echo $description | cut -d '-' -f2)  # e.g. 6
    name_commit=$(echo $description | cut -d '-' -f3)  # e.g. g382c9e0
    if [ $num_commits -eq 0 ]; then
        # This is a tagged release.
	version_string=$version_num
    else
        # This version has commits after the last tagged release.
	version_string=$description
    fi
    cat src/pbsweb.py | sed "s/VERSION_STRING/$version_string/" > src/pbsweb.tmp
}

######
# Main
######

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
if [ ! \( -f src/pbs.py -a -f src/_pbs.so \) ]; then
    echo "Error: missing pbs.py or _pbs.so"
    echo "Perhaps you forgot to run the SWIG script?"
    echo "Exiting."
    exit 0
fi

update_version
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
if [ $1 == 'test' ]; then
    cp confs/pbsweb_test.ini ${confs}/
elif [ $1 == 'prod' ]; then
    cp confs/pbsweb.ini ${confs}/
else
    echo "Error, unknown option: $1"
    exit 0
fi

# Copy the python code.
cp src/pbsweb.tmp ${dest}/pbsweb.py
cp src/pbsutils.py $dest
cp src/pbs.py $dest
cp src/_pbs.so $dest
rm -f src/pbsweb.tmp

# Copy the HTML templates.
cp -r src/views $dest
cp -r src/static $dest

# Touch the wsgi conf as this install may have updated any of the above files.
touch ${confs}/pbsweb.ini
touch ${confs}/pbsweb_test.ini

echo ""
echo "You may have to do this:"
echo "sudo systemctl restart nginx.service"
echo ""
echo "An example PBSWeb page should now be available at:"
echo "http://your_server/pbsweb.html"
echo ""

