#!/usr/bin/env python
# -*- coding: utf-8 -*

import subprocess

from apscheduler.schedulers.blocking import BlockingScheduler

import init_work_home

work_home = init_work_home.init()

from config.config import MonitorConfig
from utils.logger import logger
import monitor.node_monitor
import monitor.eos_process_monitor
import monitor.bp_status_monitor
import monitor.bp_block_monitor
import monitor.bidname_status

sched = BlockingScheduler()


def auto_claim():
    claim_command = str(work_home) + '/claim/auto_claim.sh'
    subprocess.call(claim_command)


def init_jobs():
    enable, cron = MonitorConfig.node_monitor()
    add_job(monitor.node_monitor.main, enable, cron, 'node_monitor')

    enable, cron = MonitorConfig.eos_process_monitor()
    add_job(monitor.eos_process_monitor.main, enable, cron, 'eos_process_monitor')

    enable, cron = MonitorConfig.bp_block_monitor()
    add_job(monitor.bp_block_monitor.main, enable, cron, 'bp_block_monitor')

    enable, cron = MonitorConfig.bp_status_monitor()
    add_job(monitor.bp_status_monitor.main, enable, cron, 'bp_status_monitor')

    enable, cron = MonitorConfig.bidname_monitor()
    add_job(monitor.bidname_status.main, enable, cron, 'bidname_monitor')

    enable, cron = MonitorConfig.auto_claim()
    add_job(auto_claim, enable, cron, 'auto_claim')


def add_job(func, enable, cron, id):
    logger.info('%s, %s, %s, %s', func, enable, cron, id)
    if not enable:
        return
    if cron.endswith('s'):
        seconds = int(cron.replace('s', ''))
        sched.add_job(func, 'interval', seconds=seconds, id=id)
    elif cron.endswith('m'):
        minutes = int(cron.replace('m', ''))
        sched.add_job(func, 'interval', minutes=minutes, id=id)
    elif cron.endswith('h'):
        hours = int(cron.replace('h', ''))
        sched.add_job(func, 'interval', hours=hours, id=id)


def start_jobs():
    jobs = sched.get_jobs()
    if jobs:
        logger.info(jobs)
        sched.start()


if __name__ == '__main__':
    init_jobs()
    start_jobs()
