#!/bin/bash

current_home=$(cd `dirname $0`;pwd)
work_home=$(cd ${current_home};cd ../;pwd)
get_config="${work_home}/config/config.sh"
eos_home=$(${get_config} "eos_home")
nodeos="${eos_home}/command/nodeos"
data_dir="${eos_home}/data"
config_dir="${eos_home}/config"
log_dir="${eos_home}/logs"
stderr_log="${log_dir}/stderr.txt"
stdout_log="${log_dir}/stdout.txt"
pid_file="${log_dir}/nodeos.pid"

${current_home}/stop.sh

${nodeos} --data-dir ${data_dir} --config-dir ${config_dir} "$@" >> ${stdout_log} 2>> ${stderr_log} & echo $! > ${pid_file}
[ $? -eq 0 ] && echo "Nodeos started successfully" || echo "Nodes start failed"