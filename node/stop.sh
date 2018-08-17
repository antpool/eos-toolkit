#!/bin/bash

pid_file="/opt/eosbp/logs/nodeos.pid"

if [ -f "${pid_file}" ]; then
    pid=$(cat "${pid_file}")
    echo ${pid}
    kill ${pid}
    rm -r "${pid_file}"

    echo -ne "Stopping Nodeos"

    while true; do
        [ ! -d "/proc/${pid}/fd" ] && break
        echo -ne "."
        sleep 1
    done
    echo -ne "\rNodeos stopped. \n"

fi