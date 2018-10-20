#!/bin/bash

backup_home=$(cd `dirname $0`;pwd)
work_home=$(cd ${backup_home};cd ../;pwd)
get_config="${work_home}/config/config.sh"
default_log=$(${get_config} "monitor_log_file")
log_file="${work_home}/logs/${default_log}"

. ${backup_home}/backup.sh 2>&1 >> ${log_file}