from benchmark.template_local import TemplateLocal
from benchmark.template_global import TemplateGlobal
from benchmark.tpcc.tpcc_tx_no import TPCCTxNO
from benchmark.tpcc.tpcc_tx_pay import TPCCTxPay

tx_settings = [
    {"weight": 0, "transaction_template": TemplateLocal, "transaction": TPCCTxNO},
    {"weight": 100, "transaction_template": TemplateGlobal, "transaction": TPCCTxPay},
]