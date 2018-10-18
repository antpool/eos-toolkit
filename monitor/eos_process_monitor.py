#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os

import psutil

import init_work_home

work_home = init_work_home.init()
from config.config import Config, BackupConfig
from utils.logger import logger
from utils.metric import Metric

pname = Config.get_process_name()
memory_total_bytes = float(psutil.virtual_memory().total)
memory_total_gb = memory_total_bytes / 1024 / 1024 / 1024

backup_status = '%s/backup/%s' % (work_home, BackupConfig.get_backup_status())


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

    def memory(self):
        memory_percent = process.memory_percent()
        memory_usage_gb = round(memory_total_gb * memory_percent / 100, 2)
        memory_percent = round(memory_percent, 2)
        self.metric_collect(Metric.memory_percent, memory_percent)
        self.metric_collect(Metric.memory_usage, memory_usage_gb)

    def cpu(self):
        cpu_usage_percent = process.cpu_percent(interval=1)
        cpu_usage_percent = round(cpu_usage_percent, 2)
        self.metric_collect(Metric.cpu_percent, cpu_usage_percent)

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
            if os.path.isfile(backup_status):
                logger.info('node is backup, skipped process monitor')
                return
            self.init_process()
            self.cpu()
            self.memory()
            self.connections()
        except Exception as e:
            logger.error('process monitor error: %s', e)


def usage():
    global pname
    parser = argparse.ArgumentParser(description='process cpu/ram/connections monitor tool.')
    parser.add_argument('-n', '--pname', default=pname, help='process name')
    args = parser.parse_args()
    pname = args.pname


def main():
    Monitor(pname).monitor()


if __name__ == '__main__':
    usage()
    main()
