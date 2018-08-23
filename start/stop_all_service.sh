#!/bin/bash

service_list=(
    eosmonitor.service
    eoslogmonitor.service
)

su_do=""
[ $(whoami) != "root" ] && su_do="sudo"

for service in ${service_list[*]}
do
    ${su_do} systemctl stop ${service}
    ${su_do} systemctl status ${service} -n10
done