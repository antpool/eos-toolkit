#!/bin/bash

current_home=$(cd `dirname $0`;pwd)
work_home=$(cd ${current_home};cd ../;pwd)
get_config="${work_home}/config/config.sh"
eos_home=$(${get_config} "eos_home")
log_home="${eos_home}/logs"
logger="python ${work_home}/utils/logger.py"

stdout_log="stdout.txt"
stderr_log="stderr.txt"
suffix=$(date "+%Y%m%d_%H%M")

log() {
    ${logger} -m "$@"
}

clear_history_log() {
    find_history_command="find ${log_home} -ctime +30 -type f -name '$1_*'"
    history_log=$(${find_history_command})
    if [ "${history_log}" == "" ];then
        return
    fi
    log "clear history log: $(${find_history_command})"
    ${find_history_command} | xargs rm -f
}

backup_log() {
    if [ "" == "$1" ];then
        return
    fi
    clear_history_log $1
    log_file="${log_home}/$1"
    if [ -f "${log_file}" ] && [ -s "${log_file}" ];then
        cp -f ${log_file} "${log_file}_${suffix}"
    fi
}

backup_log ${stderr_log}
backup_log ${stdout_log}