#!/bin/bash

init_config() {
    work_home=$(cd `dirname $0`;cd ..;pwd)
    notify_tool="python ${work_home}/utils/notify.py -m"
    logger="python ${work_home}/utils/logger.py -m"
    get_config="${work_home}/config/config.sh"

    node_type=$(${get_config} "node_type")
    [ "${node_type}" != "bp" ] && exit 1
    api=$(${get_config} "local_api")
    eos_config=$(${get_config} "eos_home")/config/config.ini

    check_script="${work_home}/utils/blacklist_check.sh"
}

log_and_notify() {
    info="[[ $(hostname)-blacklist ]]\n"
    ${logger} "${info}$@"
    ${notify_tool} "${info}$@"
}

check_blacklist() {
    check_result=`${check_script} ${api} ${eos_config}`
    if [ $? -gt 0 ];then
        is_success=${check_result}
    else
        is_success=`echo "${check_result}" | grep -v success`
    fi
    if [ "${is_success}" != "" ]; then
        log_and_notify "${check_result}"
    fi
}

main() {
    init_config
    check_blacklist
}

main