import logging
import os

from config.config import LogConfig

log_path = LogConfig.get_log_path()
if not os.path.isdir(log_path):
    os.makedirs(log_path)
log_file = log_path + "/" + LogConfig.get_monitor_log()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=log_file,
    filemode='a')


def info(message):
    logging.info(message)


def error(message):
    logging.error(message)
