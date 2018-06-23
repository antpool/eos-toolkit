#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import argparse
import json
import sys
import time

continuous_rate = 0.0487
useconds_per_day = 24*3600*1000000
useconds_per_year = 52*7*24*360*1000000

def usage():
    global bpname, api_url
    parser = argparse.ArgumentParser(description='BP Rewards Query Tool.')
    parser.add_argument('-u', '--url', required=True, help='eos api')
    parser.add_argument('-n', '--name', required=True, help='bp name')
    args = parser.parse_args()
    bpname, api_url = args.name, args.url

def get_vote_weight():
    global bp_vote_weight, unpaid_blocks, last_claim_time
    bp_vote_weight = None
    unpaid_blocks = 0
    last_claim_time = 0
    producers_url = api_url+"/v1/chain/get_table_rows"
    response = requests.post(producers_url, data='{"scope":"eosio","table":"producers","json":true,"code":"eosio","limit":10000}')
    for data in response.json()['rows']:
        if data['owner'] == bpname:
            bp_vote_weight = float(data['total_votes'])
            unpaid_blocks = int(data['unpaid_blocks'])
            last_claim_time = int(data['last_claim_time'])
    if bp_vote_weight == None:
        print("%s not found." % (bpname))
        sys.exit()

def get_global_info():
    global total_producer_vote_weight, pervote_bucket, total_unpaid_blocks, perblock_bucket, last_pervote_bucket_fill
    global_url = api_url+"/v1/chain/get_table_rows"
    response = requests.post(global_url, data='{"scope":"eosio","table":"global","json":true,"code":"eosio","limit":1}')
    global_data=response.json()['rows'][0]
    total_producer_vote_weight=float(global_data['total_producer_vote_weight'])
    pervote_bucket=int(global_data['pervote_bucket'])
    perblock_bucket=int(global_data['perblock_bucket'])
    total_unpaid_blocks=int(global_data['total_unpaid_blocks'])
    last_pervote_bucket_fill=int(global_data['last_pervote_bucket_fill'])

def get_issue_token():
    global pervote_bucket, perblock_bucket
    url = api_url+"/v1/chain/get_currency_stats"
    response = requests.post(url, data='{"symbol":"EOS","code":"eosio.token"}')
    supply = float(response.json()['EOS']['supply'][:-4])
    usecs_since_last_fill = ct - last_pervote_bucket_fill
    new_tokens = continuous_rate*supply*useconds_per_day/useconds_per_year
    to_producers = new_tokens / 5;
    to_per_block_pay = to_producers / 4;
    to_per_vote_pay = to_producers - to_per_block_pay;
    pervote_bucket = pervote_bucket + to_per_vote_pay;
    perblock_bucket = perblock_bucket + to_per_block_pay;

def get_vote_pay():
    global bp_vote_pay, ct
    ct = int(time.time() * 1000000)
    print bpname, api_url
    get_vote_weight()
    get_global_info()
    get_issue_token()
    #print("execute(pervote_bucket*prod.total_votes/total_producer_vote_weight): %s*%s/%s/10000" % (pervote_bucket,bp_vote_weight,total_producer_vote_weight))
    bp_vote_pay = pervote_bucket*bp_vote_weight/total_producer_vote_weight/10000
    print "bp_vote_pay:",bp_vote_pay

def get_unclaim_pay():
    diff = ct - last_claim_time
    un_claim_pay = 0
    if diff > useconds_per_day:
        un_claim_pay = bp_vote_pay+bp_block_pay
    timestamp_sec = last_claim_time/1000000
    last_claim_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp_sec))
    print "last_claim_time:", last_claim_time_str
    print "unclaim_pay:",un_claim_pay

def get_block_pay():
    global bp_block_pay
    #print("execute(perblock_bucket*prod.unpaid_blocks/total_unpaid_blocks): %s*%s/%s/10000" % (perblock_bucket,unpaid_blocks,total_unpaid_blocks))
    bp_block_pay = perblock_bucket*unpaid_blocks/total_unpaid_blocks/10000
    print "bp_block_pay:",bp_block_pay

if __name__ == '__main__':
    usage()
    get_vote_pay()
    get_block_pay()
    print 'bp_all_pay:', (bp_vote_pay+bp_block_pay)
    get_unclaim_pay()
