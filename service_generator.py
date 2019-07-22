import os
try:
    name = os.environ['name']
    description = os.environ['description']
    python3_path = os.environ['python3_path']
    pre_start_script = os.environ['pre_start_script']
    post_start_script= os.environ['post_start_script']
    pre_stop_script = os.environ['pre_stop_script']
    post_stop_script = os.environ['post_stop_script']
    watchdog_timeout = os.environ['watchdog_timeout']
    start_timeout = os.environ['start_timeout']
    kill_timeout = os.environ['kill_timeout']
    cur_dir = os.environ['cur_dir']
    install_directory = os.environ['install_directory']
    graceful_kill_attempts = os.environ['graceful_kill_attempts']

except KeyError:
    raise ImportError("Unable to import variables from environment. Please ensure that config.sh is set correctly")

if (not name) or (not description):
    raise ValueError("Name and Description can not be blank")

# SERVICE FILE GENERATE BEGINS

# UNIT SECTION
unit_template = f"""\
[Unit]
Description={description}
After=network.target

"""

service_template = f"""\
[Service]
Type=notify
ExecStartPre=/bin/bash {pre_start_script}
ExecStart=/bin/bash {os.path.join(install_directory, 'main_script.sh')}
ExecStartPost=/bin/bash {post_start_script}
WatchdogSec={watchdog_timeout}
KillMode=control-group
KillSignal=SIGTERM
TimeoutStartSec={start_timeout}
TimeoutStopSec={kill_timeout}
ExecStop=/bin/bash {pre_stop_script}
ExecStopPost=/bin/bash {post_stop_script}
Restart=always
RestartSec=10
NotifyAccess=all

"""

install_temmplate = f"""\
[Install]
WantedBy=multi-user.target

"""

service_file_path = os.path.join(cur_dir, f'{name}.service')
service_file = open(service_file_path, mode='w')
service_file.write(unit_template)
service_file.write(service_template)
service_file.write(install_temmplate)
service_file.close()


# SERVICE SCRIPT GENERATE BEGINS
script_code = f"""\
#!/bin/bash

# THIS IS A SCRIPT THAT CAN START, WATCH, AND GRACEFULLY TERMINATE OTHER PROGRAMS.
# MEANT TO BE USED ALONG WITH A SYSTEMD SERVICE. 
# MAKE TYPE OF SYSTEMD SERVICE AS 'notify' AND POINT ExecStart TO THIS SCRIPT
#
# ==========================================================
# DO NOT MODIFY ANYTHING UNTIL YOU ENCOUNTER THIS AGAIN
#===========================================================

source {os.path.join(install_directory, "config.sh")}

PROCESSES=()

send_ready_signal()
{{
    echo "Sending ready ok signal"
    $python3_path {os.path.join(install_directory, 'ready_notify.py')} &
}}

send_watchdog_ok_signal()
{{
    echo "sending watchdog ok signal"
    $python3_path {os.path.join(install_directory, 'watchdog_notify.py')} &
}}

kill_processes_and_check()
{{   # DO NOT PRINT/ECHO ANYTHING IN THIS FUNCTION except the last line
    is_running=0
    for pid in "${{PROCESSES[@]}}" 
    do
        if [[ $(ps -p $pid h) ]]; then
            # echo "$pid running"
            is_running=1
            kill -15 $pid
        fi    
    done

    echo $is_running
}}

stop_server()
{{
    logger -i "Sending SIGTERM to all children"

    # will try 3 times
    for count in {{1..{graceful_kill_attempts}}}
    do
        
        
        chk_running=$(kill_processes_and_check)
        if [ $chk_running -eq 0 ]; then
            echo "All tasks done"
            exit
        else
            echo "Tasks still running"
            sleep 3
        fi                
    done

    chk_running=$(kill_processes_and_check)
    if [ $chk_running -ne 0 ]; then
        echo "Tasks refused to stop"
        echo "Killing them"

        for pid in "${{PROCESSES[@]}}" 
        do
            if [[ $(ps -p $pid h) ]]; then
                kill -9 $pid
            fi    
        done
    fi    

    exit
}}

trap 'stop_server' 15
trap 'stop_server' 2
trap "kill -15 $$" 6

#===============================================
# START MODIFYING FROM HERE
#===============================================
logger -i "Starting Script"

# Add commands to start programs here. End each command with '&'.
# And after the command use PROCESSES+=($!)
# Example:
#
# /sample/command &
# PROCESSES+=($!)

for cmd in "${{START_SCRIPTS[@]}}"
do
    bash -c "$cmd"
    PROCESSES+=($!)
done    

echo "commands started. Waiting for $startup_check_delay before performing startup check"
sleep $startup_check_delay

echo "performing startup check"
# You can add conditions here to ensure that all programs have started correctly.
# Send ready signal only if everything has correctly started
$startup_check_script
script_status=$?

if [ $script_status -eq 0 ]; then
    send_ready_signal
    logger -i "startup check complete"
else
    logger -i "startup check failed!"
    exit 1
fi        


while :
do
    sleep $health_check_period
    logger -i "Watchdog check started"
    logger -i "watchdog: Script is running"
 
    # Add conditions here to ensure that all programs are alive correctly
    # If everything is okay, send watchdog_okay signal
    #send_watchdog_ok_signal
    
    $health_check_script
    script_status=$?    
    if [ $script_status -eq 0 ]; then
        send_watchdog_ok_signal
        logger -i "watchdog: watchdog check complete"
    else
        logger -i "watchdog: watchdog check failed"
    fi 

done 

"""

service_script_path = os.path.join(cur_dir, f'main_script.sh')
service_script_file = open(service_script_path, mode="w")
service_script_file.write(script_code)
service_script_file.close()
