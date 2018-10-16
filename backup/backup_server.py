#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os

from flask import Flask, make_response, send_file

import init_work_home

init_work_home.init()
from config.config import BackupConfig
from utils.logger import monitor_log

logging.basicConfig(filename=monitor_log, level=logging.DEBUG)
backup_home = BackupConfig.get_backup_home()
backup_host = BackupConfig.get_backup_host()
backup_port = BackupConfig.get_backup_port()
app = Flask(__name__)


@app.route("/api/backup/download/<path:file_type>/<path:filename>")
def downloader(file_type, filename):
    file_path = path(file_type, filename)
    if not os.path.isfile(file_path):
        return make_response()
    response = make_response(send_file(file_path))
    response.headers["Content-Disposition"] = "attachment; filename={};".format(filename)
    response.headers["Content-Encoding"] = "gzip"
    response.headers["Content-type"] = "application/octet-stream"
    return response


@app.route("/api/backup/query/<path:file_type>/<path:filename>")
def query_file(file_type, filename):
    return str(os.path.isfile(path(file_type, filename)))


def compare(index1, index2):
    stat_index1 = os.stat(path('indexes', index1))
    stat_index2 = os.stat(path('indexes', index2))
    if stat_index1.st_ctime < stat_index2.st_ctime:
        return 1
    elif stat_index1.st_ctime > stat_index2.st_ctime:
        return -1
    else:
        return 0


@app.route("/api/backup/list")
def query_list():
    return make_response(str(query_index_list()))


@app.route("/api/backup/list/latest")
def query_list_latest():
    indexes = query_index_list()
    if len(indexes):
        return indexes[0]
    return make_response('')


def query_index_list():
    try:
        indexes = os.listdir(path('indexes'))
        indexes.sort(compare)
        return indexes
    except Exception as e:
        app.logger.error('query_index_list error: %s', e)
        return list()


def path(file_type, filename=None):
    if filename:
        return os.path.join(backup_home, file_type, filename)
    return os.path.join(backup_home, file_type)


if __name__ == '__main__':
    app.run(host=backup_host, port=backup_port)
