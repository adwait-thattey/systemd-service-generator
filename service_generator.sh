#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "This script must run as root"
  exit
fi


set -a
source ./config.sh

cur_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

overwrite_flag=0

if [ ! -d "/opt/services" ]; then
    mkdir /opt/services

fi

if [ -d "/opt/services/$name" ] || [ -f "/etc/systemd/system/$name.service" ]; then
    echo "A service of this name already exists. Do you want to overwrite? (Press 1 or 2)"
    select yn in "Yes" "No"; do
        case $yn in
            Yes ) overwrite_flag=1; break;;
            No ) exit;;
        esac
    done
else
    mkdir /opt/services/$name
fi

install_directory=/opt/services/$name

$python3_path $cur_dir/service_generator.py

# copy all files to install directory
cp -f $cur_dir/config.sh $install_directory
cp -f $cur_dir/main_script.sh $install_directory
cp -f $cur_dir/ready_notify.py $install_directory
cp -f $cur_dir/watchdog_notify.py $install_directory
cp -f $cur_dir/$name.service $install_directory

chmod u+rwx $install_directory/*


cp -f $install_directory/$name.service /etc/systemd/system

systemctl daemon-reload
systemctl enable $name.service

echo "Service installed at $install_directory"
echo "Run systemctl start $name.service to run"
echo "Run tail -f /var/log/messages to monitor logs"
