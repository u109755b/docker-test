from dejima.errors import *
from dejima import load_executer
from dejima import bench_executer
from dejima.executer import Executer
from dejima.loader import Loader
from dejima.global_bencher import GlobalBencher
from dejima.local_bencher import LocalBencher

def get_executer(executer_name=None):
    if executer_name == "load":
        return load_executer.LoadExecuter()
    if executer_name == "bench":
        return bench_executer.BenchExecuter()
    return Executer()
