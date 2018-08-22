import argparse
import logging
import os

import init_work_home

init_work_home.init()
from logging.handlers import TimedRotatingFileHandler

from config.config import LogConfig

log_path = LogConfig.get_log_path()
if not os.path.isdir(log_path):
    os.makedirs(log_path)
log_file = log_path + "/" + LogConfig.get_monitor_log()

level = logging.INFO
simple_format = '%(asctime)s %(levelname)s %(filename)s(%(lineno)d) %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(simple_format, date_format)

logger = logging.getLogger(log_file)
logger.setLevel(level)

file_enable = LogConfig.file_enable()
console_enable = LogConfig.console_enable()
log_enable = file_enable or console_enable
if not log_enable:
    logger.disabled = 1

if file_enable:
    fileHandler = TimedRotatingFileHandler(log_file, when='MIDNIGHT', backupCount=7)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

if console_enable:
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)


def usage():
    global msg
    parser = argparse.ArgumentParser(description='logger tool.')
    parser.add_argument('-m', '--msg', default=None, help='log msg')
    args = parser.parse_args()
    msg = args.msg


if __name__ == "__main__":
    usage()
    if msg is not None:
        logger.info(msg)
