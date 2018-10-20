#!/usr/bin/env python
# -*- coding: utf-8 -*

import subprocess

from apscheduler.schedulers.blocking import BlockingScheduler

import init_work_home

work_home = init_work_home.init()

from config.config import MonitorConfig, BackupConfig
from utils.logger import logger, monitor_log
import monitor.node_monitor
import monitor.eos_process_monitor
import monitor.bp_status_monitor
import monitor.bp_block_monitor
import monitor.bidname_status
import backup.restore

sched = BlockingScheduler()


def auto_claim():
    claim_command = str(work_home) + '/claim/auto_claim.sh'
    subprocess.call(claim_command)


def auto_restart():
    restart_command = str(work_home) + '/monitor/auto_restart.sh'
    subprocess.call(restart_command)


def eos_log_handler():
    backup_command = str(work_home) + '/node/backup_log.sh'
    subprocess.call(backup_command)


def backup_handler():
    backup_command = str(work_home) + '/backup/backup.sh 2>&1 >> ' + monitor_log
    subprocess.call(backup_command)


def backup_job_init():
    if not BackupConfig.enable():
        return
    if BackupConfig.is_client():
        backup_interval_hour = '*/%s' % (BackupConfig.get_backup_interval() + 1)
        sched.add_job(backup.restore.main, 'cron', hour=backup_interval_hour, minute=2, second=0, id='backup_restore')
    else:
        backup_interval_hour = '*/%s' % (BackupConfig.get_backup_interval())
        sched.add_job(backup_handler, 'cron', hour=backup_interval_hour, minute=2, second=0, id='backup')


def blacklist_monitor():
    blacklist_monitor_command = str(work_home) + '/monitor/blacklist_monitor.sh'
    subprocess.call(blacklist_monitor_command)


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

    enable, cron = MonitorConfig.auto_restart()
    add_job(auto_restart, enable, cron, 'auto_restart')

    enable, cron = MonitorConfig.blacklist_monitor()
    add_job(blacklist_monitor, enable, cron, 'blacklist_monitor')

    sched.add_job(eos_log_handler, 'cron', hour=0, minute=0, second=5, id='eos_log_handler')
    backup_job_init()


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
