import sys
from experiment.experiment_tpcc import ExperimentTPCC
from experiment.experiment_ycsb import ExperimentYCSB


bench_name = sys.args[1]
command_name = int(sys.args[2])

if bench_name == "tpcc":
    experiment = ExperimentTPCC(bench_name)
if bench_name == "ycsb":
    experiment = ExperimentYCSB(bench_name)

# 0
if command_name == 0:
    experiment.load_data()

# 1
if command_name == 1:
    experiment.set_parameters()
    experiment.show_parameter()

    print("")
    experiment.initialize()
    experiment.execute_benchmark("2pl")

    print("")
    experiment.initialize()
    experiment.execute_benchmark("frs")
