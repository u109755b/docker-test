import os
import sys
import argparse
sys.dont_write_bytecode = True
from utils.tpcc.tpcc_env_gen import TPCCEnvGenerator
from utils.ycsb.ycsb_env_gen import YCSBEnvGenerator
from utils.tenv.tenv_env_gen import TENVEnvGenerator

# add root directory to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# types of benchmark
benchmarks = {
    "TENV": TENVEnvGenerator,
    "TPCC": TPCCEnvGenerator,
    "YCSB": YCSBEnvGenerator,
}

# receive arguments and options
parser = argparse.ArgumentParser()
parser.add_argument("benchmark_name", choices=benchmarks.keys(), help="specify which bnehmark environment to create")
parser.add_argument("N", type=int, help="number of peers")
parser.add_argument("-n", "--env_name", help="specify environment name")
parser.add_argument("-y", "--yes", action="store_true", help="automatically answer yes to everything")
args = parser.parse_args()

# generate environment
env_generator = benchmarks[args.benchmark_name](args)
env_generator.generate_env()
