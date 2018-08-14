#!/bin/bash

sudo pip install apscheduler
sudo pip install requests
sudo pip install psutil
sudo pip install sh

systemctl_config_home="/usr/lib/systemd/system"
[ ! -d ${systemctl_config_home} ] && sudo mkdir ${systemctl_config_home}
eos_monitor_config="${systemctl_config_home}/eosmonitor.service"

cur_home=$(cd `dirname $0`;pwd)
work_home=$(cd ${cur_home};cd ../;pwd)
sample_config="${work_home}/systemctl/eosmonitor.service"
sudo cp ${sample_config} ${eos_monitor_config}
sudo sed -i 's#/path/eos-toolkit#'${work_home}'#' ${sample_config}
cat ${sample_config}

sudo systemctl daemon-reload
sudo systemctl start eosmonitor.service
sudo systemctl status eosmonitor.service