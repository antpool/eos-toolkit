#!/bin/bash

init() {
    work_home=$(cd `dirname $0`;cd ..;pwd)
    get_config="${work_home}/config/config.sh"

    api=$(${get_config} "local_api")
    config=$(${get_config} "eos_home")/config/config.ini
    [ "$1" != "" ] && api=$1
    [ "$2" != "" ] && config=$2
    [ ! -f ${config} ] && echo "please check config path(${config})" && exit 1
}

get_chain_actor_list() {
    url="${api}/v1/chain/get_table_rows"
    chain_actor_list=`curl -sX POST "${url}" -d '{"scope":"theblacklist", "code":"theblacklist", "table":"theblacklist", "json": true, "limit": 100}'`
    [ "${chain_actor_list}" == "" ] && echo "please check api(${api})." && exit 1
    add_action="add_action"
    remove_action="remove_action"
    add_account="${add_action}"
    remove_account="${remove_action}"
    action=""
    for account in $(echo "${chain_actor_list}" | jq -cr '.rows[]' | while read row
        do
            _jq() {
                echo "${row}" | jq -r ''$1''
            }

            action=$(_jq '.action')
            accounts=$(_jq '.accounts[]')
            if [ "remove" == "${action}" ];then
                remove_account="${remove_account} ${accounts}"
            elif [ "add" == "${action}" ];then
                add_account="${add_account} ${accounts}"
            fi
            echo ${remove_account}
            echo ${add_account}
        done | tail -2)
    do
        if [ "${remove_action}" == "${account}" ]; then
            action=${account}
            remove_account=""
            continue
        elif [ "${add_action}" == "${account}" ]; then
            action=${account}
            add_account=""
            chain_actor_list=""
            continue
        fi
        if [ "${remove_action}" == "${action}" ]; then
            remove_account="${remove_account} ${account}"
        elif [ "${add_action}" == "${action}" ]; then
            if [ "`echo "${remove_account}" | grep ${account}`" == "" ];then
                chain_actor_list="${chain_actor_list} $(echo ${account})"
            fi
        fi
    done
    chain_actor_list=`echo "${chain_actor_list}" | awk  '{for (i=1;i<=NF;i++) printf "%s\n",$i}'| sort -u`
}

get_local_actor_list() {
    local_actor_list=`cat ${config} | grep actor-black | grep -v "#" |egrep -o '\w+$'| sort`
}

check_diff() {
    diff <(echo "${chain_actor_list}") <(echo "${local_actor_list}")| sed 's/</chain -/g' | sed 's/>/local -/g' | egrep 'chain -|local -'
}

# check local and theblacklist actor-blacklist hash
check_hash() {
    local_hash=`cat ${config} | grep actor-black | grep -v "#" | sort | tr -d " " | sha256sum`
    # get hash from table theblacklist
    chain_hash=`echo "${chain_actor_list}" | sed 's/^/actor-blacklist = /g' | tr -d " " | sha256sum`
    if [ "${local_hash}" == "${chain_hash}" ];then
        echo "success: ${chain_hash}"
    else
        echo "local: ${local_hash}"
        echo "chain: ${chain_hash}"
        exit 1
    fi
}

main() {
    init $@
    get_chain_actor_list
    get_local_actor_list
    check_diff
    check_hash
}

main $@