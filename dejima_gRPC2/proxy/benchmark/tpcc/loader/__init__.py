from benchmark.tpcc.loader.load_local import LocalLoader
from benchmark.tpcc.loader.load_stock import StockLoader
from benchmark.tpcc.loader.load_customer import CustomerLoader

def load(params):
    # loader
    Loader = {
        "local": LocalLoader,
        "stock": StockLoader,
        "customer": CustomerLoader,
    }

    # param check
    loader_name = params["data_name"]
    if not loader_name in Loader.keys():
        raise Exception("invalid loader name:", loader_name)

    # load
    loader = Loader[loader_name]()
    result = loader.load(params)

    return result
