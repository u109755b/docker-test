from benchmark.ycsb.loader.load_ycsb import YCSBLoader

loaders = {
    "ycsb": YCSBLoader,
}


from benchmark.ycsb.procedures.ycsb_tx import YCSBTx
from benchmark.ycsb.procedures.read_record import ReadRecord
from benchmark.ycsb.procedures.update_record import UpdateRecord

tx_settings = [
    {"weight": 20, "transaction": YCSBTx},
    {"weight": 40, "transaction": ReadRecord},
    {"weight": 40, "transaction": UpdateRecord},
]
