#!/bin/bash

seconds=86400

init_config() {
    claim_home=$(cd `dirname $0`;pwd)
    work_home=$(cd ${claim_home};cd ../;pwd)
    config_file="${work_home}/config/config.conf"
    api=$(get_config "local_api")
    bp_account=$(get_config "bp_account")
    wallet_name=$(get_config "wallet_name")
    wallet_pwd=$(get_config "wallet_password")
    wallet_api=$(get_config "wallet_api")
    eos_client=$(get_config "eos_client")
    cleos="${eos_client} -u ${api} --wallet-url=${wallet_api}"

    last_claim_time_cache="${claim_home}/claim_cache_info"
    can_claim=false
    notify_tool="python ${work_home}/utils/notify.py"
    logger="python ${work_home}/utils/logger.py"
    log "${cleos}"
    if [ ! -f "${eos_client}" ] || [ "${wallet_pwd}" == "" ]; then
        log "please check client or wallet_pwd config"
        exit 0
    fi
}

get_config() {
    echo `grep "$1" ${config_file} | awk '{print $3}'`
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
    [ $? != 0 ] && notify "claim fail\nunlock wallet fail" && exit 1 || return 0
}

lock_wallet() {
    ${cleos} wallet lock
}

claim_rewards() {
    unlock_wallet
    claim_result=$(${cleos} push action eosio claimrewards '{"owner":"'${bp_account}'"}' -p ${bp_account}@claimer 2>&1)
    if [ $? -gt 0 ];then
        notify "claim fail\n${claim_result}"
        update_cache
        exit 1
    fi
    log "${claim_result}"
    bpay=$(echo "${claim_result}" | grep "${bp_account} <= eosio.token::transfer" | grep "eosio.bpay" | grep -Eo "[0-9]+\.[0-9]+ EOS")
    vpay=$(echo "${claim_result}" | grep "${bp_account} <= eosio.token::transfer" | grep "eosio.vpay" | grep -Eo "[0-9]+\.[0-9]+ EOS")
    [ "" == "${vpay}" ] && vpay="0 EOS"
    [ "" == "${bpay}" ] && bpay="0 EOS"
    claim_success
}

get_balance() {
    balance="`${cleos} get currency balance eosio.token ${bp_account}`"
}

claim_success() {
    lock_wallet
    get_balance
    notify "claim success\nbpay:${bpay}\nvpay:${vpay}\nbalance:${balance}\nhttps://eosflare.io/account/${account}"
    can_claim=false
    update_cache
}

update_cache() {
    bp_info=`curl -sX POST ${api}/v1/chain/get_producers -d '{"limit":"1","lower_bound":"'${bp_account}'","json":"true"}'|jq '.rows[0]'`
    log ${bp_info}
    bp_name=`echo "${bp_info}"|jq '.owner'|sed 's/"//g'`
    [ "${bp_account}" != "${bp_name}" ] && log "${bp_account} get nothing." && return
    last_claim_time=`echo "${bp_info}"|jq '.last_claim_time'|sed 's/"//g'`
    last_claim_time_sec=`echo "${last_claim_time}/1000000"|bc`
    info=`grep "${bp_account}_last_claim_time=" ${last_claim_time_cache}`
    if [ "" == "${info}" ]; then
        echo ${bp_account}_last_claim_time=${last_claim_time_sec} >> ${last_claim_time_cache}
    else
        sed -i -e 's/'${bp_account}'_last_claim_time=.*/'${bp_account}'_last_claim_time='${last_claim_time_sec}'/g' ${last_claim_time_cache}
    fi
}

check_api() {
    code=`curl -I -m 10 -o /dev/null -s -w %{http_code} "${api}/v1/chain/get_info"`
    [ "${code}" != 200 ] && notify "claim fail\nplease check api:${api}" && exit 1
}

check_claim_time() {
    [ ! -f "${last_claim_time_cache}" ] && echo "${bp_account}_last_claim_time="> ${last_claim_time_cache}
    last_claim_time_sec=`cat ${last_claim_time_cache}|grep ${bp_account}_last_claim_time|awk -F'=' '{print $2}'`
    [ "${last_claim_time_sec}" == "" ] && update_cache
    diff_sec=`echo "$(date "+%s")-${last_claim_time_sec}"|bc`
    [ ${diff_sec} -gt ${seconds} ] && can_claim=true
    if [ ${can_claim} == false ]; then
        log "claim after $(echo ${seconds}-${diff_sec}|bc)s"
        exit 1
    fi
}

process_claim() {
    init_config
    check_api
    check_claim_time
    claim_rewards
}

main() {
    process_claim
}

main