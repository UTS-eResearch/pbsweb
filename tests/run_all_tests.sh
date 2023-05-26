#!/bin/bash

# Run all PBS node, queue and job tests.
# The output should show all have passed.
#
# Usage: 
#   cd tests 
#   ./run_all_tests.sh

# Define some colors.
GREEN='\033[0;32m'
RED='\033[0;31m'
BOLD_RED='\033[1;31m'
BOLD_GREEN='\033[1;32m'
NC='\033[0m' # No Color

# Set green for passed and bold red for failed.            
pass="${GREEN}PASSED${NC}"
fail="${BOLD_RED}FAILED${NC}"

###########
# Functions
###########

function test_pbs {
    # This just tests being able to load the pbs.py module 
    # and use that to query PBS.
    tests="\
    test_pbs_minimal.py \
    test_pbs_nodes.py   \
    test_pbs_queues.py  \
    test_pbs_jobs.py"

    for test in $tests; do
        python $test > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "$pass $test"
        else
            echo -e "$fail $test"
        fi
    done
}

function test_pbsutils {
    # This just tests the pbsutils.py module.
    for arg in nodes queues jobs; do
        python test_pbsutils.py $arg > /dev/null
        if [ $? -eq 0 ]; then
            echo -e "$pass test_pbsutils.py $arg"
        else
            echo -e "$fail test_pbsutils.py $arg"
        fi
done
}

###########
# Main
###########

thisdir="$(pwd)"
thisdir="${thisdir##*/}"

if [ "$thisdir" == "tests" ]; then
    # The Python virtual environment needs to be loaded.
    source /var/www/wsgi/virtualenvs/pbsweb/bin/activate
    test_pbs
    test_pbsutils
    deactivate
else
    echo "The tests need to be run from within the tests directory."
    echo "Exiting."
fi

