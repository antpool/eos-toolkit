#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from sh import tail

import init_work_home

init_work_home.init()
from config.config import Config
from utils.logger import logger
from utils.metric import Metric

timestamp_pattern = '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}'
eosio_log_file = Config.get_log_file()


class LogParser:
    def __init__(self, logfile):
        self.timestamp_pattern = '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}'
        self.line_pattern = '^\d{4}-\d{2}-\d{2}'
        self.eosio_log_file = logfile

    def handle_line(self, pre_line, line):
        try:
            log = pre_line + line
            if not re.match(self.line_pattern, line):
                return log
            if pre_line == "":
                return line
            log = pre_line
            log_dict = self.extract_log(log)
            self.msg_collect(log_dict['method'], log_dict['message'])
        except Exception as e:
            logger.error('handle line error: %s', e)
        return line

    def msg_collect(self, method, message):
        if method == 'on_incoming_block':
            self.extract_incoming_block(message)

    def extract_incoming_block(self, message):
        pattern = '.*?#(?P<block_header_num>\d+)\s+@\s+(?P<timestamp>{})\s+?signed by\s+?(?P<producer_name>.+?)\s.*' \
                  '\[trxs: (?P<trx_count>\d+), lib: (?P<last_irreversible_block_num>\d+), conf: (?P<confirm_count>\d+), latency: (?P<latency>.*) ms\]' \
            .format(timestamp_pattern)
        if not re.match(pattern, message):
            return
        msg_dict = self.extract_dict(pattern, message)
        if msg_dict is None:
            return
        producer_name = msg_dict['producer_name']
        trx_count = msg_dict['trx_count']
        confirm_count = msg_dict['confirm_count']
        latency = msg_dict['latency']
        logger.info('%s %s %s %s', producer_name, trx_count, confirm_count, latency)
        Metric.metric(Metric.latency, latency, producer_name)
        Metric.metric(Metric.trxs, trx_count, producer_name)

    def extract_log(self, log):
        pattern = '(?P<timestamp>{})\s+(?P<thread_name>thread-\d+)\s+(?P<file>.+):(?P<line>\d+)\s+(?P<method>~*\w+).*\]\s+(?P<message>.*)' \
            .format(self.timestamp_pattern)
        return self.extract_dict(pattern, log)

    def extract_dict(self, pattern, text):
        if text == '':
            return
        res = re.search(pattern, text)
        if res is None:
            logger.info(text)
        return res.groupdict()

    def log_parser(self):
        logger.info("Start LogParser")
        if not os.path.exists(eosio_log_file):
            logger.error("%s not exists", eosio_log_file)
            return
        while True:
            try:
                pre_line = ""
                for line in tail("-n", 1, "-f", eosio_log_file, _iter=True):
                    line = line.rstrip('\n')
                    pre_line = self.handle_line(pre_line, line)
            except Exception as e:
                logger.error("parse failed %s", e)


if __name__ == '__main__':
    LogParser(eosio_log_file).log_parser()
