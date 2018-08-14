from logger import logger

try:
    import alicms

    alicms_enable = True
except Exception as e:
    alicms_enable = False
    logger.error(e)


class Metric:
    cpu = 'eos_cpu'
    ram = 'eos_ram'
    connections = 'eos_connections'
    rank = 'eos_bp_rank'
    height_diff = 'eos_height_diff'

    def __init__(self):
        pass

    @staticmethod
    def metric(metric_name, metric_value):
        # add metric collector
        Alicms.metric(metric_name, metric_value)


class Alicms:

    @staticmethod
    def metric(metric_name, metric_value):
        if alicms_enable:
            alicms.metric(metric_name, metric_value)
