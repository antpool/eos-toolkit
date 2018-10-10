#!/bin/bash

to_seconds() {
   local config=$1
   if [[ ${config} == *s ]];then
       echo ${config}|grep -Eo "[0-9]+"
   elif [[ ${config} == *m ]];then
       echo $(echo ${config}|grep -Eo "[0-9]+")*60|bc
   elif [[ ${config} == *h ]];then
       echo $(echo ${config}|grep -Eo "[0-9]+")*3600|bc
   fi
}

init_config() {
    work_home=$(cd `dirname $0`;cd ..;pwd)
    monitor_log="${work_home}/logs/monitor.log"
    notify_tool="python ${work_home}/utils/notify.py -m"
    logger="python ${work_home}/utils/logger.py"
    restart_command="${work_home}/node/start.sh"
    get_config="${work_home}/config/config.sh"

    process_monitor_config=$(${get_config} "process_monitor"|grep -Eo "[0-9]+.*")
    auto_restart_config=$(${get_config} "auto_restart"|grep -Eo "[0-9]+.*")
    process_monitor_seconds=$(to_seconds ${process_monitor_config})
    auto_restart_seconds=$(to_seconds ${auto_restart_config})

    cpu_percent_limit=$(${get_config} "cpu_percent_limit")
    memory_percent_limit=$(${get_config} "memory_percent_limit")
    hostname=$(hostname)
}

log() {
    ${logger} -m "$@"
}

notify() {
    log "$@"
    ${notify_tool} "$@"
}

restart() {
    ${restart_command}
    if [ $? -eq 0 ]; then
        notify "${hostname} restart success"
    else
        notify "${hostname} restart failed"
    fi
}

check_cpu_percent() {
    cpu_percent=`grep eos_cpu_percent ${monitor_log}|tail -${lines_count}|grep -Eo "[0-9]+\.[0-9]+"| xargs | sed 's/ /+/g'`
    if [ "${cpu_percent}" == "" ];then
        log "not found cpu monitor data"
        return
    fi
    average=`echo "(${cpu_percent})/${lines_count}"|bc`
    log "${hostname} last ${auto_restart_config} cpu_percent is ${average}"
    if [ `echo "${average}>${cpu_percent_limit}"|bc` -eq 1 ]; then
        notify "${hostname} last ${auto_restart_config} cpu_percent is ${average}, start restart(${restart_command})..."
        restart
        exit
    fi
}

check_memory_percent() {
    memory_percent=`grep eos_memory_percent ${monitor_log}|tail -${lines_count}|grep -Eo "[0-9]+\.[0-9]+"| xargs | sed 's/ /+/g'`
    if [ "${memory_percent}" == "" ];then
        log "not found memory monitor data"
        return
    fi
    average=`echo "(${memory_percent})/${lines_count}"|bc`
    log "${hostname} last ${auto_restart_config} memory_percent is ${average}"
    if [ `echo "${average}>${memory_percent_limit}"|bc` -eq 1 ]; then
        notify "${hostname} last ${auto_restart_config} memory_percent is ${average}, start restart(${restart_command})..."
        restart
        exit
    fi
}

check() {
    lines_count=`echo "${auto_restart_seconds}/${process_monitor_seconds}"|bc`
    if [ ${lines_count} -eq 0 ];then
        log "auto restart interval too small"
        exit 1
    fi
    check_cpu_percent
    check_memory_percent
}

main() {
    init_config
    check
}

main