import os
import sys
from utils.tpcc_env_gen import TPCCEnvGenerator
from utils.ycsb_env_gen import YCSBEnvGenerator

# add root directory to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)


# get benchmark name
if len(sys.argv) < 2:
    print("At least a argument is required")
    exit()

benchmark = sys.argv[1]
if not benchmark.upper() in ["TPCC", "YCSB"]:
    print("First arg must be benchmark name 'YCSB' or 'TPCC'")
    exit()
benchmark = benchmark.upper()


# generate environment
if benchmark == "TPCC":
    env_generator = TPCCEnvGenerator(sys.argv)
if benchmark == "YCSB":
    env_generator = YCSBEnvGenerator(sys.argv)
env_generator.generate_env()
