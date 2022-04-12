#!/bin/bash

# This script installs the dependencies for the pbsweb application.
# The script should be run as a normal, unprivileged user that has sudo rights.
# This will ensure that the python virtual environments and the web application 
# does not run as root, and has minimal privileges.
#
# Usage: 
#
#   $ ./install_dependencies.sh
#

###############
# Configuration
###############

apps='/var/www/wsgi/apps'
confs='/var/www/wsgi/confs'
envs='/var/www/wsgi/virtualenvs'

# This is the Python version that will be installed in the virtual environments.
# This version of Python needs to be already available in your system.
python=python3.8

# System packages to be installed via dnf.
packages="python38-devel openssl-devel swig"

###########
# Functions
###########

function check_sudo {
    local sudo_prompt

    sudo_prompt=$(sudo -nv 2>&1)
    if [ $? -eq 0 ]; then
        echo "Your sudo access is currently valid."
	return 0
    fi

    echo $sudo_prompt | grep -q '^sudo:'
    if [ $? -eq 0 ]; then
        echo "Please enter your password to use sudo."
	sudo -v
	return 0
    fi
    echo "You do not have sudo"
}

########
# Checks
########

if [[ $EUID -eq 0 ]]; then
   echo "You should NOT be root to run this script."
   echo "You should run it as an unprivileged user that has sudo rights."
   echo "NOT be root to run this script. Exiting"
   exit 0
fi
this_user="$USER"

# Check this unprivileged user has sudo rights.
check_sudo

###################
# Start the install
###################

echo "Installing system packages ..."
for p in $packages; do
    echo "  $p"
    sudo dnf -qy install $p
done

# If there is no existing emperor service then copy this one into place.
# We will not start it. The user should enable/start it manually.
if [ ! -f /etc/systemd/system/emperor.uwsgi.service ]; then
    sudo cp confs/emperor.uwsgi.service /etc/systemd/system/
fi

# Create a directory for the web sockets.
sudo mkdir -p /run/uwsgi
sudo chown nginx:nginx /run/uwsgi

# Create directories for the application.
sudo mkdir -p /var/www/wsgi
sudo chown $this_user:$this_user /var/www/wsgi

# Underneath /var/www/wsgi the directories will be owned 
# by the user running this script.
for dir in $apps $confs $envs; do 
    if [ ! -d $dir ]; then
        echo "creating $dir"
        mkdir -p $dir
    fi
done

# Check we do have the correct Python version on this system.
which $python > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Could not find the correct Python version on this system. Exiting"
    exit 0
fi

echo "Creating $python virtual environments."
$python -m venv ${envs}/emperor --prompt="emperor"
$python -m venv ${envs}/pbsweb  --prompt="pbsweb"

# For each of these virtual environments install required packages
# and create a requirements file.

source ${envs}/emperor/bin/activate
python -m pip -q install --upgrade pip
for package in pip-review uwsgi; do
    pip -q install $package
done
pip freeze > ${envs}/requirements_emperor.txt
echo "UWSGI version = $(uwsgi --version)"
deactivate

source ${envs}/pbsweb/bin/activate
python -m pip -q install --upgrade pip
for package in pip-review bottle Jinja2; do
    pip -q install $package
done
pip freeze > ${envs}/requirements_pbsweb.txt
deactivate

echo ''
echo 'The dependencies for pbs have now been installed.'
echo 'You should now be able to run "./install_pbsweb.sh"'
echo ''

