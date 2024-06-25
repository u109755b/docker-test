import sys
from experiment.experiment_tpcc import ExperimentTPCC
from experiment.experiment_ycsb import ExperimentYCSB
from experiment.experiment_tenv import ExperimentTENV


bench_name = sys.argv[1].lower()
command_name = int(sys.argv[2])

if bench_name == "tpcc":
    experiment = ExperimentTPCC(bench_name)
elif bench_name == "ycsb":
    experiment = ExperimentYCSB(bench_name)
elif bench_name == "tenv":
    experiment = ExperimentTENV(bench_name)
else:
    print("invalid bench_name")
    exit()

# 0
if command_name == 0:
    experiment.load_data()

# 1
elif command_name == 1:
    experiment.set_parameters()
    experiment.show_parameter()

    print("")
    experiment.initialize()
    experiment.execute_benchmark("2pl")

    # print("")
    # experiment.initialize()
    # experiment.execute_benchmark("frs")

    # print("")
    # experiment.initialize()
    # experiment.execute_benchmark("hybrid")

    experiment.show_remaining_locks()

# 2  (tenv)
elif command_name == 2:
    # experiment.set_parameters()
    # experiment.initialize()
    experiment.execute_benchmark()

else:
    print("invalid command_name")
