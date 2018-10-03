#!/bin/bash

seconds=86400

init_config() {
    claim_home=$(cd `dirname $0`;pwd)
    work_home=$(cd ${claim_home};cd ../;pwd)
    get_config="${work_home}/config/config.sh"
    api=$(${get_config} "local_api")
    bp_account=$(${get_config} "bp_account")
    wallet_name=$(${get_config} "wallet_name")
    wallet_pwd=$(${get_config} "wallet_password")
    wallet_api=$(${get_config} "wallet_api")
    claim_permission=$(${get_config} "claim_permission")
    eos_client=$(${get_config} "eos_client")
    cleos="${eos_client} -u ${api} --wallet-url=${wallet_api}"

    last_claim_time_cache="${claim_home}/claim_cache_info"
    last_claim_time_cache_key="${bp_account}_last_claim_time"
    last_claim_check_cache_key="${bp_account}_claim_check_count"
    can_claim=false
    notify_tool="python ${work_home}/utils/notify.py"
    reward_tool="python ${work_home}/monitor/bp_status_monitor.py"
    logger="python ${work_home}/utils/logger.py"
    if [ ! -f "${eos_client}" ] || [ "${wallet_pwd}" == "" ]; then
        log "please check client or wallet_pwd config"
        exit 0
    fi
    init_cache
}

log() {
    ${logger} -m "$@"
}

notify() {
    log "$@"
    ${notify_tool} -m "$@"
}

unlock_wallet() {
    lock_wallet
    ${cleos} wallet unlock -n ${wallet_name} --password=${wallet_pwd} > /dev/null
    if [ $? != 0 ];then
        notify "claim fail\nunlock wallet fail"
        exit 1
    fi
}

lock_wallet() {
    ${cleos} wallet lock
}

get_balance() {
    balance="`${cleos} get currency balance eosio.token ${bp_account}`"
}

update_cache_file() {
    local key=$1
    local value=$2
    info=`grep "${key}" ${last_claim_time_cache}`
    if [ "" == "${info}" ]; then
        echo ${key}=${value} >> ${last_claim_time_cache}
    else
        sed -i -e 's/'${key}'=.*/'${key}'='${value}'/g' ${last_claim_time_cache}
    fi
}

update_claim_time_cache() {
    bp_info=`curl -sX POST ${api}/v1/chain/get_producers -d '{"limit":"1","lower_bound":"'${bp_account}'","json":"true"}'|jq '.rows[0]'`
    log "update claim cache: ${bp_info}"
    bp_name=`echo "${bp_info}"|jq '.owner'|sed 's/"//g'`
    [ "${bp_account}" != "${bp_name}" ] && log "${bp_account} get nothing." && return
    last_claim_time=`echo "${bp_info}"|jq '.last_claim_time'|sed 's/"//g'`
    last_claim_time_sec=`echo "${last_claim_time}/1000000"|bc`
    update_cache_file ${last_claim_time_cache_key} ${last_claim_time_sec}
}

update_claim_check_cache() {
    claim_check_count=$1
    if [ "$1" == "" ];then
        claim_check_count=$(get_cache_value ${last_claim_check_cache_key})
        let claim_check_count=claim_check_count+1
    fi
    update_cache_file ${last_claim_check_cache_key} ${claim_check_count}
}

get_cache_value() {
    local key=$1
    value=`cat ${last_claim_time_cache}|grep ${key}|awk -F'=' '{print $2}'`
    echo ${value}
}

init_cache() {
    if [ ! -f "${last_claim_time_cache}" ];then
        echo "${last_claim_time_cache_key}="> ${last_claim_time_cache}
        echo "${last_claim_check_cache_key}=0">> ${last_claim_time_cache}
    else
        if [ "$(get_cache_value ${last_claim_time_cache_key})" == "" ];then
            update_claim_time_cache
        fi
        if [ "$(get_cache_value ${last_claim_check_cache_key})" == "" ];then
            update_claim_check_cache 0
        fi
    fi
}

check_api() {
    code=`curl -I -m 10 -o /dev/null -s -w %{http_code} "${api}/v1/chain/get_info"`
    if [ "${code}" != 200 ];then
        notify "claim fail\nplease check api:${api}"
        exit 1
    fi
}

check_claim_time() {
    last_claim_time_sec=$(get_cache_value ${last_claim_time_cache_key})
    if [ "${last_claim_time_sec}" == "" ];then
        update_claim_time_cache
    fi
    claim_check_count=$(get_cache_value ${last_claim_check_cache_key})
    if [ ${claim_check_count} -lt 5 ];then
        update_claim_time_cache
    fi
    last_claim_time_sec=$(get_cache_value ${last_claim_time_cache_key})
    diff_sec=$(echo "$(date "+%s")-${last_claim_time_sec}"|bc)
    [ ${diff_sec} -gt ${seconds} ] && can_claim=true
    if [ ${can_claim} == false ]; then
        update_claim_check_cache
        log "claim after $(echo ${seconds}-${diff_sec}|bc)s"
        exit 1
    fi
}

check_rewards() {
    reward_pay=`${reward_tool} -r "rewards"`
    if [ "${reward_pay}" == "" ]; then
        log "query reward error"
        exit 1
    elif [ $(echo "100.0>${reward_pay}"|bc) -eq 1 ]; then
        log "${reward_pay} reward not enough"
        exit 1
    fi
}

claim_success() {
    lock_wallet
    get_balance
    notify "claim success\nbpay:${bpay}\nvpay:${vpay}\nbalance:${balance}\nhttps://eosflare.io/account/${bp_account}"
    can_claim=false
    update_claim_time_cache
    update_claim_check_cache 0
}

claim_rewards() {
    unlock_wallet
    claim_result=$(${cleos} push action eosio claimrewards '{"owner":"'${bp_account}'"}' -p ${bp_account}@${claim_permission} 2>&1)
    if [ $? -gt 0 ];then
        # remove color code
        claim_result=$(echo "${claim_result}" | sed -r "s/\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]//g")
        notify "claim fail\n${claim_result}"
        update_claim_time_cache
        exit 1
    fi
    log "${claim_result}"
    bpay=$(echo "${claim_result}" | grep "${bp_account} <= eosio.token::transfer" | grep "eosio.bpay" | grep -Eo "[0-9]+\.[0-9]+ EOS")
    vpay=$(echo "${claim_result}" | grep "${bp_account} <= eosio.token::transfer" | grep "eosio.vpay" | grep -Eo "[0-9]+\.[0-9]+ EOS")
    [ "" == "${vpay}" ] && vpay="0 EOS"
    [ "" == "${bpay}" ] && bpay="0 EOS"
    claim_success
}

process_claim() {
    init_config
    check_api
    check_claim_time
    check_rewards
    claim_rewards
}

main() {
    process_claim
}

main