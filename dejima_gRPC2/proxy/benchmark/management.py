import random
from dejima import config
from benchmark.tenv import tenv_config
from benchmark.tpcc import tpcc_config
from benchmark.ycsb import ycsb_config

class BenchmarkManagement:
    def __init__(self, bench_name):
        self.bench_name = bench_name
        # select a config file
        if bench_name == "tenv":
            self.config = tenv_config
        if bench_name == "tpcc":
            self.config = tpcc_config
        if bench_name == "ycsb":
            self.config = ycsb_config


    # get loader
    def get_loader(self, params):
        loader_name = params["data_name"]
        loader = self.config.loaders[loader_name]()
        return loader


    # get tx class
    def get_tx_class(self):
        weights = []
        tx_classes = []

        # read config data
        for tx_setting in self.config.tx_settings:
            weights.append(tx_setting["weight"])
            tx_classes.append(tx_setting["transaction"])
        if sum(weights) != 100:
            raise ValueError("sum of weights must be 100")

        # select specific transaction and return it
        threshold = random.randint(1,100)
        weight_sum = 0
        for i, weight in enumerate(weights):
            self.tx_idx = i
            weight_sum += weight
            if threshold <= weight_sum:
                config.tx_type_count[tx_classes[i].tx_type] += 1
                return tx_classes[i]
