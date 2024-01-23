from benchmark.template_local import TemplateLocal
from benchmark.template_global import TemplateGlobal
from benchmark.tpcc.tpcc_tx_no import TPCCTxNO
from benchmark.tpcc.tpcc_tx_pay import TPCCTxPay

tx_settings = [
    {"weight": 50, "transaction_template": TemplateGlobal, "transaction": TPCCTxNO},
    {"weight": 50, "transaction_template": TemplateGlobal, "transaction": TPCCTxPay},
]