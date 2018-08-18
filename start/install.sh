#!/bin/bash

service_list=(
    eosmonitor.service
    eoslogmonitor.service
)

py_package_list=(
    requests
    apscheduler
    psutil
    sh
)

linux_command_list=(
    jq
    bc
)

cur_home=$(cd `dirname $0`;pwd)
work_home=$(cd ${cur_home};cd ../;pwd)
su_do=""
[ $(whoami) != "root" ] && su_do="sudo"

check_py_requirement() {
    require_package=$1
    is_install=$(${su_do} pip list 2>/dev/null | grep -i ${require_package})
    if [ "${is_install}" == "" ];then
        ${su_do} pip install ${require_package}
    fi
}

check_linux_command() {
    linux_command=$1
    msg=$(${linux_command} --help 2>&1)
    is_install=$(echo ${msg} | egrep 'command not found|currently not installed')
    if [ "${is_install}" != "" ];then
        ${su_do} apt-get install ${linux_command}
    fi
}

check_requirements() {
    for py_package in ${py_package_list[*]}
    do
        check_py_requirement ${py_package}
    done
    for linux_command in ${linux_command_list[*]}
    do
        check_linux_command ${linux_command}
    done
}

install_systemctl() {
    service_name=$1
    sample_config="${work_home}/systemctl/${service_name}"
    systemctl_config_home="/usr/lib/systemd/system"
    [ ! -d ${systemctl_config_home} ] && ${su_do} mkdir ${systemctl_config_home}
    service_config="${systemctl_config_home}/${service_name}"
    ${su_do} cp ${sample_config} ${service_config}
    ${su_do} sed -i 's#/path/eos-toolkit#'${work_home}'#' ${service_config}
    ${su_do} sed -i 's#User=eos#User='$(whoami)'#' ${service_config}
    ${su_do} cat ${service_config}
    ${su_do} systemctl daemon-reload
    ${su_do} systemctl status ${service_name}
}

install_all_systemctl() {
    for service in ${service_list[*]}
    do
        install_systemctl ${service}
    done
}

main() {
    check_requirements
    install_all_systemctl
}

main