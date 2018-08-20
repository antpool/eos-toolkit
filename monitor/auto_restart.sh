#!/bin/bash

init_config() {
    work_home=$(cd `dirname $0`;cd ..;pwd)
    monitor_log="${work_home}/logs/monitor.log"
    notify_tool="python ${work_home}/utils/notify.py -m"
    logger="python ${work_home}/utils/logger.py"
    restart_command="${work_home}/node/start.sh"
    config_file="${work_home}/config/config.conf"

    # minute
    restart_interval=$(get_config "auto_restart"|grep -Eo "[0-9]+")
    cpu_percent_limit=$(get_config "cpu_percent_limit")
    hostname=$(hostname)
}

get_config() {
    echo `egrep -m 1 "^$1" ${config_file} |sed -n 's/^[^=]*=\s* *\(.*\)\s* *$/\1/p'`
}

log() {
    ${logger} -m "$@"
}

notify() {
    log "$@"
    ${notify_tool} "$@"
}

restart() {
    notify "${hostname} last ${restart_interval}m cpu_percent is ${average}, start restart(${restart_command})..."
    ${restart_command}
    if [ $? -eq 0 ]; then
        notify "${hostname} restart success"
    else
        notify "${hostname} restart failed"
    fi
}

check_cpu_percent() {
    count=`echo "${restart_interval}*2"|bc`
    cpu_percent=`grep eos_cpu_percent ${monitor_log}|tail -${count}|grep -Eo "[0-9]+\.[0-9]+"| xargs | sed 's/ /+/g'`
    average=`echo "(${cpu_percent})/${count}"|bc`
    if [ `echo "${average}>${cpu_percent_limit}"|bc` -eq 1 ]; then
        restart
    fi
}

main() {
    init_config
    check_cpu_percent
}

main