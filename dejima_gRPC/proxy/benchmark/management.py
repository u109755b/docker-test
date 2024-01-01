import random
from benchmark.tpcc import tpcc_config
from benchmark.ycsb import ycsb_config

class BenchmarkManagement:
    def __init__(self, bench_name):
        self.bench_name = bench_name
        # select a config file
        if bench_name == "tpcc":
            self.config = tpcc_config
        if bench_name == "ycsb":
            self.config = ycsb_config

    def get_tx_template(self):
        weights = []
        tx_templates = []

        # read config data
        for tx_setting in self.config.tx_settings:
            weights.append(tx_setting["weight"])
            tx_templates.append(tx_setting["transaction_template"])
        if sum(weights) != 100:
            raise ValueError("sum of weights must be 100")

        # select specific transaction and return it
        threshold = random.randint(1,100)
        weight_sum = 0
        for i, weight in enumerate(weights):
            self.tx_idx = i
            weight_sum += weight
            if threshold <= weight_sum:
                return tx_templates[i]

    def get_tx(self):
        return self.config.tx_settings[self.tx_idx]["transaction"]