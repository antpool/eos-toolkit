#!/bin/bash

current_home=$(cd `dirname $0`;pwd)
work_home=$(cd ${current_home};cd ../;pwd)
get_config="${work_home}/config/config.sh"
eos_home=$(${get_config} "eos_home")
pid_file="${eos_home}/logs/nodeos.pid"

if [ -f "${pid_file}" ]; then
    pid=$(cat "${pid_file}")
    kill ${pid}
    rm -r "${pid_file}"

    echo -ne "Stopping Nodeos(${pid})"

    while true; do
        [ ! -d "/proc/${pid}/fd" ] && break
        echo -ne "."
        sleep 1
    done
    echo -ne "\rNodeos stopped. \n"

fi