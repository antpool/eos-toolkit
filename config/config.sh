#!/usr/bin/env bash

init_config() {
     config_home=$(cd `dirname $0`;pwd)
     config_file="${config_home}/config.conf"
}

get_config() {
    echo `egrep -m 1 "^$1" ${config_file} |sed -n 's/^[^=]*=\s* *\(.*\)\s* *$/\1/p'`
}

main() {
    init_config
    get_config $1
}

main $1