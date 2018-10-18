#!/bin/bash

current_home=$(cd `dirname $0`;pwd)
work_home=$(cd ${current_home};cd ../;pwd)
get_config="${work_home}/config/config.sh"
eos_home=$(${get_config} "eos_home")
nodeos="${eos_home}/command/nodeos"
data_dir="${eos_home}/data"
config_dir="${eos_home}/config"
log_dir="${eos_home}/logs"

${current_home}/stop.sh
${current_home}/backup_log.sh

${nodeos} --data-dir ${data_dir} --config-dir ${config_dir} "$@" > ${log_dir}/stdout.txt 2> ${log_dir}/stderr.txt &  echo $! > ${log_dir}/nodeos.pid
[ $? -eq 0 ] && echo "Nodeos started successfully" || echo "Nodes start failed"