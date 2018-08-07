#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import logging

import psutil


class Log:
    def __init__(self, log):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=log,
            filemode='a')

    def info(self, message):
        logging.info(message)

    def error(self, message):
        logging.error(message)


class Monitor:
    def __init__(self, pid, log):
        self.__pid = int(pid)
        self.__log = log

    def init_process(self):
        global pid, process
        process = psutil.Process(self.__pid)

    def ram(self):
        ram_usage = process.memory_percent()
        ram_usage = round(ram_usage, 2)
        self.__log.info("%s %s" % (self.__pid, ram_usage))
        # add metric collector

    def cpu(self):
        cpu_usage = process.cpu_percent(interval=1)
        cpu_usage = round(cpu_usage, 2)
        self.__log.info("%s %s" % (self.__pid, cpu_usage))
        # add metric collector

    def monitor(self):
        try:
            self.init_process()
            self.cpu()
            self.ram()
        except Exception as e:
            self.__log.error(str(e))


def usage():
    global id, log
    parser = argparse.ArgumentParser(description='process cpu/ram monitor tool.')
    parser.add_argument('-p', '--pid', required=True, help='process pid')
    parser.add_argument('-l', '--log', required=True, help='log file')
    args = parser.parse_args()
    id = args.pid
    log = args.log


if __name__ == '__main__':
    usage()
    Monitor(id, Log(log)).monitor()
