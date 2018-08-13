#!/bin/bash

eos_home="/opt/eosbp"
nodeos="${eos_home}/command/nodeos"
data_dir="${eos_home}/data"
config_dir="${eos_home}/config"
log_dir="${eos_home}/logs"

current_home=$(cd `dirname $0`;pwd)
${current_home}/stop.sh

${nodeos} --data-dir ${data_dir} --config-dir ${config_dir} "$@" > ${log_dir}/stdout.txt 2> ${log_dir}/stderr.txt &  echo $! > ${log_dir}/nodeos.pid