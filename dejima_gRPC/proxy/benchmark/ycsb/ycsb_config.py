from benchmark.template_global import TemplateGlobal
from benchmark.ycsb.ycsb_tx import YCSBTx

tx_settings = [
    {"weight": 100, "transaction_template": TemplateGlobal, "transaction": YCSBTx},
]