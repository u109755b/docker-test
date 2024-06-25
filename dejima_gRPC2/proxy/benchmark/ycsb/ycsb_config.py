from benchmark.ycsb.loader.load_ycsb import YCSBLoader

loaders = {
    "ycsb": YCSBLoader,
}


from benchmark.ycsb.procedures.ycsb_tx import YCSBTx
from benchmark.ycsb.procedures.read_record import ReadRecord
from benchmark.ycsb.procedures.update_record import UpdateRecord

tx_settings = [
    {"weight": 0, "transaction": YCSBTx},
    {"weight": 50, "transaction": ReadRecord},
    {"weight": 50, "transaction": UpdateRecord},
]
