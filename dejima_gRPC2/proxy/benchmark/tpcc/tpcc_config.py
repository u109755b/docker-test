from benchmark.tpcc.loader.load_local import LocalLoader
from benchmark.tpcc.loader.load_stock import StockLoader
from benchmark.tpcc.loader.load_customer import CustomerLoader

loaders = {
    "local": LocalLoader,
    "stock": StockLoader,
    "customer": CustomerLoader,
}


from benchmark.tpcc.procedures.tpcc_tx_no import TPCCTxNO
from benchmark.tpcc.procedures.tpcc_tx_pay import TPCCTxPay

tx_settings = [
    {"weight": 50, "transaction": TPCCTxNO},
    {"weight": 50, "transaction": TPCCTxPay},
]
