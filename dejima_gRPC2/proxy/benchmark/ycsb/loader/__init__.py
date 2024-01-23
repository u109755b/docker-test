from benchmark.ycsb.loader.load_ycsb import YCSBLoader

def load(params):
    # load
    loader = YCSBLoader()
    result = loader.load(params)
    return result
