#!/usr/bin/env python
# -*- coding: utf-8 -*

import argparse
import time

import init_work_home

init_work_home.init()

from config.config import Config
from utils.logger import logger
from utils.metric import Metric
from utils.notify import Notify
from utils import http

continuous_rate = 0.0487
useconds_per_day = 24 * 3600 * 1000000
useconds_per_year = 52 * 7 * 24 * 360 * 1000000

ct = int(time.time() * 1000000)
bp_name = Config.get_bp_account()
url = Config.get_local_api()
just_get_rewards = None


def notify(*args):
    logger.info(args)
    Notify.notify(*args)


def get_global_info():
    global total_vote_weight, pervote_bucket, total_unpaid_blocks, perblock_bucket, last_pervote_bucket_fill
    global_url = url + "/v1/chain/get_table_rows"
    response = http.post(global_url, global_url,
                         data='{"scope":"eosio","table":"global","json":true,"code":"eosio","limit":1}')
    global_data = response.json()['rows'][0]
    total_vote_weight = float(global_data['total_producer_vote_weight'])
    pervote_bucket = int(global_data['pervote_bucket'])
    perblock_bucket = int(global_data['perblock_bucket'])
    total_unpaid_blocks = int(global_data['total_unpaid_blocks'])
    last_pervote_bucket_fill = int(global_data['last_pervote_bucket_fill'])


def get_account_info():
    global bp_vote_weight, unpaid_blocks, last_claim_time, rank
    find_bp = False
    producers_api = url + "/v1/chain/get_producers"
    response = http.post(producers_api, producers_api, data='{"json":true,"limit":1000}')
    for data in response.json()['rows']:
        if data['owner'] == bp_name:
            bp_vote_weight = float(data['total_votes'])
            unpaid_blocks = int(data['unpaid_blocks'])
            last_claim_time = int(data['last_claim_time'])
            find_bp = True
            break
        rank = rank + 1
    if not find_bp:
        logger.info("%s not found." % (bp_name))
        return


def get_issue_token():
    global pervote_bucket, perblock_bucket
    currency_url = url + "/v1/chain/get_currency_stats"
    response = http.post(currency_url, currency_url, data='{"symbol":"EOS","code":"eosio.token"}')
    supply = float(response.json()['EOS']['supply'][:-4])
    usecs_since_last_fill = ct - last_pervote_bucket_fill
    new_tokens = continuous_rate * supply * usecs_since_last_fill / useconds_per_year
    to_producers = new_tokens / 5
    to_per_block_pay = to_producers / 4
    to_per_vote_pay = to_producers - to_per_block_pay
    pervote_bucket = pervote_bucket + to_per_vote_pay
    perblock_bucket = perblock_bucket + to_per_block_pay


def get_rewards_info():
    global vote_pay, block_pay
    vote_pay = pervote_bucket * bp_vote_weight / total_vote_weight / 10000
    block_pay = perblock_bucket * unpaid_blocks / total_unpaid_blocks / 10000
    get_unclaim_pay(vote_pay, block_pay)


def get_unclaim_pay(vote_pay, block_pay):
    global last_claim_time_str, un_claim_pay
    diff = ct - last_claim_time
    un_claim_pay = 0
    if diff > useconds_per_day:
        un_claim_pay = vote_pay + block_pay
    timestamp_sec = last_claim_time / 1000000
    last_claim_time_str = time.strftime("%F %T %Z", time.localtime(timestamp_sec))


def get_bp_account_info():
    get_global_info()
    get_account_info()
    get_issue_token()
    get_rewards_info()
    Metric.metric(Metric.rank, rank)
    bp = 'bp: %s' % bp_name
    votes = 'votes: %s' % votes2eos(bp_vote_weight)
    rank_info = 'rank: %s' % rank
    vote_rate = 'rate: %s' % (bp_vote_weight / total_vote_weight)
    vote_weight = 'weight: %s' % int(bp_vote_weight)
    all_reward = vote_pay + block_pay
    reward_info = 'reward: %s' % (all_reward)
    claim_info = 'claim: %s' % last_claim_time_str
    un_pay = 'unpay: %s' % un_claim_pay
    if just_get_rewards is None:
        notify(bp, votes, rank_info, vote_rate, vote_weight, reward_info, claim_info, un_pay)
    else:
        print(all_reward)


def votes2eos(votes):
    date = (int(time.time()) - (946684800000 / 1000))
    weight = float(date / (24 * 3600 * 7)) / float(52)
    return (float(votes) / pow(2, weight)) / 10000


def usage():
    global bp_name, url, just_get_rewards
    parser = argparse.ArgumentParser(description='BP account status monitor tool.')
    parser.add_argument('-bp', '--bp_name', default=bp_name, help='bp name')
    parser.add_argument('-u', '--url', default=url, help='node api')
    parser.add_argument('-r', '--rewards', default=None, help='just get rewards amount')
    args = parser.parse_args()
    bp_name = args.bp_name
    url = args.url
    just_get_rewards = args.rewards


def main():
    global rank
    try:
        rank = -1
        get_bp_account_info()
    except Exception as e:
        logger.error("occurs exception:%s" % e)


if __name__ == '__main__':
    usage()
    main()
