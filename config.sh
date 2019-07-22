
# This tool uses python3. Make this variable to point to the location of python3
# rhel and centos ship with python2 by default. Make sure to install and point appropriately
# A python3 dependency is package sdnotify
# install using: pip install sdnotify  (in python3)
python3_path="/opt/rh/rh-python36/root/usr/bin/python"

# The place where all the files will be kept. Location will be $install_location/$name
install_location="/opt/services"

# name of the service. only alphabets,numbers and underscores allowed. Should start with an alaphabet
name="trial_002"

# Description of the service. Line breaks not allowed. Single line description
description="Keycloak Trial 2 Service"

# This script is run everytime before the service starts (also on restarts)
pre_start_script="/home/coderdude/gen_services/keycloak/prestart.sh"

START_SCRIPTS=()
# $START_SCRIPTS is the array containing all the scripts or commands to run your programs which will be executed
# make sure to give absolute paths in START_SCRIPTS
# START_SCRIPTS need to be enclosed with '...' or ""...""
# If you have quotes inside, escape them using \
# Example : START_SCRIPTS[0]="echo \" Hello World \" "

START_SCRIPTS[0]="/home/coderdude/keycloak/keycloak-6.0.1/bin/standalone.sh >> /home/coderdude/keycloak/keycloak_logs.log 2>&1 &"
START_SCRIPTS[1]="echo \"Another sample command\" "


# This script checks whether application started properly. 
# script should exit with code 0 if everything is fine or 1 if error occured
startup_check_script="/home/coderdude/keycloak/startup_check.sh"

# The startup_check will be performed after these many seconds of starting the program
# Keep this big enough to allow your commands to strt properly
startup_check_delay=30

# This script checks if the application is working properly. 
# script should exit with code 0 is everything is fine or 1 if error occured
health_check_script="/home/coderdude/keycloak/watchdog_check.sh"

# health check will be performed after every these many seconds periodically
# Note this should be less than half of watchdog timeout, else watchdog will keep on restarting service
health_check_period=15

# This script will be run everytime after the service gets initialized
post_start_script="/home/coderdude/gen_services/keycloak/poststart.sh"

# This script is run everytime before the service stops.
pre_stop_script="/home/coderdude/gen_services/keycloak/prestop.sh"

# This script is run everytime after the service stops
post_stop_script="/home/coderdude/gen_services/keycloak/poststop.sh"

# If watchdog doesn't receive OK signal within this timeframe (in seconds), the service will be restarted
watchdog_timeout=30

# If the service doesn't initialize within this time of starting (in seconds), 
# it will be considered failed and restarted
start_timeout=0

# The service script will try to gracefully stop the code these many times before sending a SIGKILL
graceful_kill_attempts=3

# on stop, SIGTERM is sent to the service. 
# If service fails to stop within this timeframe(in seconds), it will be forced with SIGKILL
kill_timeout=60
