#!/usr/bin/env python
# -*- coding: utf-8 -*

import argparse
import time

import requests

import init_work_home

init_work_home.init()

from config.config import Config
from utils.logger import logger
from utils.metric import Metric
from utils.notify import Notify

continuous_rate = 0.0487
useconds_per_day = 24 * 3600 * 1000000
useconds_per_year = 52 * 7 * 24 * 360 * 1000000


def notify(*args):
    if len(args) < 1:
        return
    logger.info(args)
    Notify.notify(*args)


def get_global_info():
    global total_producer_vote_weight, pervote_bucket, total_unpaid_blocks, perblock_bucket, last_pervote_bucket_fill
    global_url = url + "/v1/chain/get_table_rows"
    response = requests.post(global_url, data='{"scope":"eosio","table":"global","json":true,"code":"eosio","limit":1}',
                             timeout=3.0)
    global_data = response.json()['rows'][0]
    total_producer_vote_weight = float(global_data['total_producer_vote_weight'])
    pervote_bucket = int(global_data['pervote_bucket'])
    perblock_bucket = int(global_data['perblock_bucket'])
    total_unpaid_blocks = int(global_data['total_unpaid_blocks'])
    last_pervote_bucket_fill = int(global_data['last_pervote_bucket_fill'])


def get_issue_token():
    global pervote_bucket, perblock_bucket
    url = api_url + "/v1/chain/get_currency_stats"
    response = requests.post(url, data='{"symbol":"EOS","code":"eosio.token"}')
    supply = float(response.json()['EOS']['supply'][:-4])
    usecs_since_last_fill = ct - last_pervote_bucket_fill
    new_tokens = continuous_rate * supply * usecs_since_last_fill / useconds_per_year
    to_producers = new_tokens / 5
    to_per_block_pay = to_producers / 4
    to_per_vote_pay = to_producers - to_per_block_pay
    pervote_bucket = pervote_bucket + to_per_vote_pay
    perblock_bucket = perblock_bucket + to_per_block_pay


def get_vote_pay():
    global bp_vote_pay, ct
    ct = int(time.time() * 1000000)
    get_global_info()
    get_issue_token()
    bp_vote_pay = pervote_bucket * bp_vote_weight / total_producer_vote_weight / 10000


def get_unclaim_pay():
    global last_claim_time_str, un_claim_pay
    diff = ct - last_claim_time
    un_claim_pay = 0
    if diff > useconds_per_day:
        un_claim_pay = bp_vote_pay + bp_block_pay
    timestamp_sec = last_claim_time / 1000000
    last_claim_time_str = time.strftime("%F %T %Z", time.localtime(timestamp_sec))


def get_block_pay():
    global bp_block_pay
    bp_block_pay = perblock_bucket * unpaid_blocks / total_unpaid_blocks / 10000


def get_rewards_info(bp, url):
    global bpname, api_url
    api_url = url
    bpname = bp
    get_vote_pay()
    get_block_pay()
    get_unclaim_pay()
    reward = 'reward: %s' % (bp_vote_pay + bp_block_pay)
    claim = 'claim: %s' % last_claim_time_str
    unpay = 'unpay: %s' % un_claim_pay
    return reward, claim, unpay


def get_producer_info(url, bp_name):
    global bp_vote_weight, unpaid_blocks, last_claim_time
    get_global_info()
    bp_vote_weight = None
    producers_url = url + "/v1/chain/get_producers"
    response = requests.post(producers_url, data='{"json":true,"limit":600}', timeout=3.0)
    i = 1
    for data in response.json()['rows']:
        if data['owner'] == bp_name:
            bp_vote_weight = float(data['total_votes'])
            unpaid_blocks = int(data['unpaid_blocks'])
            last_claim_time = int(data['last_claim_time'])
            break
        i = i + 1
    if bp_vote_weight is None:
        logger.info("%s not found." % (bp_name))
        return
    Metric.metric(Metric.rank, i)
    bp = 'bp: %s' % bp_name
    votes = 'votes: %s' % votes2eos(bp_vote_weight)
    rank = 'rank: %s' % i
    rate = 'rate: %s' % (bp_vote_weight / total_producer_vote_weight)
    weight = 'weight: %s' % int(bp_vote_weight)
    reward, claim, unpay = get_rewards_info(bp_name, url)
    notify(bp, votes, rank, rate, weight, reward, claim, unpay)


def votes2eos(votes):
    date = (int(time.time()) - (946684800000 / 1000))
    weight = float(date / (24 * 3600 * 7)) / float(52)
    return (float(votes) / pow(2, weight)) / 10000


def usage():
    global bp_name, url
    bp_name = Config.get_bp_account()
    url = Config.get_local_api()
    parser = argparse.ArgumentParser(description='BP account status monitor tool.')
    parser.add_argument('-bp', '--bp_name', default=bp_name, help='bp name')
    parser.add_argument('-u', '--url', default=url, help='node api')
    args = parser.parse_args()
    bp_name = args.bp_name
    url = args.url


def main():
    try:
        get_producer_info(url, bp_name)
    except Exception as e:
        logger.error("occurs exception:%s" % e)


if __name__ == '__main__':
    usage()
    main()
