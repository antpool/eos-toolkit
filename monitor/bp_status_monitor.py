#!/usr/bin/env python
# -*- coding: utf-8 -*

import argparse
import re
import time

import init_work_home

init_work_home.init()

from config.config import Config
from utils.logger import logger
from utils.metric import Metric
from utils.notify import Notify
from api import eos_api

continuous_rate = 0.0487
useconds_per_day = 24 * 3600 * 1000000
useconds_per_year = 52 * 7 * 24 * 360 * 1000000

ct = int(time.time() * 1000000)
bp_name = Config.get_bp_account()
url = Config.get_local_api()
just_get_rewards = None


def notify(*args):
    logger.info(args)
    Notify.notify_status(*args)


def init_timezone():
    global timezone
    timezone = str(time.strftime("%z", time.localtime()))
    timezone = timezone.replace("+", "")
    timezone = timezone.replace("0", "")
    if not timezone:
        timezone = 0
    else:
        int(timezone)


def timestamp(date):
    pattern = re.compile("\..*")
    result = re.sub(pattern, '', date)
    reformat_date = result.replace("T", " ")
    millions_secs = int(time.mktime(time.strptime(reformat_date, "%Y-%m-%d %H:%M:%S"))) * 1000000
    return millions_secs + int(timezone) * 3600 * 1000000


def get_global_info():
    global total_vote_weight, pervote_bucket, total_unpaid_blocks, perblock_bucket, last_pervote_bucket_fill
    global_data = eos_api.get_global_info(url)
    total_vote_weight = float(global_data['total_producer_vote_weight'])
    pervote_bucket = int(global_data['pervote_bucket'])
    perblock_bucket = int(global_data['perblock_bucket'])
    total_unpaid_blocks = int(global_data['total_unpaid_blocks'])
    last_pervote_bucket_fill = timestamp(global_data['last_pervote_bucket_fill'])


def get_account_info():
    global bp_vote_weight, unpaid_blocks, last_claim_time, rank, find_bp
    rank = 0
    find_bp = False
    producer = eos_api.get_producers(url, account=bp_name, limit=1000)
    if not producer:
        return
    find_bp = True
    rank = int(producer['rank'])
    bp_vote_weight = float(producer['total_votes'])
    unpaid_blocks = int(producer['unpaid_blocks'])
    last_claim_time = timestamp(producer['last_claim_time'])


def get_issue_token():
    global pervote_bucket, perblock_bucket
    response = eos_api.get_currency_stats(url=url, symbol=Config.get_symbol())
    supply = float(response['supply'][:-4])
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
    get_account_info()
    if not find_bp:
        logger.info("%s not found." % (bp_name))
        return
    get_global_info()
    get_issue_token()
    get_rewards_info()
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
        Metric.metric(Metric.rank, rank, bp_name)
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
        init_timezone()
        get_bp_account_info()
    except Exception as e:
        logger.error("occurs exception:%s" % e)


if __name__ == '__main__':
    usage()
    main()
