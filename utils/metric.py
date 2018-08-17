import socket

import http
from config.config import MetricConfig
from logger import logger

try:
    import alicms

    alicms_enable = True
except Exception as e:
    alicms_enable = False


class Metric:
    cpu_percent = 'eos_cpu_percent'
    memory_percent = 'eos_memory_percent'
    memory_usage = 'eos_memory_usage'
    connections = 'eos_connections'
    rank = 'eos_bp_rank'
    height_diff = 'eos_height_diff'
    latency = 'eos_latency'
    trxs = 'eos_trxs'

    def __init__(self):
        pass

    @staticmethod
    def metric(metric_name, metric_value, producer_name=None, version=None):
        try:
            # add metric collector
            Alicms.metric(metric_name, metric_value)
            Prometheus.push_metrics(metric_name, metric_value, producer_name=producer_name, version=version)
        except Exception as e:
            logger.error('push metrics error:%s', e)


class Prometheus:
    headers = {'X-Requested-With': 'Python requests', 'Content-type': 'text/xml'}
    action = 'prometheus_metrics'
    job = 'nodeos'
    hostname = socket.gethostname()
    instance = hostname

    @staticmethod
    def _submit(metric):
        host_port = MetricConfig.get_prometheus_host_port()
        if host_port is None or host_port is "":
            return
        url = 'http://%s/metrics/job/%s/instance/%s' % (host_port, Prometheus.job, Prometheus.instance)
        data = '%s\n' % metric
        http.post(Prometheus.action, url, data=data, headers=Prometheus.headers)

    @staticmethod
    def push_metrics(metric_name, metric_value, producer_name=None, version=None):
        metric = '%s{hostname="%s"' % (metric_name, Prometheus.hostname)
        if producer_name is not None:
            metric = '%s, producer_name="%s"' % (metric, producer_name)
        if version is not None:
            metric = '%s, version="%s"' % (metric, version)
        metric = '%s} %s' % (metric, metric_value)
        Prometheus._submit(metric)


class Alicms:

    @staticmethod
    def metric(metric_name, metric_value):
        if alicms_enable:
            alicms.metric(metric_name, metric_value)
