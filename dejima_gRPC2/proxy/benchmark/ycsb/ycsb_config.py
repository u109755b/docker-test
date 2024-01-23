from benchmark.template_global import TemplateGlobal
from benchmark.template_local import TemplateLocal
from benchmark.ycsb.procedures.ycsb_tx import YCSBTx
from benchmark.ycsb.procedures.read_record import ReadRecord
from benchmark.ycsb.procedures.update_record import UpdateRecord

tx_settings = [
    {"weight": 100, "transaction_template": TemplateGlobal, "transaction": YCSBTx},
    # {"weight": 50, "transaction_template": TemplateLocal, "transaction": ReadRecord},
    # {"weight": 50, "transaction_template": TemplateGlobal, "transaction": UpdateRecord},
]