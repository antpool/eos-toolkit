#!/usr/bin/env python
# -*- coding: utf-8 -*

from apscheduler.schedulers.blocking import BlockingScheduler

import init_work_home

init_work_home.init()

from config.config import MonitorConfig
from utils.logger import logger
import node_monitor
import eos_process_monitor
import bp_status_monitor
import bp_block_monitor
import bidname_status

sched = BlockingScheduler()


def init_jobs():
    if MonitorConfig.bp_status_monitor_enable():
        sched.add_job(bp_status_monitor.main, 'interval', minutes=10, id='bp_status_monitor')
    if MonitorConfig.node_monitor_enable():
        sched.add_job(node_monitor.main, 'interval', minutes=5, id='node_monitor')
    if MonitorConfig.eos_process_monitor_enable():
        sched.add_job(eos_process_monitor.main, 'interval', seconds=30, id='process_monitor')
    if MonitorConfig.bp_block_monitor_enable():
        sched.add_job(bp_block_monitor.main, 'interval', minutes=5, id='bp_block_monitor')
    if MonitorConfig.bidname_monitor_enable():
        sched.add_job(bidname_status.main, 'interval', minutes=30, id='bidname')


def start_jobs():
    jobs = sched.get_jobs()
    if jobs:
        logger.info(jobs)
        sched.start()


if __name__ == '__main__':
    init_jobs()
    start_jobs()
