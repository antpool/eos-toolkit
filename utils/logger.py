import argparse
import logging
import os

import init_work_home

init_work_home.init()

from config.config import LogConfig
from MultiprocessHandler import MultiprocessHandler

log_path = LogConfig.get_log_path()
if not os.path.isdir(log_path):
    os.makedirs(log_path)
monitor_log = log_path + "/" + LogConfig.get_monitor_log()
eos_log_parser_log = log_path + "/eos_log_parser.log"

level = logging.INFO
simple_format = '%(asctime)s %(levelname)s %(filename)s(%(lineno)d) %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(simple_format, date_format)

file_enable = LogConfig.file_enable()
console_enable = LogConfig.console_enable()
log_enable = file_enable or console_enable


def get_logger(name=None):
    if name is None:
        log_file = monitor_log
    else:
        log_file = eos_log_parser_log
    logger = logging.getLogger(log_file)
    logger.setLevel(level)
    if not log_enable:
        logger.disabled = 1
    if file_enable:
        file_handler = MultiprocessHandler(log_file, when='D', backupCount=7)
        file_handler.setFormatter(formatter)
        if len(logger.handlers) == 0:
            logger.addHandler(file_handler)
    if console_enable:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        if len(logger.handlers) <= 1:
            logger.addHandler(console_handler)
    return logger


logger = get_logger()


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
