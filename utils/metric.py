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
        pass
