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
    def metric(metric_name, metric_value, producer_name=None):
        try:
            # add metric collector
            Alicms.metric(metric_name, metric_value)
            Prometheus.push_metrics(metric_name, metric_value, producer_name=producer_name)
        except Exception as e:
            logger.error('push metrics error:%s', e)


class Prometheus:
    headers = {'X-Requested-With': 'Python requests', 'Content-type': 'text/xml'}
    action = 'prometheus_metrics'
    hostname = socket.gethostname()

    @staticmethod
    def _submit(metric_name, metric_value):
        host_port = MetricConfig.get_prometheus_host_port()
        if host_port is None or host_port is "":
            return
        url = 'http://%s/metrics/job/%s' % (host_port, metric_name)
        data = '%s\n' % metric_value
        http.post(Prometheus.action, url, data=data, headers=Prometheus.headers)

    @staticmethod
    def push_metrics(metric_name, metric_value, producer_name=None):
        if producer_name is None:
            value = '{hostname="%s"} %s' % (Prometheus.hostname, metric_value)
        else:
            value = '{producer_name="%s",hostname="%s"} %s' % (producer_name, Prometheus.hostname, metric_value)
        value = metric_name + value
        Prometheus._submit(metric_name=metric_name, metric_value=value)


class Alicms:

    @staticmethod
    def metric(metric_name, metric_value):
        if alicms_enable:
            alicms.metric(metric_name, metric_value)
