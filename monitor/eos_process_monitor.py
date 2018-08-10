#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

import psutil

import init_work_home

init_work_home.init()
from config.config import Config
from utils.logger import logger
from utils.metric import Metric


class Monitor:
    def __init__(self, pname):
        self.pname = str(pname)
        self.pid = None

    def init_pid(self):
        try:
            for p in psutil.process_iter():
                if p.name().lower() == self.pname.lower():
                    self.pid = p.pid
                    break
        except Exception as e:
            logger.error(e)
        if self.pid is None:
            raise Exception(('process(%s) not exists' % self.pname))

    def init_process(self):
        global process
        self.init_pid()
        process = psutil.Process(self.pid)

    def ram(self):
        ram_usage = process.memory_percent()
        ram_usage = round(ram_usage, 2)
        self.metric_collect(Metric.ram, ram_usage)

    def cpu(self):
        cpu_usage = process.cpu_percent(interval=1)
        cpu_usage = round(cpu_usage, 2)
        self.metric_collect(Metric.cpu, cpu_usage)

    def connections(self):
        connections = psutil.net_connections('tcp')
        connection_count = 0
        for sconn in connections:
            if self.pid == sconn.pid:
                connection_count = connection_count + 1
        self.metric_collect(Metric.connections, connection_count)

    def metric_collect(self, key, value):
        logger.info("%s %s %s" % (self.pid, key, value))
        Metric.metric(key, value)

    def monitor(self):
        try:
            self.init_process()
            self.cpu()
            self.ram()
            self.connections()
        except Exception as e:
            logger.error('process monitor error: %s', e)


def usage():
    global pname
    default_name = Config.get_process_name()
    parser = argparse.ArgumentParser(description='process cpu/ram/connections monitor tool.')
    parser.add_argument('-n', '--pname', default=default_name, help='process name')
    args = parser.parse_args()
    pname = args.pname


if __name__ == '__main__':
    usage()
    Monitor(pname).monitor()
